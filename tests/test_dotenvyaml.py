"""Comprehensive tests for dotenvyaml."""

import os
import sys
from pathlib import Path

import pytest

from dotenvyaml import (
    DotEnvYamlError,
    FileNotFoundError,
    ParseError,
    find_env_file,
    load,
    load_dotenvyaml,
    load_env,
)
from dotenvyaml._rust import parse_yaml, parse_yaml_raw


# ── Rust parser: parse_yaml (flatten) ────────────────────────────────────────


class TestParseYaml:
    """Tests for the Rust parse_yaml function."""

    def test_simple_key_value(self):
        result = parse_yaml("KEY: value\nNUM: 42")
        assert result["KEY"] == "value"
        assert result["NUM"] == 42

    def test_nested_keys_flattened(self):
        yaml = "database:\n  host: localhost\n  port: 5432"
        result = parse_yaml(yaml)
        assert result["DATABASE_HOST"] == "localhost"
        assert result["DATABASE_PORT"] == 5432

    def test_deeply_nested(self):
        yaml = "a:\n  b:\n    c:\n      d: deep"
        result = parse_yaml(yaml)
        assert result["A_B_C_D"] == "deep"

    def test_uppercase_default(self):
        result = parse_yaml("my_key: val")
        assert "MY_KEY" in result

    def test_uppercase_disabled(self):
        result = parse_yaml("my_key: val", "_", False)
        assert "my_key" in result
        assert "MY_KEY" not in result

    def test_custom_separator(self):
        yaml = "db:\n  host: localhost"
        result = parse_yaml(yaml, ".", True)
        assert result["DB.HOST"] == "localhost"

    def test_list_to_comma_separated(self):
        yaml = "HOSTS:\n  - a.com\n  - b.com\n  - c.com"
        result = parse_yaml(yaml)
        assert result["HOSTS"] == "a.com,b.com,c.com"

    def test_boolean_values(self):
        result = parse_yaml("DEBUG: true\nVERBOSE: false")
        assert result["DEBUG"] is True
        assert result["VERBOSE"] is False

    def test_integer_values(self):
        result = parse_yaml("PORT: 8080")
        assert result["PORT"] == 8080
        assert isinstance(result["PORT"], int)

    def test_float_values(self):
        result = parse_yaml("RATE: 3.14")
        assert result["RATE"] == pytest.approx(3.14)

    def test_string_values(self):
        result = parse_yaml('NAME: "hello world"')
        assert result["NAME"] == "hello world"

    def test_null_values(self):
        result = parse_yaml("KEY: null")
        assert result["KEY"] is None

    def test_empty_yaml(self):
        result = parse_yaml("")
        assert result == {}

    def test_empty_document(self):
        result = parse_yaml("---")
        assert result == {}

    def test_invalid_yaml_raises(self):
        with pytest.raises(ValueError, match="YAML parse error"):
            parse_yaml("{{bad yaml")

    def test_non_mapping_raises(self):
        with pytest.raises(ValueError, match="Expected YAML mapping"):
            parse_yaml("- item1\n- item2")

    def test_mixed_nested_and_flat(self):
        yaml = "TOP: val\ngroup:\n  sub: nested"
        result = parse_yaml(yaml)
        assert result["TOP"] == "val"
        assert result["GROUP_SUB"] == "nested"


# ── Rust parser: parse_yaml_raw ──────────────────────────────────────────────


class TestParseYamlRaw:
    """Tests for the Rust parse_yaml_raw function."""

    def test_simple_dict(self):
        result = parse_yaml_raw("key: value")
        assert result == {"key": "value"}

    def test_nested_dict(self):
        yaml = "db:\n  host: localhost\n  port: 5432"
        result = parse_yaml_raw(yaml)
        assert result == {"db": {"host": "localhost", "port": 5432}}

    def test_list_values(self):
        yaml = "items:\n  - a\n  - b\n  - c"
        result = parse_yaml_raw(yaml)
        assert result == {"items": ["a", "b", "c"]}

    def test_preserves_types(self):
        yaml = "s: hello\ni: 42\nf: 3.14\nb: true\nn: null"
        result = parse_yaml_raw(yaml)
        assert result["s"] == "hello"
        assert result["i"] == 42
        assert result["f"] == pytest.approx(3.14)
        assert result["b"] is True
        assert result["n"] is None

    def test_empty(self):
        result = parse_yaml_raw("")
        assert result is None

    def test_invalid_yaml_raises(self):
        with pytest.raises(ValueError, match="YAML parse error"):
            parse_yaml_raw("{{bad")


