from typing import Any, Mapping, NewType

# Основные типы для симуляции
Tick = NewType("Tick", int)  # Номер тика симуляции (шага времени)
IndividualId = NewType("IndividualId", str)  # Уникальный ID агента
TerritoryId = NewType("TerritoryId", str)  # Уникальный ID территории

# Типы для работы с JSON
JSON = dict[str, Any]  # Словарь, представляющий JSON объект
JSONLike = Mapping[str, Any]  # Неизменяемый mapping, совместимый с JSON
