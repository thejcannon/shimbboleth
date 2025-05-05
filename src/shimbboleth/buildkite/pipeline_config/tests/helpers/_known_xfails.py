import pytest
import pathlib
import re

def mark_known_xfails(items: list[pytest.Item]) -> None:
    """Mark tests from xfail file as expected to fail."""
    xfail_file = pathlib.Path(__file__).parent.parent / "xfail_nodeids.txt"

    if not xfail_file.exists():
        return

    nodeid_patterns = {
        re.compile(re.escape(line.strip()).replace("\\*", "\\w+"))
        for line in xfail_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }

    for item in items:
        for pattern in nodeid_patterns:
            if pattern.search(item.nodeid):
                item.add_marker(
                    pytest.mark.xfail(reason="Listed in xfail_nodeids.txt", strict=True)
                )
