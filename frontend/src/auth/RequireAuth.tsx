import type { PropsWithChildren } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthProvider";

export function RequireAuth({ children }: PropsWithChildren) {
    const { user, isLoading } = useAuth();
    const location = useLocation();

    if (isLoading) {
        return <p>Loading...</p>;
    }

    if (user === null) {
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    return children;
}
