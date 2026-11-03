# LANGS Allowlist Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a case-sensitive `LANGS` allowlist so a user can render only chosen languages, in WakaTime time order.

**Architecture:** One selection pipeline, `_select_languages()`, owns the allowlist, ignore list, count, and stop-at-other rules. `prep_content()` only formats the rows it returns. Percentages stay exactly as the API reports them.

**Tech Stack:** Python 3.12, `unittest`, GitHub Actions Docker action, PyGithub, requests, faker.

**Spec:** `docs/superpowers/specs/2026-11-03-langs-allowlist-design.md`

## Global Constraints

- Python `>=3.12`; no new runtime dependencies.
- `LANGS` is comma-separated, case-sensitive, exact match against the API `name`.
- Percentages are never renormalized.
- Empty `LANGS` must reproduce current output exactly.
- `LANG_COUNT` applies after `LANGS` and `IGNORED_LANGUAGES`; `-1` means all; `0` means none.
- `IGNORED_LANGUAGES` wins when a name appears in both filters.
- Selected order is WakaTime order, not the order typed in `LANGS`.

## Review Focus

- `LANGS` set but no name matches: section keeps title/total and renders no language rows; it must not fall back to other languages.
- Case mismatch (`javascript` vs `JavaScript`): omitted with a warning, never silently matched.
- `LANGS` plus `IGNORED_LANGUAGES` overlap: the ignored language never renders.
- `LANG_COUNT` after filtering: ignored or unselected languages must not consume slots.
- `STOP_AT_OTHER` with `LANG_COUNT=-1`: `Other` is included then iteration stops.

---

### Task 1: Dev environment and `_parse_langs`

**Files:**
- Modify: `main.py` (add helper below `_extract_ignored_languages`)
- Test: `tests/test_main.py`

**Interfaces:**
- Produces: `_parse_langs(raw: str) -> list[str]` — splits on commas, trims each entry, drops empty entries and duplicates, preserves first-seen order.

- [ ] **Step 1: Create the local test environment**

Run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install faker pygithub requests
```

Expected: install completes; `.venv` is ignored by git.

- [ ] **Step 2: Write the failing test**

Add to `tests/test_main.py` inside `TestMain`:

```python
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
        self.assertEqual(prime._parse_langs("   "), [])
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `.venv/bin/python -m unittest tests.test_main.TestMain.test_parse_langs -v`

Expected: FAIL with `AttributeError: module 'main' has no attribute '_parse_langs'`.

- [ ] **Step 4: Implement `_parse_langs`**

In `main.py`, beside `_extract_ignored_languages`:

```python
def _parse_langs(raw: str, /) -> list[str]:
    """Parse a comma-separated language allowlist."""
    parsed: list[str] = []
    for entry in raw.split(","):
        name = entry.strip()
        if name and name not in parsed:
            parsed.append(name)
    return parsed
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `.venv/bin/python -m unittest tests.test_main.TestMain.test_parse_langs -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: parse comma-separated LANGS allowlist"
```

---

### Task 2: `_select_languages` pipeline

**Files:**
- Modify: `main.py` (add helper beside `prep_content`)
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: `_parse_langs()`, `_extract_ignored_languages()`, globals `wk_i.langs`, `wk_i.ignored_languages`, `wk_i.language_count`, `wk_i.stop_at_other`.
- Produces: `_select_languages(lang_info: list[dict[str, Any]]) -> list[dict[str, Any]]` — returns rows to render, already allowlisted, ignored, counted, and stopped at `Other`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_main.py` inside `TestMain`:

```python
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
        self.assertEqual(
            [row["name"] for row in prime._select_languages(self._lang_info())],
            ["Python", "JavaScript", "Go", "Other"],
        )

    def test_select_languages_count_zero_returns_nothing(self) -> None:
        """LANG_COUNT=0 disables the language list."""
        self._set_wk(language_count=0)
        self.assertEqual(prime._select_languages(self._lang_info()), [])
```

Add `from unittest.mock import patch` to the test imports.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m unittest tests.test_main.TestMain.test_select_languages_allowlist_keeps_api_order -v`

Expected: FAIL with `AttributeError: module 'main' has no attribute '_select_languages'`.

- [ ] **Step 3: Add the `LANGS` input to `WakaInput`**

In `main.py`, inside `WakaInput`, next to `ignored_languages`:

```python
    langs: str = os.getenv("INPUT_LANGS", "")
