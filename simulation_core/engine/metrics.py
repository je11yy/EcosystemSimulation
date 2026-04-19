from ..agent.registry import AgentRegistry
from .logs import AppliedActionResult, DeathResult, HuntEvent, Metrics


class MetricsCollector:
    def collect(
        self,
        agents: AgentRegistry,
        deaths: list[DeathResult],
        hunts: list[HuntEvent],
        applied_results: list[AppliedActionResult],
    ) -> Metrics:
        alive_agents = [agent for agent in agents.all() if agent.state.is_alive]
        occupancy_by_territory: dict[str, int] = {}
        for agent in alive_agents:
            territory_id = str(agent.state.location)
            occupancy_by_territory[territory_id] = occupancy_by_territory.get(territory_id, 0) + 1

        deaths_by_reason: dict[str, int] = {}
        for death in deaths:
            deaths_by_reason[death.reason] = deaths_by_reason.get(death.reason, 0) + 1

        avg_hunger = 0.0
        if alive_agents:
            avg_hunger = sum(agent.state.hunger for agent in alive_agents) / len(alive_agents)

        return Metrics(
            alive_population=len(alive_agents),
            avg_hunger=avg_hunger,
            occupancy_by_territory=occupancy_by_territory,
            deaths_by_reason=deaths_by_reason,
            successful_hunts=sum(1 for hunt in hunts if hunt.success),
            unsuccessful_hunts=sum(1 for hunt in hunts if not hunt.success),
            consumed_food=sum(result.consumed_food for result in applied_results),
        )
