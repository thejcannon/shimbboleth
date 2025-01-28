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
    def inner(step_fields, **kwargs):
        return load_pipeline(
            {"steps": [{**step_fields, "type": "command"}]}, **kwargs
        ).steps[0]

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
    step = load_step({"agents": {"str": "string", "int": "0", "bool": "true"}})
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
        {"cache": {"paths": ["path"], "size": "20g", "name": "name"}},
        id="dict",
    )
    assert step.cache.paths == ["path"]
    assert step.cache.size == "20g"
    assert step.cache.name == "name"


@pytest.mark.parametrize("value, expected", BOOLVALS)
def test_cancel_on_build_failing(value, expected, *, load_step):
    assert (
        load_step({"cancel_on_build_failing": value}).cancel_on_build_failing
        == expected
    )


def test_concurrency(*, load_step):
    step = load_step({"concurrency": 1, "concurrency_group": "group"})
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


class TestMatrix:
    @pytest.fixture
    @staticmethod
    def load_matrix(load_step):
        def inner(matrix_config, **kwargs):
            return load_step({"matrix": matrix_config}, **kwargs).matrix

        return inner

    def test_array(self, *, load_matrix):
        assert load_matrix(["string", 0, True]) == ["string", 0, True]

    class TestSingleDim:
        def test_simple(self, *, load_matrix):
            assert (
                load_matrix({"setup": ["value"]}, id="no-adjustments")
                == load_matrix(
                    {"setup": ["value"], "adjustments": []},
                    id="no-empty-adjustments",
                )
                == CommandStep.Matrix.SingleDim(setup=["value"])
            )

        @pytest.mark.upstream_schema_invalid
        def test_with_adjustments(self, *, load_matrix):
            assert load_matrix(
                {"setup": ["value"], "adjustments": [{"with": "newvalue"}]}
            ) == CommandStep.Matrix.SingleDim(
                setup=["value"],
                adjustments=[
                    CommandStep.Matrix.SingleDim.Adjustment(with_value="newvalue")
                ],
            )

        @pytest.mark.upstream_schema_invalid
        @pytest.mark.parametrize("value, expected", SOFT_FAIL_VALS)
        def test_with_adjustments_with_soft_fail(self, value, expected, *, load_matrix):
            assert load_matrix(
                {
                    "setup": ["value"],
                    "adjustments": [{"with": "newvalue", "soft_fail": value}],
                }
            ) == CommandStep.Matrix.SingleDim(
                setup=["value"],
                adjustments=[
                    CommandStep.Matrix.SingleDim.Adjustment(
                        with_value="newvalue", soft_fail=expected
                    )
                ],
            )

        @pytest.mark.upstream_schema_invalid
        @pytest.mark.parametrize("value, expected", SKIP_VALS)
        def test_with_adjustments_with_skip(self, value, expected, *, load_matrix):
            assert load_matrix(
                {
                    "setup": ["value"],
                    "adjustments": [{"with": "newvalue", "skip": value}],
                }
            ) == CommandStep.Matrix.SingleDim(
                setup=["value"],
                adjustments=[
                    CommandStep.Matrix.SingleDim.Adjustment(
                        with_value="newvalue", skip=expected
                    )
                ],
            )

    class TestMultiDim:
        def test_simple(self, *, load_matrix):
            assert (
                load_matrix(
                    {"setup": {"key": "value"}},
                    id="scalar",
                    upstream_schema_invalid=True,
                )
                == load_matrix(
                    {"setup": {"key": ["value"]}},
                    id="list",
                )
                == load_matrix(
                    {
                        "setup": {"key": ["value"]},
                        "adjustments": [],
                    },
                    id="empty-adjustments",
                )
                == CommandStep.Matrix.MultiDim(setup={"key": ["value"]})
            )

        def test_with_adjustments(self, *, load_matrix):
            assert load_matrix(
                {
                    "setup": {"key": ["value"]},
                    "adjustments": [{"with": {"key": "newvalue"}}],
                }
            ) == CommandStep.Matrix.MultiDim(
                setup={"key": ["value"]},
                adjustments=[
                    CommandStep.Matrix.MultiDim.Adjustment(
                        with_value={"key": "newvalue"}
                    )
                ],
            )

        @pytest.mark.parametrize("value, expected", SOFT_FAIL_VALS)
        def test_with_adjustments_with_soft_fail(self, value, expected, *, load_matrix):
            assert load_matrix(
                {
                    "setup": {"key": ["value"]},
                    "adjustments": [{"with": {"key": "newvalue"}, "soft_fail": value}],
                }
            ) == CommandStep.Matrix.MultiDim(
                setup={"key": ["value"]},
                adjustments=[
                    CommandStep.Matrix.MultiDim.Adjustment(
                        with_value={"key": "newvalue"}, soft_fail=expected
                    )
                ],
            )

        @pytest.mark.parametrize("value, expected", SKIP_VALS)
        def test_with_adjustments_with_skip(self, value, expected, *, load_matrix):
            assert load_matrix(
                {
                    "setup": {"key": ["value"]},
                    "adjustments": [{"with": {"key": "newvalue"}, "skip": value}],
                }
            ) == CommandStep.Matrix.MultiDim(
                setup={"key": ["value"]},
                adjustments=[
                    CommandStep.Matrix.MultiDim.Adjustment(
                        with_value={"key": "newvalue"}, skip=expected
                    )
                ],
            )


