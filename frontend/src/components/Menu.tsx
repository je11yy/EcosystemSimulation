import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useAuth } from "src/auth/AuthProvider";

export function Menu() {
    const { t } = useTranslation();
    const { user, logout } = useAuth();

    return (
        <nav style={{ display: "flex", gap: 16, padding: 16, backgroundColor: "#eee" }}>
            <Link to="/simulations">{t("simulations")}</Link>
            <Link to="/genomes">{t("genomes")}</Link>
            {user ? (
                <>
                    <span>{user.nickname}</span>
                    <button type="button" onClick={() => void logout()}>
                        {t("logout")}
                    </button>
                </>
            ) : (
                <Link to="/login">{t("login")}</Link>
            )}
        </nav>
    );
}
