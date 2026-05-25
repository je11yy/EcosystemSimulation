from dataclasses import dataclass

from ..effect_type import GeneEffectType


@dataclass
class Gene:
    id: int
    effect_type: GeneEffectType
    x: float = 0.0
    y: float = 0.0

    # Порог активации: значение условия, после которого ген начинает работать
    # или усиливает влияние. Например, HUNGER_DRIVE может включаться при
    # hunger >= threshold, а HEAT_RESISTANCE - при temperature >= threshold.
    threshold: float = 0.0

    # Сила гена: насколько сильно ген влияет на итоговый признак или поведение.
    # Для статовых генов вроде MAX_HP/STRENGTH/DEFENSE это множитель базового
    # значения. Для поведенческих генов это вес в выборе действия.
    weight: float = 1.0

    # Включен по умолчанию: ген работает всегда, даже если состояние агента
    # сейчас не достигает порога активации.
    default_active: bool = False

    # Текущее состояние активности для конкретного агента. Этот флаг можно
    # пересчитывать по AgentState перед добавлением агента в симуляцию.
    is_active: bool = False

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
