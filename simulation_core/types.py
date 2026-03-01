from typing import Any, Mapping, NewType

Tick = NewType("Tick", int)
IndividualId = NewType("IndividualId", str)
TerritoryId = NewType("TerritoryId", str)

JSON = dict[str, Any]
JSONLike = Mapping[str, Any]
