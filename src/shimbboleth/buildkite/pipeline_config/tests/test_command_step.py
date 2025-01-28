import pytest
from pytest import param

from shimbboleth.buildkite.pipeline_config import CommandStep
from shimbboleth.buildkite.pipeline_config.notify import Notify
from shimbboleth.buildkite.pipeline_config.tests.conftest import (
    STEP_TYPE_PARAMS,
    BOOLVALS,
    SKIP_VALS,
    SOFT_FAIL_VALS,
)


@pytest.fixture
def load_step(load_pipeline, request):
    def inner(step_fields, *, id=None):
        return load_pipeline({"steps": [{**step_fields, "type": "command"}]}, id=id).steps[0]

    return inner


def test_aliases(*, load_step):
    assert (
        load_step({"command": "cmd"}, id="command-scalar").command
        == load_step({"command": ["cmd"]}, id="command-list").command
        == load_step({"commands": "cmd"}, id="commands-scalar").command
        == load_step({"commands": ["cmd"]}, id="commands-list").command
        == ["cmd"]
    )


def test_agents(*, load_step):
    # @TODO: type coersion?
    step = load_step(
        {
            "agents": {
                "str": "string",
                "int": "0",
                "bool": "true",
            }
        }
    )
    assert step.agents == {"str": "string", "int": "0", "bool": "true"}


def test_artifact_paths(*, load_step):
    assert (
        load_step({"artifact_paths": "path"}).artifact_paths
        == load_step({"artifact_paths": ["path"]}).artifact_paths
        == ["path"]
    )


def test_cache(*, load_step):
    assert load_step({"cache": []}, id="empty-list").cache.paths == []
    assert (
        load_step({"cache": "path"}, id="scalar").cache.paths
        == load_step({"cache": ["path"]}, id="list").cache.paths
        == ["path"]
    )

    step = load_step(
        {
            "cache": {
                "paths": ["path"],
                "size": "20g",
                "name": "name",
            }
        },
        id="dict",
    )
    assert step.cache.paths == ["path"]
    assert step.cache.size == "20g"
    assert step.cache.name == "name"


@pytest.mark.parametrize("value, expected", BOOLVALS.items())
def test_cancel_on_build_failing(value, expected, *, load_step):
    assert (
        load_step({"cancel_on_build_failing": value}).cancel_on_build_failing
        == expected
    )


def test_concurrency(*, load_step):
    step = load_step(
        {
            "concurrency": 1,
            "concurrency_group": "group",
        }
    )
    assert step.concurrency == 1
    assert step.concurrency_group == "group"
    assert step.concurrency_method is None

    step = load_step(
        {
            "concurrency": 1,
            "concurrency_group": "group",
            "concurrency_method": "ordered",
        }
    )
    assert step.concurrency_method == "ordered"

    step = load_step(
        {
            "concurrency": 1,
            "concurrency_group": "group",
            "concurrency_method": "eager",
        }
    )
    assert step.concurrency_method == "eager"


def test_env(*, load_step):
    # @TODO: test types
    step = load_step(
        {
            "env": {
                "string": "string",
                "int": "0",
                "bool": "true",
            }
        }
    )
    assert step.env == {"string": "string", "int": "0", "bool": "true"}


def test_matrix_array(*, load_step):
    # @TEST: test different types
    assert load_step({"matrix": ["string", 0, True]}).matrix == ["string", 0, True]


class TestSingleDimMatrix:
    # @TODO: helper method

    def test_simple(self, *, load_step):
        assert (
            load_step({"matrix": {"setup": ["value"]}}, id="no-adjustments").matrix
            == load_step(
                {"matrix": {"setup": ["value"], "adjustments": []}},
                id="no-empty-adjustments",
            ).matrix
            == CommandStep.Matrix.SingleDim(setup=["value"])
        )

    def test_with_adjustments(self, *, load_step):
        assert load_step(
            {"matrix": {"setup": ["value"], "adjustments": [{"with": "newvalue"}]}}
        ).matrix == CommandStep.Matrix.SingleDim(
            setup=["value"],
            adjustments=[
                CommandStep.Matrix.SingleDim.Adjustment(with_value="newvalue")
            ],
        )

    @pytest.mark.parametrize("value, expected", SOFT_FAIL_VALS)
    def test_with_adjustments_with_soft_fail(self, value, expected, *, load_step):
        assert load_step(
            {
                "matrix": {
                    "setup": ["value"],
                    "adjustments": [{"with": "newvalue", "soft_fail": value}],
                }
            }
        ).matrix == CommandStep.Matrix.SingleDim(
            setup=["value"],
            adjustments=[
                CommandStep.Matrix.SingleDim.Adjustment(
                    with_value="newvalue", soft_fail=expected
                )
            ],
        )

    @pytest.mark.parametrize("value, expected", SKIP_VALS.items())
    def test_with_adjustments_with_skip(self, value, expected, *, load_step):
        assert load_step(
            {
                "matrix": {
                    "setup": ["value"],
                    "adjustments": [{"with": "newvalue", "skip": value}],
                }
            }
        ).matrix == CommandStep.Matrix.SingleDim(
            setup=["value"],
            adjustments=[
                CommandStep.Matrix.SingleDim.Adjustment(
                    with_value="newvalue", skip=expected
                )
            ],
        )


