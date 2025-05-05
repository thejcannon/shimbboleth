
import pytest

def filter_empty_paramsets(items: list[pytest.Item]) -> None:
    """
    Remove paramsets with no valid parameters.
    
    (otherwise pytest marks them as skipped)
    """
    for index, item in reversed(list(enumerate(items))):
        marks = item.own_markers
        for mark in marks:
            if mark.name== "skip" and mark.args == () and mark.kwargs.get("reason", "").startswith("got empty parameter set "):
                items.pop(index)
                break
        
