
def test_unknown_step(*, invalid_pipeline):
    invalid_pipeline(
        {"steps": ["unknown"]},
        error="Expected `'unknown'` to be a valid Buildkite pipeline step",
        path=".steps[0]",
        id="string-unknown",
    )
    invalid_pipeline(
        {"steps": [None]},
        error="Expected `None` to be of type `str | dict[str, typing.Any]",
        path=".steps[0]",
        id="none",
    )
    invalid_pipeline(
        {"steps": [{"type": "unknown"}]},
        error="Expected `{'type': 'unknown'}` to be a valid Buildkite pipeline step",
        path=".steps[0]",
        id="type-unknown",
    )
def test_invalid_env(*, invalid_pipeline):
    invalid_pipeline(
        {"steps": [], "env": ["key"]},
        error="Expected `['key']` to be of type `dict`",
        path=".env",
        id="env_list",
    )

def test_invalid_notify(*, invalid_pipeline):
    invalid_pipeline(
        {"steps": [], "notify": ["unknown"]},
        error="Expected `'unknown'` to be a valid notification type",
        path=".notify[0]",
        id="notify_unknown",
    )
    invalid_pipeline(
        {"steps": [], "notify": [{"unknown": ""}]},
        error="Expected `{'unknown': ''}` to be a valid notification type",
        path=".notify[0]",
        id="notify_unknown_dict",
    )
    invalid_pipeline(
        {"steps": [], "notify": [{"slack": {"channels": []}}]},
        error="Expected `[]` to be non-empty",
        path=".notify[0].slack.channels",
        id="notify_slack_empty_channels",
    )
