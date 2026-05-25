import unittest

from simulation_core.agent.actions import ActionOption
from simulation_core.agent.registry import Agent
from simulation_core.agent.state import AgentState
from simulation_core.config import SimConfig
from simulation_core.engine.applier import ActionApplier
from simulation_core.enums import AgentActionType, AgentSex
from simulation_core.genome.models import Genome
from simulation_core.world import TerritoryState, WorldState


class ActionApplierMoveTests(unittest.TestCase):
    def test_move_respects_edge_direction(self) -> None:
        cfg = SimConfig()
        world = WorldState()
        world.add_territory(
            TerritoryState(id=1, food=5, temperature=20, food_regen_per_tick=1, food_capacity=10)
        )
        world.add_territory(
            TerritoryState(id=2, food=5, temperature=20, food_regen_per_tick=1, food_capacity=10)
        )
        world.add_edge(1, 2, 1.0)

        applier = ActionApplier(cfg)
        agent = Agent(
            state=AgentState(
                id=1,
                sex=AgentSex.FEMALE,
                hunger=1.0,
                hp=5.0,
                is_pregnant=False,
                ticks_to_birth=0,
                satisfaction=3.0,
                hunt_cooldown=0,
                base_strength=1.0,
                base_defense=1.0,
                base_temp_pref=20.0,
                location=1,
            ),
            genome=Genome(),
        )

        forward = applier.apply_move(
            agent,
            ActionOption(type=AgentActionType.MOVE, to_territory=2),
            applier.cost_calculator.calculate(
                agent.state, ActionOption(type=AgentActionType.MOVE, to_territory=2)
            ),
            world,
        )
        self.assertTrue(forward.success)
        self.assertEqual(agent.state.location, 2)

        backward = applier.apply_move(
            agent,
            ActionOption(type=AgentActionType.MOVE, to_territory=1),
            applier.cost_calculator.calculate(
                agent.state, ActionOption(type=AgentActionType.MOVE, to_territory=1)
            ),
            world,
        )
        self.assertFalse(backward.success)
        self.assertEqual(backward.reason, "territory_unreachable")
        self.assertEqual(agent.state.location, 2)


if __name__ == "__main__":
    unittest.main()