class TestMultiDimMatrix:
    def test_simple(self, *, load_step):
        assert (
            load_step(
                {
                    "matrix": {
                        "setup": {"key": "value"},
                    }
                },
                id="scalar",
            ).matrix
            == load_step(
                {
                    "matrix": {
                        "setup": {"key": ["value"]},
                    }
                },
                id="list",
            ).matrix
            == load_step(
                {
                    "matrix": {
                        "setup": {"key": ["value"]},
                        "adjustments": [],
                    }
                }
            ).matrix
            == CommandStep.Matrix.MultiDim(setup={"key": ["value"]})
        )

    def test_with_adjustments(self, *, load_step):
        assert load_step(
            {
                "matrix": {
                    "setup": {"key": ["value"]},
                    "adjustments": [{"with": {"key": "newvalue"}}],
                }
            }
        ).matrix == CommandStep.Matrix.MultiDim(
            setup={"key": ["value"]},
            adjustments=[
                CommandStep.Matrix.MultiDim.Adjustment(with_value={"key": "newvalue"})
            ],
        )

    @pytest.mark.parametrize("value, expected", SOFT_FAIL_VALS)
    def test_with_adjustments_with_soft_fail(self, value, expected, *, load_step):
        assert load_step(
            {
                "matrix": {
                    "setup": {"key": ["value"]},
                    "adjustments": [{"with": {"key": "newvalue"}, "soft_fail": value}],
                }
            }
        ).matrix == CommandStep.Matrix.MultiDim(
            setup={"key": ["value"]},
            adjustments=[
                CommandStep.Matrix.MultiDim.Adjustment(
                    with_value={"key": "newvalue"}, soft_fail=expected
                )
            ],
        )

    @pytest.mark.parametrize("value, expected", SKIP_VALS.items())
    def test_with_adjustments_with_skip(self, value, expected, *, load_step):
        assert load_step(
            {
                "matrix": {
                    "setup": {"key": ["value"]},
                    "adjustments": [{"with": {"key": "newvalue"}, "skip": value}],
                }
            }
        ).matrix == CommandStep.Matrix.MultiDim(
            setup={"key": ["value"]},
            adjustments=[
                CommandStep.Matrix.MultiDim.Adjustment(
                    with_value={"key": "newvalue"}, skip=expected
                )
            ],
        )


class TestNotify:
    def test_github_check(self, *, load_step):
        assert (
            load_step({"notify": ["github_check"]}, id="string").notify
            == load_step({"notify": [{"github_check": {}}]}, id="dict").notify
            == [Notify.GitHubCheck()]
        )
        assert load_step({"notify": [{"github_check": {"name": "name"}}]}).notify == [
            Notify.GitHubCheck(info={"name": "name"})
        ]

    def test_github_commit_status(self, *, load_step):
        assert load_step({"notify": ["github_commit_status"]}, id="string").notify == [
            Notify.GitHubCommitStatus()
        ]
        assert load_step(
            {"notify": [{"github_commit_status": {"context": "context"}}]},
            id="with-context",
        ).notify == [
            Notify.GitHubCommitStatus(
                info=Notify.GitHubCommitStatus.Info(context="context")
            )
        ]

    def test_basecamp_campfire(self, *, load_step):
        assert load_step({"notify": [{"basecamp_campfire": "url"}]}).notify == [
            Notify.BasecampCampfire(url="url")
        ]

    def test_slack(self, *, load_step):
        assert (
            load_step({"notify": [{"slack": "#general"}]}, id="string").notify
            == load_step(
                {"notify": [{"slack": {"channels": "#general"}}]}, id="channels-string"
            ).notify
            == load_step(
                {"notify": [{"slack": {"channels": ["#general"]}}]}, id="channels-list"
            ).notify
            == [Notify.Slack(info=Notify.Slack.Info(channels=["#general"]))]
        )
        assert load_step(
            {"notify": [{"slack": {"channels": ["#general"], "message": "message"}}]},
            id="with-message",
        ).notify == [
            Notify.Slack(
                info=Notify.Slack.Info(channels=["#general"], message="message")
            )
        ]


