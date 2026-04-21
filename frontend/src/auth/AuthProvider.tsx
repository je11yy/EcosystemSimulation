import type { PropsWithChildren } from "react";
import { createContext, useContext } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
    getCurrentUser,
    login as loginRequest,
    logout as logoutRequest,
    register as registerRequest,
    type AuthCredentials,
} from "src/api/auth";
import type { User } from "src/api/types";

type AuthContextValue = {
    user: User | null;
    isLoading: boolean;
    login: (credentials: AuthCredentials) => Promise<void>;
    register: (credentials: AuthCredentials) => Promise<void>;
    logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
    const queryClient = useQueryClient();
    const meQuery = useQuery({
        queryKey: ["auth", "me"],
        queryFn: getCurrentUser,
        retry: false,
    });

    const login = async (credentials: AuthCredentials) => {
        const user = await loginRequest(credentials);
        queryClient.setQueryData(["auth", "me"], user);
    };

    const register = async (credentials: AuthCredentials) => {
        const user = await registerRequest(credentials);
        queryClient.setQueryData(["auth", "me"], user);
    };

    const logout = async () => {
        await logoutRequest();
        queryClient.setQueryData(["auth", "me"], null);
        queryClient.removeQueries({
            predicate: query => query.queryKey[0] !== "auth",
        });
    };

    return (
        <AuthContext.Provider
            value={{
                user: meQuery.data ?? null,
                isLoading: meQuery.isLoading,
                login,
                register,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === null) {
        throw new Error("useAuth must be used inside AuthProvider");
    }
    return context;
}
