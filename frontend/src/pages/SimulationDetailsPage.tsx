import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	deleteAgent,
	getSimulation,
	getSimulationState,
	pauseSimulation,
	runSimulation,
	startSimulation,
	stepSimulation,
	stopSimulation,
} from "../api/simulations";
import type { StepSimulationResponse } from "../api/types";
import { SimulationControls } from "../components/SimulationControls";
import { TerritoryGraph } from "../components/TerritoryGraph";
import { LastStepPanel, type LastStepResult } from "../components/LastStepPanel";
import { CreateTerritoryForm } from "../components/CreateTerritoryForm";
import { CreateAgentForm } from "../components/CreateAgentForm";
import {
	createAgent,
	createTerritory,
	createTerritoryEdge,
	deleteTerritory,
	updateTerritory,
	deleteTerritoryEdge,
} from "../api/simulations";
import { TerritoryDetailsPanel } from "../components/TerritoryDetailsPanel";
import { EdgeDetailsPanel } from "../components/EdgeDetailsPanel";
import { AgentDetailsPanel } from "../components/AgentDetailsPanel";

export function SimulationDetailsPage() {
	const params = useParams();
	const queryClient = useQueryClient();
	const [lastStepResult, setLastStepResult] = useState<LastStepResult | null>(null);
	const [selectedTerritoryId, setSelectedTerritoryId] = useState<string | null>(null);
	const [edgeTargetMode, setEdgeTargetMode] = useState(false);
	const [edgeSourceTerritoryId, setEdgeSourceTerritoryId] = useState<string | null>(null);
	const [selectedEdgeId, setSelectedEdgeId] = useState<number | null>(null);
	const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

	const simulationId = useMemo(() => Number(params.simulationId), [params.simulationId]);

	const simulationQuery = useQuery({
		queryKey: ["simulation", simulationId],
		queryFn: () => getSimulation(simulationId),
		enabled: Number.isFinite(simulationId),
		refetchInterval: 1500,
	});

	const stateQuery = useQuery({
		queryKey: ["simulation-state", simulationId],
		queryFn: () => getSimulationState(simulationId),
		enabled: Number.isFinite(simulationId),
		refetchInterval: 1500,
	});

	const commonOnSuccess = async () => {
		await queryClient.invalidateQueries({ queryKey: ["simulation", simulationId] });
		await queryClient.invalidateQueries({ queryKey: ["simulation-state", simulationId] });
		await queryClient.invalidateQueries({ queryKey: ["simulations", 1] });
	};

	const startMutation = useMutation({
		mutationFn: () => startSimulation(simulationId),
		onSuccess: async () => {
			await commonOnSuccess();
		},
	});

	const stepMutation = useMutation({
		mutationFn: () => stepSimulation(simulationId),
		onSuccess: async (data: StepSimulationResponse) => {
			setLastStepResult(data.step_result);
			await commonOnSuccess();
		},
	});

	const runMutation = useMutation({
		mutationFn: () => runSimulation(simulationId),
		onSuccess: async () => {
			await commonOnSuccess();
		},
	});

	const pauseMutation = useMutation({
		mutationFn: () => pauseSimulation(simulationId),
		onSuccess: async () => {
			await commonOnSuccess();
		},
	});

	const stopMutation = useMutation({
		mutationFn: () => stopSimulation(simulationId),
		onSuccess: async () => {
			await commonOnSuccess();
		},
	});

	const createTerritoryMutation = useMutation({
		mutationFn: (payload: {
			food: number;
			temperature: number;
			food_regen_per_tick: number;
			food_capacity: number;
			x?: number | null;
			y?: number | null;
		}) => createTerritory(simulationId, payload),
		onSuccess: commonOnSuccess,
	});

	const createAgentMutation = useMutation({
		mutationFn: (payload: {
			territory_id: number;
			hunger: number;
			hp: number;
			base_strength: number;
			base_defense: number;
			sex: string;
			pregnant: boolean;
			ticks_to_birth: number;
			father_id?: number | null;
			base_temp_pref: number;
			satisfaction: number;
			alive: boolean;
		}) => createAgent(simulationId, payload),
		onSuccess: commonOnSuccess,
	});

	const deleteAgentMutation = useMutation({
		mutationFn: (agentId: string) => deleteAgent(simulationId, agentId),
		onSuccess: async () => {
			setSelectedAgentId(null);
			await commonOnSuccess();
		},
	});

	const createEdgeMutation = useMutation({
		mutationFn: (payload: {
			source_territory_id: number;
			target_territory_id: number;
			movement_cost: number;
		}) => createTerritoryEdge(simulationId, payload),
		onSuccess: async () => {
			setEdgeTargetMode(false);
			setEdgeSourceTerritoryId(null);
			await commonOnSuccess();
		},
	});

	const updateTerritoryMutation = useMutation({
		mutationFn: (payload: {
			territoryId: number;
			data: {
				food?: number;
				temperature?: number;
				food_regen_per_tick?: number;
				food_capacity?: number;
				x?: number | null;
				y?: number | null;
			};
		}) => updateTerritory(simulationId, payload.territoryId, payload.data),
		onSuccess: commonOnSuccess,
	});

	const deleteTerritoryMutation = useMutation({
		mutationFn: (territoryId: number) => deleteTerritory(simulationId, territoryId),
		onSuccess: async () => {
			setSelectedTerritoryId(null);
			setEdgeTargetMode(false);
			setEdgeSourceTerritoryId(null);
			await commonOnSuccess();
		},
	});

	const deleteEdgeMutation = useMutation({
		mutationFn: (edgeId: number) => deleteTerritoryEdge(simulationId, edgeId),
		onSuccess: async () => {
			setSelectedEdgeId(null);
			await commonOnSuccess();
		},
	});

	const isBusy =
		startMutation.isPending ||
		stepMutation.isPending ||
		runMutation.isPending ||
		pauseMutation.isPending ||
		stopMutation.isPending ||
		createTerritoryMutation.isPending ||
		createAgentMutation.isPending ||
		createEdgeMutation.isPending ||
		updateTerritoryMutation.isPending ||
		deleteTerritoryMutation.isPending ||
		deleteEdgeMutation.isPending ||
		deleteAgentMutation.isPending;

	const selectedTerritory =
		stateQuery.data?.territories.find((territory) => territory.id === selectedTerritoryId) ?? null;

	const selectedEdge =
		stateQuery.data?.territory_edges.find((edge) => edge.id === selectedEdgeId) ?? null;

	const selectedAgent =
		stateQuery.data?.agents.find((agent) => agent.id === selectedAgentId) ?? null;

	const handleTerritoryMoveEnd = (territoryId: string, x: number, y: number) => {
		updateTerritoryMutation.mutate({
			territoryId: Number(territoryId),
			data: { x, y },
		});
	};

	const handleTerritoryClick = (territoryId: string) => {
		setSelectedEdgeId(null);
		setSelectedAgentId(null);

		if (edgeTargetMode && edgeSourceTerritoryId && edgeSourceTerritoryId !== territoryId) {
			createEdgeMutation.mutate({
				source_territory_id: Number(edgeSourceTerritoryId),
				target_territory_id: Number(territoryId),
				movement_cost: 1,
			});
			return;
		}

		setSelectedTerritoryId(territoryId);
	};

	const handleEdgeClick = (edgeId: number) => {
		setSelectedTerritoryId(null);
		setSelectedEdgeId(edgeId);
		setEdgeTargetMode(false);
		setEdgeSourceTerritoryId(null);
		setSelectedAgentId(null);
	};

	return (
		<div style={{ padding: 24 }}>
			<Link to="/">← Назад</Link>

			<h1>Симуляция #{simulationId}</h1>

			{simulationQuery.data && (
				<p>
					статус: <b>{simulationQuery.data.status}</b> | tick: <b>{simulationQuery.data.tick}</b>
				</p>
			)}

			<SimulationControls
				onStart={() => startMutation.mutate()}
				onStep={() => stepMutation.mutate()}
				onRun={() => runMutation.mutate()}
				onPause={() => pauseMutation.mutate()}
				onStop={() => stopMutation.mutate()}
				isBusy={isBusy}
			/>

			{stateQuery.isLoading && <p>Загрузка состояния...</p>}
			{stateQuery.isError && <p>Не удалось загрузить состояние</p>}

			<div style={{ display: "grid", gap: 24 }}>
				<LastStepPanel stepResult={lastStepResult} />

				{stateQuery.data && (
					<>
						<div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
							<CreateTerritoryForm
								onSubmit={(payload) => createTerritoryMutation.mutate(payload)}
								isBusy={isBusy}
							/>
							<CreateAgentForm
								territories={stateQuery.data.territories}
								onSubmit={(payload) => createAgentMutation.mutate(payload)}
								isBusy={isBusy}
							/>
						</div>

						<div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 24 }}>
							<TerritoryGraph
								territories={stateQuery.data.territories}
								edges={stateQuery.data.territory_edges}
								agents={stateQuery.data.agents}
								selectedTerritoryId={selectedTerritoryId}
								selectedEdgeId={selectedEdgeId}
								edgeCreationMode={edgeTargetMode}
								onTerritoryClick={handleTerritoryClick}
								onEdgeClick={handleEdgeClick}
								onTerritoryMoveEnd={handleTerritoryMoveEnd}
							/>

							<div style={{ display: "grid", gap: 24 }}>
								<TerritoryDetailsPanel
									territory={selectedTerritory}
									agents={stateQuery.data.agents}
									selectedAgentId={selectedAgentId}
									edgeTargetMode={edgeTargetMode}
									edgeSourceTerritoryId={edgeSourceTerritoryId}
									onStartEdgeMode={() => {
										if (!selectedTerritoryId) return;
										setSelectedEdgeId(null);
										setEdgeSourceTerritoryId(selectedTerritoryId);
										setEdgeTargetMode(true);
									}}
									onCancelEdgeMode={() => {
										setEdgeTargetMode(false);
										setEdgeSourceTerritoryId(null);
									}}
									onDelete={(territoryId) => deleteTerritoryMutation.mutate(Number(territoryId))}
									onSave={(territoryId, payload) =>
										updateTerritoryMutation.mutate({
											territoryId: Number(territoryId),
											data: payload,
										})
									}
									onAgentClick={(agentId) => {
										setSelectedEdgeId(null);
										setSelectedAgentId(agentId);
									}}
									isBusy={isBusy}
								/>

								<EdgeDetailsPanel
									edge={selectedEdge}
									onDelete={(edgeId) => deleteEdgeMutation.mutate(edgeId)}
									isBusy={isBusy}
								/>

								<AgentDetailsPanel
									agent={selectedAgent}
									onDelete={(agentId) => deleteAgentMutation.mutate(agentId)}
									isBusy={isBusy}
								/>
							</div>
						</div>
					</>
				)}
			</div>
		</div>
	);
}