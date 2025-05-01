from collections import defaultdict
from itertools import pairwise
from functools import partial
import warnings
import pytest
from _pytest.python import Function
from shimbboleth.buildkite.pipeline_config import BuildkitePipeline
from shimbboleth.internal.clay.validation import ValidationError
from shimbboleth.buildkite.pipeline_config.tests.generator.generated_tests import (
    test_generated_schema,
    test_upstream_json_schema,
)

# Maps nodeid to (metadata, config)
PIPELINE_CONFIGS = defaultdict(list)
COLLECTING_PIPELINES = True


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "upstream_schema_invalid: although the config is valid, the upstream JSON Schema considers it invalid",
    )


def pytest_collection_modifyitems(config, items, session: pytest.Session):
    """
    This hook is used to help us generate the test cases that test the configs against:
        - our generated schema
        - the upstream schema
        - the upstream API
    We do this by running the test itself here in the collection (if it fails oh well),
    and collecting the pipeline configs. Then for each of those, generate each of the tests above.

    It's SUPER hacky, but it results in a relatively clean/easy/intuitive test writing and running
    experience.
    """
    return items

    def _generate_test(real_node, metadata, func):
        id = metadata.get("id", "")
        suffix = f"-{id}" if id else ""
        item = Function.from_parent(
            name=real_node.name + f"[*{func.__name__}{suffix}]",
            parent=real_node.parent,
            callobj=partial(func, config),
            fixturefuncinfo=session._fixturemanager.getfixtureinfo(
                real_node.parent, func, None
            ),
        )

        if metadata.get("generated_schema_invalid"):
            item.add_marker(pytest.mark.generated_schema_invalid)
        if real_node.get_closest_marker("upstream_schema_invalid") or metadata.get(
            "upstream_schema_invalid"
        ):
            item.add_marker(pytest.mark.upstream_schema_invalid)

        return item

    our_items = [
        item
        for item in items
        if item.parent and item.parent.parent and item.parent.parent.name == "generator"
    ]
    items_by_nodeid = {}
    for item, nextitem in pairwise(our_items + [None]):
        item.session._setupstate.setup(item)
        try:
            item.runtest()
        except Exception:
            pass
        item.session._setupstate.teardown_exact(nextitem)
        items_by_nodeid[item.nodeid] = item

    COLLECTING_PIPELINES = False

    for nodeid, configs in PIPELINE_CONFIGS.items():
        if len(configs) == 1:
            assert not configs[0][0][
                "id"
            ], f"{nodeid} has only one pipeline, but it uses `id=`"
        else:
            for metadata, config in configs:
                assert metadata[
                    "id"
                ], f"{nodeid} loads multiple pipeline configs, but not all of them specify `id=`"

    with warnings.catch_warnings(action="ignore"):
        for index, item in reversed(list(enumerate(items))):
            nodeid = item.nodeid
            configs = PIPELINE_CONFIGS.get(nodeid)
            if not configs:
                continue

            real_node = items_by_nodeid[nodeid]
            for metadata, config in configs:
                items.insert(
                    index + 1,
                    _generate_test(real_node, metadata, test_generated_schema),
                )
                items.insert(
                    index + 1,
                    _generate_test(real_node, metadata, test_upstream_json_schema),
                )


@pytest.fixture(scope="session")
def load_pipeline(request):
    def model_load(
        config,
        *,
        id=None,
        generated_schema_invalid=False,
        upstream_schema_invalid=False,
    ):
        assert isinstance(config, dict)
        global PIPELINE_CONFIGS, COLLECTING_PIPELINES

        if COLLECTING_PIPELINES:
            PIPELINE_CONFIGS[request.node.nodeid].append(
                (
                    {
                        "id": id,
                        "generated_schema_invalid": generated_schema_invalid,
                        "upstream_schema_invalid": upstream_schema_invalid,
                    },
                    config,
                )
            )
        return BuildkitePipeline.model_load(config)

    return model_load


@pytest.fixture(scope="session")
def invalid_pipeline(request, load_pipeline):
    def model_load(
        config,
        *,
        error,
        path,
        id=None,
        upstream_schema_valid=False,
    ):
        with pytest.raises(ValidationError) as e:
            load_pipeline(
                config,
                id=id,
                upstream_schema_invalid=not upstream_schema_valid,
                generated_schema_invalid=True,
            )
        assert error in str(e.value)
        assert f"Path: {path}\n" in str(e.value) + "\n"

    return model_load
