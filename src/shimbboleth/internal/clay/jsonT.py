from typing import TypeAlias, Sequence, MutableMapping, TYPE_CHECKING, Any

if TYPE_CHECKING:
    JSON: TypeAlias = (
        MutableMapping[str, "JSON"] | Sequence["JSON"] | str | int | float | bool | None
    )
    JSONObject: TypeAlias = MutableMapping[str, JSON]
    JSONArray: TypeAlias = Sequence[JSON]
else:
    JSON = Any
    JSONObject: TypeAlias = dict[str, JSON]
    JSONArray: TypeAlias = list[JSON]
