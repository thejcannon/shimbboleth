import pytest
from pytest import param
from shimbboleth.buildkite.pipeline_config import BuildkitePipeline, Notify


def test_empty(*, load_pipeline):
    assert load_pipeline({"steps": []}) == BuildkitePipeline(steps=[])


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


class TestNotify:
    @pytest.fixture
    @staticmethod
    def load_notify(load_pipeline):
        def inner(notify_config, **kwargs):
            return load_pipeline({"steps": [], "notify": notify_config}, **kwargs).notify

        return inner

    def test_notify__email(self, load_notify):
        assert load_notify([{"email": "email@example.com"}]) == [
            Notify.Email(address="email@example.com")
        ]

    def test_notify__basecamp_campfire(self, load_notify):
        BASECAMP_CAMPFIRE_URL = "https://3.basecamp.com/123456/integrations/abcdef/buckets/1234567/chats/89012345/lines"
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

    def test_notify_webhook(self, load_notify):
        assert load_notify([{"webhook": "https://example.com"}]) == [
            Notify.Webhook(url="https://example.com")
        ]

    def test_notify_pagerduty(self, load_notify):
        assert load_notify([{"pagerduty_change_event": "pagerduty_change_event"}]) == [
            Notify.Pagerduty(change_event="pagerduty_change_event")
        ]

    def test_notify__github_check(self, load_notify):
        assert load_notify(["github_check"], id="string") == [Notify.GitHubCheck()]
        assert load_notify([{"github_check": {}}], id="dict") == [Notify.GitHubCheck()]

    def test_notify__github_commit_status(self, load_notify):
        assert load_notify(["github_commit_status"], id="string") == [
            Notify.GitHubCommitStatus()
        ]
        assert load_notify(
            [{"github_commit_status": {"context": "context"}}],
            id="dict",
        ) == [
            Notify.GitHubCommitStatus(
                info=Notify.GitHubCommitStatus.Info(context="context")
            )
        ]


def test_extra_keys(*, load_pipeline):
    assert load_pipeline({"steps": [], "one-king-mop": "mop-all-around"})._extra == {
        "one-king-mop": "mop-all-around"
    }
