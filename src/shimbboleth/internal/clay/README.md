# `shimbboleth.internal.clay`

`clay` is an internal modeling library for the `shimbboleth` project,
focused on type-safe data modeling with JSON support.

At its core, `clay` provides a `Model` base class for defining data models
which itself builds on top of vanilla `dataclasses`.

## Features

- Heirarchical modeling, combined with `dataclasses.dataclass` foundation
- JSON serialization and deserialization
- Uses type hints for validation (where validation is performed on assignment)
- Custom pluggable JSON loaders/dumpers/schema

## Usage

```python
from typing import Annotated
from shimbboleth.internal.clay import Model, field

class MyModel(Model):
    # Fields are validated on JSON load
    name: str = "default"
    # Support for interesting validators
    count: Annotated[int, NonEmpty] = field()

# Custom JSON loader
@Model._json_loader_(field="count")
def load_count(value: str | int) -> int:
    return int(value)
```

## Philosohpies

- This is an internal library meant for support of the wider `shimbboleth` project. It doesn't need to be perfect, just good enough.
- Data is assumed to be type-correct in Python APIs (e.g. only type-validate when taking in JSON)
- Data restrictions (like "must not be empty") are a property of a field's **type** (e.g. the field should have type `Annotated[..., NonEmpty]`)
  and not a property of the field itself.
- Field types should be "reduced" to their lowest-common-denominator. (E.g. `str | list[str]` should be `list[str]` when applicable)
  (and JSON loaders can be used if the input data allows `str | list[str]`)
