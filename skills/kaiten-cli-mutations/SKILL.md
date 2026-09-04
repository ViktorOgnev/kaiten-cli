---
name: kaiten-cli-mutations
description: Use when planning or executing Kaiten writes through kaiten-cli. Enforces profile probing, exact previews, resumable manifests, bounded batches, and field-scoped readback.
---

# kaiten-cli mutations

Use this skill for card, checklist, relation, comment, membership, document, or
other remote writes.

## Required sequence

1. Discover the exact command once with `search-tools`, `describe`, and
   `examples`.
2. Select the profile explicitly and verify authentication without a write:

   ```bash
   kaiten --json --profile <name> --read-only profile probe
   ```

3. Perform investigation reads with `--read-only`. Use batch or snapshot paths
   instead of entity loops.
4. Show the exact targets, ordering, exclusions, and payload preview before
   requesting authorization.
5. After authorization, persist a private resumable manifest outside the
   repository.
6. Execute small bounded batches and record each result before continuing.
7. Read back only the fields that were intended to change.

## Resumable manifest

Use JSONL with one operation per line:

```json
{"operation_id":"stable-hash","canonical_name":"cards.update","target_key":"CARD-1","input":{"card_id":"CARD-1","title":"New title"},"status":"pending","attempts":0}
```

- Derive `operation_id` from canonical command, stable target key, and normalized
  input so the same planned write keeps the same identifier.
- Store the file with mode `0600` in a user-selected temporary or work
  directory; never commit it.
- Do not store tokens, profile configuration, raw API headers, or unrelated
  entity data.
- Update status only after recording the command result. Use
  `pending`, `applied`, `verified`, or `failed`.
- On resume, skip `verified`, read back `applied`, and retry `failed` only after
  classifying the error.

## Safety rules

- A normal profile can mutate. `sandbox` profile metadata is not a safety gate.
- Never remove `--read-only` until the preview has been authorized.
- Use command-specific dry-run when `describe` reports it; do not invent a
  universal `--dry-run`.
- Do not retry 401, 403, 404, 405, or 422 as transient failures.
- Retry only bounded 429, 5xx, timeout, or transport failures.
- After an ambiguous timeout, read back before retrying a create/update.
- Prefer existing batch commands. Do not create an external per-entity loop
  when a bulk alternative exists.
- Do not mark a source checklist item complete or add comments/status changes
  unless those effects were explicitly authorized.

## Addon data writes

Addon state is not part of the card entity. A card's GitHub attachments, and any
other addon's per-card state, live in a separate row reached through
`card-addon-data` / `github-addon`, and never show up in `cards get`. Treat them
as their own mutation family:

- Prefer `github-addon <pulls|branches|commits|issues> attach|detach` over raw
  `card-addon-data set`. The typed commands read the current list, dedup by the
  addon's own identity, and rewrite only the key they touch.
- Raw `card-addon-data set` merges by top-level key, so a partial value for a key
  replaces that whole key. Sending one attachment overwrites the rest. Read the
  current value first and send the full replacement list.
- Preview with the command's own `--dry-run`. It performs the read and reports the
  outcome without writing, but it is still classified as a mutation, so it does
  not run under `--read-only`. Do investigation with `github-addon ... list`
  (a plain read), then drop `--read-only` for the dry run, then authorize.
- `detach` refuses a selector that matches more than one attachment. Narrow it
  with `--owner`/`--repo` rather than reaching for `--all`.
- In the manifest, the stable target key is card id plus addon key plus the
  attachment identity (PR/issue id, `owner/repo/branch`, commit sha), not the
  card id alone.

## Readback

Readback must be field-scoped and target-scoped:

```bash
kaiten --json --profile <name> cards batch-get \
  --card-ids '[101,102]' \
  --fields id,title,state \
  --compact
```

For an addon write, read back the addon store instead: a card read shows nothing,
because the change never lands in a card field.

```bash
kaiten --json --profile <name> github-addon pulls list \
  --card-id 101 \
  --fields number,htmlUrl,state
```

Compare the returned fields with the manifest, mark matching operations
`verified`, and report requested/applied/verified/failed counts.

## Product boundary

There is no universal mutation runner in this version. Use the manifest as an
agent-side recovery contract and prefer existing command-specific batch tools.
Propose a new product batch command only when a later audit finds the same
mutation family in at least three sessions or at least 20 calls.
