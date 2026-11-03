"""Unit Tests."""

# standard
from dataclasses import dataclass  # , field
from importlib import import_module
from itertools import product
import os
import sys
import unittest
from unittest.mock import patch

# from pathlib import Path
# from inspect import cleandoc
# from typing import Any
# from json import load

try:
    prime = import_module("main")
    # works when running as
    # python -m unittest discover
except ImportError as err:
    print(err)
    # sys.exit(1)


@dataclass
class TestData:
    """Test Data."""

    # for future tests
    # waka_json: dict[str, dict[str, Any]] = field(
    #     default_factory=lambda: {}
    # )
    bar_percent: tuple[int | float, ...] | None = None
    graph_blocks: tuple[str, ...] | None = None
    waka_graphs: tuple[list[str], ...] | None = None
    dummy_readme: str = ""

    def populate(self) -> None:
        """Populate Test Data."""
        # for future tests
        # with open(
        #     file=Path(__file__).parent / "sample_data.json",
        #     encoding="utf-8",
        #     mode="rt",
        # ) as wkf:
        #     self.waka_json = load(wkf)

        self.bar_percent = (0, 100, 49.999, 50, 25, 75, 3.14, 9.901, 87.334, 87.333, 4.666, 4.667)

        self.graph_blocks = ("░▒▓█", "⚪⚫", "⓪①②③④⑤⑥⑦⑧⑨⑩")

        self.waka_graphs = (
            [
                "░░░░░░░░░░░░░░░░░░░░░░░░░",
                "█████████████████████████",
                "████████████▒░░░░░░░░░░░░",
                "████████████▓░░░░░░░░░░░░",
                "██████▒░░░░░░░░░░░░░░░░░░",
                "██████████████████▓░░░░░░",
                "▓░░░░░░░░░░░░░░░░░░░░░░░░",
                "██▒░░░░░░░░░░░░░░░░░░░░░░",
                "██████████████████████░░░",
                "█████████████████████▓░░░",
                "█░░░░░░░░░░░░░░░░░░░░░░░░",
                "█▒░░░░░░░░░░░░░░░░░░░░░░░",
            ],
            [
                "⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪",
                "⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫",
                "⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪",
                "⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪",
                "⚫⚫⚫⚫⚫⚫⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪",
                "⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚪⚪⚪⚪⚪⚪",
                "⚫⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪",
                "⚫⚫⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪",
                "⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚪⚪⚪",
                "⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚫⚪⚪⚪",
                "⚫⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪",
                "⚫⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪",
            ],
            [
                "⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪",
                "⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩",
                "⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑤⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪",
                "⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑤⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪",
                "⑩⑩⑩⑩⑩⑩③⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪",
                "⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑧⓪⓪⓪⓪⓪⓪",
                "⑧⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪",
                "⑩⑩⑤⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪",
                "⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑧⓪⓪⓪",
                "⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑩⑧⓪⓪⓪",
                "⑩②⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪",
                "⑩②⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪⓪",
            ],
        )

        # self.dummy_readme = cleandoc("""
        # My Test Readme Start
        # <!--START_SECTION:waka-->
        # <!--END_SECTION:waka-->
        # My Test Readme End
        # """)


