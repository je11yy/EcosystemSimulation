from ..world import WorldState
from .observation import Observation, ObservedAgent, ObservedTerritory
from .registry import Agent, AgentRegistry


class AgentObserver:
    def build(self, agent: Agent, world: WorldState, agents: AgentRegistry) -> Observation:
        neighboring_territories = world.get_neighbors(agent.state.location)
        territory_occupants = {}
        for other_agent in agents.all():
            territory_occupants[other_agent.state.location] = (
                territory_occupants.get(other_agent.state.location, 0) + 1
            )

        current_territory = world.get_territory(agent.state.location)
        observed_current_territory = ObservedTerritory(
            id=current_territory.id,
            temperature=current_territory.temperature,
            food=current_territory.food,
            movement_cost=0.0,
            occupant_count=territory_occupants.get(current_territory.id, 0),
        )

        observed_territories = []
        for territory_id, weight in neighboring_territories.items():
            territory = world.get_territory(territory_id)
            observed_territories.append(
                ObservedTerritory(
                    id=territory.id,
                    temperature=territory.temperature,
                    food=territory.food,
                    movement_cost=weight,
                    occupant_count=territory_occupants.get(territory_id, 0),
                )
            )

        observed_agents = []
        for other_agent in agents.all():
            if (
                other_agent.state.location == agent.state.location
                and other_agent.state.id != agent.state.id
            ):
                observed_agents.append(
                    ObservedAgent(
                        id=other_agent.state.id,
                        sex=other_agent.state.sex,
                        hp=other_agent.state.hp,
                        strength=other_agent.state.effective_strength,
                        defense=other_agent.state.effective_defense,
                        is_alive=other_agent.state.is_alive,
                    )
                )

        return Observation(
            current_territory=observed_current_territory,
            agents=observed_agents,
            neighboring_territories=observed_territories,
        )
