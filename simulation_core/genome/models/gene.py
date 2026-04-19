from dataclasses import dataclass

from ..effect_type import GeneEffectType


@dataclass
class Gene:
    id: int
    name: str
    effect_type: GeneEffectType

    # Порог активации: значение условия, после которого ген начинает работать
    # или усиливает влияние. Например, HUNGER_DRIVE может включаться при
    # hunger >= threshold, а HEAT_RESISTANCE - при temperature >= threshold.
    threshold: float

    # Сила гена: насколько сильно ген влияет на итоговый признак или поведение.
    # Для статовых генов вроде MAX_HP/STRENGTH/DEFENSE это множитель базового
    # значения. Для поведенческих генов это вес в выборе действия.
    weight: float

    # Включен по умолчанию: ген работает всегда, даже если состояние агента
    # сейчас не достигает порога активации.
    default_active: bool

    # Текущее состояние активности для конкретного агента. Этот флаг можно
    # пересчитывать по AgentState перед добавлением агента в симуляцию.
    is_active: bool

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
