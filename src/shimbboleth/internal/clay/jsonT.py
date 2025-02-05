from typing import TypeAlias, Sequence, MutableMapping, TYPE_CHECKING, Any

if TYPE_CHECKING:
    JSON: TypeAlias = (
        dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
    )
    JSONObject: TypeAlias = dict[str, JSON]
    JSONArray: TypeAlias = list[JSON]
else:
    JSON = Any
    JSONObject: TypeAlias = dict[str, JSON]
    JSONArray: TypeAlias = list[JSON]
