# Document Yjs helper

The wheel ships `src/kaiten_cli/assets/document_yjs.cjs` and its license files.
End users need an existing Node.js 20+ only for `--content-mode yjs`. Neither
Python installation nor command execution invokes npm or installs Node.

Maintainer build (Node and npm already installed):

```sh
npm ci --ignore-scripts
npm run build
npm test
```

The lockfile pins the dependency graph. Commit the generated bundle and license
files. The sdist contains these sources so the bundle can be rebuilt; building a
Python wheel uses the checked-in bundle and does not run npm.

`schemas.json` contains headless ProseMirror construction rules for Kaiten document
schemas v1–v28. It excludes browser rendering/parsing functions and private server
code. Refresh it from a known Kaiten library checkout, then rebuild and test:

```sh
node export-schemas.cjs /path/to/kaiten-lib
```

Only the maintenance export needs that checkout. The runtime bundle does not
depend on `kaiten-lib`, node_modules, a browser, or any external file.

The parent sends one JSON request over stdin. After schema/content validation and
initial synchronization the child emits `write_ready` and waits for a `write`
permission line. The parent clears cache before releasing the update. The child
sends one batch, waits for its ack, and verifies a fresh full server state. No-op
updates return `unchanged` without write permission. JWTs and document content
must never be printed in diagnostics, errors or subprocess arguments. Error
output contains fixed protocol codes only. Socket reconnection and write retries
are disabled. A concurrent edit during preparation aborts; one during persistence
can cause a verification conflict, which is reported without overwriting it.
