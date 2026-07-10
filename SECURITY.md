# Security Policy

## Reporting a vulnerability

Use GitHub private vulnerability reporting or a private Security Advisory for this repository. Include the affected CLI version, the smallest reproducible scenario, expected impact and any known mitigation.

Do not publish API tokens, profile config, cached API responses, local snapshots, tenant URLs or exploit details in a public issue. If GitHub private reporting is unavailable, open a public issue containing no sensitive details and ask the maintainer for a private contact channel.

## Supported versions

Security fixes target the latest released version. Before reporting, reproduce against the newest tag when it is safe to do so.

## Local data

`kaiten-cli` can persist API tokens in its profile config, API responses in `http-cache.sqlite3`, and Kaiten datasets in `snapshots.sqlite3`. Treat all three as sensitive. Keep them out of source control, diagnostics and shared archives; remove or redact them before attaching any evidence.

The CLI creates these files with user-only permissions on supported POSIX systems. Application-owned config/cache/data directories are also restricted to the user. When an explicit config or trace path points into an existing user-managed directory, the CLI preserves that directory's mode and restricts only the file.

## Agent gateway trust boundary

The bundled agent gateway is intended for trusted local automation. Its read-only prompt, `KAITEN_CLI_READ_ONLY=1`, `KAITEN_CLI_STORAGE_READ_ONLY=1`, filesystem sandbox, environment allowlist, disabled ambient Codex config/rules, process-group timeout cleanup, and output redaction reduce accidental writes and common secret leaks. Existing snapshots remain readable, while build/refresh/delete fail before API collection. These controls do not form a hard security boundary: the child has a shell and Kaiten credentials, can attempt direct HTTP, and can read files made visible to the Codex process. Output redaction only covers known inherited credential values.

- Do not expose the gateway to untrusted prompts or tenants.
- Prefer a Kaiten credential whose server-side permissions exclude writes.
- Configure a bearer token even on loopback when other local principals or browser-driven input are in scope.
- A non-loopback bind requires a bearer token, but the built-in server is plaintext HTTP. Put it behind a TLS reverse proxy or private authenticated network and configure connection/body deadlines there.
- Treat `workdir` and every `--add-dir` as readable by the agent; do not point them at unrelated secrets.
