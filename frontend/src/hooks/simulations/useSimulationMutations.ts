import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
    createSimulation,
    deleteSimulation,
    updateSimulationName,
    runSimulation,
    createSimulationFromScenario,
} from "src/api/simulations";

/** Мутации для страницы списка симуляций */
export function useSimulationsListMutations() {
    const queryClient = useQueryClient();

    const invalidate = () => {
        queryClient.invalidateQueries({ queryKey: ["simulations"] });
    };

    const createMutation = useMutation({
        mutationFn: (name: string) => createSimulation(name),
        onSuccess: invalidate,
    });

    const createFromScenarioMutation = useMutation({
        mutationFn: (scenarioKey: string) => createSimulationFromScenario(scenarioKey),
        onSuccess: invalidate,
    });

    const deleteMutation = useMutation({
        mutationFn: (simulationId: number) => deleteSimulation(simulationId),
        onSuccess: invalidate,
    });

    const updateNameMutation = useMutation({
        mutationFn: ({ simulationId, name }: { simulationId: number; name: string }) =>
            updateSimulationName(simulationId, name),
        onSuccess: invalidate,
    });

    return { createMutation, createFromScenarioMutation, deleteMutation, updateNameMutation };
}

/** Мутации управления симуляцией (запуск, шаг, пауза и т.д.) */
export function useSimulationControlMutations(simulationId: number) {
    const queryClient = useQueryClient();
    const defaultChunkSize = 10;

    const invalidate = () => {
        queryClient.invalidateQueries({ queryKey: ["simulation", simulationId] });
        queryClient.invalidateQueries({ queryKey: ["agents", simulationId] });
    };

    const runMutation = useMutation({
        mutationFn: async ({
            steps,
            onProgress,
        }: {
            steps: number;
            onProgress?: (completed: number, total: number) => void;
        }) => {
            let completed = 0;
            let lastResponse = null;

            onProgress?.(0, steps);

            while (completed < steps) {
                const chunkSteps = Math.min(defaultChunkSize, steps - completed);
                lastResponse = await runSimulation(simulationId, { steps: chunkSteps });
                completed += chunkSteps;
                onProgress?.(completed, steps);
            }

            return lastResponse;
        },
        onSuccess: invalidate,
    });

    const updateNameMutation = useMutation({
        mutationFn: (name: string) => updateSimulationName(simulationId, name),
        onSuccess: invalidate,
    });

    const deleteMutation = useMutation({
        mutationFn: () => deleteSimulation(simulationId),
    });

    return {
        runMutation,
        updateNameMutation,
        deleteMutation,
    };
}
