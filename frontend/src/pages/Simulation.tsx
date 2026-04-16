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

export function SimulationPage() {
    const { t } = useTranslation();

    const params = useParams();
    const simulationId = useMemo(() => Number(params.simulationId), [params.simulationId]);
    const [selectedTerritory, setSelectedTerritory] = useState<Territory | null>(null);

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

    const territories = simulationQuery.data?.territories ?? [];
    const territoriesEdges = simulationQuery.data?.territories_edges ?? [];
    const agents = agentsQuery.data ?? [];

    const graph = {
        nodes: territories,
        edges: territoriesEdges,
    };

    const territoryById = new Map(territories.map((t: Territory) => [t.id, t]));

    return (
        <div>
            <h1>{t('simulation')}</h1>
            <TerritoryGraphComponent
                graph={graph}
                width={800}
                height={600}
                selectedNodeId={selectedTerritory?.id || null}
                onNodeClick={(territoryId: number) => setSelectedTerritory(territoryById.get(territoryId) || null)}
                selectedEdgeId={null}
                onEdgeClick={() => { }}
                onNodePositionChange={() => { }} />
            {selectedTerritory && (
                <Modal title={`${t('territory')} ${selectedTerritory.id}`} onClose={() => setSelectedTerritory(null)}>
                    <TerritoryDetails territory={selectedTerritory} />
                    <h2>{t('agents')}</h2>
                    {agents.filter((agent: Agent) => agent.territory_id === selectedTerritory.id).map((agent: Agent) => (
                        <AgentSmallDetails key={agent.id} agent={agent} />
                    ))}
                </Modal>
            )}
        </div>
    );
}
