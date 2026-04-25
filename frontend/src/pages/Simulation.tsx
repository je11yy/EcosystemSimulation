import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import type { Territory } from "../components/territory/types";
import type { Agent } from "../components/agent/types";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { TerritoryGraphComponent } from "src/components/territory/Graph";
import type { Edge as GraphEdge } from "src/components/graph/types";
import { TerritoryDetails } from "src/components/territory/Details";
import { Modal } from "src/components/Modal";
import { AgentSmallDetails } from "src/components/agent/SmallDetails";
import { getSimulation } from "src/api/simulations";
import { getAgents } from "src/api/agents";
import { getAvailableGenomes } from "src/api/genomes";
import type { SimulationDetails, TickAgentSnapshot } from "src/api/types";
import { NewTerritory } from "src/components/forms/Territory";
import { NewAgent } from "src/components/forms/Agent";
import { NewEdgeWeight } from "src/components/forms/Edge";
import { StepResult } from "src/components/simulation/StepResult";
import { MetricsCharts } from "src/components/simulation/MetricsCharts";
import { useTerritoryMutations } from "src/hooks/territories/useTerritoryMutations";
import { useAgentMutations } from "src/hooks/agents/useAgentMutations";
import { useSimulationControlMutations } from "src/hooks/simulations/useSimulationMutations";

type SimulationModal = "territory" | "edge-weight" | "edge-editor" | "agent" | null;
type EdgeDraft = { source: number; target: number } | null;
type EdgePortOverrides = Record<string, { source: number; target: number }>;
type RunProgress = { completed: number; total: number } | null;
type DisplayedTerritoryEdge = GraphEdge & {
    edgeIds?: number[];
    displayKey?: string;
};
type DisplayedAgent = Pick<
    TickAgentSnapshot,
    "id" | "sex" | "territory_id" | "hunger" | "hp" | "satisfaction" | "is_alive"
>;

