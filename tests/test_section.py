from typing import ItemsView, KeysView, ValuesView

from pytest import raises

import cabina
from cabina import computed
from cabina.errors import ConfigAttrError, ConfigError, ConfigKeyError


def test_section():
    class Section(cabina.Section):
        pass

    assert issubclass(Section, cabina.Section)
    assert not issubclass(Section, cabina.Config)


def test_section_init_not_allowed():
    class Section(cabina.Section):
        pass

    with raises(Exception) as exc_info:
        Section()

    assert exc_info.type is ConfigError
    assert str(exc_info.value) == f"Attempted to initialize section {Section!r}"


def test_section_get_attr():
    class Section(cabina.Section):
        API_HOST = "localhost"
        API_PORT = 8080

    assert Section.API_HOST == "localhost"
    assert Section.API_PORT == 8080


def test_section_get_nonexisting_attr():
    class Section(cabina.Section):
        API_HOST = "localhost"

    with raises(Exception) as exc_info:
        Section.API_PORT

    assert exc_info.type is ConfigAttrError
    assert str(exc_info.value) == f"'API_PORT' does not exist in {Section!r}"


def test_section_set_attr_not_allowed():
    class Section(cabina.Section):
        pass

    with raises(Exception) as exc_info:
        Section.API_HOST = "localhost"

    assert exc_info.type is ConfigError
    assert str(exc_info.value) == f"Attempted to add 'API_HOST' to {Section!r} at runtime"


def test_section_override_attr_not_allowed():
    class Section(cabina.Section):
        API_HOST = "localhost"

    with raises(Exception) as exc_info:
        Section.API_HOST = "127.0.0.1"

    assert exc_info.type is ConfigError
    assert str(exc_info.value) == f"Attempted to override 'API_HOST' in {Section!r}"


def test_section_del_attr_not_allowed():
    class Section(cabina.Section):
        API_HOST = "localhost"

    with raises(Exception) as exc_info:
        del Section.API_HOST

    assert exc_info.type is ConfigError
    assert str(exc_info.value) == f"Attempted to remove 'API_HOST' from {Section!r}"


def test_section_get_item():
    class Section(cabina.Section):
        API_HOST = "localhost"
        API_PORT = 8080

    assert Section["API_HOST"] == "localhost"
    assert Section["API_PORT"] == 8080


def test_section_get_nonexisting_item():
    class Section(cabina.Section):
        pass

    with raises(Exception) as exc_info:
        Section["API_HOST"]

    assert exc_info.type is ConfigKeyError
    assert str(exc_info.value) == f"'API_HOST' does not exist in {Section!r}"


def test_section_set_item_not_allowed():
    class Section(cabina.Section):
        pass

    with raises(Exception) as exc_info:
        Section["API_HOST"] = "localhost"

    assert exc_info.type is ConfigError
    assert str(exc_info.value) == f"Attempted to add 'API_HOST' to {Section!r} at runtime"


def test_section_del_item_not_allowed():
    class Section(cabina.Section):
        API_HOST = "localhost"

    with raises(Exception) as exc_info:
        del Section["API_HOST"]

    assert exc_info.type is ConfigError
    assert str(exc_info.value) == f"Attempted to remove 'API_HOST' from {Section!r}"


def test_section_len_without_options():
    class Section(cabina.Section):
        pass

    assert len(Section) == 0


def test_section_len_with_options():
    class Section(cabina.Section):
        API_HOST = "localhost"
        API_PORT = 8080

    assert len(Section) == 2


def test_section_iter_without_options():
    class Section(cabina.Section):
        pass

    options = [option for option in Section]
    assert options == []


def test_section_iter_with_options():
    class Section(cabina.Section):
        API_HOST = "localhost"
        API_PORT = 8080

    options = [option for option in Section]
    assert options == ["API_HOST", "API_PORT"]


def test_section_contains():
    class Section(cabina.Section):
        DEBUG = False

    assert "DEBUG" in Section
    assert "banana" not in Section


