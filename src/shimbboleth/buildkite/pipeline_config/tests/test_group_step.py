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
    def inner(step_config, *, id=None):
        return load_pipeline(
            [{"group": "group", "steps": ["wait"], **step_config}], id=id
        ).steps[0]

    return inner


def test_label_name(*, load_step):
    assert load_step({}, id="group").group == "group"
    assert load_step({"name": "name"}, id="name").group == "name"
    step = load_step({"label": "label", "name": "name"}, id="both")
    assert step.group == "label"


def test_steps(*, load_step):
    assert load_step({}, id="single").steps == [WaitStep()]
    assert load_step({"steps": ["wait", "wait"]}, id="multiple").steps == [
        WaitStep(),
        WaitStep(),
    ]


def test_notify__github_check(*, load_step):
    assert (
        load_step({"notify": ["github_check"]}, id="string").notify
        == load_step({"notify": [{"github_check": {}}]}, id="dict").notify
        == [Notify.GitHubCheck()]
    )


def test_notify__github_commit_status(*, load_step):
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


def test_notify__basecamp_campfire(*, load_step):
    assert load_step(
        {"notify": [{"basecamp_campfire": BASECAMP_CAMPFIRE_URL}]}
    ).notify == [Notify.BasecampCampfire(url=BASECAMP_CAMPFIRE_URL)]


def test_notify__slack(*, load_step):
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
        Notify.Slack(info=Notify.Slack.Info(channels=["#general"], message="message"))
    ]


@pytest.mark.parametrize("value, expected", SKIP_VALS.items())
def test_skip(value, expected, *, load_step):
    assert load_step({"skip": value}).skip == expected
