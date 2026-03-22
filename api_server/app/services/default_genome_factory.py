from app.models.gene import Gene
from app.models.gene_edge import GeneEdge
from app.models.gene_state import GeneState


# В будущем заменить!!!
class DefaultGenomeFactory:
    def build_for_agent(self, agent_id: int):
        genes = [
            Gene(
                agent_id=agent_id,
                gene_key="g_hunger_drive",
                name="Hunger drive",
                chromosome_id="chr1",
                position=1.0,
                default_active=False,
                threshold=0.2,
            ),
            Gene(
                agent_id=agent_id,
                gene_key="g_risk_move",
                name="Risk movement",
                chromosome_id="chr1",
                position=2.0,
                default_active=False,
                threshold=0.0,
            ),
            Gene(
                agent_id=agent_id,
                gene_key="g_low_activity",
                name="Low activity",
                chromosome_id="chr1",
                position=3.0,
                default_active=False,
                threshold=0.3,
            ),
            Gene(
                agent_id=agent_id,
                gene_key="g_heat_resistance",
                name="Heat resistance",
                chromosome_id="chr2",
                position=1.0,
                default_active=False,
                threshold=0.0,
            ),
            Gene(
                agent_id=agent_id,
                gene_key="g_cold_resistance",
                name="Cold resistance",
                chromosome_id="chr2",
                position=2.0,
                default_active=False,
                threshold=0.0,
            ),
            Gene(
                agent_id=agent_id,
                gene_key="g_reproduction_drive",
                name="Reproduction drive",
                chromosome_id="chr2",
                position=3.0,
                default_active=False,
                threshold=0.1,
            ),
        ]

        gene_edges = [
            GeneEdge(
                agent_id=agent_id,
                source_gene_key="g_hunger_drive",
                target_gene_key="g_risk_move",
                weight=0.4,
            ),
        ]

        gene_states = [
            GeneState(agent_id=agent_id, gene_key="g_hunger_drive", is_active=False),
            GeneState(agent_id=agent_id, gene_key="g_risk_move", is_active=False),
            GeneState(agent_id=agent_id, gene_key="g_low_activity", is_active=False),
            GeneState(agent_id=agent_id, gene_key="g_heat_resistance", is_active=False),
            GeneState(agent_id=agent_id, gene_key="g_cold_resistance", is_active=False),
            GeneState(agent_id=agent_id, gene_key="g_reproduction_drive", is_active=False),
        ]

        return genes, gene_edges, gene_states
