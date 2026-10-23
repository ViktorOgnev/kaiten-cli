# Document Yjs transport verification

Verified on a local instance on 2026-10-20 and on two explicitly authorized,
synthetic cloud documents on 2026-10-20–21. The cloud experiment reproduced
duplication with API replacement; the Yjs document matched the intended content.
No release was published. The transport uses Kaiten's internal collaboration
protocol, so this is not a claim of a stable Public API contract.

## Behaviour

- API `data`/`text` replacement is blocked without an explicit unsafe permission,
  including empty fields, mixed metadata requests and programmatic execution.
- The Russian refusal and permitted-PATCH stderr warning explicitly say that the
  update can duplicate the entire document. JSON stdout remains parseable.
- Yjs requires an existing Node.js 20+; no runtime installation, npm invocation,
  write retry or fallback to PATCH is implemented.
- Missing Node fails with `config_error` / exit 3 before HTTP. The read-only
  policy blocks both transports. Unknown schema, nodes, marks and attributes fail
  rather than being silently removed. Content validation preserves the API's
  javascript-URL restriction.
- Lost confirmation reports an unknown write result; a verification conflict
  reports an acknowledged but unverified update. Neither causes another write.

## Automated checks

- Python suite: **1458 passed**, 3 live tests deselected. Existing Click 9
  deprecation warnings remain.
- Final local recheck on 2026-10-23: **1458 Python tests passed**, and **16
  JavaScript tests passed** on Node **24.2.0**. The previous 15-test JavaScript
  suite also passed on Node **20.20.0**. CI now runs the complete JavaScript suite
  on Node 20 and checks reproducibility of the committed helper and license files.
- JavaScript coverage includes all bundled schema versions v1–v28, a table with
  122 rows, distributed deletion of 24 rows and insertion of 36 new rows,
  identity preservation of an unchanged block, old-state replay, duplicate
  delivery, parallel edits, Socket.IO acknowledgements, access/schema rejection,
  timeout, disconnect and verification conflict.
- The bundled helper was exercised as a standalone child process without
  node_modules beside it. IPC requires parent permission before sending content.
- Ruff, EN/RU catalog coverage and generated command documentation checks passed.
- Wheel and sdist built successfully. The sdist includes helper source and its
  lockfile and excludes node_modules. The wheel includes the helper and licenses.
- A fresh environment installed from the wheel was checked for blocked API
  replacement, missing Node and a real Yjs no-op on Node 20. Both refusal cases
  made zero HTTP requests.

## Real local Kaiten lifecycle

The local application and a dedicated socket process were used with one new
temporary document and a private resumable manifest. No existing documents were
edited. This used the real HTTP controllers, Socket.IO handler and persistence;
the second client was a headless protocol client, not a browser UI test.

1. Create a temporary document and populate an introduction plus one 122-row
   table through Yjs.
2. Subscribe a second client, retain its Yjs state, and disconnect it.
3. Update the introduction and one table cell through `documents update
   --content-mode yjs`.
4. Reconnect the second client and submit its retained old state to synchronization.
5. Verify a fresh full socket state and reread the document through HTTP.

Both reads contained **one table with 122 rows**, the new introduction and the
changed cell. No duplicate introduction or table appeared. The socket write
received an acknowledgement and passed the fresh-state comparison.

The initial local run also proved that Public API serialization may omit
`schema_version`. The CLI now retrieves `/document-schemas/latest` when needed
instead of guessing v1; the verified local lifecycle used **v28**.

The temporary document was deleted and a subsequent read returned 404. Temporary
credential copies were removed. Parallel-edit and failure injection coverage is
from the automated protocol tests, not cloud concurrency or browser UI verification.

## Authorized cloud comparison

Two synthetic documents were reused for successive content updates. All writes
and authoritative readbacks used the CLI. The first document used explicit Yjs
mode; the second used API replacement with explicit unsafe permission. Browser
tabs were opened before the final round, but browser sessions were not used to
edit content. After the user restricted verification to tooling, final evidence
came only from fresh CLI reads with the persistent read cache bypassed.

The documents contained headings, formatting, lists, checklists, code, columns,
a toggle, tabs and four tables. Their initial table row counts were
`[122, 9, 6, 4]`, including header rows. An earlier round rewrote fragments
containing approximately half the source text without observed duplication.

The final round deleted every fifth original data row (24 rows), inserted 36
new rows with unique identifiers, and distributed paragraph/list/nested-block
deletions and new content across the document. Percentages count literal deleted
and inserted text characters against each document's own pre-update text.

| Observation | Yjs | Explicit API replacement |
| --- | --- | --- |
| Deleted text in submitted target | 20.62% | 20.54% |
| Added text in submitted target | 29.95% | 29.99% |
| Intended text characters | 50,230 | 50,232 |
| Observed text characters | 50,230 | 96,125 |
| Observed table row counts | `[134, 9, 6, 4]` | `[122, 9, 6, 4, 134, 9, 6, 4]` |
| End markers | V4 once, V3 absent | V3 once and V4 once |

The Yjs write was acknowledged and verified by fresh synchronization. A subsequent
HTTP read matched the entire target, including schema-normalized attributes.
All 40 selected deleted fragments were absent, all 49 inserted fragments were
present once, and unchanged identified blocks matched the prepared target.

The API result retained the complete old document as its prefix and the new
target text as its suffix. All 39 selected deleted fragments remained in the old
copy. Five nested-tab attributes differed from the submitted target; this is
not a claim of attribute-preserving API behavior. A subsequent CLI read confirmed
the duplicate. No corrective write or automatic retry was performed.

This cloud observation does not establish a controlled stale-editor reconnect:
the browser transport was not instrumented, and page reload is not such a test.
The controlled old-state reconnect remains the separate local lifecycle above.
Raw documents, tenant/document identifiers, credentials, screenshots, traces and
private manifests are excluded from the repository.

## Package size

Compared with a wheel built from the original Git HEAD using the same builder:

| Measurement | Bytes |
| --- | ---: |
| Original wheel | 392,090 |
| Updated wheel | 479,912 |
| Download increase | 87,822 |
| Uncompressed package increase | 399,586 |
| Helper and license files, uncompressed | 374,492 |
| Helper and license files, ZIP-compressed | 79,853 |

The Node runtime is separate and is not included in the wheel. These are build
measurements, not the installed size including Python dependencies or bytecode.
