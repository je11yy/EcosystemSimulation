import { apiFetch } from "./client";
import type {
    Response,
    ScenarioCreateResponse,
    ScenarioPreset,
    Simulation,
    SimulationDetails,
    Log,
} from "./types";

export function getSimulations(): Promise<Simulation[]> {
    return apiFetch<Simulation[]>("/simulations");
};

export function getSimulation(simulationId: number): Promise<SimulationDetails> {
    return apiFetch<SimulationDetails>(`/simulations/${simulationId}`);
};

export function getSimulationLogs(simulationId: number): Promise<Log[]> {
    return apiFetch<Log[]>(`/simulations/${simulationId}/logs`);
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

export function startSimulation(simulationId: number): Promise<Response> {
	return apiFetch<Response>(`/simulations/${simulationId}/start`, {
		method: "POST",
	});
}

export function buildSimulation(simulationId: number): Promise<Response> {
	return apiFetch<Response>(`/simulations/${simulationId}/build`, {
		method: "POST",
	});
}

export function stepSimulation(simulationId: number): Promise<Response> {
	return apiFetch<Response>(`/simulations/${simulationId}/step`, {
		method: "POST",
	});
}

export function runSimulation(simulationId: number): Promise<Response> {
	return apiFetch<Response>(`/simulations/${simulationId}/run`, {
		method: "POST",
	});
}

export function pauseSimulation(simulationId: number): Promise<Response> {
	return apiFetch<Response>(`/simulations/${simulationId}/pause`, {
		method: "POST",
	});
}

export function stopSimulation(simulationId: number): Promise<Response> {
	return apiFetch<Response>(`/simulations/${simulationId}/stop`, {
		method: "POST",
	});
}
