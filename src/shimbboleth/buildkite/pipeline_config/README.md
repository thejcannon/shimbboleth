# Buildkite Pipeline Config Types

This module provides rich Python types for working with [Buildkite pipeline configurations](https://buildkite.com/docs/pipelines/configure).

The primary goal is to enable reading existing pipeline YAML files into strongly-typed Python objects for analysis and transformation,
with the ability to write them back out as well.

## Key Features

- Full type coverage of the [Buildkite Pipeline Schema](https://github.com/buildkite/pipeline-schema)
- `dataclass`-based modeling (see `shimmboleth.internal.clay`)
- Support for all pipeline step types (Command, Wait, Block, Input, Trigger, Group)
- Field aliases to support common alternative names (e.g. `name`/`label`)
- Automatic canonicalization of certain field types (e.g. `str | list[str]` -> `list[str]`)

## Intent and Limitations

This module is primarily designed for:

- Reading and parsing existing pipeline configurations
- Programmatically analyzing pipeline structure
- Making targeted modifications to pipelines

It is not specifically designed for:

- Creating pipelines from scratch (though possible!)
- Perfectly round-trip preserving pipeline files
- Complete validation of all Buildkite pipeline rules
  - (Although I really try to come close!)

Additionally _we do not veriy data types at the Python boundary_. Meaning:

- data types are verified when loading from JSON
- but otherwise, we assume that data is type-correct in Python code

## Usage

```python
from shimbboleth.buildkite.pipeline_config import BuildkitePipeline
import yaml

# Read an existing pipeline
with open('pipeline.yml') as f:
    pipeline = BuildkitePipeline.model_load(yaml.safe_load(f))

# Access typed fields
for step in pipeline.steps:
    if isinstance(step, CommandStep):
        print(f"Command step: {step.label}")

# Make changes
pipeline.steps[1].label = "Updated label"
pipeline.steps[1].command = ["./my_script.sh", "--flag", "value"]

# And write it back out
with open('pipeline.yml', 'w') as f:
    yaml.dump(pipeline.model_dump(), f)
```

## JSON Schema

We also define a (completely generated) JSON Schema for the Buildkite Pipeline configuration format at `./schema.json`.

(At the time of writing is is more correct than the upstream JSON Schema).

## Testing

- Extensive testing is done on generated pipelines:
  - Loading/dumping to/from JSON and Python
  - Correctness with regards to the generated JSON Schema (both valid and invalid pipelines)
  - Correctness with regards to the upstream [JSON Schema](https://github.com/buildkite/pipeline-schema)
  - Correctness with regards to the upstream [Buildkite Pipeline API](https://buildkite.com/docs/apis/rest-api/pipelines#update-a-pipeline)
- As well as Python-specific tests for `shimbboleth` additions (e.g. field aliasing, JSON loaders, etc...)
