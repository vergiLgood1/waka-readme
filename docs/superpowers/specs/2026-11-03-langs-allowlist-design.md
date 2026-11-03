# LANGS allowlist — design

## Intent

Today `LANG_COUNT` shows the top N languages by tracked time. Users who want a
specific set of languages have to rely on `IGNORED_LANGUAGES`, which is
open-ended: it hides unwanted languages but cannot force a language into the
list, and it does not let the user curate the set.

Add a `LANGS` input that acts as an allowlist. When set, only the named
languages are rendered.

## Goals

- Render only languages named in `LANGS`, in WakaTime time order.
- Keep existing behavior when `LANGS` is unset.
- Make `LANG_COUNT`, `STOP_AT_OTHER`, `IGNORED_LANGUAGES`, and `LANGS` compose
  predictably.
- Keep percentages as WakaTime reports them: share of all tracked time in the
  selected `TIME_RANGE`.
- Cover the parsing and filtering with unit tests.

## Non-goals

- Custom display order driven by the order of names in `LANGS`.
- Renormalizing percentages to the selected subset (a separate opt-in flag may
  come later).
- Changing the output format, title, or total-time lines.
- Building a generic templating or stats engine.

## Decisions

| Topic | Decision |
| --- | --- |
| Syntax | Comma-separated string: `LANGS: JavaScript, Python, Go` |
| Matching | Case-sensitive, exact match against the API `name` field |
| Whitespace | Trim around each entry; empty entries dropped; duplicates dropped |
| Order | WakaTime order (descending time), not the order typed by the user |
| Precedence | `LANGS` first, then `IGNORED_LANGUAGES`; ignore wins on overlap |
| Count | `LANG_COUNT` applies after both filters |
| Unknown names | Log a warning, continue; no hard failure |
| No matches | Render title/total only, no language rows; never fall back to unselected languages |
| Unset/empty `LANGS` | Current behavior, no breaking change |
| Percentages | Unchanged, global to the time range |

Warnings are preferred over failure because a selected language may legitimately
have zero tracked time in a short range such as `last_7_days`.

## Approaches considered

**A. Inline filter inside the render loop.** Smallest diff, but the existing
loop indexes the raw API list. Ignored or unselected languages would still
consume `LANG_COUNT` slots, which is the bug tracked by PR #182.

**B. Filter the list, then render.** Parse the allowlist, filter the list,
apply ignore and count, then render. Fixes the counting bug and is easy to
review, but the filter stages stay spread between `prep_content` and a helper.

**C. One selection pipeline (chosen).** A `_select_languages()` helper owns
allowlist, ignore, count, and stop-at-other, and returns the exact rows to
render. `prep_content` only formats. Chosen for long-term structure: future
filters and the AI-metrics work in PR #180 can extend one function instead of
another conditional in the render loop.

## How it works

1. Add `INPUT_LANGS` to `WakaInput` (`langs: str = os.getenv("INPUT_LANGS", "")`).
2. Add `_parse_langs(raw)` that splits on commas, trims, drops empties and
   duplicates, and preserves first-seen order for warning messages.
3. Add `_select_languages(lang_info)`:
   - if an allowlist exists, warn for each name not present in `lang_info`;
   - keep only allowlisted names;
   - drop ignored names;
   - apply `STOP_AT_OTHER` (include `Other`, then stop) and `LANG_COUNT`
     (`-1` means all, `0` means none).
   - return the selected list.
4. `prep_content` calls `_select_languages()`, computes padding from the
   selected list only, and renders it unchanged.
5. Percentages are read from the API value and are not touched.

## Wiring and docs

- `action.yml`: new `LANGS` input, default `""`.
- `dockerfile`: add `INPUT_LANGS` to the `ENV` passthrough list.
- `.env.template`: add `INPUT_LANGS=`.
- `README.md`: new row in Content Tweaks, plus the example workflow.
- `CONTRIBUTING.md`: optional, add the variable to the sample `.env`.

## Tests

- Parse: comma list, extra whitespace, trailing comma, empty entries,
  duplicates, empty string.
- Selection: allowlist only; case sensitivity; unknown name warning path;
  overlap with ignore; `LANG_COUNT` applied after filtering; `LANG_COUNT=-1`;
  `STOP_AT_OTHER`; `LANGS` set with zero matches.
- Keep the existing graph, title, and bool tests passing.
- Prefer synthetic `lang_info`; `tests/sample_data.json` may be used for one
  end-to-end selection case.

## Coordination

- PR #182 fixes `LANG_COUNT` counting after `IGNORED_LANGUAGES`. This design
  subsumes that fix. Check whether #182 lands first and rebase, or mention in
  the new PR that it supersedes that part.
- PR #180 adds AI metrics near `prep_content`. Expect a small conflict.

## Left to the builder

- Exact function names and whether helpers live beside `prep_content` or in a
  small "selection" section.
- Warning message wording.
- Whether the parse helper returns a list or a tuple.