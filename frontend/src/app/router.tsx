import { createBrowserRouter } from "react-router-dom";
import { SimulationsPage } from "../pages/SimulationsPage";
import { SimulationDetailsPage } from "../pages/SimulationDetailsPage";
import { GenomeTemplatesPage } from "../pages/GenomeTemplatesPage";
import { GenomeTemplateDetailsPage } from "../pages/GenomeTemplateDetailsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <SimulationsPage />,
  },
  {
    path: "/simulations/:simulationId",
    element: <SimulationDetailsPage />,
  },
  {
    path: "/genome-templates",
    element: <GenomeTemplatesPage />,
  },
  {
    path: "/genome-templates/:templateId",
    element: <GenomeTemplateDetailsPage />,
  },
]);