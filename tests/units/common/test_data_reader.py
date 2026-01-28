"""Unit tests for common.runner.data_reader CSVDataReader (escape handling for XPath in CSV)."""
import os
import tempfile

import pytest

from optics_framework.common.runner.data_reader import CSVDataReader
from optics_framework.common.utils import escape_csv_value, unescape_csv_value


class TestCSVDataReaderUnescape:
    """Tests that CSVDataReader unescapes \\n, \\t, \\r, \\\\ in element IDs and module params."""

    def setup_method(self):
        self.reader = CSVDataReader()

    def test_read_elements_unescapes_newline_in_element_id(self):
        """read_elements turns \\n in Element_ID* columns into a real newline."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write(
                "Element_Name,Element_ID_xpath,Element_ID\n"
                '"icici","//android.widget.ImageView[@content-desc=""I\\nIcici Bank Limited""]","img.png"\n'
            )
            path = f.name
        try:
            result = self.reader.read_elements(path)
            assert "icici" in result
            # element_ids are lists; first value is from Element_ID_xpath (or order depends on dict)
            ids = result["icici"]
            assert isinstance(ids, list)
            xpath_val = next(v for v in ids if "ImageView" in v)
            assert "\n" in xpath_val
            assert xpath_val == '//android.widget.ImageView[@content-desc="I\nIcici Bank Limited"]'
        finally:
            os.unlink(path)

    def test_read_modules_unescapes_newline_in_param(self):
        """read_modules turns \\n in param_* values into a real newline."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write(
                "module_name,module_step,param_1,param_2\n"
                'm1,Get Text,"//*[@desc=""A\\nB""]",\n'
            )
            path = f.name
        try:
            result = self.reader.read_modules(path)
            assert "m1" in result
            steps = result["m1"]
            assert len(steps) == 1
            kw, params = steps[0]
            assert kw == "Get Text"
            assert len(params) >= 1
            assert "\n" in params[0]
            assert params[0] == '//*[@desc="A\nB"]'
        finally:
            os.unlink(path)


class TestEscapeCsvValue:
    """Direct unit tests for escape_csv_value (used by get_interactive_elements in verifier)."""

    def test_escape_csv_value_newline(self):
        """escape_csv_value turns newline into \\n."""
        assert escape_csv_value("a\nb") == "a\\nb"

    def test_escape_csv_value_tab(self):
        """escape_csv_value turns tab into \\t."""
        assert escape_csv_value("a\tb") == "a\\tb"

    def test_escape_csv_value_carriage_return(self):
        """escape_csv_value turns carriage return into \\r."""
        assert escape_csv_value("a\rb") == "a\\rb"

    def test_escape_csv_value_backslash(self):
        """escape_csv_value turns backslash into \\\\."""
        assert escape_csv_value("a\\b") == "a\\\\b"

    def test_escape_csv_value_backslash_then_n(self):
        """escape_csv_value escapes backslash first so backslash+n becomes \\\\n (not newline)."""
        assert escape_csv_value("a\\nc") == "a\\\\nc"

    def test_escape_csv_value_empty_string(self):
        """escape_csv_value returns empty string for empty input."""
        assert escape_csv_value("") == ""

    def test_escape_csv_value_raises_on_non_string(self):
        """escape_csv_value requires str and raises TypeError otherwise."""
        with pytest.raises(TypeError, match="expects str, got"):
            escape_csv_value(None)
        with pytest.raises(TypeError, match="expects str, got"):
            escape_csv_value(123)


class TestUnescapeCsvValueTypeContract:
    """unescape_csv_value(s: str) -> str raises TypeError for non-str."""

    def test_unescape_csv_value_raises_on_non_string(self):
        """unescape_csv_value requires str and raises TypeError otherwise."""
        with pytest.raises(TypeError, match="expects str, got"):
            unescape_csv_value(None)
        with pytest.raises(TypeError, match="expects str, got"):
            unescape_csv_value(123)


class TestEscapeUnescapeInverses:
    """escape_csv_value and unescape_csv_value must be true inverses for verifier/output round-trip."""

    def test_unescape_then_escape_round_trip(self):
        """For CSV-escaped strings, escape(unescape(s)) == s."""
        cases = [
            "//*[@desc=\"A\\nB\"]",
            "a\\\\nc",
            "I\\nIcici Bank Limited",
            "a\\tb\\rc",
            "plain",
        ]
        for escaped in cases:
            assert escape_csv_value(unescape_csv_value(escaped)) == escaped, escaped

    def test_escape_then_unescape_round_trip(self):
        """For raw strings, unescape(escape(s)) == s."""
        cases = [
            "a\nb",
            "a\tb",
            "a\rb",
            "a\\nc",
            "//*[@desc=\"A\nB\"]",
            "",
        ]
        for raw in cases:
            assert unescape_csv_value(escape_csv_value(raw)) == raw, repr(raw)
