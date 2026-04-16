import { apiFetch } from "./client";
import type { Agent } from "src/components/agent/types";
import type { AgentCreate, Response } from "./types";

export function getAgents(simulationId: number): Promise<Agent[]> {
    return apiFetch<Agent[]>(`/agents?simulation_id=${simulationId}`);
};

export function createAgent(agent: AgentCreate): Promise<Response> {
    return apiFetch<Response>("/agents", {
        method: "POST",
        body: JSON.stringify(agent)
    });
};

export function deleteAgent(agentId: number): Promise<Response> {
    return apiFetch<Response>(`/agents/${agentId}`, {
        method: "DELETE"
    });
};

export function updateAgent(agentId: number, agent: AgentCreate): Promise<Response> {
    return apiFetch<Response>(`/agents/${agentId}`, {
        method: "PUT",
        body: JSON.stringify(agent)
    });
};