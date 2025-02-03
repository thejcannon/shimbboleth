from hypothesis.strategies._internal.core import fixed_dictionaries
import pytest
from hypothesis import given
from hypothesis import strategies as st

from shimbboleth.buildkite.pipeline_config import CommandStep
from shimbboleth.buildkite.pipeline_config.notify import Notify


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


@st.composite
def str2list(draw):
    value = draw(st.text())
    return value, [value]


def ident(strategy):
    return strategy.map(lambda x: (x, x))

bool_strategy = st.one_of(
    st.just((True, True)),
    st.just((False, False)),
    st.just(("true", True)),
    st.just(("false", False)),
)
skip_strategy = st.one_of(
    st.just((OMITTED, False)),
    bool_strategy,
    st.just(("", False)),
    st.text().map(lambda x: (x, True)),
)
optional_int_strategy = st.one_of(
    st.just((OMITTED, None)),
    st.integers().map(lambda x: (x, x)),
)
optional_str_strategy = st.one_of(
    st.just((OMITTED, None)),
    st.text().map(lambda x: (x, x)),
)
list_str_strategy = st.one_of(
    st.just((OMITTED, [])),
    str2list(),
    ident(st.lists(st.text())),
)

@given(
    test_case=st.builds(
        dict,
        # @TODO: agents
        artifact_paths=list_str_strategy,
        branches=list_str_strategy,
        cache=st.one_of(
            list_str_strategy.map(lambda s: (s[0], CommandStep.Cache(paths=s[1]))),
            fixed_dictionaries(
                dict(
                    # @TEST: Can paths be a scalar?
                    paths=st.lists(st.text()),
                ),
                optional=dict(
                    name=st.text(),
                    size=st.from_regex("^\\d+g$", fullmatch=True),
                )
            ).map(lambda input: (input, CommandStep.Cache(**input)))
        ),
        cancel_on_build_failing=st.one_of(
            st.just((OMITTED, False)),
            bool_strategy,
        ),
        command=list_str_strategy,
        # @TODO: Concurrency fields
        # @TODO: env
        label=optional_str_strategy,
        # @TODO: matrix
        # @TODO: notify
        parallelism=optional_int_strategy,
        # @TODO: plugins
        priorotiy=optional_int_strategy,
        # @TODO: retry
        # @TODO: signature
        skip =skip_strategy,
        # @TODO: soft_fail
        timeout_in_minutes=st.one_of(
            st.just((OMITTED, None)),
            st.integers(min_value=1).map(lambda x: (x, x)),
        ),
    )
)
def test_command_step(load_step, test_case):
    data = {}
    for fieldname, (input, expected) in test_case.items():
        if input is OMITTED:
            continue
        data[fieldname] = input

    step = load_step(data)
    for fieldname, (input, expected) in test_case.items():
        assert getattr(step, fieldname) == expected
