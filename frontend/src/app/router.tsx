import { createBrowserRouter } from "react-router-dom";
import { SimulationsPage } from "../pages/SimulationsPage";
import { SimulationDetailsPage } from "../pages/SimulationDetailsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <SimulationsPage />,
  },
  {
    path: "/simulations/:simulationId",
    element: <SimulationDetailsPage />,
  },
]);