class TestNotify:
    @pytest.fixture
    @staticmethod
    def load_notify(load_step):
        def inner(notify_config, **kwargs):
            return load_step({"notify": notify_config}, **kwargs).notify

        return inner

    def test_github_check(self, load_notify):
        assert load_notify(["github_check"], id="string") == [Notify.GitHubCheck()]
        assert load_notify([{"github_check": {}}], id="dict") == [Notify.GitHubCheck()]
        assert load_notify([{"github_check": {"name": "name"}}]) == [
            Notify.GitHubCheck(info={"name": "name"})
        ]

    def test_github_commit_status(self, load_notify):
        assert load_notify(["github_commit_status"], id="string") == [
            Notify.GitHubCommitStatus()
        ]
        assert load_notify(
            [{"github_commit_status": {"context": "context"}}],
            id="with-context",
        ) == [
            Notify.GitHubCommitStatus(
                info=Notify.GitHubCommitStatus.Info(context="context")
            )
        ]

    def test_basecamp_campfire(self, load_notify):
        assert load_notify([{"basecamp_campfire": "url"}]) == [
            Notify.BasecampCampfire(url="url")
        ]

    def test_slack(self, load_notify):
        assert (
            load_notify(
                [{"slack": {"channels": "#general"}}],
                id="scalar",
                upstream_schema_invalid=True,
            )
            == load_notify([{"slack": "#general"}], id="string")
            == load_notify([{"slack": {"channels": ["#general"]}}], id="channels-list")
            == [Notify.Slack(info=Notify.Slack.Info(channels=["#general"]))]
        )
        assert load_notify(
            [{"slack": {"channels": ["#general"], "message": "message"}}],
            id="with-message",
        ) == [
            Notify.Slack(
                info=Notify.Slack.Info(channels=["#general"], message="message")
            )
        ]


def test_parallelism(*, load_step):
    assert load_step({"parallelism": 1}).parallelism == 1


class TestPlugins:
    @pytest.fixture
    @staticmethod
    def load_plugins(load_step):
        def inner(plugins_config, *, id=None):
            return load_step({"plugins": plugins_config}, id=id).plugins

        return inner

    def test_plugin_list_string(self, *, load_plugins):
        plugins = load_plugins(["plugin"])
        assert plugins[0].spec == "plugin"
        assert plugins[0].config is None

    def test_plugin_list_dict(self, *, load_plugins):
        plugins = load_plugins([{"plugin": {"key": "value"}}])
        assert plugins[0].spec == "plugin"
        assert plugins[0].config == {"key": "value"}

    def test_plugin_dict_no_config(self, *, load_plugins):
        plugins = load_plugins([{"plugin": None}])
        assert plugins[0].spec == "plugin"
        assert plugins[0].config is None

    def test_plugin_dict_with_config(self, *, load_plugins):
        plugins = load_plugins([{"plugin": {"key": "value"}}])
        assert plugins[0].spec == "plugin"
        assert plugins[0].config == {"key": "value"}


