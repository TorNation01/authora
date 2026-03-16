# One-Command Bootstrap

The `bootstrap-one.sh` script delegates to `deploy.sh` for the full setup flow.

## Usage

```bash
./scripts/bootstrap-one.sh [repo_url]
```

Or use the main deploy script directly:

```bash
./scripts/deploy.sh
# or
npm run deploy
```

## Quickstart

```bash
git clone https://github.com/TorNation01/authora.git && cd authora && cp .env.example .env && ./scripts/deploy.sh
```

See **[DEPLOY_QUICKSTART](DEPLOY_QUICKSTART.md)** for full details, failure messages, and production flow.
