import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
    createTerritory,
    deleteTerritory,
    updateTerritory,
    updateTerritoryPosition,
    createTerritoriesEdge,
    deleteTerritoriesEdge,
    updateTerritoriesEdgeWeight,
} from "src/api/territories";
import type { TerritoryCreate, TerritoryEdgeCreate } from "src/api/types";
import type { Position } from "src/components/graph/types";

export function useTerritoryMutations(simulationId: number) {
    const queryClient = useQueryClient();

    const invalidate = () => {
        queryClient.invalidateQueries({ queryKey: ["simulation", simulationId] });
    };

    const createMutation = useMutation({
        mutationFn: (territory: TerritoryCreate) =>
            createTerritory({ ...territory, simulation_id: simulationId }),
        onSuccess: invalidate,
    });

    const deleteMutation = useMutation({
        mutationFn: (territoryId: number) => deleteTerritory(territoryId),
        onSuccess: invalidate,
    });

    const updateMutation = useMutation({
        mutationFn: ({ territoryId, territory }: { territoryId: number; territory: TerritoryCreate }) =>
            updateTerritory(territoryId, territory),
        onSuccess: invalidate,
    });

    const updatePositionMutation = useMutation({
        mutationFn: ({ territoryId, position }: { territoryId: number; position: Position }) =>
            updateTerritoryPosition(territoryId, position),
        onSuccess: invalidate,
    });

    const createEdgeMutation = useMutation({
        mutationFn: (edge: TerritoryEdgeCreate) =>
            createTerritoriesEdge({ ...edge, simulation_id: simulationId }),
        onSuccess: invalidate,
    });

    const deleteEdgeMutation = useMutation({
        mutationFn: (edgeId: number) => deleteTerritoriesEdge(edgeId),
        onSuccess: invalidate,
    });

    const updateEdgeWeightMutation = useMutation({
        mutationFn: ({ edgeId, weight }: { edgeId: number; weight: number }) =>
            updateTerritoriesEdgeWeight(edgeId, weight),
        onSuccess: invalidate,
    });

    return {
        createMutation,
        deleteMutation,
        updateMutation,
        updatePositionMutation,
        createEdgeMutation,
        deleteEdgeMutation,
        updateEdgeWeightMutation,
    };
}
