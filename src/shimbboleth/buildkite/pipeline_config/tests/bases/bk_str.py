import pytest

from shimbboleth.buildkite.pipeline_config.tests.bases.schema import SchemaTestBase
from shimbboleth.buildkite.pipeline_config.tests.bases._base import FieldTestBase
from pytest import param

parameterize_bk_strs = pytest.mark.parametrize(
    "value, expected",
    [
        pytest.param(None, None, id="none"),
        pytest.param("", "", id="empty_string"),
        pytest.param("string", "string", id="string"),
    ],
)

class BKStrTestBase(FieldTestBase[str], SchemaTestBase):
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.VALID_STEPS += [
            param({cls.ATTR_NAME: None, "type": cls.TYPENAME}, id="none"),
            param({cls.ATTR_NAME: "", "type": cls.TYPENAME}, id="empty_string"),
            param({cls.ATTR_NAME: "string", "type": cls.TYPENAME}, id="string"),
            # NB: Buildkite treats Falsey values as `None`/`""`/not-given
            param({cls.ATTR_NAME: [], "type": cls.TYPENAME}, id="empty_list"),
            param({cls.ATTR_NAME: {}, "type": cls.TYPENAME}, id="empty_dict"),
            # NB: Buildkite stringifies ints
            param({cls.ATTR_NAME: 1, "type": cls.TYPENAME}, id="int"),
        ]
        cls.INVALID_STEPS += [
            param({cls.ATTR_NAME: [1], "type": cls.TYPENAME}, id="int_list"),
            param({cls.ATTR_NAME: {"a-key": 1}, "type": cls.TYPENAME}, id="dict"),
            # NB: Buildkite doesn't stringify floats
            param({cls.ATTR_NAME: 1.234, "type": cls.TYPENAME}, id="float"),
        ]

    def test__model_dump(self):
        assert self.ATTR_NAME not in self.model_load().model_dump()
        assert (
            self.ATTR_NAME
            not in self.model_load({self.ATTR_NAME: self.DEFAULT}).model_dump()
        )
        a_string = "string"
        assert (
            self.model_load({self.ATTR_NAME: a_string}).model_dump()[self.ATTR_NAME]
            == a_string
        )

    @parameterize_bk_strs
    def test__python_ctor(self, value, expected):
        instance = self.ctor(**{self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected

    @parameterize_bk_strs
    def test__setter(self, value, expected):
        wait_step = self.ctor()
        setattr(wait_step, self.ATTR_NAME, value)
        assert getattr(wait_step, self.ATTR_NAME) == expected

    @parameterize_bk_strs
    def test__json_load(self, value, expected):
        instance = self.model_load({self.ATTR_NAME: value})
        assert getattr(instance, self.ATTR_NAME) == expected