```

- [ ] **Step 4: Implement `_select_languages`**

In `main.py`, above `prep_content`:

```python
def _select_languages(lang_info: list[dict[str, Any]], /) -> list[dict[str, Any]]:
    """Apply allowlist, ignore list, count, and stop-at-other rules."""
    requested = _parse_langs(wk_i.langs)
    if requested:
        available = {str(lang["name"]) for lang in lang_info}
        for name in requested:
            if name not in available:
                logger.warning(f"LANGS entry '{name}' not found in WakaTime stats")
        wanted = set(requested)
        lang_info = [lang for lang in lang_info if str(lang["name"]) in wanted]

    ignored = set(_extract_ignored_languages())
    logger.debug(f"Ignoring {', '.join(ignored)}")
    lang_info = [lang for lang in lang_info if str(lang["name"]) not in ignored]

    count = int(wk_i.language_count)
    if count == 0:
        logger.debug(
            "Set INPUT_LANG_COUNT to -1 to retrieve all language"
            + " or specify a positive number (ie. above 0)"
        )
        return []

    selected: list[dict[str, Any]] = []
    for lang in lang_info:
        selected.append(lang)
        if wk_i.stop_at_other and str(lang["name"]) == "Other":
            break
        if count > 0 and len(selected) >= count:
            break
    return selected
```

- [ ] **Step 5: Run the selection tests to verify they pass**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_main.TestMain.test_select_languages_allowlist_keeps_api_order \
  tests.test_main.TestMain.test_select_languages_is_case_sensitive \
  tests.test_main.TestMain.test_select_languages_warns_for_unknown_name \
  tests.test_main.TestMain.test_select_languages_ignore_wins \
  tests.test_main.TestMain.test_select_languages_count_applies_after_filters \
  tests.test_main.TestMain.test_select_languages_count_minus_one_and_stop_at_other \
  tests.test_main.TestMain.test_select_languages_count_zero_returns_nothing -v
```

Expected: 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: add language selection pipeline"
```

---

### Task 3: Render selected languages in `prep_content`

**Files:**
- Modify: `main.py` (`prep_content`)
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: `_select_languages(lang_info) -> list[dict[str, Any]]`.
- Produces: unchanged `prep_content(stats: dict[str, Any], /) -> str`; only selected rows appear, and padding is computed from those rows.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_main.py` inside `TestMain`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m unittest tests.test_main.TestMain.test_prep_content_renders_only_allowlisted_languages -v`

Expected: FAIL because `Python, JavaScript, Go` all render.

- [ ] **Step 3: Replace the selection logic in `prep_content`**

In `main.py`, after the empty-`languages` guard, replace the `pad_len`, `language_count`/`stop_at_other`, ignore, and loop setup with:

```python
    selected = _select_languages(lang_info)
    if not selected:
        return contents.rstrip("\n")

    pad_len = len(max((str(lang["name"]) for lang in selected), key=len))
    for lang in selected:
        lang_name = str(lang["name"])
        lang_time = str(lang["text"]) if wk_i.show_time else ""
        lang_ratio = float(lang["percent"])
        lang_bar = make_graph(wk_i.block_style, lang_ratio, wk_i.graph_length, lang_name)
        prefix_length = wk_i.prefix_length
        contents += (
            f"{lang_name.ljust(pad_len)}   "
            + f"{lang_time: <{prefix_length}}{lang_bar}   "
            + f"{lang_ratio:.2f}".zfill(5)
            + " %\n"
        )
```

Delete the now-unused `language_count`, `stop_at_other`, `ignored_languages`, `idx`, and break/continue lines from `prep_content`. The `LANG_COUNT=0` hint now lives in `_select_languages`.

- [ ] **Step 4: Run the full suite**

Run: `.venv/bin/python -m unittest discover -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: render only allowlisted languages"
```

---

### Task 4: Action input and documentation

**Files:**
- Modify: `action.yml`, `dockerfile`, `containerfile`, `.env.template`, `README.md`, `CONTRIBUTING.md`

**Interfaces:**
- Produces: `INPUT_LANGS` reachable from the Action and documented in every setup path.

- [ ] **Step 1: Add the action input**

In `action.yml`, under Content Tweaks after `IGNORED_LANGUAGES`:

```yaml
  LANGS:
    description: "Comma-separated, case-sensitive list of languages to show"
    default: ""
    required: false
```

- [ ] **Step 2: Pass the variable through both containers**

Add `INPUT_LANGS \` after `INPUT_IGNORED_LANGUAGES \` in the `ENV` list of both `dockerfile` and `containerfile`.

- [ ] **Step 3: Update the env template and contributing sample**

Add `INPUT_LANGS=` after `INPUT_IGNORED_LANGUAGES=` in `.env.template` and in the sample block in `CONTRIBUTING.md`.

- [ ] **Step 4: Document the flag**

In `README.md`, add this row to the Content Tweaks table after `IGNORED_LANGUAGES`:

```markdown
| `LANGS`             | <code> </code>, `JavaScript, Python, Go`                                 | Show only the comma-separated, case-sensitive languages listed                  |
```

Add `LANGS: JavaScript, Python, Go # optional` to the same position in the example workflow's content block.

- [ ] **Step 5: Verify the wiring**

Run:

```bash
grep -n "LANGS" action.yml dockerfile containerfile .env.template README.md CONTRIBUTING.md
```

Expected: at least one match in every file.

- [ ] **Step 6: Commit**

```bash
git add action.yml dockerfile containerfile .env.template README.md CONTRIBUTING.md
git commit -m "docs: document LANGS allowlist input"
```