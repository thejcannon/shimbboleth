import pytest

from shimbboleth.buildkite.pipeline_config import (
    BuildkitePipeline,
    GroupStep,
    WaitStep,
    Notify,
)
from shimbboleth.buildkite.pipeline_config.tests.conftest import BOOLVALS, SKIP_VALS

BASECAMP_CAMPFIRE_URL = "https://3.basecamp.com/123456/integrations/abcdef/buckets/1234567/chats/89012345/lines"


@pytest.fixture
def load_step(load_pipeline):
    def inner(step_config, **kwargs):
        return load_pipeline(
            {"steps": [{"group": "group", "steps": ["wait"], **step_config}]}, **kwargs
        ).steps[0]

    return inner


def test_label_name(*, load_step):
    assert load_step({}, id="group").group == "group"
    assert load_step({"name": "name"}, id="name").group == "name"
    assert load_step({"label": "label", "name": "name"}, id="both").group == "label"


def test_steps(*, load_step):
    assert load_step({}, id="single").steps == [WaitStep()]
    assert load_step({"steps": ["wait", "wait"]}, id="multiple").steps == [
        WaitStep(),
        WaitStep(),
    ]


class TestNotify:
    @pytest.fixture
    @staticmethod
    def load_notify(load_step):
        def inner(notify_config, *, id=None):
            return load_step({"notify": notify_config}, id=id).notify

        return inner

    def test_notify__github_check(self, load_notify):
        assert load_notify(["github_check"], id="string") == [Notify.GitHubCheck()]
        assert load_notify([{"github_check": {}}], id="dict") == [Notify.GitHubCheck()]

    def test_notify__github_commit_status(self, load_notify):
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

    def test_notify__basecamp_campfire(self, load_notify):
        assert load_notify([{"basecamp_campfire": BASECAMP_CAMPFIRE_URL}]) == [
            Notify.BasecampCampfire(url=BASECAMP_CAMPFIRE_URL)
        ]

    @pytest.mark.upstream_schema_invalid
    def test_notify__slack__scalar(self, load_notify):
        # same as below, but upstream invalid
        assert load_notify([{"slack": {"channels": "#general"}}]) == [
            Notify.Slack(info=Notify.Slack.Info(channels=["#general"]))
        ]

    def test_notify__slack(self, load_notify):
        assert (
            load_notify([{"slack": "#general"}], id="string")
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


@pytest.mark.parametrize("value, expected", SKIP_VALS)
def test_skip(value, expected, *, load_step):
    assert load_step({"skip": value}).skip == expected
