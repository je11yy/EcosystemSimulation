import { apiFetch } from "./client";
import type { User, Response } from "./types";

export type AuthCredentials = {
    nickname: string;
    password: string;
};

export async function getCurrentUser(): Promise<User | null> {
    try {
        return await apiFetch<User>("/auth/me");
    } catch (error) {
        if (error instanceof Error && error.message.startsWith("API error 401:")) {
            return null;
        }
        throw error;
    }
}

export function login(credentials: AuthCredentials): Promise<User> {
    return apiFetch<User>("/auth/login", {
        method: "POST",
        body: JSON.stringify(credentials),
    });
}

export function register(credentials: AuthCredentials): Promise<User> {
    return apiFetch<User>("/auth/register", {
        method: "POST",
        body: JSON.stringify(credentials),
    });
}

export function logout(): Promise<Response> {
    return apiFetch<Response>("/auth/logout", {
        method: "POST",
    });
}
