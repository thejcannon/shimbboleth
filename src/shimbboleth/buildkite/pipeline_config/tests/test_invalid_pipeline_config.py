def test_unknown_step(*, load_invalid_pipeline):
    load_invalid_pipeline(
        {"steps": ["unknown"]},
        error="Expected `'unknown'` to be a valid Buildkite pipeline step",
        path=".steps[0]",
        id="string-unknown",
    )
    load_invalid_pipeline(
        {"steps": [None]},
        error="Expected `None` to be of type `str | dict[str, typing.Any]",
        path=".steps[0]",
        id="none",
    )
    load_invalid_pipeline(
        {"steps": [{"type": "unknown"}]},
        error="Expected `{'type': 'unknown'}` to be a valid Buildkite pipeline step",
        path=".steps[0]",
        id="type-unknown",
    )
