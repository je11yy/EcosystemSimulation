import { apiFetch } from "./client";
import type {
    Response,
    ScenarioCreateResponse,
    ScenarioPreset,
    Simulation,
    SimulationBatchRunRequest,
    SimulationDetails,
} from "./types";

export function getSimulations(): Promise<Simulation[]> {
    return apiFetch<Simulation[]>("/simulations");
};

export function getSimulation(simulationId: number): Promise<SimulationDetails> {
    return apiFetch<SimulationDetails>(`/simulations/${simulationId}`);
};

export function createSimulation(name: string): Promise<Response> {
	return apiFetch<Response>("/simulations", {
		method: "POST",
		body: JSON.stringify({ name }),
	});
};

export function getScenarioPresets(): Promise<ScenarioPreset[]> {
    return apiFetch<ScenarioPreset[]>("/simulations/scenarios");
}

export function createSimulationFromScenario(
    scenarioKey: string,
): Promise<ScenarioCreateResponse> {
    return apiFetch<ScenarioCreateResponse>(`/simulations/scenarios/${scenarioKey}`, {
        method: "POST",
    });
}

export function deleteSimulation(simulationId: number): Promise<Response> {
	return apiFetch<Response>(`/simulations/${simulationId}`, {
		method: "DELETE",
	});
}

export function updateSimulationName(simulationId: number, name: string): Promise<Response> {
	return apiFetch<Response>(`/simulations/${simulationId}/name`, {
		method: "PUT",
		body: JSON.stringify({ name }),
	});
}

export function runSimulation(
    simulationId: number,
    payload: SimulationBatchRunRequest,
): Promise<Response> {
	return apiFetch<Response>(`/simulations/${simulationId}/run`, {
		method: "POST",
		body: JSON.stringify(payload),
	});
}
