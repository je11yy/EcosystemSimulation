import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useAuth } from "src/auth/AuthProvider";

export function Menu() {
    const { t } = useTranslation();
    const { user, logout } = useAuth();

    return (
        <nav className="top-nav">
            <svg className="icon" xmlns="http://www.w3.org/2000/svg" version="1.0" viewBox="0 0 512.000000 512.000000" preserveAspectRatio="xMidYMid meet">
                <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)" fill="#ffffff" stroke="none">
                    <path d="M1144 4759 c-148 -128 -328 -377 -454 -629 -285 -568 -325 -1111 -119 -1628 119 -299 242 -496 420 -674 l117 -117 -19 -73 c-22 -82 -55 -263 -64 -353 -6 -53 -4 -64 15 -88 19 -24 29 -28 63 -25 58 4 73 30 92 168 51 361 182 757 355 1070 537 973 1543 1577 2761 1656 l106 7 26 -134 c62 -314 82 -536 74 -842 -8 -337 -47 -579 -138 -852 -186 -557 -533 -976 -1056 -1277 -230 -132 -447 -212 -688 -253 -209 -36 -490 -36 -682 0 -95 18 -333 93 -333 105 0 4 35 31 78 61 564 385 1093 948 1451 1542 94 156 111 191 111 225 0 55 -79 94 -122 60 -8 -7 -39 -56 -68 -108 -73 -131 -261 -413 -363 -543 -567 -726 -1286 -1263 -2062 -1541 -137 -50 -165 -69 -165 -118 0 -35 40 -78 73 -78 24 0 151 43 287 98 165 66 433 198 572 281 l36 22 69 -34 c211 -106 457 -157 768 -157 340 0 582 47 844 163 753 334 1233 890 1441 1671 131 492 133 1173 3 1720 -32 138 -40 146 -138 146 -184 0 -617 -62 -874 -125 -498 -122 -968 -345 -1314 -622 -38 -30 -70 -53 -71 -51 -2 1 -11 50 -21 108 -80 486 -323 905 -659 1132 -75 52 -218 119 -266 125 -32 5 -42 0 -86 -38z m317 -258 c270 -204 482 -601 543 -1022 28 -186 30 -177 -77 -289 -312 -324 -552 -712 -718 -1159 l-54 -143 -75 79 c-109 115 -201 249 -280 408 -81 163 -118 267 -154 427 -89 398 -34 810 163 1213 100 204 240 411 379 557 l55 58 76 -40 c42 -22 106 -62 142 -89z"/>
                </g>
            </svg>
            <Link className="simulations-menu-item" to="/simulations">{t("simulations")}</Link>
            <Link className="genomes-menu-item" to="/genomes">{t("genomes")}</Link>
            {user ? (
                <div className="nav-user">
                    <span className="user-pill">{user.nickname}</span>
                    <button type="button" onClick={() => void logout()}>
                        {t("logout")}
                    </button>
                </div>
            ) : (
                <Link to="/login">{t("login")}</Link>
            )}
        </nav>
    );
}
