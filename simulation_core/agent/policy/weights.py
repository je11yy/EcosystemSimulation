from dataclasses import dataclass


@dataclass(frozen=True)
class EatScoreWeights:
    # Срочная потребность в выживании важнее всего: голодный агент ищет еду.
    hunger_need: float = 0.55
    # Наличие еды важно, но вторично по отношению к текущему голоду.
    local_food: float = 0.25
    # Большое количество особей слегка снижает привлекательность еды на текущей территории.
    low_density: float = 0.1
    # Генетическая тяга к еде дает небольшой сдвиг, но не отменяет ограничения среды.
    hunger_drive: float = 0.1


@dataclass(frozen=True)
class MoveScoreWeights:
    # Голодные агенты сильнее ценят территории с большим количеством еды.
    food_gain_when_hungry: float = 0.25
    # Большое количество особей на текущей территории подталкивает к расселению.
    current_density_pressure: float = 0.2
    # Подходящая температура важна, но не должна перекрывать базовое выживание.
    temperature_fit: float = 0.2
    # DISPERSAL_DRIVE - основной генетический push к перемещению.
    dispersal_drive: float = 0.25
    # SITE_FIDELITY сопротивляется перемещению.
    site_fidelity_penalty: float = 0.15
    # Перенаселенная целевая территория менее привлекательна.
    target_density_penalty: float = 0.15
    # Стоимость движения уже учитывается DEB-ценой, поэтому здесь это небольшой штраф пути.
    movement_cost_penalty: float = 0.1


@dataclass(frozen=True)
class MateScoreWeights:
    # REPRODUCTION_DRIVE - основной генетический фактор склонности к размножению.
    reproduction_drive: float = 0.35
    # Удовлетворенность приблизительно показывает, подходят ли условия для потомства.
    satisfaction: float = 0.25
    # Здоровье агента и партнера важны, но не должны полностью запрещать размножение.
    own_health: float = 0.15
    partner_health: float = 0.1
    # Голод снижает склонность к размножению: энергия сначала уходит в поддержание жизни.
    hunger_penalty: float = 0.25


@dataclass(frozen=True)
class HuntScoreWeights:
    # Голод - основной стимул к охоте.
    hunger_pressure: float = 0.35
    # PREDATION_DRIVE - основной генетический фактор склонности к охоте.
    predation_drive: float = 0.25
    # Агрессия слегка подталкивает конфликтных агентов к охоте.
    aggression_drive: float = 0.1
    # Более сильные агенты охотнее идут на риск охоты.
    attack_advantage: float = 0.2
    # Слабая цель привлекательнее и безопаснее.
    target_weakness: float = 0.1


@dataclass(frozen=True)
class RestScoreWeights:
    # Отдых в первую очередь нужен для восстановления.
    hp_need: float = 0.45
    # SITE_FIDELITY повышает склонность остаться на месте и отдыхать.
    site_fidelity: float = 0.25
    # Голод мешает отдыху, потому что поиск еды становится срочнее.
    hunger_penalty: float = 0.2


@dataclass(frozen=True)
class CostPenaltyWeights:
    # Цена в голоде ожидаема для большинства действий, поэтому штраф умеренный.
    hunger: float = 0.35
    # Цена в hp - прямой риск смерти, поэтому штраф сильнее.
    hp: float = 0.65


@dataclass(frozen=True)
class PolicyScoreWeights:
    eat: EatScoreWeights = EatScoreWeights()
    move: MoveScoreWeights = MoveScoreWeights()
    mate: MateScoreWeights = MateScoreWeights()
    hunt: HuntScoreWeights = HuntScoreWeights()
    rest: RestScoreWeights = RestScoreWeights()
    cost_penalty: CostPenaltyWeights = CostPenaltyWeights()
