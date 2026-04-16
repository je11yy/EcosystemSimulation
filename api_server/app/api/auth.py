from fastapi import APIRouter, HTTPException, status
from fastapi import Response as FastAPIResponse
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession
from app.core.config import settings
from app.core.security import create_session_token, hash_password, verify_password
from app.repositories.user import UserRepository
from app.schemas import AuthCredentials, Response, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
async def register(
    credentials: AuthCredentials,
    response: FastAPIResponse,
    db: DbSession,
) -> UserRead:
    users = UserRepository(db)
    existing_user = await users.get_by_nickname(credentials.nickname)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nickname already exists",
        )

    user = await users.create(
        nickname=credentials.nickname,
        hashed_password=hash_password(credentials.password),
    )
    try:
        await db.commit()
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nickname already exists",
        ) from error

    _set_session_cookie(response, user.id)
    return UserRead(id=user.id, nickname=user.nickname)


@router.post("/login", response_model=UserRead)
async def login(
    credentials: AuthCredentials,
    response: FastAPIResponse,
    db: DbSession,
) -> UserRead:
    user = await UserRepository(db).get_by_nickname(credentials.nickname)
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid nickname or password",
        )

    _set_session_cookie(response, user.id)
    return UserRead(id=user.id, nickname=user.nickname)


@router.post("/logout", response_model=Response)
async def logout(response: FastAPIResponse) -> Response:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        httponly=True,
        samesite="lax",
    )
    return Response(success=True, message="Logged out")


@router.get("/me", response_model=UserRead)
async def get_current_user(current_user: CurrentUser) -> UserRead:
    return UserRead(id=current_user.id, nickname=current_user.nickname)


def _set_session_cookie(response: FastAPIResponse, user_id: int) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=create_session_token(user_id),
        max_age=settings.auth_token_ttl_seconds,
        httponly=True,
        samesite="lax",
        secure=False,
    )
