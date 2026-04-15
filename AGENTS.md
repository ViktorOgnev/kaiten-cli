# kaiten-cli for Agents

## Install from Git

Recommended:

```bash
uv tool install git+https://github.com/ViktorOgnev/kaiten-cli.git
```

Alternative:

```bash
pipx install git+https://github.com/ViktorOgnev/kaiten-cli.git
```

Fallback if `uv` and `pipx` are unavailable:

```bash
python3 -m venv .venv
.venv/bin/pip install "git+https://github.com/ViktorOgnev/kaiten-cli.git"
```

## Smoke Check

These commands do not need Kaiten credentials:

```bash
kaiten --version
kaiten --help
kaiten search-tools cards
```

If the package is installed into the current Python environment, this fallback also works:

```bash
python -m kaiten_cli --help
```

## Runtime Configuration

Required environment variables:

```bash
export KAITEN_DOMAIN=sandbox
export KAITEN_TOKEN=your-api-token
```

Safe first call:

```bash
kaiten --json spaces list --compact --fields id,title
```

Reusable local profile:

```bash
kaiten profile add sandbox --domain sandbox --token "$KAITEN_TOKEN" --sandbox --set-active
```

## Safety

- Start with read-only commands.
- Mutations are blocked unless the selected profile is marked as sandbox or uses the `sandbox` domain.
- Live validation is opt-in and requires `KAITEN_LIVE=1`.
