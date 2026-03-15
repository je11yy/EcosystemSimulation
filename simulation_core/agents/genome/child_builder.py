import random
from dataclasses import dataclass

from simulation_core.agents.genome.genome import Genome
from simulation_core.agents.genome.mutation import MutationModel
from simulation_core.agents.genome.recombination import RecombinationModel
from simulation_core.agents.registry import Agent


@dataclass
class ChildGenomeBuilder:
    recombination_model: RecombinationModel
    mutation_model: MutationModel

    def build_child_genome(
        self,
        parent_a: Agent,
        parent_b: Agent,
        rng: random.Random,
    ) -> Genome:
        recombined = self.recombination_model.recombine(
            parent_a=parent_a.genome,
            parent_b=parent_b.genome,
            rng=rng,
        )

        mutated = self.mutation_model.mutate(
            genome=recombined,
            rng=rng,
        )

        return mutated
