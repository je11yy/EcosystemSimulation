import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
    createSimulation,
    deleteSimulation,
    updateSimulationName,
    buildSimulation,
    startSimulation,
    stepSimulation,
    runSimulation,
    pauseSimulation,
    stopSimulation,
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

    const invalidate = () => {
        queryClient.invalidateQueries({ queryKey: ["simulation", simulationId] });
        queryClient.invalidateQueries({ queryKey: ["agents", simulationId] });
    };

    const buildMutation = useMutation({
        mutationFn: () => buildSimulation(simulationId),
        onSuccess: invalidate,
    });

    const startMutation = useMutation({
        mutationFn: () => startSimulation(simulationId),
        onSuccess: invalidate,
    });

    const stepMutation = useMutation({
        mutationFn: () => stepSimulation(simulationId),
        onSuccess: invalidate,
    });

    const runMutation = useMutation({
        mutationFn: () => runSimulation(simulationId),
        onSuccess: invalidate,
    });

    const pauseMutation = useMutation({
        mutationFn: () => pauseSimulation(simulationId),
        onSuccess: invalidate,
    });

    const stopMutation = useMutation({
        mutationFn: () => stopSimulation(simulationId),
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
        buildMutation,
        startMutation,
        stepMutation,
        runMutation,
        pauseMutation,
        stopMutation,
        updateNameMutation,
        deleteMutation,
    };
}