class TestMain(unittest.TestCase):
    """Testing Main Module."""

    def test_make_graph(self) -> None:
        """Test graph maker."""
        if not tds.graph_blocks or not tds.waka_graphs or not tds.bar_percent:
            raise AssertionError("Data population failed")

        for (idx, grb), (jdy, bpc) in product(
            enumerate(tds.graph_blocks), enumerate(tds.bar_percent)
        ):
            self.assertEqual(prime.make_graph(grb, bpc, 25), tds.waka_graphs[idx][jdy])

    def test_make_title(self) -> None:
        """Test title maker."""
        self.assertRegex(
            prime.make_title("2022-01-11T23:18:19Z", "2021-12-09T10:22:06Z"),
            r"From: \d{2} \w{3,9} \d{4} - To: \d{2} \w{3,9} \d{4}",
        )

    def test_parse_langs(self) -> None:
        """Test comma-separated language allowlist parsing."""
        self.assertEqual(
            prime._parse_langs("JavaScript, Python, Go"),
            ["JavaScript", "Python", "Go"],
        )
        self.assertEqual(prime._parse_langs(" Python ,,Go, "), ["Python", "Go"])
        self.assertEqual(prime._parse_langs("Go, Go, Python"), ["Go", "Python"])
        self.assertEqual(
            prime._parse_langs("Visual Basic .NET,Jupyter Notebook"),
            ["Visual Basic .NET", "Jupyter Notebook"],
        )
        self.assertEqual(prime._parse_langs(""), [])
        self.assertEqual(prime._parse_langs("Go, go"), ["Go", "go"])
        self.assertEqual(prime._parse_langs("   "), [])

    def _set_wk(self, **kwargs) -> None:
        """Replace the module config for a selection test."""
        self._old_wk_i = getattr(prime, "wk_i", None)
        prime.wk_i = prime.WakaInput(**kwargs)

    def tearDown(self) -> None:
        """Restore the module config after a selection test."""
        if hasattr(self, "_old_wk_i"):
            if self._old_wk_i is None:
                del prime.wk_i
            else:
                prime.wk_i = self._old_wk_i

    @staticmethod
    def _lang_info() -> list[dict]:
        """Synthetic WakaTime language rows."""
        return [
            {"name": "Python", "text": "10 hrs", "percent": 60.0},
            {"name": "JavaScript", "text": "4 hrs", "percent": 25.0},
            {"name": "Go", "text": "2 hrs", "percent": 10.0},
            {"name": "Other", "text": "1 hr", "percent": 5.0},
        ]

    def test_select_languages_allowlist_keeps_api_order(self) -> None:
        """Allowlist filters but keeps descending-time order."""
        self._set_wk(langs="Go, Python", language_count=5)
        self.assertEqual(
            [row["name"] for row in prime._select_languages(self._lang_info())],
            ["Python", "Go"],
        )

    def test_select_languages_is_case_sensitive(self) -> None:
        """Lowercase allowlist entries do not match API names."""
        self._set_wk(langs="python", language_count=5)
        self.assertEqual(prime._select_languages(self._lang_info()), [])

    def test_select_languages_warns_for_unknown_name(self) -> None:
        """Unknown allowlist entries are warned about and skipped."""
        self._set_wk(langs="Python, Rust", language_count=5)
        with patch.object(prime.logger, "warning") as warn:
            selected = prime._select_languages(self._lang_info())
        self.assertEqual([row["name"] for row in selected], ["Python"])
        warn.assert_any_call("LANGS entry 'Rust' not found in WakaTime stats")

    def test_select_languages_ignore_wins(self) -> None:
        """IGNORED_LANGUAGES overrides LANGS on overlap."""
        self._set_wk(langs="Python, Go", ignored_languages="Go", language_count=5)
        self.assertEqual(
            [row["name"] for row in prime._select_languages(self._lang_info())],
            ["Python"],
        )

    def test_select_languages_count_applies_after_filters(self) -> None:
        """Filtered-out rows do not consume LANG_COUNT slots."""
        self._set_wk(ignored_languages="Python", language_count=2)
        self.assertEqual(
            [row["name"] for row in prime._select_languages(self._lang_info())],
            ["JavaScript", "Go"],
        )

    def test_select_languages_count_minus_one_and_stop_at_other(self) -> None:
        """Unlimited count still honors STOP_AT_OTHER."""
        self._set_wk(language_count=-1, stop_at_other=True)
        lang_info = [
            {"name": "Python", "text": "10 hrs", "percent": 60.0},
            {"name": "Other", "text": "1 hr", "percent": 5.0},
            {"name": "JavaScript", "text": "4 hrs", "percent": 25.0},
            {"name": "Go", "text": "2 hrs", "percent": 10.0},
        ]
        self.assertEqual(
            [row["name"] for row in prime._select_languages(lang_info)],
            ["Python", "Other"],
        )

    def test_select_languages_count_zero_returns_nothing(self) -> None:
        """LANG_COUNT=0 disables the language list."""
        self._set_wk(language_count=0)
        self.assertEqual(prime._select_languages(self._lang_info()), [])

    def test_select_languages_empty_langs_keeps_current_output(self) -> None:
        """Empty LANGS selects the full API list unchanged."""
        self._set_wk(language_count=5, langs="")
        self.assertEqual(
            [row["name"] for row in prime._select_languages(self._lang_info())],
            ["Python", "JavaScript", "Go", "Other"],
        )

    def test_select_languages_count_minus_one_returns_all(self) -> None:
        """LANG_COUNT=-1 returns every row when STOP_AT_OTHER is off."""
        self._set_wk(language_count=-1)
        self.assertEqual(
            [row["name"] for row in prime._select_languages(self._lang_info())],
            ["Python", "JavaScript", "Go", "Other"],
        )

    @staticmethod
    def _stats() -> dict:
        """Synthetic WakaTime stats payload."""
        return {
            "languages": [
                {"name": "Python", "text": "2 hrs", "percent": 60.0},
                {"name": "JavaScript", "text": "1 hr", "percent": 30.0},
                {"name": "Go", "text": "20 mins", "percent": 10.0},
            ]
        }

    def test_prep_content_renders_only_allowlisted_languages(self) -> None:
        """Only LANGS rows render; percentages stay global."""
        self._set_wk(langs="Python, Go", language_count=10, show_time=True)
        content = prime.prep_content(self._stats())
        self.assertIn("Python", content)
        self.assertIn("Go", content)
        self.assertNotIn("JavaScript", content)
        self.assertIn("60.00 %", content)
        self.assertIn("10.00 %", content)

    def test_prep_content_pads_to_selected_names_only(self) -> None:
        """Padding ignores filtered-out long names."""
        self._set_wk(langs="Python, Go", language_count=10, show_time=True)
        lines = prime.prep_content(self._stats()).splitlines()
        self.assertTrue(lines[0].startswith("Python   "))
        self.assertTrue(lines[1].startswith("Go       "))

    def test_prep_content_no_match_returns_no_language_rows(self) -> None:
        """A non-matching allowlist renders no language rows."""
        self._set_wk(langs="Rust", language_count=10)
        self.assertEqual(prime.prep_content(self._stats()), "")

    def test_strtobool(self) -> None:
        """Test string to bool."""
        self.assertTrue(prime.strtobool("Yes"))
        self.assertFalse(prime.strtobool("nO"))
        self.assertTrue(prime.strtobool(True))
        self.assertRaises(AttributeError, prime.strtobool, None)
        self.assertRaises(ValueError, prime.strtobool, "yo!")
        self.assertRaises(AttributeError, prime.strtobool, 20.5)


tds = TestData()
tds.populate()

if __name__ == "__main__":
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        import main as prime

        # works when running as
        # python tests/test_main.py
    except ImportError as im_er:
        print(im_er)
        sys.exit(1)
    unittest.main()
