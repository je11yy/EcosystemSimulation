import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional

from simulation_core.agents.actions import ActionOption, ActionType
from simulation_core.agents.genome.compatibility import GenomeCompatibilityCalculator
from simulation_core.agents.phenotype import PhenotypeSnapshot
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
    hunger_restored: int = 0
    target_id: Optional[str] = None
    damage_to_target: int = 0
    target_died: bool = False
    hunter_died: bool = False
    hunger_delta: int = 0


class ActionApplier:
    def __init__(self) -> None:
        self.compatibility_calculator = GenomeCompatibilityCalculator(max_distance=0.3)

    def apply(
        self,
        agent: Agent,
        action: ActionOption,
        world: WorldReadAPI,
        agents: AgentRegistry,
        cfg: SimConfig,
        rng: random.Random | None = None,
        actor_phenotype: Optional[PhenotypeSnapshot] = None,
        phenotype_provider: Optional[Callable[[Agent], PhenotypeSnapshot]] = None,
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

        if action.type == ActionType.HUNT:
            if action.target_id is None:
                return AppliedActionResult(
                    agent_id=str(agent.state.id),
                    action_type=action.type.value,
                    success=False,
                    reason="HUNT action requires target_id",
                )
            return self._apply_hunt(
                agent=agent,
                target_id=action.target_id,
                agents=agents,
                cfg=cfg,
                rng=rng,
                actor_phenotype=actor_phenotype,
                phenotype_provider=phenotype_provider,
            )

        if action.type == ActionType.EAT:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.EAT.value,
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
            hunger_restored=1,
            hunger_delta=-1,
        )

    def _apply_move(
        self,
        agent: Agent,
        target_territory: TerritoryId,
        world: WorldReadAPI,
    ) -> AppliedActionResult:
        current_id = agent.state.location
        neighbor_edges = list(world.graph().neighbors(current_id))
        neighbor_ids = {edge.to for edge in neighbor_edges}

        if target_territory not in neighbor_ids:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MOVE.value,
                success=False,
                reason="Target territory is not adjacent",
                hunger_delta=0,
            )

        movement_cost = 1.0
        for edge in neighbor_edges:
            if edge.to == target_territory:
                movement_cost = edge.cost
                break

        action_cost = max(1, round(movement_cost))

        agent.state.move_to(target_territory)

        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=ActionType.MOVE.value,
            success=True,
            hunger_delta=action_cost,
        )

    def _apply_rest(self, agent: Agent) -> AppliedActionResult:
        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=ActionType.REST.value,
            success=True,
            hunger_delta=0,
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
                hunger_delta=1,
            )

        mate_cost = self._mate_hunger_cost(agent)

        if agent.state.location != partner.state.location:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MATE.value,
                success=False,
                reason="Partner is on another territory",
                hunger_delta=mate_cost,
            )

        if agent.state.sex == partner.state.sex:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MATE.value,
                success=False,
                reason="Same sex pairing is not supported in current reproduction model",
                hunger_delta=mate_cost,
            )

        if agent.state.species_group != partner.state.species_group:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MATE.value,
                success=False,
                reason="Agents belong to different species groups",
                hunger_delta=mate_cost,
            )

        compatibility = self.compatibility_calculator.check(
            agent.genome,
            partner.genome,
        )
        if not compatibility.compatible:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MATE.value,
                success=False,
                reason=f"Genome distance too high: {compatibility.distance:.3f}",
                hunger_delta=mate_cost,
            )

        male = agent if agent.state.sex == "male" else partner
        female = agent if agent.state.sex == "female" else partner

        if female.state.pregnant:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.MATE.value,
                success=False,
                reason="Female is already pregnant",
                hunger_delta=mate_cost,
            )

        female.state.pregnant = True
        female.state.ticks_to_birth = cfg.pregnancy_duration_ticks
        female.state.father_id = male.state.id

        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=ActionType.MATE.value,
            success=True,
            created_pregnancy=True,
            hunger_delta=mate_cost,
        )

    def _apply_hunt(
        self,
        agent: Agent,
        target_id: IndividualId,
        agents: AgentRegistry,
        cfg: SimConfig,
        rng: random.Random | None,
        actor_phenotype: Optional[PhenotypeSnapshot],
        phenotype_provider: Optional[Callable[[Agent], PhenotypeSnapshot]],
    ) -> AppliedActionResult:
        try:
            target = agents.get(target_id)
        except KeyError:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.HUNT.value,
                success=False,
                reason="Target not found",
                hunger_delta=1,
            )

        if not target.state.alive:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.HUNT.value,
                success=False,
                reason="Target is already dead",
                hunger_delta=1,
            )

        if agent.state.location != target.state.location:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.HUNT.value,
                success=False,
                reason="Target is on another territory",
                hunger_delta=1,
            )

        if actor_phenotype is None or phenotype_provider is None:
            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.HUNT.value,
                success=False,
                reason="Phenotypes are required for hunt resolution",
                hunger_delta=1,
            )

        target_phenotype = phenotype_provider(target)

        attack_score = max(1, actor_phenotype.strength - target_phenotype.defense + 3)
        counter_score = max(1, target_phenotype.strength - actor_phenotype.defense + 3)

        target_hp_before = target.state.hp

        if rng is None:
            hunt_success = attack_score >= counter_score
        else:
            total = attack_score + counter_score
            roll = rng.uniform(0, total)
            hunt_success = roll < attack_score

        if hunt_success:
            damage = min(
                max(1, actor_phenotype.strength - target_phenotype.defense + 1),
                cfg.hp_max,
            )
            target.state.decrease_hp(damage, cfg)

            hunger_restored = 0
            consumed_food = False

            if not target.state.alive:
                agent.state.hunt_cooldown = 2
                hunger_restored = self._calculate_hunt_hunger_restore(
                    hunter=agent,
                    target=target,
                    actor_phenotype=actor_phenotype,
                    target_phenotype=target_phenotype,
                    target_hp_before=target_hp_before,
                    cfg=cfg,
                )
                if hunger_restored > 0:
                    agent.state.decrease_hunger(hunger_restored, cfg)
                    consumed_food = True

            target_status = " and died" if not target.state.alive else ""
            food_suffix = (
                f"; hunter restored {hunger_restored} hunger" if hunger_restored > 0 else ""
            )

            net_hunger_delta = 1 - hunger_restored

            return AppliedActionResult(
                agent_id=str(agent.state.id),
                action_type=ActionType.HUNT.value,
                success=True,
                reason=f"Target {target.state.id} took {damage} damage{target_status}{food_suffix}",
                consumed_food=consumed_food,
                hunger_restored=hunger_restored,
                target_id=str(target.state.id),
                damage_to_target=damage,
                target_died=not target.state.alive,
                hunter_died=not agent.state.alive,
                hunger_delta=net_hunger_delta,
            )

        retaliation_damage = min(
            max(1, target_phenotype.strength - actor_phenotype.defense + 1),
            cfg.hp_max,
        )
        agent.state.decrease_hp(retaliation_damage, cfg)

        hunter_status = " and died" if not agent.state.alive else ""
        return AppliedActionResult(
            agent_id=str(agent.state.id),
            action_type=ActionType.HUNT.value,
            success=False,
            reason=(
                f"Hunt failed against {target.state.id}; "
                f"retaliation dealt {retaliation_damage} damage{hunter_status}"
            ),
            hp_loss=retaliation_damage,
            target_id=str(target.state.id),
            damage_to_target=0,
            target_died=not target.state.alive,
            hunter_died=not agent.state.alive,
            hunger_delta=1,
        )

    def _calculate_hunt_hunger_restore(
        self,
        hunter: Agent,
        target: Agent,
        actor_phenotype: PhenotypeSnapshot,
        target_phenotype: PhenotypeSnapshot,
        target_hp_before: int,
        cfg: SimConfig,
    ) -> int:
        hp_component = 0.0
        if cfg.hp_max > 0:
            hp_component = min(1.0, max(0.0, target_hp_before / cfg.hp_max))

        body_component = min(
            1.0,
            max(0.0, (target_phenotype.strength + target_phenotype.defense) / 10.0),
        )

        prey_value = 0.5 * hp_component + 0.5 * body_component

        assimilation = 0.60
        if self._has_active_effect(hunter, "CARNIVORE_DIGESTION"):
            assimilation = 0.85

        raw_restore = 1.0 + 2.0 * prey_value * assimilation
        hunger_restored = round(raw_restore)

        return max(1, min(3, hunger_restored))

    def _has_active_effect(self, agent: Agent, effect_name: str) -> bool:
        for gene in agent.genome.all_genes():
            if gene.effect_type.name != effect_name:
                continue
            if agent.genome_state.is_active(gene.id):
                return True
        return False

    def _mate_hunger_cost(self, agent: Agent) -> int:
        if self._has_active_effect(agent, "PARENTAL_INVESTMENT"):
            return 2
        return 1
