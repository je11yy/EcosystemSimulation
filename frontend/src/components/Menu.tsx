import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useAuth } from "src/auth/AuthProvider";

export function Menu() {
    const { t } = useTranslation();
    const { user, logout } = useAuth();

    return (
        <nav className="top-nav">
            <Link to="/simulations">{t("simulations")}</Link>
            <Link to="/genomes">{t("genomes")}</Link>
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
