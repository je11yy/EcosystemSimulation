import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import type { Territory } from "../components/territory/types";
import type { Agent } from "../components/agent/types";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { TerritoryGraphComponent } from "src/components/territory/Graph";
import { TerritoryDetails } from "src/components/territory/Details";
import { Modal } from "src/components/Modal";
import { AgentSmallDetails } from "src/components/agent/SmallDetails";
import { getSimulation } from "src/api/simulations";
import { getAgents } from "src/api/agents";
import { getAvailableGenomes } from "src/api/genomes";
import { NewTerritory } from "src/components/forms/Territory";
import { NewAgent } from "src/components/forms/Agent";
import { NewEdgeWeight } from "src/components/forms/Edge";
import { useTerritoryMutations } from "src/hooks/territories/useTerritoryMutations";
import { useAgentMutations } from "src/hooks/agents/useAgentMutations";

type SimulationModal = "territory" | "edge-weight" | "agent" | null;
type EdgeDraft = { source: number; target: number } | null;

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

    const simulationQuery = useQuery({
        queryKey: ["simulation", simulationId],
        queryFn: () => getSimulation(simulationId),
        enabled: Number.isFinite(simulationId),
        refetchInterval: 1500,
    });

    const agentsQuery = useQuery({
        queryKey: ["agents", simulationId],
        queryFn: () => getAgents(simulationId),
        enabled: Number.isFinite(simulationId),
        refetchInterval: 1500,
    });

    const availableGenomesQuery = useQuery({
        queryKey: ["genomes", "available"],
        queryFn: getAvailableGenomes,
    });

    const territoryMutations = useTerritoryMutations(simulationId);
    const agentMutations = useAgentMutations(simulationId);

    const territories = simulationQuery.data?.territories ?? [];
    const territoriesEdges = simulationQuery.data?.territories_edges ?? [];
    const agents = agentsQuery.data ?? [];

    const graph = {
        nodes: territories,
        edges: territoriesEdges,
    };

    const territoryById = new Map(territories.map((t: Territory) => [t.id, t]));
    const territoryOptions = territories.map((territory: Territory) => ({
        id: territory.id,
        name: `${t("territory")} ${territory.id}`,
    }));
    const availableGenomeOptions = availableGenomesQuery.data ?? [];
    const selectedNodeId = edgeSourceId ?? selectedTerritory?.id ?? null;

    const resetEdgeMode = () => {
        setIsEdgeMode(false);
        setEdgeSourceId(null);
        setEdgeDraft(null);
    };

    const handleTerritoryClick = (territoryId: number) => {
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

    return (
        <div>
            <h1>{simulationQuery.data?.name ?? t('simulation')}</h1>
            <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
                <button onClick={() => setActiveModal("territory")}>
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
                    disabled={territories.length < 2}
                >
                    {isEdgeMode ? t("cancel_edge_mode") : t("create_edge")}
                </button>
                <button
                    onClick={() => setActiveModal("agent")}
                    disabled={territories.length === 0}
                >
                    {t("create_agent")}
                </button>
            </div>
            {isEdgeMode && (
                <p>
                    {edgeSourceId === null
                        ? t("select_source_node")
                        : t("select_target_node")}
                </p>
            )}
            <TerritoryGraphComponent
                graph={graph}
                width={800}
                height={600}
                selectedNodeId={selectedNodeId}
                onNodeClick={handleTerritoryClick}
                selectedEdgeId={null}
                onEdgeClick={() => { }}
                onNodePositionChange={(territoryId, position) => {
                    territoryMutations.updatePositionMutation.mutate({ territoryId, position });
                }}
                canDragNodes={!isEdgeMode} />
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
                        sourceName={`${t("territory")} ${edgeDraftSource.id}`}
                        targetName={`${t("territory")} ${edgeDraftTarget.id}`}
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
                            <button type="button" onClick={() => setIsEditingTerritory(false)}>
                                {t("cancel")}
                            </button>
                        </>
                    ) : (
                        <>
                            <TerritoryDetails territory={selectedTerritory} />
                            <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
                                <button type="button" onClick={() => setIsEditingTerritory(true)}>
                                    {t("edit")}
                                </button>
                                <button
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
                        </>
                    )}
                    <h2>{t('agents')}</h2>
                    {agents.filter((agent: Agent) => agent.territory_id === selectedTerritory.id).map((agent: Agent) => (
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
                    ))}
                </Modal>
            )}
        </div>
    );
}