def test_parallelism(*, load_step):
    assert load_step({"parallelism": 1}).parallelism == 1


class TestPlugins:
    def test_plugin_list_string(self, *, load_step):
        step = load_step({"plugins": ["plugin"]})
        assert step.plugins[0].spec == "plugin"
        assert step.plugins[0].config is None

    def test_plugin_list_dict(self, *, load_step):
        step = load_step({"plugins": [{"plugin": {"key": "value"}}]})
        assert step.plugins[0].spec == "plugin"
        assert step.plugins[0].config == {"key": "value"}

    def test_plugin_dict_no_config(self, *, load_step):
        step = load_step({"plugins": [{"plugin": None}]})
        assert step.plugins[0].spec == "plugin"
        assert step.plugins[0].config is None

    def test_plugin_dict_with_config(self, *, load_step):
        step = load_step({"plugins": [{"plugin": {"key": "value"}}]})
        assert step.plugins[0].spec == "plugin"
        assert step.plugins[0].config == {"key": "value"}


def test_priority(*, load_step):
    assert load_step({"priority": 1}).priority == 1


class TestRetry:
    class TestAutomatic:
        @pytest.mark.parametrize("value, expected", BOOLVALS.items())
        def test_boolean_values(self, value, expected, *, load_step):
            step = load_step({"retry": {"automatic": value}})
            assert len(step.retry.automatic) == (1 if expected else 0)

        def test_exit_status_scalar(self, *, load_step):
            step = load_step({"retry": {"automatic": {"exit_status": 1}}})
            assert step.retry.automatic[0].exit_status == [1]

        def test_exit_status_wildcard(self, *, load_step):
            step = load_step({"retry": {"automatic": {"exit_status": "*"}}})
            assert step.retry.automatic[0].exit_status == "*"

        def test_exit_status_list(self, *, load_step):
            step = load_step({"retry": {"automatic": {"exit_status": [1, 2]}}})
            assert step.retry.automatic[0].exit_status == [1, 2]

        def test_limit(self, *, load_step):
            step = load_step({"retry": {"automatic": [{"limit": 5}]}})
            assert step.retry.automatic[0].limit == 5

        def test_signal(self, *, load_step):
            step = load_step({"retry": {"automatic": [{"signal": "signal"}]}})
            assert step.retry.automatic[0].signal == "signal"

        @pytest.mark.parametrize(
            "reason",
            [
                "*",
                "none",
                "agent_refused",
                "agent_stop",
                "cancel",
                "process_run_error",
                "signature_rejected",
            ],
        )
        def test_signal_reason(self, reason, *, load_step):
            step = load_step({"retry": {"automatic": [{"signal_reason": reason}]}})
            assert step.retry.automatic[0].signal_reason == reason

    class TestManual:
        @pytest.mark.parametrize("value, expected", BOOLVALS.items())
        def test_boolean_values(self, value, expected, *, load_step):
            step = load_step({"retry": {"manual": value}})
            assert step.retry.manual.allowed == expected

        @pytest.mark.parametrize("value, expected", BOOLVALS.items())
        def test_allowed(self, value, expected, *, load_step):
            step = load_step({"retry": {"manual": {"allowed": value}}})
            assert step.retry.manual.allowed == expected

        @pytest.mark.parametrize("value, expected", BOOLVALS.items())
        def test_permit_on_passed(self, value, expected, *, load_step):
            step = load_step({"retry": {"manual": {"permit_on_passed": value}}})
            assert step.retry.manual.permit_on_passed == expected

        def test_reason(self, *, load_step):
            step = load_step(
                {"retry": {"manual": {"reason": "reason", "allowed": True}}}
            )
            assert step.retry.manual.reason == "reason"
            assert step.retry.manual.allowed is True


def test_signature(*, load_step):
    # @TODO: signed_fields as scalar string?
    step = load_step({"signature": {}})
    assert step.signature.algorithm is None
    assert step.signature.signed_fields == []
    assert step.signature.value is None

    step = load_step(
        {
            "signature": {
                "algorithm": "sha256",
                "signed_fields": ["field1"],
                "value": "value",
            }
        }
    )
    assert step.signature.algorithm == "sha256"
    assert step.signature.signed_fields == ["field1"]
    assert step.signature.value == "value"


@pytest.mark.parametrize("value, expected", SKIP_VALS.items())
def test_skip(value, expected, *, load_step):
    assert load_step({"skip": value}).skip == expected


@pytest.mark.parametrize("value, expected", SOFT_FAIL_VALS)
def test_soft_fail(value, expected, *, load_step):
    assert load_step({"soft_fail": value}).soft_fail == expected


def test_timeout_in_minutes(*, load_step):
    assert load_step({"timeout_in_minutes": 1}).timeout_in_minutes == 1
