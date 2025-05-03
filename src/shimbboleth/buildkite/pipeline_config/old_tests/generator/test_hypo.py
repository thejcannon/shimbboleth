from hypothesis.strategies._internal.core import fixed_dictionaries
import pytest
from hypothesis import given
from hypothesis import strategies as st

from shimbboleth.buildkite.pipeline_config import CommandStep


@pytest.fixture(scope="session")
def load_step(load_pipeline, request):
    def inner(step_fields, **kwargs):
        return load_pipeline(
            {"steps": [{**step_fields, "type": "command"}]}, **kwargs
        ).steps[0]

    return inner


@object.__new__
class OMITTED:
    def __repr__(self):
        return "OMITTED"


def optional(strategy, default=None):
    """Make a strategy optional, defaulting to None when omitted."""
    return st.one_of(
        st.just((OMITTED, default)),
        strategy,
    )


str2list = st.text().map(lambda x: (x, [x]))
list_str_strategy = optional(st.one_of(str2list, st.lists(st.text())), [])

# Core strateg
bool_strategy = st.one_of(
    st.just((True, True)),
    st.just((False, False)),
    st.just(("true", True)),
    st.just(("false", False)),
)

skip_strategy = st.one_of(
    bool_strategy,
    st.just(("", False)),
    st.text(min_size=1),
)

soft_fail_strategy = optional(
    bool_strategy,
    st.lists(
        st.fixed_dictionaries({"exit_status": st.one_of(st.just("*"), st.integers())}),
        min_size=1,
    ),
    False,
)

# ===== command strategies =====

cache_strategy = optional(
    st.one_of(
        st.text().map(lambda s: (s, CommandStep.Cache(paths=[s]))),
        st.lists(st.text()).map(lambda l: (l, CommandStep.Cache(paths=l))),
        fixed_dictionaries(
            dict(
                paths=st.lists(st.text()),
            ),
            optional=dict(
                name=st.text(),
                size=st.from_regex("^\\d+g$", fullmatch=True),
            ),
        ).map(lambda input: (input, CommandStep.Cache(**input))),
    ),
    CommandStep.Cache(paths=[]),
)


@given(
    test_case=st.builds(
        dict,
        # @TODO: agents
        artifact_paths=list_str_strategy,
        branches=list_str_strategy,
        cache=cache_strategy,
        cancel_on_build_failing=optional(bool_strategy, False),
        command=list_str_strategy,
        # @TODO: Concurrency fields
        # @TODO: env
        label=optional(st.text()),
        # @TODO: matrix
        # @TODO: notify
        parallelism=optional(st.integers()),
        # @TODO: plugins
        priority=optional(st.integers()),
        # @TODO: retry
        # @TODO: signature
        skip=optional(skip_strategy, False),
        soft_fail=soft_fail_strategy,
        timeout_in_minutes=optional(st.integers(min_value=1)),
    )
)
def test_command_step(load_step, test_case):
    # @TODO: Move this to `.map`?
    test_case = {
        fieldname: (input if isinstance(input, tuple) else (input, input))
        for fieldname, input in test_case.items()
    }
    data = {
        fieldname: input
        for fieldname, (input, _) in test_case.items()
        if input is not OMITTED
    }

    step = load_step(data)
    for fieldname, (_, expected) in test_case.items():
        assert getattr(step, fieldname) == expected
