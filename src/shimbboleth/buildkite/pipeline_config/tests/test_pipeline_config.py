"""
This module is responsible for generating the pipelines in the `pipelienes` directory.

We use a multi-step process for a few reasons:
    - YAML files on disk are easier to grok than Python
        - And closer align with Buildkite's usage
    - It's easier to lint YAML files than Python code
        - Ensure we aren't duplicating test cases, etc...
    - It's easier to review changes to YAML files than Python code
    - We can define a single test case, and it be "expanded" into multiple
        tests scenarios

However it does lead to some complications:
    - We need to ensure we fail (especially in CI) if we don't have the right files generated
"""

# Procdure:
#   - General the YAML into a session-wide tempdir
#   - (if they don't match, copy it to repo dir, and fail)
#   - At the end, compare the files/dirs from tempdir and repo
#       (to see if there's extra files in repo not in tempdir/vice versa)
#   - (but somehow only do this if we're running a full suite?)

import pytest
from pytest import param
from shimbboleth.buildkite.pipeline_config import BuildkitePipeline, Notify


def test_empty(*, load_pipeline):
    assert load_pipeline([]) == BuildkitePipeline(steps=[])


def test_agents_dict(*, load_pipeline):
    assert load_pipeline(
        {"steps": [], "agents": {"str": "Teddy", "int": 0, "bool": True}}
        # @TODO: Are they actually string?
    ).agents == {"str": "Teddy", "int": "0", "bool": "true"}


def test_agents_list(*, load_pipeline):
    assert load_pipeline(
        {"steps": [], "agents": ["noequals", "simple=1", "with-equals=key=value"]}
    ).agents == {
        "noequals": "true",
        "simple": "1",
        "with-equals": "key=value",
    }


@pytest.mark.skip
def test_agents_list__repeated_key(*, load_pipeline):
    # Apparently this is allowed? Not sure the semantics though...
    # (FWIW I tried this and the API, which results "agent query rules" as a list-of-strings
    #   had them both...)
    assert load_pipeline(
        {"steps": [], "agents": ["key=value1", "key=value2"]}
    ).agents == {
        "noequals": "true",
        "simple": "1",
        "with-equals": "key=value",
    }


def test_env(*, load_pipeline):
    assert load_pipeline(
        {"steps": [], "env": {"string": "string", "int": 0, "bool": True}}
    ).env == {"string": "string", "int": "0", "bool": "true"}


# @TODO: For each notify, also test `if`
#   (use param)


def test_notify__email(*, load_pipeline):
    assert load_pipeline(
        {"steps": [], "notify": [{"email": "email@example.com"}]}
    ).notify == [Notify.Email(address="email@example.com")]


def test_notify__basecamp_campfire(*, load_pipeline):
    BASECAMP_CAMPFIRE_URL = "https://3.basecamp.com/123456/integrations/abcdef/buckets/1234567/chats/89012345/lines"
    assert load_pipeline(
        {"steps": [], "notify": [{"basecamp_campfire": BASECAMP_CAMPFIRE_URL}]}
    ).notify == [Notify.BasecampCampfire(url=BASECAMP_CAMPFIRE_URL)]


def test_notify__slack(*, load_pipeline):
    assert (
        load_pipeline(
            {"steps": [], "notify": [{"slack": "#general"}]}, id="string"
        ).notify
        == load_pipeline(
            {"steps": [], "notify": [{"slack": {"channels": "#general"}}]},
            id="channels-string",
        ).notify
        == load_pipeline(
            {"steps": [], "notify": [{"slack": {"channels": ["#general"]}}]},
            id="channels-list",
        ).notify
        == [Notify.Slack(info=Notify.Slack.Info(channels=["#general"]))]
    )
    assert load_pipeline(
        {
            "steps": [],
            "notify": [{"slack": {"channels": ["#general"], "message": "message"}}],
        },
        id="with-message",
    ).notify == [
        Notify.Slack(info=Notify.Slack.Info(channels=["#general"], message="message"))
    ]


def test_notify_webhook(*, load_pipeline):
    assert load_pipeline(
        {"steps": [], "notify": [{"webhook": "https://example.com"}]}
    ).notify == [Notify.Webhook(url="https://example.com")]


def test_notify_pagerduty(*, load_pipeline):
    assert load_pipeline(
        {
            "steps": [],
            "notify": [{"pagerduty_change_event": "pagerduty_change_event"}],
        }
    ).notify == [Notify.Pagerduty(change_event="pagerduty_change_event")]


def test_notify__github_check(*, load_pipeline):
    assert load_pipeline(
        {"steps": [], "notify": ["github_check"]}, id="string"
    ).notify == [Notify.GitHubCheck()]
    assert load_pipeline(
        {"steps": [], "notify": [{"github_check": {}}]}, id="dict"
    ).notify == [Notify.GitHubCheck()]


def test_notify__github_commit_status(*, load_pipeline):
    assert load_pipeline(
        {"steps": [], "notify": ["github_commit_status"]}, id="string"
    ).notify == [Notify.GitHubCommitStatus()]
    assert load_pipeline(
        {"steps": [], "notify": [{"github_commit_status": {"context": "context"}}]},
        id="dict",
    ).notify == [
        Notify.GitHubCommitStatus(
            info=Notify.GitHubCommitStatus.Info(context="context")
        )
    ]


def test_extra_keys(*, load_pipeline):
    assert load_pipeline({"steps": [], "one-king-mop": "mop-all-around"})._extra == {
        "one-king-mop": "mop-all-around"
    }