def test_priority(*, load_step):
    assert load_step({"priority": 1}).priority == 1


class TestRetry:
    class TestAutomatic:
        @pytest.fixture
        @staticmethod
        def load_automatic_retry(load_step):
            def inner(retry_config, *, id=None):
                return load_step(
                    {"retry": {"automatic": retry_config}}, id=id
                ).retry.automatic

            return inner

        @pytest.mark.parametrize("value, expected", BOOLVALS)
        def test_boolean_values(self, value, expected, *, load_automatic_retry):
            automatic_retry = load_automatic_retry(value)
            assert len(automatic_retry) == (1 if expected else 0)

        def test_exit_status_scalar(self, *, load_automatic_retry):
            automatic_retry = load_automatic_retry({"exit_status": 1})
            assert automatic_retry[0].exit_status == [1]

        def test_exit_status_wildcard(self, *, load_automatic_retry):
            automatic_retry = load_automatic_retry({"exit_status": "*"})
            assert automatic_retry[0].exit_status == "*"

        def test_exit_status_list(self, *, load_automatic_retry):
            automatic_retry = load_automatic_retry({"exit_status": [1, 2]})
            assert automatic_retry[0].exit_status == [1, 2]

        def test_limit(self, *, load_automatic_retry):
            automatic_retry = load_automatic_retry([{"limit": 5}])
            assert automatic_retry[0].limit == 5

        def test_signal(self, *, load_automatic_retry):
            automatic_retry = load_automatic_retry([{"signal": "signal"}])
            assert automatic_retry[0].signal == "signal"

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
        def test_signal_reason(self, reason, *, load_automatic_retry):
            automatic_retry = load_automatic_retry([{"signal_reason": reason}])
            assert automatic_retry[0].signal_reason == reason

    class TestManual:
        @pytest.fixture
        @staticmethod
        def load_manual_retry(load_step):
            def inner(retry_config, *, id=None):
                return load_step(
                    {"retry": {"manual": retry_config}}, id=id
                ).retry.manual

            return inner

        @pytest.mark.parametrize("value, expected", BOOLVALS)
        def test_boolean_values(self, value, expected, *, load_manual_retry):
            manual_retry = load_manual_retry(value)
            assert manual_retry.allowed == expected

        @pytest.mark.parametrize("value, expected", BOOLVALS)
        def test_allowed(self, value, expected, *, load_manual_retry):
            manual_retry = load_manual_retry({"allowed": value})
            assert manual_retry.allowed == expected

        @pytest.mark.parametrize("value, expected", BOOLVALS)
        def test_permit_on_passed(self, value, expected, *, load_manual_retry):
            manual_retry = load_manual_retry({"permit_on_passed": value})
            assert manual_retry.permit_on_passed == expected

        def test_reason(self, *, load_manual_retry):
            manual_retry = load_manual_retry({"reason": "reason", "allowed": True})
            assert manual_retry.reason == "reason"
            assert manual_retry.allowed is True


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


@pytest.mark.parametrize("value, expected", SKIP_VALS)
def test_skip(value, expected, *, load_step):
    assert load_step({"skip": value}).skip == expected


@pytest.mark.parametrize("value, expected", SOFT_FAIL_VALS)
def test_soft_fail(value, expected, *, load_step):
    assert load_step({"soft_fail": value}).soft_fail == expected


def test_timeout_in_minutes(*, load_step):
    assert load_step({"timeout_in_minutes": 1}).timeout_in_minutes == 1
