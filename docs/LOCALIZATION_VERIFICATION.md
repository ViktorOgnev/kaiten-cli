# EN/RU localization verification

Verified locally on 2026-09-22 with Python 3.11.15 and Click 8.5.0.

## Implementation

The CLI accepts `--locale ru|en` before the command. Precedence is explicit flag,
`KAITEN_CLI_LOCALE`, then `en`. English source templates and the packaged Russian
catalog cover CLI-owned help, discovery metadata, diagnostics and errors.
The agent selects the locale from the current conversation. The gateway passes
through the environment setting and instructs its agent to supply the flag.

## Claims and assumptions

- Selection happens before help, parsing failures and command execution.
- Locale state belongs to one invocation and resets on errors as well as success.
- Runtime messages opt in with `tr`; discovery translates an explicit set of
  prose fields. Neither mechanism translates arbitrary response objects.
- Only English and Russian are supported. The agent uses English for other
  conversation languages; the CLI does not infer language from the OS or profile.
- Templates are trusted package resources. No translation service or API call is
  introduced. Raw API, OS and library diagnostics retain their original language.

## Invariants and test obligations

| Invariant | Evidence |
| --- | --- |
| Flag overrides environment; OS language is irrelevant | Precedence, invalid/empty locale, root-option boundary and environment override tests |
| A Russian invocation cannot contaminate the next English invocation | EN → RU → EN help comparison for all 1,406 command/group/alias paths; exception, thread and async isolation tests |
| Discovery changes prose only | Structural comparison across all 417 canonical tools; source metadata remains unchanged |
| Defaults, enums, schema keys and user content are not translated | Schema tests with matching message IDs inside defaults, enum values and user-defined property keys |
| API calls and successful data remain unchanged | Mock HTTP comparison of URLs, bodies, headers and returned card data between locales |
| Batch workers inherit locale without translating user values | Concurrent batch test with one success and one CLI validation failure |
| Search results do not depend on output locale | Russian/English query comparisons, including ambiguous catalog/card-field terminology |
| Executable completion scripts remain unchanged | Byte-for-byte EN/RU comparison |
| Generated export headings may change; content does not | Markdown export comparison with titles and attachment names matching catalog entries |
| New known prose has a Russian translation with compatible placeholders | Catalog check for 2,894 required messages, format/percent placeholders and command flags; direct unlocalized runtime-output literals are rejected |
| Installed distributions include the catalog | Wheel built from sdist, installed into a temporary target, then EN/RU help and RU JSON discovery executed outside the checkout |

## Edge conditions and differential checks

Invalid locales return validation errors rather than silently choosing a language.
Tests include repeated flags, `--locale=value`, options inside user payloads,
`--` boundaries, invalid numeric input, absent credentials and misplaced global
options. Boolean JSON schemas and nested locale contexts are also covered.

English output is compared before and after Russian execution. All metadata is
compared after removing only documented prose fields. Existing regression tests
remain in place; prior mixed-language help expectations were updated to the new
English default. A cached Click help-option leak found by these checks was fixed
by retaining canonical source text and returning a localized copy.

## Verification results

- `pytest -q --cov=kaiten_cli --cov-branch --cov-report=term --cov-fail-under=75`:
  **1,104 passed, 2 deselected; 84.01% total coverage**.
- `ruff check src tests scripts`, `ruff format --check src tests scripts`, and
  `git diff --check`: passed.
- `python scripts/check_locales.py`: passed, 2,894 required messages.
- `python scripts/generate_reference_docs.py --check` with
  `KAITEN_CLI_LOCALE=ru`: passed; generated docs remain language-stable.
- `uv build --out-dir /tmp/kaiten-locale-dist`: sdist and wheel built; temporary
  installed-wheel smoke test passed.

## Risk areas and observability

Click's gettext callbacks are dispatched through an invocation context. Click
upgrades therefore need catalog and help/error regression checks; CI now runs the
catalog check explicitly in addition to the tests. Unknown messages fall back to
English so missing translations cannot prevent command execution. The catalog
check detects known missing translations and literal prose at runtime output
sinks without emitting extra fields into API responses or traces.

The local run covers Python 3.11 on macOS. The existing CI matrix covers Python
3.11–3.14; those remote jobs were not run in this task. Nine pre-existing Click
`get_text_stream` deprecation warnings remain. Live Kaiten tests were not run:
transport invariants were verified with mocks, and this change does not require
production writes. Better model tool selection from matching languages is an
unmeasured hypothesis, not an implementation guarantee.

## Integration verdict

**Safe to integrate.** The locale boundary, state isolation, machine contracts,
catalog completeness and installed-package behavior have executable evidence.
Keep the new checks enabled when adding prose or upgrading Click.