export function SimulationPage() {
    const { t } = useTranslation();

    const params = useParams();
    const simulationId = useMemo(() => Number(params.simulationId), [params.simulationId]);
    const [selectedTerritory, setSelectedTerritory] = useState<Territory | null>(null);
    const [activeModal, setActiveModal] = useState<SimulationModal>(null);
    const [isEditingTerritory, setIsEditingTerritory] = useState(false);
    const [isEdgeMode, setIsEdgeMode] = useState(false);
    const [edgeSourceId, setEdgeSourceId] = useState<number | null>(null);
    const [edgeDraft, setEdgeDraft] = useState<EdgeDraft>(null);
    const [selectedEdgeId, setSelectedEdgeId] = useState<number | null>(null);
    const [stepsToRun, setStepsToRun] = useState<string>("");
    const [selectedTick, setSelectedTick] = useState<number | null>(null);
    const [isEditMode, setIsEditMode] = useState(false);
    const [runProgress, setRunProgress] = useState<RunProgress>(null);
    const [edgePortOverrides, setEdgePortOverrides] = useState<EdgePortOverrides>(() => {
        if (!Number.isFinite(simulationId)) {
            return {};
        }
        if (typeof window === "undefined") {
            return {};
        }
        try {
            const raw = window.localStorage.getItem(`simulation-edge-ports:${simulationId}`);
            return raw ? JSON.parse(raw) : {};
        } catch {
            return {};
        }
    });

    const simulationQuery = useQuery({
        queryKey: ["simulation", simulationId],
        queryFn: () => getSimulation(simulationId),
        enabled: Number.isFinite(simulationId),
    });

    const agentsQuery = useQuery({
        queryKey: ["agents", simulationId],
        queryFn: () => getAgents(simulationId),
        enabled: Number.isFinite(simulationId),
    });

    const availableGenomesQuery = useQuery({
        queryKey: ["genomes", "available"],
        queryFn: getAvailableGenomes,
    });

    const territoryMutations = useTerritoryMutations(simulationId);
    const agentMutations = useAgentMutations(simulationId);
    const simulationMutations = useSimulationControlMutations(simulationId);

    const territories = simulationQuery.data?.territories ?? [];
    const territoriesEdges = simulationQuery.data?.territories_edges ?? [];
    const logs = simulationQuery.data?.logs ?? [];
    const agents = agentsQuery.data ?? [];
    const selectedLog = useMemo(
        () => logs.find((log) => log.tick === selectedTick) ?? logs.at(-1) ?? null,
        [logs, selectedTick],
    );
    const latestTick = logs.at(-1)?.tick ?? null;
    const isViewingLatestTick = selectedLog === null || selectedLog.tick === latestTick;

    useEffect(() => {
        if (logs.length === 0) {
            setSelectedTick(null);
            return;
        }
        if (selectedTick === null || !logs.some((log) => log.tick === selectedTick)) {
            setSelectedTick(logs.at(-1)?.tick ?? null);
        }
    }, [logs, selectedTick]);

    useEffect(() => {
        if (!Number.isFinite(simulationId) || typeof window === "undefined") {
            return;
        }
        window.localStorage.setItem(
            `simulation-edge-ports:${simulationId}`,
            JSON.stringify(edgePortOverrides),
        );
    }, [simulationId, edgePortOverrides]);

    const displayedTerritories = useMemo(() => {
        if (!selectedLog?.snapshot?.territories) {
            return territories;
        }
        const baseById = new Map(territories.map((territory) => [territory.id, territory]));
        return selectedLog.snapshot.territories.map((territorySnapshot) => {
            const base = baseById.get(territorySnapshot.id);
            return {
                ...base,
                ...territorySnapshot,
                position: base?.position ?? { x: 100, y: 100 },
            } satisfies Territory;
        });
    }, [selectedLog, territories]);

    const displayedAgents = useMemo(() => {
        if (!selectedLog?.snapshot?.agents) {
            return agents.map<DisplayedAgent>((agent) => ({
                id: agent.id,
                sex: agent.sex,
                territory_id: agent.territory_id,
                hunger: agent.hunger,
                hp: agent.hp,
                satisfaction: agent.satisfaction,
                is_alive: agent.is_alive,
            }));
        }
        return selectedLog.snapshot.agents.map<DisplayedAgent>((agent) => ({
            id: agent.id,
            sex: agent.sex,
            territory_id: agent.territory_id,
            hunger: agent.hunger,
            hp: agent.hp,
            satisfaction: agent.satisfaction,
            is_alive: agent.is_alive,
        }));
    }, [selectedLog, agents]);

    const agentsForTerritoryOccupancy = useMemo(() => {
        if (isViewingLatestTick) {
            return agents.map<DisplayedAgent>((agent) => ({
                id: agent.id,
                sex: agent.sex,
                territory_id: agent.territory_id,
                hunger: agent.hunger,
                hp: agent.hp,
                satisfaction: agent.satisfaction,
                is_alive: agent.is_alive,
            }));
        }

        return displayedAgents;
    }, [agents, displayedAgents, isViewingLatestTick]);

    const graph = useMemo(() => {
        const occupantCountByTerritory = new Map<number, number>();
        for (const agent of agentsForTerritoryOccupancy) {
            if (!agent.is_alive) {
                continue;
            }
            occupantCountByTerritory.set(
                agent.territory_id,
                (occupantCountByTerritory.get(agent.territory_id) ?? 0) + 1,
            );
        }

        const enrichedTerritories = displayedTerritories.map((territory: Territory) => ({
            ...territory,
            occupant_count: occupantCountByTerritory.get(territory.id) ?? 0,
        }));
        const displayedEdges: DisplayedTerritoryEdge[] = buildDisplayedTerritoryEdges(territoriesEdges).map((edge) => {
            const portOverride = edge.displayKey ? edgePortOverrides[edge.displayKey] : undefined;
            return {
                ...edge,
                sourcePortOffset: portOverride?.source ?? 0,
                targetPortOffset: portOverride?.target ?? 0,
            };
        });

        return {
            nodes: layoutTerritoriesByEdgeWeight(enrichedTerritories, territoriesEdges),
            edges: displayedEdges,
        };
    }, [agentsForTerritoryOccupancy, displayedTerritories, edgePortOverrides, territoriesEdges]);

    const territoryById = new Map(graph.nodes.map((t: Territory) => [t.id, t]));
    const territoryOptions = territories.map((territory: Territory) => ({
        id: territory.id,
        name: `${t("territory")} ${territory.id}`,
    }));
    const availableGenomeOptions = availableGenomesQuery.data ?? [];
    const selectedNodeId = edgeSourceId ?? selectedTerritory?.id ?? null;
    const selectedEdge = graph.edges.find((edge) => edge.id === selectedEdgeId) ?? null;

    const resetEdgeMode = () => {
        setIsEdgeMode(false);
        setEdgeSourceId(null);
        setEdgeDraft(null);
    };

    const handleTerritoryClick = (territoryId: number) => {
        setSelectedEdgeId(null);
        if (!isEdgeMode) {
            setSelectedTerritory(territoryById.get(territoryId) || null);
            setIsEditingTerritory(false);
            return;
        }

        if (edgeSourceId === null) {
            setEdgeSourceId(territoryId);
            setSelectedTerritory(null);
            return;
        }

        if (edgeSourceId === territoryId) {
            setEdgeSourceId(null);
            return;
        }

        setEdgeDraft({ source: edgeSourceId, target: territoryId });
        setActiveModal("edge-weight");
    };

    const edgeDraftSource = edgeDraft ? territoryById.get(edgeDraft.source) : null;
    const edgeDraftTarget = edgeDraft ? territoryById.get(edgeDraft.target) : null;
    const selectedEdgeSource = selectedEdge ? territoryById.get(selectedEdge.source) : null;
    const selectedEdgeTarget = selectedEdge ? territoryById.get(selectedEdge.target) : null;
    const isSimulationControlBusy = simulationMutations.runMutation.isPending;
    const simulationControlError = simulationMutations.runMutation.error;
    const runProgressPercent = runProgress ? Math.round((runProgress.completed / runProgress.total) * 100) : 0;
    const selectedTickDisplay = (selectedLog?.tick ?? logs[logs.length - 1]?.tick ?? 0) + 1;

    return (
        <div>
            <div className="simulation-header">
                <h1>{simulationQuery.data?.name ?? t('simulation')}</h1>
                {isViewingLatestTick && (
                    <button
                        onClick={() => setIsEditMode(!isEditMode)}
                        style={{ marginLeft: 8, fontSize: '1.2em', border: 'none', background: 'none', cursor: 'pointer' }}
                        title={isEditMode ? t('exit_edit_mode') : t('enter_edit_mode')}
                    >
                        <svg className="icon" xmlns="http://www.w3.org/2000/svg" version="1.0" width="512.000000pt" height="512.000000pt" viewBox="0 0 512.000000 512.000000" preserveAspectRatio="xMidYMid meet">
                            <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)" stroke="none">
                                <path d="M3810 4678 c-51 -19 -153 -118 -1597 -1561 l-1541 -1540 -21 -81 c-74 -295 -221 -942 -221 -972 0 -49 45 -94 94 -94 34 0 993 221 1039 240 12 4 713 701 1558 1547 1711 1714 1582 1573 1582 1718 0 129 -15 151 -321 456 -244 243 -272 268 -325 288 -75 27 -172 27 -247 -1z m173 -199 c31 -16 475 -459 493 -491 8 -15 14 -44 14 -64 0 -36 -15 -52 -332 -371 -183 -183 -337 -333 -343 -333 -13 0 -595 582 -595 595 0 13 637 649 665 664 26 14 71 14 98 0z m-618 -1119 l300 -300 -1098 -1098 -1099 -1099 -390 -92 c-215 -50 -393 -90 -395 -88 -2 3 37 179 87 393 l92 389 1096 1098 c603 603 1099 1097 1102 1097 3 0 140 -135 305 -300z" />
                                <path d="M1758 623 c-56 -35 -66 -117 -19 -164 l29 -29 1636 0 c1183 0 1642 3 1660 11 60 28 71 122 20 170 l-26 24 -1636 2 c-1512 2 -1639 1 -1664 -14z" />
                            </g>
                        </svg>
                    </button>
                )}
                {!isEditMode && (
                    <div className="simulation-run-panel">
                        <label htmlFor="simulation-steps">{t("run_steps")}:</label>
                        <div className="create-form">
                            <input
                                className="form-input"
                                id="simulation-steps"
                                type="number"
                                min={1}
                                max={150}
                                value={stepsToRun}
                                onChange={(event) => setStepsToRun(event.target.value)}
                            />
                            <button
                                className="form-input-button"
                                type="button"
                                onClick={() => {
                                    const totalSteps = stepsToRun === "" ? 25 : Number(stepsToRun);
                                    simulationMutations.runMutation.mutate(
                                        {
                                            steps: totalSteps,
                                            onProgress: (completed, total) => {
                                                setRunProgress({ completed, total });
                                            },
                                        },
                                        {
                                            onSettled: () => {
                                                setRunProgress(null);
                                            },
                                        },
                                    );
                                }}
                                disabled={
                                    isSimulationControlBusy
                                    || stepsToRun === ""
                                    || Number(stepsToRun) < 1
                                    || Number(stepsToRun) > 150
                                }
                            >
                                {t("run")}
                            </button>
                        </div>
                        {logs.length !== 0 && (
                            <button
                                type="button"
                                onClick={() => downloadSimulationResults(simulationQuery.data)}
                                disabled={logs.length === 0}
                            >
                                {t("download_results")}
                            </button>
                        )}
                    </div>
                )}
                {runProgress && (
                    <div className="simulation-progress" aria-live="polite">
                        <div className="simulation-progress__header">
                            <strong>{t("run_progress")}</strong>
                            <span>{t("run_progress_ticks", { completed: runProgress.completed, total: runProgress.total })}</span>
                        </div>
                        <progress
                            className="simulation-progress__bar"
                            value={runProgress.completed}
                            max={runProgress.total}
                        />
                        <span className="simulation-progress__percent">{runProgressPercent}%</span>
                    </div>
                )}
                {isEditMode && (
                    <div className="simulation-run-panel" style={{ display: "flex", gap: 8, marginBottom: 12 }}>
                        <button onClick={() => setActiveModal("territory")} disabled={!isViewingLatestTick}>
                            {t("create_territory")}
                        </button>
                        <button
                            onClick={() => {
                                if (isEdgeMode) {
                                    resetEdgeMode();
                                } else {
                                    setIsEdgeMode(true);
                                    setSelectedTerritory(null);
                                }
                            }}
                            disabled={territories.length < 2 || !isViewingLatestTick}
                        >
                            {isEdgeMode ? t("cancel_edge_mode") : t("create_edge")}
                        </button>
                        <button
                            onClick={() => setActiveModal("agent")}
                            disabled={territories.length === 0 || !isViewingLatestTick}
                        >
                            {t("create_agent")}
                        </button>
                    </div>
                )}
            </div>
            {simulationControlError && (
                <p className="form-error">{getErrorMessage(simulationControlError)}</p>
            )}
            {isEdgeMode && (
                <p>
                    {edgeSourceId === null
                        ? t("select_source_node")
                        : t("select_target_node")}
                </p>
            )}
            <div className="simulation-workspace">
                <div className="simulation-workspace__graph">
                    <div className="territory-legend">
                        <div className="territory-legend__title">{t("territory_legend")}</div>
                        <div className="territory-legend__scale" aria-hidden="true" />
                        <div className="territory-legend__labels">
                            <span>{t("resources_low")}</span>
                            <span>{t("resources_high")}</span>
                        </div>
                    </div>
                    <TerritoryGraphComponent
                        graph={graph}
                        selectedNodeId={selectedNodeId}
                        onNodeClick={handleTerritoryClick}
                        selectedEdgeId={selectedEdgeId}
                        onEdgeClick={(edgeId) => {
                            if (isEdgeMode || !isViewingLatestTick) {
                                return;
                            }
                            setSelectedTerritory(null);
                            setSelectedEdgeId(edgeId);
                            setActiveModal("edge-editor");
                        }}
                        onNodePositionChange={(territoryId, position) => {
                            territoryMutations.updatePositionMutation.mutate({ territoryId, position });
                        }}
                        canDragNodes={!isEdgeMode && isViewingLatestTick && isEditMode} />
                </div>
                {!isEditMode && logs.length > 0 && (
                    <div className="simulation-timeline">
                        <span>
                            {t("selected_tick")} {selectedTickDisplay}
                        </span>
                        <input
                            id="simulation-tick-range"
                            type="range"
                            min={logs[0].tick}
                            max={logs[logs.length - 1].tick}
                            value={selectedTick ?? logs[logs.length - 1].tick}
                            onChange={(event) => setSelectedTick(Number(event.target.value))}
                        />
                    </div>
                )}
                {!isEditMode && (
                    <StepResult selectedLog={selectedLog} />
                )}
            </div>
            {!isEditMode && (
                <MetricsCharts logs={logs} />
            )}
            {activeModal === "territory" && (
                <Modal title={t("create_territory")} onClose={() => setActiveModal(null)}>
                    <NewTerritory
                        onCreate={(territory) => {
                            territoryMutations.createMutation.mutate(territory, {
                                onSuccess: () => setActiveModal(null),
                            });
                        }}
                    />
                </Modal>
            )}
            {activeModal === "edge-weight" && edgeDraft && edgeDraftSource && edgeDraftTarget && (
                <Modal
                    title={t("create_edge")}
                    onClose={() => {
                        setActiveModal(null);
                        resetEdgeMode();
                    }}
                >
                    <NewEdgeWeight
                        onCreate={(weight) => {
                            territoryMutations.createEdgeMutation.mutate(
                                { source: edgeDraft.source, target: edgeDraft.target, weight },
                                {
                                    onSuccess: () => {
                                        setActiveModal(null);
                                        resetEdgeMode();
                                    },
                                },
                            );
                        }}
                    />
                </Modal>
            )}
            {activeModal === "edge-editor" && selectedEdge && selectedEdgeSource && selectedEdgeTarget && (
                <Modal
                    title={t("edit_edge")}
                    onClose={() => {
                        setActiveModal(null);
                        setSelectedEdgeId(null);
                    }}
                >
                    <EditTerritoryEdgeForm
                        sourceName={`${t("territory")} ${selectedEdgeSource.id}`}
                        targetName={`${t("territory")} ${selectedEdgeTarget.id}`}
                        initialWeight={selectedEdge.weight}
                        initialSourceOffset={selectedEdge.sourcePortOffset ?? 0}
                        initialTargetOffset={selectedEdge.targetPortOffset ?? 0}
                        onSave={async ({ weight, sourceOffset, targetOffset }) => {
                            const edgeIds = selectedEdge.edgeIds ?? [selectedEdge.id];
                            await Promise.all(
                                edgeIds.map((edgeId: number) =>
                                    territoryMutations.updateEdgeWeightMutation.mutateAsync({
                                        edgeId,
                                        weight,
                                    }),
                                ),
                            );
                            const displayKey = selectedEdge.displayKey;
                            if (displayKey) {
                                setEdgePortOverrides((current) => ({
                                    ...current,
                                    [displayKey]: {
                                        source: sourceOffset,
                                        target: targetOffset,
                                    },
                                }));
                            }
                            setActiveModal(null);
                            setSelectedEdgeId(null);
                        }}
                        onDelete={async () => {
                            const edgeIds = selectedEdge.edgeIds ?? [selectedEdge.id];
                            await Promise.all(
                                edgeIds.map((edgeId: number) =>
                                    territoryMutations.deleteEdgeMutation.mutateAsync(edgeId),
                                ),
                            );
                            const displayKey = selectedEdge.displayKey;
                            if (displayKey) {
                                setEdgePortOverrides((current) => {
                                    const next = { ...current };
                                    delete next[displayKey];
                                    return next;
                                });
                            }
                            setActiveModal(null);
                            setSelectedEdgeId(null);
                        }}
                    />
                </Modal>
            )}
            {activeModal === "agent" && (
                <Modal title={t("create_agent")} onClose={() => setActiveModal(null)}>
                    <NewAgent
                        availableGenomes={availableGenomeOptions}
                        availableTerritories={territoryOptions}
                        onCreate={(sex, genome_id, territory_id) => {
                            agentMutations.createMutation.mutate(
                                { sex, genome_id, territory_id },
                                { onSuccess: () => setActiveModal(null) },
                            );
                        }}
                    />
                </Modal>
            )}
            {selectedTerritory && (
                <Modal
                    title={`${t('territory')} ${selectedTerritory.id}`}
                    onClose={() => {
                        setSelectedTerritory(null);
                        setIsEditingTerritory(false);
                    }}
                >
                    {isEditingTerritory ? (
                        <>
                            <NewTerritory
                                initialValue={{
                                    food: selectedTerritory.food,
                                    food_capacity: selectedTerritory.food_capacity,
                                    food_regen_per_tick: selectedTerritory.food_regen_per_tick,
                                    temperature: selectedTerritory.temperature,
                                    position: selectedTerritory.position,
                                }}
                                submitLabel={t("save")}
                                onCreate={(territory) => {
                                    territoryMutations.updateMutation.mutate(
                                        {
                                            territoryId: selectedTerritory.id,
                                            territory,
                                        },
                                        {
                                            onSuccess: () => setIsEditingTerritory(false),
                                        },
                                    );
                                }}
                            />
                            <button className="modal-button" type="button" onClick={() => setIsEditingTerritory(false)}>
                                {t("cancel")}
                            </button>
                        </>
                    ) : (
                        <>
                            <TerritoryDetails territory={selectedTerritory} />
                            {isViewingLatestTick && (
                                <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
                                    <button className="modal-button" type="button" onClick={() => setIsEditingTerritory(true)}>
                                        {t("edit")}
                                    </button>
                                    <button
                                        className="modal-button"
                                        type="button"
                                        onClick={() => {
                                            territoryMutations.deleteMutation.mutate(selectedTerritory.id, {
                                                onSuccess: () => {
                                                    setSelectedTerritory(null);
                                                    setIsEditingTerritory(false);
                                                },
                                            });
                                        }}
                                    >
                                        {t("delete")}
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                    {!isEditingTerritory && (
                        <div className="modal-agents_container">
                            <h2>{t('agents')}</h2>
                            <div className="modal-agents">
                                {isViewingLatestTick ? (
                                    agents
                                        .filter((agent: Agent) => agent.is_alive && agent.territory_id === selectedTerritory.id)
                                        .map((agent: Agent) => (
                                            <AgentSmallDetails
                                                key={agent.id}
                                                agent={agent}
                                                availableGenomes={availableGenomeOptions}
                                                availableTerritories={territoryOptions}
                                                onDelete={(agentId) => {
                                                    agentMutations.deleteMutation.mutate(agentId);
                                                }}
                                                onUpdate={(agentId, sex, genome_id, territory_id) => {
                                                    agentMutations.updateMutation.mutate({
                                                        agentId,
                                                        agent: { sex, genome_id, territory_id },
                                                    });
                                                }}
                                            />
                                        ))
                                ) : (
                                    displayedAgents
                                        .filter((agent) => agent.is_alive && agent.territory_id === selectedTerritory.id)
                                        .map((agent) => (
                                            <article className="tick-agent-card" key={agent.id}>
                                                <strong>#{agent.id}</strong>
                                                <p>{t("sex")}: {t(agent.sex)}</p>
                                                <p>{t("health")}: {agent.hp.toFixed(2)}</p>
                                                <p>{t("hunger")}: {agent.hunger.toFixed(2)}</p>
                                                <p>{t("satisfaction")}: {agent.satisfaction.toFixed(2)}</p>
                                            </article>
                                        ))
                                )}
                            </div>
                        </div>
                    )}
                </Modal>
            )}
        </div>
    );
}

const TERRITORY_EDGE_DISTANCE_SCALE = 140;
const TERRITORY_LAYOUT_WIDTH = 800;
const TERRITORY_LAYOUT_HEIGHT = 600;
const TERRITORY_LAYOUT_PADDING = 40;

function layoutTerritoriesByEdgeWeight(territories: Territory[], edges: { source: number; target: number; weight: number }[]) {
    if (territories.length === 0) {
        return territories;
    }

    const collapsedEdges = collapseUndirectedTerritoryEdges(edges);
    if (collapsedEdges.length === 0) {
        return territories;
    }

    const territoryIds = territories.map((territory) => territory.id);
    const adjacency = buildTerritoryAdjacency(territoryIds, collapsedEdges);
    const directDistanceMap = buildDirectDistanceMap(collapsedEdges);
    const shortestPathDistances = buildShortestPathDistances(territoryIds, adjacency);
    const componentIds = getTerritoryComponents(territoryIds, adjacency);
    const initialPositions = initializeTerritoryLayout(territories, componentIds);
    const anchorPositions = new Map(initialPositions.entries());
    const positions = new Map(initialPositions.entries());

    for (let iteration = 0; iteration < 220; iteration += 1) {
        for (let index = 0; index < territoryIds.length; index += 1) {
            const sourceId = territoryIds[index];
            const source = positions.get(sourceId);
            if (!source) {
                continue;
            }

            for (let targetIndex = index + 1; targetIndex < territoryIds.length; targetIndex += 1) {
                const targetId = territoryIds[targetIndex];
                if (componentIds.get(sourceId) !== componentIds.get(targetId)) {
                    continue;
                }

                const target = positions.get(targetId);
                if (!target) {
                    continue;
                }

                const pathDistance = shortestPathDistances.get(sourceId)?.get(targetId);
                if (!pathDistance || !Number.isFinite(pathDistance)) {
                    continue;
                }

                const desiredDistance = pathDistance * TERRITORY_EDGE_DISTANCE_SCALE;
                let dx = target.x - source.x;
                let dy = target.y - source.y;
                let currentDistance = Math.hypot(dx, dy);
                if (currentDistance < 0.0001) {
                    const angle = ((index + 1) * (targetIndex + 3)) % 360;
                    const radians = (angle * Math.PI) / 180;
                    dx = Math.cos(radians);
                    dy = Math.sin(radians);
                    currentDistance = 1;
                }

                const unitX = dx / currentDistance;
                const unitY = dy / currentDistance;
                const distanceError = currentDistance - desiredDistance;
                const pairKey = makeTerritoryEdgeKey(sourceId, targetId);
                const directWeight = directDistanceMap.get(pairKey);
                const stiffness = directWeight !== undefined ? 0.14 : 0.028;
                const correction = distanceError * stiffness * 0.5;

                source.x += unitX * correction;
                source.y += unitY * correction;
                target.x -= unitX * correction;
                target.y -= unitY * correction;

                const minimumSpacing = 92;
                if (currentDistance < minimumSpacing) {
                    const repulsion = ((minimumSpacing - currentDistance) / minimumSpacing) * 6;
                    source.x -= unitX * repulsion;
                    source.y -= unitY * repulsion;
                    target.x += unitX * repulsion;
                    target.y += unitY * repulsion;
                }
            }
        }

        for (const territoryId of territoryIds) {
            const position = positions.get(territoryId);
            const anchor = anchorPositions.get(territoryId);
            if (!position || !anchor) {
                continue;
            }

            position.x += (anchor.x - position.x) * 0.01;
            position.y += (anchor.y - position.y) * 0.01;
            position.x = clamp(
                position.x,
                TERRITORY_LAYOUT_PADDING,
                TERRITORY_LAYOUT_WIDTH - TERRITORY_LAYOUT_PADDING,
            );
            position.y = clamp(
                position.y,
                TERRITORY_LAYOUT_PADDING,
                TERRITORY_LAYOUT_HEIGHT - TERRITORY_LAYOUT_PADDING,
            );
        }
    }

    return territories.map((territory) => ({
        ...territory,
        position: positions.get(territory.id) ?? territory.position,
    }));
}

function collapseUndirectedTerritoryEdges(edges: { source: number; target: number; weight: number }[]) {
    const collapsed = new Map<string, { source: number; target: number; totalWeight: number; count: number }>();
    for (const edge of edges) {
        const source = Math.min(edge.source, edge.target);
        const target = Math.max(edge.source, edge.target);
        const key = makeTerritoryEdgeKey(source, target);
        const existing = collapsed.get(key);
        collapsed.set(key, {
            source,
            target,
            totalWeight: (existing?.totalWeight ?? 0) + edge.weight,
            count: (existing?.count ?? 0) + 1,
        });
    }
    return [...collapsed.values()].map((edge) => ({
        source: edge.source,
        target: edge.target,
        weight: edge.totalWeight / edge.count,
    }));
}

function makeTerritoryEdgeKey(sourceId: number, targetId: number) {
    return `${Math.min(sourceId, targetId)}:${Math.max(sourceId, targetId)}`;
}

function buildDisplayedTerritoryEdges(
    edges: { id: number; source: number; target: number; weight: number }[],
): DisplayedTerritoryEdge[] {
    const grouped = new Map<string, typeof edges>();
    for (const edge of edges) {
        const key = makeTerritoryEdgeKey(edge.source, edge.target);
        grouped.set(key, [...(grouped.get(key) ?? []), edge]);
    }

    const displayEdges: DisplayedTerritoryEdge[] = [];
    for (const pairEdges of grouped.values()) {
        const forward: typeof edges = [];
        const reverse: typeof edges = [];
        const minNodeId = Math.min(...pairEdges.map((edge) => edge.source), ...pairEdges.map((edge) => edge.target));

        for (const edge of pairEdges) {
            if (edge.source === minNodeId) {
                forward.push(edge);
            } else {
                reverse.push(edge);
            }
        }

        const reverseUsed = new Set<number>();
        for (const edge of forward) {
            const reverseMatch = reverse.find(
                (candidate) =>
                    !reverseUsed.has(candidate.id)
                    && Math.abs(candidate.weight - edge.weight) < 0.0001,
            );
            if (!reverseMatch) {
                displayEdges.push({
                    ...edge,
                    edgeIds: [edge.id],
                    displayKey: `edge:${edge.id}`,
                });
                continue;
            }

            reverseUsed.add(reverseMatch.id);
            displayEdges.push({
                id: Math.min(edge.id, reverseMatch.id),
                source: Math.min(edge.source, edge.target),
                target: Math.max(edge.source, edge.target),
                weight: edge.weight,
                directed: false,
                bidirectionalArrows: true,
                edgeIds: [edge.id, reverseMatch.id].sort((left, right) => left - right),
                displayKey: `edge:${[edge.id, reverseMatch.id].sort((left, right) => left - right).join("-")}`,
            });
        }

        for (const edge of reverse) {
            if (reverseUsed.has(edge.id)) {
                continue;
            }
            displayEdges.push({
                ...edge,
                edgeIds: [edge.id],
                displayKey: `edge:${edge.id}`,
            });
        }
    }

    return displayEdges;
}

function buildDirectDistanceMap(edges: { source: number; target: number; weight: number }[]) {
    return new Map(
        edges.map((edge) => [makeTerritoryEdgeKey(edge.source, edge.target), edge.weight]),
    );
}

function buildTerritoryAdjacency(
    territoryIds: number[],
    edges: { source: number; target: number; weight: number }[],
) {
    const adjacency = new Map<number, Array<{ target: number; weight: number }>>(
        territoryIds.map((territoryId) => [territoryId, []]),
    );
    for (const edge of edges) {
        adjacency.get(edge.source)?.push({ target: edge.target, weight: edge.weight });
        adjacency.get(edge.target)?.push({ target: edge.source, weight: edge.weight });
    }
    return adjacency;
}

function buildShortestPathDistances(
    territoryIds: number[],
    adjacency: Map<number, Array<{ target: number; weight: number }>>,
) {
    const distances = new Map<number, Map<number, number>>();

    for (const territoryId of territoryIds) {
        const queue: Array<{ id: number; distance: number }> = [{ id: territoryId, distance: 0 }];
        const best = new Map<number, number>([[territoryId, 0]]);

        while (queue.length > 0) {
            queue.sort((left, right) => left.distance - right.distance);
            const current = queue.shift();
            if (!current) {
                continue;
            }
            if (current.distance > (best.get(current.id) ?? Infinity)) {
                continue;
            }

            for (const neighbor of adjacency.get(current.id) ?? []) {
                const nextDistance = current.distance + neighbor.weight;
                if (nextDistance >= (best.get(neighbor.target) ?? Infinity)) {
                    continue;
                }
                best.set(neighbor.target, nextDistance);
                queue.push({ id: neighbor.target, distance: nextDistance });
            }
        }

        distances.set(territoryId, best);
    }

    return distances;
}

function getTerritoryComponents(
    territoryIds: number[],
    adjacency: Map<number, Array<{ target: number; weight: number }>>,
) {
    const componentIds = new Map<number, number>();
    let componentIndex = 0;

    for (const territoryId of territoryIds) {
        if (componentIds.has(territoryId)) {
            continue;
        }

        const queue = [territoryId];
        componentIds.set(territoryId, componentIndex);

        while (queue.length > 0) {
            const current = queue.shift();
            if (current === undefined) {
                continue;
            }
            for (const neighbor of adjacency.get(current) ?? []) {
                if (componentIds.has(neighbor.target)) {
                    continue;
                }
                componentIds.set(neighbor.target, componentIndex);
                queue.push(neighbor.target);
            }
        }

        componentIndex += 1;
    }

    return componentIds;
}

function initializeTerritoryLayout(
    territories: Territory[],
    componentIds: Map<number, number>,
) {
    const positions = new Map<number, { x: number; y: number }>();
    const components = new Map<number, Territory[]>();

    for (const territory of territories) {
        const componentId = componentIds.get(territory.id) ?? 0;
        components.set(componentId, [...(components.get(componentId) ?? []), territory]);
    }

    const componentEntries = [...components.entries()];
    const slotWidth = TERRITORY_LAYOUT_WIDTH / Math.max(componentEntries.length, 1);

    componentEntries.forEach(([, componentTerritories], componentIndex) => {
        const centerX = slotWidth * componentIndex + slotWidth / 2;
        const centerY = TERRITORY_LAYOUT_HEIGHT / 2;
        const hasDiversePositions = new Set(
            componentTerritories.map(
                (territory) => `${Math.round(territory.position.x)}:${Math.round(territory.position.y)}`,
            ),
        ).size > Math.max(1, Math.floor(componentTerritories.length / 2));

        componentTerritories.forEach((territory, index) => {
            if (hasDiversePositions) {
                positions.set(territory.id, { ...territory.position });
                return;
            }

            const angle = (Math.PI * 2 * index) / Math.max(componentTerritories.length, 1);
            const radius = Math.max(70, componentTerritories.length * 24);
            positions.set(territory.id, {
                x: clamp(
                    centerX + radius * Math.cos(angle),
                    TERRITORY_LAYOUT_PADDING,
                    TERRITORY_LAYOUT_WIDTH - TERRITORY_LAYOUT_PADDING,
                ),
                y: clamp(
                    centerY + radius * Math.sin(angle),
                    TERRITORY_LAYOUT_PADDING,
                    TERRITORY_LAYOUT_HEIGHT - TERRITORY_LAYOUT_PADDING,
                ),
            });
        });
    });

    return positions;
}

function clamp(value: number, min: number, max: number) {
    return Math.max(min, Math.min(max, value));
}

function getErrorMessage(error: unknown): string {
    if (error instanceof Error) {
        return error.message;
    }
    return String(error);
}

function downloadSimulationResults(simulation: SimulationDetails | undefined) {
    if (!simulation) {
        return;
    }

    const exportPayload = roundReadableNumbers(simulation);
    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], {
        type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `simulation-${simulation.id}-results.json`;
    link.click();
    URL.revokeObjectURL(url);
}

function roundReadableNumbers(value: unknown): unknown {
    if (Array.isArray(value)) {
        return value.map((item) => roundReadableNumbers(item));
    }
    if (value && typeof value === "object") {
        return Object.fromEntries(
            Object.entries(value).map(([key, nestedValue]) => [key, roundReadableNumbers(nestedValue)]),
        );
    }
    if (typeof value === "number" && !Number.isInteger(value)) {
        return Number(value.toFixed(2));
    }
    return value;
}

interface EditTerritoryEdgeFormProps {
    sourceName: string;
    targetName: string;
    initialWeight: number;
    initialSourceOffset: number;
    initialTargetOffset: number;
    onSave: (payload: { weight: number; sourceOffset: number; targetOffset: number }) => Promise<void>;
    onDelete: () => Promise<void>;
}

function EditTerritoryEdgeForm({
    sourceName,
    targetName,
    initialWeight,
    initialSourceOffset,
    initialTargetOffset,
    onSave,
    onDelete,
}: EditTerritoryEdgeFormProps) {
    const { t } = useTranslation();

    const [weight, setWeight] = useState<string>(
        initialWeight !== undefined ? String(initialWeight) : "",
    );

    const [sourceOffset, setSourceOffset] = useState<string>(
        initialSourceOffset !== undefined ? String(initialSourceOffset) : "",
    );

    const [targetOffset, setTargetOffset] = useState<string>(
        initialTargetOffset !== undefined ? String(initialTargetOffset) : "",
    );

    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSave = async () => {
        setIsSubmitting(true);

        try {
            await onSave({
                weight: weight === "" ? initialWeight : Number(weight),
                sourceOffset: sourceOffset === "" ? initialSourceOffset : Number(sourceOffset),
                targetOffset: targetOffset === "" ? initialTargetOffset : Number(targetOffset),
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDelete = async () => {
        setIsSubmitting(true);

        try {
            await onDelete();
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div>
            <p>
                {sourceName} -&gt; {targetName}
            </p>

            <div>
                <label htmlFor="editEdgeWeight">{t("distance")}:</label>
                <input
                    type="number"
                    id="editEdgeWeight"
                    min={0}
                    value={weight}
                    onChange={(event) => setWeight(event.target.value)}
                />
            </div>

            <div>
                <label htmlFor="edgeSourceOffset">{t("source_attachment")}:</label>
                <input
                    type="number"
                    id="edgeSourceOffset"
                    min={-18}
                    max={18}
                    step={2}
                    value={sourceOffset}
                    onChange={(event) => setSourceOffset(event.target.value)}
                />
            </div>

            <div>
                <label htmlFor="edgeTargetOffset">{t("target_attachment")}:</label>
                <input
                    type="number"
                    id="edgeTargetOffset"
                    min={-18}
                    max={18}
                    step={2}
                    value={targetOffset}
                    onChange={(event) => setTargetOffset(event.target.value)}
                />
            </div>

            <p className="form-hint">{t("edge_visual_hint")}</p>

            <div style={{ display: "flex", gap: 8 }}>
                <button type="button" onClick={handleSave} disabled={isSubmitting}>
                    {t("save")}
                </button>
                <button type="button" onClick={handleDelete} disabled={isSubmitting}>
                    {t("delete")}
                </button>
            </div>
        </div>
    );
}
