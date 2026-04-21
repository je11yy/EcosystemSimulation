import type { Territory } from "src/components/territory/types";
import { apiFetch } from "./client";
import type { Response, TerritoryCreate, TerritoryEdgeCreate, TerritoryEdge } from "./types";
import type { Position } from "src/components/graph/types";

export function getTerritories(simulationId: number): Promise<Territory[]> {
    return apiFetch<Territory[]>(`/territories?simulation_id=${simulationId}`);
};

export function createTerritory(territory: TerritoryCreate): Promise<Response> {
    return apiFetch<Response>("/territories", {
        method: "POST",
        body: JSON.stringify(territory)
    });
};

export function deleteTerritory(territoryId: number): Promise<Response> {
    return apiFetch<Response>(`/territories/${territoryId}`, {
        method: "DELETE"
    });
};

export function updateTerritory(territoryId: number, territory: TerritoryCreate): Promise<Response> {
    return apiFetch<Response>(`/territories/${territoryId}`, {
        method: "PUT",
        body: JSON.stringify(territory)
    });
}

export function updateTerritoryPosition(territoryId: number, position: Position): Promise<Response> {
    return apiFetch<Response>(`/territories/${territoryId}/position`, {
        method: "PUT",
        body: JSON.stringify(position)
    });
}

export function getTerritoriesEdges(simulationId: number): Promise<TerritoryEdge[]> {
    return apiFetch<TerritoryEdge[]>(`/territories/edges?simulation_id=${simulationId}`);
}

export function createTerritoriesEdge(territoryEdge: TerritoryEdgeCreate): Promise<Response> {
    return apiFetch<Response>("/territories/edges", {
        method: "POST",
        body: JSON.stringify(territoryEdge)
    });
}

export function deleteTerritoriesEdge(id: number): Promise<Response> {
    return apiFetch<Response>(`/territories/edges/${id}`, {
        method: "DELETE"
    });
}

export function updateTerritoriesEdgeWeight(id: number, weight: number): Promise<Response> {
    return apiFetch<Response>(`/territories/edges/${id}`, {
        method: "PUT",
        body: JSON.stringify({ weight })
    });
}