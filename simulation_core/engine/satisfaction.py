from ..agent.registry import AgentRegistry
from ..config import SimConfig
from ..utils import clamp
from ..world import WorldState


class SatisfactionUpdater:
    def __init__(self, cfg: SimConfig):
        self.cfg = cfg

    def update(self, agents: AgentRegistry, world: WorldState) -> None:
        occupants_by_territory = self._occupants_by_territory(agents)

        for agent in agents.all():
            if not agent.state.is_alive:
                agent.state.satisfaction = self.cfg.satisfaction_min
                continue
            if agent.state.location not in world.territories:
                agent.state.satisfaction = self.cfg.satisfaction_min
                continue

            territory = world.get_territory(agent.state.location)
            occupant_count = occupants_by_territory.get(agent.state.location, 0)
            score = self._calculate_agent_satisfaction(agent, territory, occupant_count)
            agent.state.satisfaction = clamp(
                score,
                self.cfg.satisfaction_min,
                self.cfg.satisfaction_max,
            )

    def _calculate_agent_satisfaction(self, agent, territory, occupant_count: int) -> float:
        hunger_score = 1 - _ratio(agent.state.hunger, self.cfg.hunger_max)
        hp_score = _ratio(agent.state.hp, agent.state.max_hp)
        food_score = _ratio(territory.food, max(territory.food_capacity, 1.0))
        temperature_score = self._temperature_score(agent, territory.temperature)
        density_score = self._density_score(agent, occupant_count)

        normalized_score = (
            0.28 * hunger_score
            + 0.22 * hp_score
            + 0.2 * food_score
            + 0.18 * temperature_score
            + 0.12 * density_score
        )
        return self.cfg.satisfaction_min + normalized_score * (
            self.cfg.satisfaction_max - self.cfg.satisfaction_min
        )

    def _temperature_score(self, agent, temperature: float) -> float:
        delta = temperature - agent.state.base_temp_pref
        resistance = (
            agent.state.traits.heat_resistance if delta > 0 else agent.state.traits.cold_resistance
        )
        discomfort = max(0.0, abs(delta) - resistance)
        return 1 - _ratio(discomfort, 20.0)

    def _density_score(self, agent, occupant_count: int) -> float:
        comfortable_count = 2 + max(0.0, agent.state.traits.social_tolerance)
        pressure = max(0.0, occupant_count - comfortable_count)
        return 1 - _ratio(pressure, max(comfortable_count, 1.0))

    def _occupants_by_territory(self, agents: AgentRegistry) -> dict[int, int]:
        occupants: dict[int, int] = {}
        for agent in agents.all():
            if not agent.state.is_alive:
                continue
            occupants[agent.state.location] = occupants.get(agent.state.location, 0) + 1
        return occupants


def _ratio(value: float, maximum: float) -> float:
    if maximum <= 0:
        return 0.0
    return max(0.0, min(1.0, value / maximum))
