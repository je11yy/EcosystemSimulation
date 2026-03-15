import random
from dataclasses import dataclass
from typing import Sequence

from simulation_core.agents.phenotype import PhenotypeSnapshot
from simulation_core.agents.registry import Agent
from simulation_core.config import SimConfig


@dataclass(frozen=True)
class FightResult:
    territory_id: str
    winner_id: str
    loser_id: str
    loser_hp_loss: int


class ConflictResolver:
    """
    Разрешает конфликты за еду между агентами на одной территории.
    """

    def resolve_food_conflict(
        self,
        territory_id: str,
        contenders: Sequence[tuple[Agent, PhenotypeSnapshot]],
        rng: random.Random,
        cfg: SimConfig,
    ) -> tuple[Agent, list[FightResult]]:
        """
        Возвращает победителя и список результатов боёв.
        """
        if not contenders:
            raise ValueError("No contenders for conflict")

        if len(contenders) == 1:
            return contenders[0][0], []

        current_winner, current_winner_pheno = contenders[0]
        fight_results: list[FightResult] = []

        for challenger, challenger_pheno in contenders[1:]:
            winner, loser, loser_damage = self._resolve_duel(
                a=current_winner,
                a_pheno=current_winner_pheno,
                b=challenger,
                b_pheno=challenger_pheno,
                rng=rng,
                cfg=cfg,
            )

            loser.state.decrease_hp(loser_damage, cfg)

            fight_results.append(
                FightResult(
                    territory_id=territory_id,
                    winner_id=str(winner.state.id),
                    loser_id=str(loser.state.id),
                    loser_hp_loss=loser_damage,
                )
            )

            if winner.state.id == challenger.state.id:
                current_winner = challenger
                current_winner_pheno = challenger_pheno

        return current_winner, fight_results

    def _resolve_duel(
        self,
        a: Agent,
        a_pheno: PhenotypeSnapshot,
        b: Agent,
        b_pheno: PhenotypeSnapshot,
        rng: random.Random,
        cfg: SimConfig,
    ) -> tuple[Agent, Agent, int]:
        """
        Простая вероятностная модель дуэли.
        """
        a_score = max(1, a_pheno.strength - b_pheno.defense + 3)
        b_score = max(1, b_pheno.strength - a_pheno.defense + 3)

        total = a_score + b_score
        roll = rng.uniform(0, total)

        if roll < a_score:
            winner = a
            loser = b
            raw_damage = max(1, a_pheno.strength - b_pheno.defense + 1)
        else:
            winner = b
            loser = a
            raw_damage = max(1, b_pheno.strength - a_pheno.defense + 1)

        damage = min(raw_damage, cfg.hp_max)
        return winner, loser, damage
