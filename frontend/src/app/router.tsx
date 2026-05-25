import { lazy } from "react";
import { createBrowserRouter } from "react-router-dom";
import { App } from "../App";
import { RequireAuth } from "src/auth/RequireAuth";

const SimulationPage = lazy(async () => ({
    default: (await import("src/pages/Simulation")).SimulationPage,
}));
const SimulationsPage = lazy(async () => ({
    default: (await import("src/pages/Simulations")).SimulationsPage,
}));
const GenomesPage = lazy(async () => ({
    default: (await import("src/pages/Genomes")).GenomesPage,
}));
const GenomePage = lazy(async () => ({
    default: (await import("src/pages/Genome")).GenomePage,
}));
const LoginPage = lazy(async () => ({
    default: (await import("src/pages/Login")).LoginPage,
}));

export const router = createBrowserRouter([
    {
        path: "/",
        element: <App />,
        children: [
            {
                index: true,
                element: <RequireAuth><SimulationsPage /></RequireAuth>,
            },
            {
                path: "login",
                element: <LoginPage />,
            },
            {
                path: "simulations",
                element: <RequireAuth><SimulationsPage /></RequireAuth>,
            },
            {
                path: "simulations/:simulationId",
                element: <RequireAuth><SimulationPage /></RequireAuth>,
            },
            {
                path: "genomes",
                element: <RequireAuth><GenomesPage /></RequireAuth>,
            },
            {
                path: "genomes/:genomeId",
                element: <RequireAuth><GenomePage /></RequireAuth>,
            },
        ],
    },
]);
