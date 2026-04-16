import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createAgent, deleteAgent, updateAgent } from "src/api/agents";
import type { AgentCreate } from "src/api/types";

export function useAgentMutations(simulationId: number) {
    const queryClient = useQueryClient();

    const invalidate = () => {
        queryClient.invalidateQueries({ queryKey: ["simulation", simulationId] });
        queryClient.invalidateQueries({ queryKey: ["agents", simulationId] });
    };

    const createMutation = useMutation({
        mutationFn: (agent: AgentCreate) => createAgent(agent),
        onSuccess: invalidate,
    });

    const deleteMutation = useMutation({
        mutationFn: (agentId: number) => deleteAgent(agentId),
        onSuccess: invalidate,
    });

    const updateMutation = useMutation({
        mutationFn: ({ agentId, agent }: { agentId: number; agent: AgentCreate }) =>
            updateAgent(agentId, agent),
        onSuccess: invalidate,
    });

    return { createMutation, deleteMutation, updateMutation };
}