def test_section_keys():
    class Section(cabina.Section):
        API_HOST = "localhost"
        API_PORT = 8080

    assert isinstance(Section.keys(), KeysView)
    assert list(Section.keys()) == ["API_HOST", "API_PORT"]


def test_section_kwargs():
    class Section(cabina.Section):
        host = "localhost"
        port = 8080
        debug = False

    def connect(host, port, **kwargs):
        return host, port

    assert connect(**Section) == (Section.host, Section.port)


def test_section_values():
    class Section(cabina.Section):
        API_HOST = "localhost"
        API_PORT = 8080

    assert isinstance(Section.values(), ValuesView)
    assert list(Section.values()) == ["localhost", 8080]


def test_section_items():
    class Section(cabina.Section):
        API_HOST = "localhost"
        API_PORT = 8080

    assert isinstance(Section.items(), ItemsView)
    assert list(Section.items()) == [
        ("API_HOST", "localhost"),
        ("API_PORT", 8080)
    ]


def test_section_get():
    class Section(cabina.Section):
        API_HOST = "localhost"

    assert Section.get("API_HOST") == Section.API_HOST
    assert Section.get("banana", None) is None

    with raises(Exception) as exc_info:
        Section.get("banana")

    assert exc_info.type is ConfigKeyError
    assert str(exc_info.value) == f"'banana' does not exist in {Section!r}"


def test_section_eq():
    class Section1(cabina.Section):
        pass

    class Section2(cabina.Section):
        pass

    assert Section1 == Section1
    assert Section1 != Section2


def test_section_repr():
    class Main(cabina.Section):
        pass

    assert repr(Main) == "<Main>"


def test_section_with_subsections_repr():
    class Section(cabina.Section):
        class SubSection(cabina.Section):
            pass

    assert repr(Section.SubSection) == "<Section.SubSection>"
    assert repr(Section) == "<Section>"


def test_section_unique_keys():
    with raises(Exception) as exc_info:
        class Section(cabina.Section):
            DEBUG = True
            DEBUG = False

    assert exc_info.type is ConfigError
    assert str(exc_info.value) == "Attempted to reuse 'DEBUG' in 'Section'"


def test_section_reserved_keys():
    reserved_keys = [key for key in dir(cabina.Config.__class__) if not key.startswith("__")]

    for reserved_key in reserved_keys:
        with raises(Exception) as exc_info:
            type("Section", (cabina.Section,), {reserved_key: None})

        assert exc_info.type is ConfigError
        assert str(exc_info.value) == f"Attempted to use reserved {reserved_key!r} in 'Section'"


def test_section_inheritance():
    class Section(cabina.Section):
        DEBUG = False

    class AnotherSection(Section):
        pass

    assert Section.DEBUG == AnotherSection.DEBUG


def test_section_inheritance_overriding():
    class Section(cabina.Section):
        DEBUG = False

    class AnotherSection(Section):
        DEBUG = True
        TZ = "UTC"

    assert Section.DEBUG != AnotherSection.DEBUG
    assert AnotherSection.TZ == "UTC"

    with raises(Exception) as exc_info:
        Section.TZ

    assert exc_info.type is ConfigAttrError
    assert str(exc_info.value) == f"'TZ' does not exist in {Section!r}"


def test_section_multiple_inheritance():
    class Section(cabina.Section):
        DEBUG = False

    class AnotherSection(Section, cabina.Section):
        pass

    assert Section.DEBUG == AnotherSection.DEBUG


def test_section_invalid_multiple_inheritance():
    with raises(Exception) as exc_info:
        class Section(cabina.Section, dict):
            pass

    assert exc_info.type is ConfigError
    assert str(exc_info.value) == f"Attempted to inherit {dict}"


def test_section_computed():
    class Section(cabina.Section):
        HOST = "localhost"
        PORT = 8080

        @computed
        def URL(cls):
            return f"http://{cls.HOST}:{cls.PORT}"

    assert Section.URL == "http://localhost:8080"
