from dataclasses import dataclass

from simulation_core.world.api import WorldReadAPI


@dataclass(frozen=True)
class SimpleFoodDiffusionModel:
    """
    Простая диффузия еды по графу территорий.

    Для каждой пары соседних территорий часть еды перетекает
    из более богатой территории в более бедную.
    """

    diffusion_rate: float = 0.1

    def diffuse(self, world: WorldReadAPI) -> None:
        graph = world.graph()

        # накапливаем дельты отдельно, чтобы обновление было "одновременным"
        food_delta: dict[str, float] = {
            str(territory.id): 0.0 for territory in world.all_territories()
        }

        processed_edges: set[tuple[str, str]] = set()

        for territory in world.all_territories():
            source_id = str(territory.id)

            for edge in graph.neighbors(territory.id):
                target_id = str(edge.to)

                a, b = sorted((source_id, target_id))
                edge_key = (a, b)
                if edge_key in processed_edges:
                    continue
                processed_edges.add(edge_key)

                source = world.get_territory(territory.id)
                target = world.get_territory(edge.to)

                food_a = source.food
                food_b = target.food

                if food_a == food_b:
                    continue

                if food_a > food_b:
                    flow = self.diffusion_rate * (food_a - food_b)
                    flow = min(flow, food_a)
                    food_delta[source_id] -= flow
                    food_delta[target_id] += flow
                else:
                    flow = self.diffusion_rate * (food_b - food_a)
                    flow = min(flow, food_b)
                    food_delta[target_id] -= flow
                    food_delta[source_id] += flow

        for territory in world.all_territories():
            territory.food += food_delta[str(territory.id)]

            if territory.food < 0:
                territory.food = 0.0
