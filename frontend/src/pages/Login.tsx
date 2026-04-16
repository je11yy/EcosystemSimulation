import type { FormEvent } from "react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "src/auth/AuthProvider";

type LoginLocationState = {
    from?: {
        pathname: string;
    };
};

export function LoginPage() {
    const { t } = useTranslation();
    const { user, login, register } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    const [nickname, setNickname] = useState("");
    const [password, setPassword] = useState("");
    const [mode, setMode] = useState<"login" | "register">("login");
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const redirectTo = (location.state as LoginLocationState | null)?.from?.pathname ?? "/simulations";

    if (user !== null) {
        return <Navigate to={redirectTo} replace />;
    }

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError(null);
        setIsSubmitting(true);
        try {
            const credentials = { nickname, password };
            if (mode === "login") {
                await login(credentials);
            } else {
                await register(credentials);
            }
            navigate(redirectTo, { replace: true });
        } catch (submitError) {
            setError(submitError instanceof Error ? submitError.message : t("auth_error"));
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <main style={{ maxWidth: 360, margin: "48px auto", display: "grid", gap: 12 }}>
            <h1>{mode === "login" ? t("login") : t("register")}</h1>
            <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
                <input
                    value={nickname}
                    onChange={event => setNickname(event.target.value)}
                    placeholder={t("nickname")}
                    minLength={3}
                    maxLength={64}
                    required
                />
                <input
                    value={password}
                    onChange={event => setPassword(event.target.value)}
                    placeholder={t("password")}
                    type="password"
                    minLength={6}
                    maxLength={128}
                    required
                />
                <button type="submit" disabled={isSubmitting}>
                    {mode === "login" ? t("login") : t("register")}
                </button>
            </form>
            <button
                type="button"
                onClick={() => setMode(mode === "login" ? "register" : "login")}
            >
                {mode === "login" ? t("create_account") : t("already_have_account")}
            </button>
            {error && <p>{error}</p>}
        </main>
    );
}
