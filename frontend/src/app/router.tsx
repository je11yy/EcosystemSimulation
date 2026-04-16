import { createBrowserRouter } from "react-router-dom";
import { App } from "../App";
import { SimulationPage } from "src/pages/Simulation";
import { SimulationsPage } from "src/pages/Simulations";
import { GenomesPage } from "src/pages/Genomes";
import { GenomePage } from "src/pages/Genome";
import { LoginPage } from "src/pages/Login";
import { RequireAuth } from "src/auth/RequireAuth";

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