# ── File discovery ───────────────────────────────────────────────────────────


class TestFindEnvFile:
    """Tests for find_env_file."""

    def test_finds_env_yaml(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("KEY: val")
        result = find_env_file(search_path=tmp_path)
        assert result == tmp_path / ".env.yaml"

    def test_finds_env_yml(self, tmp_path):
        (tmp_path / ".env.yml").write_text("KEY: val")
        result = find_env_file(search_path=tmp_path)
        assert result == tmp_path / ".env.yml"

    def test_prefers_yaml_over_yml(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("KEY: yaml")
        (tmp_path / ".env.yml").write_text("KEY: yml")
        result = find_env_file(search_path=tmp_path)
        assert result == tmp_path / ".env.yaml"

    def test_custom_file_names(self, tmp_path):
        (tmp_path / "config.yaml").write_text("KEY: val")
        result = find_env_file(file_names=["config.yaml"], search_path=tmp_path)
        assert result == tmp_path / "config.yaml"

    def test_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="No environment file found"):
            find_env_file(search_path=tmp_path)

    def test_auto_cwd(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("KEY: val")
        original = Path.cwd()
        os.chdir(tmp_path)
        try:
            result = find_env_file()
            assert result == tmp_path / ".env.yaml"
        finally:
            os.chdir(original)


# ── load() ───────────────────────────────────────────────────────────────────


class TestLoad:
    """Tests for the load function."""

    def test_returns_dict(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("KEY: value")
        config = load(file_path=tmp_path / ".env.yaml")
        assert config == {"KEY": "value"}

    def test_does_not_modify_environ(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("LOAD_TEST_VAR: secret")
        before = os.environ.copy()
        load(file_path=tmp_path / ".env.yaml")
        assert os.environ == before

    def test_flatten_nested(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("db:\n  host: localhost\n  port: 5432")
        config = load(file_path=tmp_path / ".env.yaml")
        assert config == {"DB_HOST": "localhost", "DB_PORT": 5432}

    def test_flatten_disabled(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("db:\n  host: localhost")
        config = load(file_path=tmp_path / ".env.yaml", flatten=False)
        assert config == {"db": {"host": "localhost"}}

    def test_auto_discovery(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("AUTO: found")
        original = Path.cwd()
        os.chdir(tmp_path)
        try:
            config = load()
            assert config == {"AUTO": "found"}
        finally:
            os.chdir(original)

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="File not found"):
            load(file_path=tmp_path / "nope.yaml")

    def test_invalid_yaml(self, tmp_path):
        (tmp_path / "bad.yaml").write_text("{{invalid")
        with pytest.raises(ParseError, match="YAML parse error"):
            load(file_path=tmp_path / "bad.yaml")

    @pytest.mark.skipif(sys.platform == "win32", reason="chmod doesn't work on Windows")
    def test_unreadable_file(self, tmp_path):
        f = tmp_path / "noperm.yaml"
        f.write_text("KEY: val")
        f.chmod(0o000)
        try:
            with pytest.raises(ParseError, match="Failed to read"):
                load(file_path=f)
        finally:
            f.chmod(0o644)

    def test_type_preservation(self, tmp_path):
        yaml_content = 'S: "hello"\nI: 42\nF: 3.14\nB: true'
        (tmp_path / ".env.yaml").write_text(yaml_content)
        config = load(file_path=tmp_path / ".env.yaml")
        assert config["S"] == "hello"
        assert config["I"] == 42
        assert config["F"] == pytest.approx(3.14)
        assert config["B"] is True

    def test_list_values(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("HOSTS:\n  - a\n  - b\n  - c")
        config = load(file_path=tmp_path / ".env.yaml")
        assert config["HOSTS"] == "a,b,c"

    def test_empty_file(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("")
        config = load(file_path=tmp_path / ".env.yaml")
        assert config == {}

    def test_comments_ignored(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("# comment\nKEY: val\n# another")
        config = load(file_path=tmp_path / ".env.yaml")
        assert config == {"KEY": "val"}


# ── load() with interpolation ────────────────────────────────────────────────


class TestLoadInterpolation:
    """Tests for variable expansion."""

    def test_simple_interpolation(self, tmp_path):
        yaml = "DOMAIN: example.com\nURL: https://${DOMAIN}/api"
        (tmp_path / ".env.yaml").write_text(yaml)
        config = load(file_path=tmp_path / ".env.yaml", interpolate=True)
        assert config["URL"] == "https://example.com/api"

    def test_default_value(self, tmp_path):
        yaml = 'MISSING: ${UNDEFINED_VAR:-fallback}'
        (tmp_path / ".env.yaml").write_text(yaml)
        config = load(file_path=tmp_path / ".env.yaml", interpolate=True)
        assert config["MISSING"] == "fallback"

    def test_from_os_environ(self, tmp_path):
        os.environ["DOTENVYAML_TEST_EXT"] = "from_env"
        try:
            yaml = "VAL: ${DOTENVYAML_TEST_EXT}"
            (tmp_path / ".env.yaml").write_text(yaml)
            config = load(file_path=tmp_path / ".env.yaml", interpolate=True)
            assert config["VAL"] == "from_env"
        finally:
            del os.environ["DOTENVYAML_TEST_EXT"]

    def test_no_interpolation_by_default(self, tmp_path):
        yaml = "URL: ${DOMAIN}/api"
        (tmp_path / ".env.yaml").write_text(yaml)
        config = load(file_path=tmp_path / ".env.yaml")
        assert config["URL"] == "${DOMAIN}/api"

    def test_circular_reference_safe(self, tmp_path):
        yaml = "A: ${B}\nB: ${A}"
        (tmp_path / ".env.yaml").write_text(yaml)
        config = load(file_path=tmp_path / ".env.yaml", interpolate=True)
        # Should not infinite-loop; circular refs left as-is
        assert isinstance(config["A"], str)
        assert isinstance(config["B"], str)

    def test_non_string_values_untouched(self, tmp_path):
        yaml = "NUM: 42\nREF: ${NUM}"
        (tmp_path / ".env.yaml").write_text(yaml)
        config = load(file_path=tmp_path / ".env.yaml", interpolate=True)
        assert config["NUM"] == 42
        assert config["REF"] == "42"


# ── load_env() ───────────────────────────────────────────────────────────────


class TestLoadEnv:
    """Tests for load_env (sets os.environ)."""

    def test_sets_environ(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("LOADENV_KEY: hello")
        os.environ.pop("LOADENV_KEY", None)
        load_env(file_path=tmp_path / ".env.yaml")
        assert os.environ["LOADENV_KEY"] == "hello"
        del os.environ["LOADENV_KEY"]

    def test_no_override_by_default(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("LOADENV_KEY: new")
        os.environ["LOADENV_KEY"] = "old"
        load_env(file_path=tmp_path / ".env.yaml")
        assert os.environ["LOADENV_KEY"] == "old"
        del os.environ["LOADENV_KEY"]

    def test_override(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("LOADENV_KEY: new")
        os.environ["LOADENV_KEY"] = "old"
        load_env(file_path=tmp_path / ".env.yaml", override=True)
        assert os.environ["LOADENV_KEY"] == "new"
        del os.environ["LOADENV_KEY"]

    def test_converts_to_string(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("PORT: 8080\nDEBUG: true")
        os.environ.pop("PORT", None)
        os.environ.pop("DEBUG", None)
        load_env(file_path=tmp_path / ".env.yaml")
        assert os.environ["PORT"] == "8080"
        assert os.environ["DEBUG"] == "True"
        del os.environ["PORT"]
        del os.environ["DEBUG"]

    def test_returns_dict(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("RET: val")
        os.environ.pop("RET", None)
        result = load_env(file_path=tmp_path / ".env.yaml")
        assert result == {"RET": "val"}
        del os.environ["RET"]


# ── Backwards compatibility ──────────────────────────────────────────────────


class TestBackwardsCompat:
    """Test that load_dotenvyaml still works."""

    def test_load_dotenvyaml_is_load_env(self):
        assert load_dotenvyaml is load_env

    def test_load_dotenvyaml_works(self, tmp_path):
        (tmp_path / ".env.yaml").write_text("COMPAT: yes")
        os.environ.pop("COMPAT", None)
        result = load_dotenvyaml(file_path=tmp_path / ".env.yaml")
        assert result == {"COMPAT": "yes"}
        assert os.environ["COMPAT"] == "yes"
        del os.environ["COMPAT"]


# ── Exception hierarchy ──────────────────────────────────────────────────────


class TestExceptions:
    """Test exception hierarchy."""

    def test_file_not_found_is_dotenvyaml_error(self):
        assert issubclass(FileNotFoundError, DotEnvYamlError)

    def test_parse_error_is_dotenvyaml_error(self):
        assert issubclass(ParseError, DotEnvYamlError)

    def test_catch_base_exception(self, tmp_path):
        with pytest.raises(DotEnvYamlError):
            load(file_path=tmp_path / "nope.yaml")
