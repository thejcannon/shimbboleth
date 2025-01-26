import dataclasses

from shimbboleth.internal.clay.model import Model, field
from shimbboleth.internal.clay.validation import NonEmptyList
from shimbboleth.internal.clay.json_load import JSONLoadError
from shimbboleth.internal.clay.jsonT import JSONObject


class _Service(Model, extra=False):
    # @TEST: Is an empty string considered a skip?
    if_condition: str | None = field(default=None, json_alias="if")


# @TODO: Should we overload `__new__` (for convenience)?
#   E.g. Notify(email="")
#   I think so...
class Notify(Model, extra=False):
    class Email(_Service, extra=False):
        address: str = field(json_alias="email")

    class BasecampCampfire(_Service, extra=False):
        url: str = field(json_alias="basecamp_campfire")

    class Slack(_Service, extra=False):
        class Info(Model, extra=False):
            # @VALIDATE: The `slack` notification is invalid: Each channel should be defined as
            #   `#channel-name`, `team-name#channel-name`, 'team-name@user-name', '@user-name', 'U12345678', 'W12345678', or 'S12345678'
            channels: NonEmptyList[str]
            message: str | None = None

        info: Info = field(json_alias="slack")

    class Webhook(_Service, extra=False):
        url: str = field(json_alias="webhook")

    class Pagerduty(_Service, extra=False):
        change_event: str = field(json_alias="pagerduty_change_event")

    class GitHubCommitStatus(_Service, extra=False):
        class Info(Model, extra=True):
            # @TODO: JSON: allowed to be a boolean?
            context: str | None = None

        info: Info = field(default_factory=Info, json_alias="github_commit_status")

    class GitHubCheck(_Service, extra=False):
        # NB: See https://github.com/buildkite/pipeline-schema/pull/117#issuecomment-2537680177
        # @TODO: JSON can be null
        info: dict[str, str] = field(default_factory=dict, json_alias="github_check")


def _parse_notify(
    value: str | JSONObject,
) -> (
    Notify.Email
    | Notify.BasecampCampfire
    | Notify.Slack
    | Notify.Webhook
    | Notify.Pagerduty
    | Notify.GitHubCheck
    | Notify.GitHubCommitStatus
):
    if value == "github_check":
        return Notify.GitHubCheck()
    if value == "github_commit_status":
        return Notify.GitHubCommitStatus()

    if isinstance(value, dict):
        # NB: There are other/shorter ways of doing this, but I like the explicit
        if "email" in value:
            return Notify.Email.model_load(value)
        if "basecamp_campfire" in value:
            return Notify.BasecampCampfire.model_load(value)
        if "slack" in value:
            return Notify.Slack.model_load(value)
        if "webhook" in value:
            return Notify.Webhook.model_load(value)
        if "pagerduty_change_event" in value:
            return Notify.Pagerduty.model_load(value)
        if "github_commit_status" in value:
            return Notify.GitHubCommitStatus.model_load(value)
        if "github_check" in value:
            return Notify.GitHubCheck.model_load(value)

    raise JSONLoadError(value=value, expectation="be a valid notification type")


def _parse_step_notify(
    value: str | JSONObject,
) -> (
    Notify.BasecampCampfire
    | Notify.Slack
    | Notify.GitHubCheck
    | Notify.GitHubCommitStatus
):
    parsed = _parse_notify(value)
    if isinstance(parsed, (Notify.Email, Notify.Webhook, Notify.Pagerduty)):
        keyname = dataclasses.fields(parsed)[1].name
        # NB: It IS a valid _build_ notification though
        raise JSONLoadError(value=keyname, expectation="be a valid step notification")
    return parsed
