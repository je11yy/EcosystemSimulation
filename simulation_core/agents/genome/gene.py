from dataclasses import dataclass

from simulation_core.agents.genome.effect_type import GeneEffectType


@dataclass(frozen=True)
class Gene:
    """Описание одного гена как узла в графе генома.

    Ген имеет порог активации и может быть активен или неактивен
    в зависимости от входных сигналов и связей с другими генами.
    """

    id: int  # Уникальный идентификатор гена
    name: str  # Человеко-читаемое имя гена

    effect_type: GeneEffectType  # Тип эффекта, который оказывает ген

    chromosome_id: str  # Идентификатор хромосомы, к которой принадлежит ген
    position: float  # Позиция гена на хромосоме (для визуализации и мутаций)

    default_active: bool = False  # Активен ли ген по умолчанию при инициализации
    threshold: float = 0.0  # Порог активации (входной сигнал должен превысить этот порог)
