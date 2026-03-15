from dataclasses import dataclass
from typing import Optional

from simulation_core.agents.actions import ActionOption, ActionType
from simulation_core.agents.registry import Agent, AgentRegistry
from simulation_core.config import SimConfig
from simulation_core.types import IndividualId, TerritoryId
from simulation_core.world.api import WorldReadAPI


@dataclass(frozen=True)
class AppliedActionResult:
    agent_id: str
    action_type: str
    success: bool
    reason: Optional[str] = None
    consumed_food: bool = False
    created_pregnancy: bool = False
    hp_loss: int = 0


class ActionApplier:
    def apply(
        self,
        agent: Agent,
        action: ActionOption,
        world: WorldReadAPI,
        agents: AgentRegistry,
        cfg: SimConfig,
    ) -> AppliedActionResult:
        if action.type == ActionType.MOVE:
            if action.to_territory is None:
                return AppliedActionResult(
                    agent_id=str(agent.state.id),
                    action_type=action.type.value,
                    success=False,
                    reason="MOVE action requires to_territory",
                )
            return self._apply_move(
                agent=agent,
                target_territory=action.to_territory,
                world=world,
            )

        if action.type == ActionType.REST:
            return self._apply_rest(agent=agent)

        if action.type == ActionType.MATE:
            if action.partner_id is None:
                return AppliedActionResult(
                    agent_id=str(agent.state.id),
                    action_type=action.type.value,
                    success=False,
                    reason="MATE action requires partner_id",
                )
            return self._apply_mate(
                agent=agent,
                partner_id=action.partner_id,
                agents=agents,
                cfg=cfg,
            )

        if action.type == ActionType.EAT:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=action.type.value,
                success=False,
                reason="EAT must be resolved through food conflict pipeline",
            )

        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=action.type.value,
            success=False,
            reason=f"Unsupported action type: {action.type}",
        )

    def apply_successful_eat(
        self,
        agent: Agent,
        world: WorldReadAPI,
        cfg: SimConfig,
    ) -> AppliedActionResult:
        territory = world.get_territory(agent.state.location)

        if not territory.consume_food(1):
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.EAT.value,
                success=False,
                reason="Not enough food on territory",
                consumed_food=False,
            )

        agent.state.decrease_hunger(1, cfg)

        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=ActionType.EAT.value,
            success=True,
            consumed_food=True,
        )

    def _apply_move(
        self,
        agent: Agent,
        target_territory: TerritoryId,
        world: WorldReadAPI,
    ) -> AppliedActionResult:
        current_id = agent.state.location
        neighbor_ids = {edge.to for edge in world.graph().neighbors(current_id)}

        if target_territory not in neighbor_ids:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MOVE.value,
                success=False,
                reason="Target territory is not adjacent",
            )

        agent.state.move_to(target_territory)

        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=ActionType.MOVE.value,
            success=True,
        )

    def _apply_rest(self, agent: Agent) -> AppliedActionResult:
        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=ActionType.REST.value,
            success=True,
        )

    def _apply_mate(
        self,
        agent: Agent,
        partner_id: IndividualId,
        agents: AgentRegistry,
        cfg: SimConfig,
    ) -> AppliedActionResult:
        try:
            partner = agents.get(partner_id)
        except KeyError:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MATE.value,
                success=False,
                reason="Partner not found",
            )

        if agent.state.location != partner.state.location:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MATE.value,
                success=False,
                reason="Partner is on another territory",
            )

        if agent.state.sex == partner.state.sex:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MATE.value,
                success=False,
                reason="Same sex pairing is not supported in current reproduction model",
            )

        male = agent if agent.state.sex == "male" else partner
        female = agent if agent.state.sex == "female" else partner

        if female.state.pregnant:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MATE.value,
                success=False,
                reason="Female is already pregnant",
            )

        female.state.pregnant = True
        female.state.ticks_to_birth = cfg.pregnancy_duration_ticks
        female.state.father_id = male.state.id

        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=ActionType.MATE.value,
            success=True,
            created_pregnancy=True,
        )
