# ruff: noqa: F401
"""
Re-exports of the model-related definitions
"""

from shimbboleth.internal.clay.model._field_alias import FieldAlias
from shimbboleth.internal.clay.model._field import field

# NB: Don't re-export `ModelMeta`. That should be an implementation detail.
from shimbboleth.internal.clay.model._model import Model
