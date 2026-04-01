import { apiFetch } from "./client";
import type {
	SimulationRead,
	SimulationStateResponse,
	StartSimulationResponse,
	StepSimulationResponse,
	StopSimulationResponse,
	TerritoryCreatePayload,
	AgentCreatePayload,
	TerritoryEdgeCreatePayload,
	TerritoryUpdatePayload,
	SimulationPresetCreatePayload,
	SimulationStateStepSnapshot,
} from "./types";

export function getSimulations(userId: number): Promise<SimulationRead[]> {
	return apiFetch<SimulationRead[]>(`/simulations?user_id=${userId}`);
}

export function createSimulation(userId: number, name: string): Promise<SimulationRead> {
	return apiFetch<SimulationRead>(`/simulations?user_id=${userId}`, {
		method: "POST",
		body: JSON.stringify({ name }),
	});
}

export function getSimulation(simulationId: number): Promise<SimulationRead> {
	return apiFetch<SimulationRead>(`/simulations/${simulationId}`);
}

export function getSimulationState(
	simulationId: number
): Promise<SimulationStateResponse & SimulationStateStepSnapshot> {
	return apiFetch<SimulationStateResponse & SimulationStateStepSnapshot>(
		`/simulations/${simulationId}/state`
	);
}

export function startSimulation(simulationId: number): Promise<StartSimulationResponse> {
	return apiFetch<StartSimulationResponse>(`/simulations/${simulationId}/start`, {
		method: "POST",
	});
}

export function stepSimulation(simulationId: number): Promise<StepSimulationResponse> {
	return apiFetch<StepSimulationResponse>(`/simulations/${simulationId}/step`, {
		method: "POST",
	});
}

export function runSimulation(simulationId: number): Promise<{ simulation_id: number; status: string; started: boolean }> {
	return apiFetch(`/simulations/${simulationId}/run`, {
		method: "POST",
	});
}

export function pauseSimulation(simulationId: number): Promise<{ simulation_id: number; status: string; loop_stopped: boolean }> {
	return apiFetch(`/simulations/${simulationId}/pause`, {
		method: "POST",
	});
}

export function stopSimulation(simulationId: number): Promise<StopSimulationResponse> {
	return apiFetch<StopSimulationResponse>(`/simulations/${simulationId}/stop`, {
		method: "POST",
	});
}

export function createTerritory(simulationId: number, payload: TerritoryCreatePayload) {
	return apiFetch(`/simulations/${simulationId}/territories`, {
		method: "POST",
		body: JSON.stringify(payload),
	});
}

export function createAgent(simulationId: number, payload: AgentCreatePayload) {
	return apiFetch(`/simulations/${simulationId}/agents`, {
		method: "POST",
		body: JSON.stringify(payload),
	});
}

export function createTerritoryEdge(simulationId: number, payload: TerritoryEdgeCreatePayload) {
	return apiFetch(`/simulations/${simulationId}/edges`, {
		method: "POST",
		body: JSON.stringify(payload),
	});
}

export function updateTerritory(
	simulationId: number,
	territoryId: number,
	payload: TerritoryUpdatePayload
) {
	return apiFetch(`/simulations/${simulationId}/territories/${territoryId}`, {
		method: "PATCH",
		body: JSON.stringify(payload),
	});
}

export function deleteTerritory(simulationId: number, territoryId: number) {
	return apiFetch(`/simulations/${simulationId}/territories/${territoryId}`, {
		method: "DELETE",
	});
}

export function deleteTerritoryEdge(simulationId: number, edgeId: number) {
	return apiFetch(`/simulations/${simulationId}/edges/${edgeId}`, {
		method: "DELETE",
	});
}

export function deleteAgent(simulationId: number, agentId: string) {
	return apiFetch(`/simulations/${simulationId}/agents/${agentId}`, {
		method: "DELETE",
	});
}

export function createSimulationFromPreset(
	userId: number,
	payload: SimulationPresetCreatePayload
): Promise<SimulationRead> {
	return apiFetch<SimulationRead>(`/simulations/preset?user_id=${userId}`, {
		method: "POST",
		body: JSON.stringify(payload),
	});
}