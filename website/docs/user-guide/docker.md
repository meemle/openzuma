---
sidebar_position: 7
title: "Docker"
description: "Running Openzuma Agent in Docker and using Docker as a terminal backend"
---

# Openzuma Agent — Docker

There are two distinct ways Docker intersects with Openzuma Agent:

1. **Running Openzuma IN Docker** — the agent itself runs inside a container (this page's primary focus)
2. **Docker as a terminal backend** — the agent runs on your host but executes commands inside a Docker sandbox (see [Configuration → terminal.backend](./configuration.md))

This page covers option 1. The container stores all user data (config, API keys, sessions, skills, memories) in a single directory mounted from the host at `/opt/data`. The image itself is stateless and can be upgraded by pulling a new version without losing any configuration.

## Quick start

If this is your first time running Openzuma Agent, create a data directory on the host and start the container interactively to run the setup wizard:

```sh
mkdir -p ~/.openzuma
docker run -it --rm \
  -v ~/.openzuma:/opt/data \
  nousresearch/openzuma-agent setup
```

This drops you into the setup wizard, which will prompt you for your API keys and write them to `~/.openzuma/.env`. You only need to do this once. It is highly recommended to set up a chat system for the gateway to work with at this point.

## Running in gateway mode

Once configured, run the container in the background as a persistent gateway (Telegram, Discord, Slack, WhatsApp, etc.):

```sh
docker run -d \
  --name openzuma \
  --restart unless-stopped \
  -v ~/.openzuma:/opt/data \
  -p 8742:8742 \
  nousresearch/openzuma-agent gateway run
```

Port 8742 exposes the gateway's [OpenAI-compatible API server](./api-server.md) and health endpoint. It's optional if you only use chat platforms (Telegram, Discord, etc.), but required if you want the dashboard or external tools to reach the gateway.

Opening any port on an internet facing machine is a security risk. You should not do it unless you understand the risks.

## Running the dashboard

The built-in web dashboard can run alongside the gateway as a separate container. 

To run the dashboard as its own container, point it at the gateway's health endpoint so it can detect gateway status across containers:

```sh
docker run -d \
  --name openzuma-dashboard \
  --restart unless-stopped \
  -v ~/.openzuma:/opt/data \
  -p 9219:9219 \
  -e GATEWAY_HEALTH_URL=http://$HOST_IP:8742 \
  nousresearch/openzuma-agent dashboard
```

Replace `$HOST_IP` with the IP address of the machine running the gateway container (e.g. `192.168.1.100`), or use a Docker network hostname if both containers share a network (see the [Compose example](#docker-compose-example) below).

| Environment variable | Description | Default |
|---------------------|-------------|---------|
| `GATEWAY_HEALTH_URL` | Base URL of the gateway's API server, e.g. `http://gateway:8742` | *(unset — local PID check only)* |
| `GATEWAY_HEALTH_TIMEOUT` | Health probe timeout in seconds | `3` |

Without `GATEWAY_HEALTH_URL`, the dashboard falls back to local process detection — which only works when the gateway runs in the same container or on the same host.

## Running interactively (CLI chat)

To open an interactive chat session against a running data directory:

```sh
docker run -it --rm \
  -v ~/.openzuma:/opt/data \
  nousresearch/openzuma-agent
```

## Persistent volumes

The `/opt/data` volume is the single source of truth for all Openzuma state. It maps to your host's `~/.openzuma/` directory and contains:

| Path | Contents |
|------|----------|
| `.env` | API keys and secrets |
| `config.yaml` | All Openzuma configuration |
| `SOUL.md` | Agent personality/identity |
| `sessions/` | Conversation history |
| `memories/` | Persistent memory store |
| `skills/` | Installed skills |
| `cron/` | Scheduled job definitions |
| `hooks/` | Event hooks |
| `logs/` | Runtime logs |
| `skins/` | Custom CLI skins |

:::warning
Never run two Openzuma **gateway** containers against the same data directory simultaneously — session files and memory stores are not designed for concurrent write access. Running a dashboard container alongside the gateway is safe since the dashboard only reads data.
:::

## Environment variable forwarding

API keys are read from `/opt/data/.env` inside the container. You can also pass environment variables directly:

```sh
docker run -it --rm \
  -v ~/.openzuma:/opt/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  nousresearch/openzuma-agent
```

Direct `-e` flags override values from `.env`. This is useful for CI/CD or secrets-manager integrations where you don't want keys on disk.

## Docker Compose example

For persistent deployment with both the gateway and dashboard, a `docker-compose.yaml` is convenient:

```yaml
services:
  openzuma:
    image: nousresearch/openzuma-agent:latest
    container_name: openzuma
    restart: unless-stopped
    command: gateway run
    ports:
      - "8742:8742"
    volumes:
      - ~/.openzuma:/opt/data
    networks:
      - openzuma-net
    # Uncomment to forward specific env vars instead of using .env file:
    # environment:
    #   - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    #   - OPENAI_API_KEY=${OPENAI_API_KEY}
    #   - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: "2.0"

  dashboard:
    image: nousresearch/openzuma-agent:latest
    container_name: openzuma-dashboard
    restart: unless-stopped
    command: dashboard --host 0.0.0.0
    ports:
      - "9219:9219"
    volumes:
      - ~/.openzuma:/opt/data
    environment:
      - GATEWAY_HEALTH_URL=http://openzuma:8742
    networks:
      - openzuma-net
    depends_on:
      - openzuma
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "0.5"

networks:
  openzuma-net:
    driver: bridge
```

Start with `docker compose up -d` and view logs with `docker compose logs -f`.

## Resource limits

The Openzuma container needs moderate resources. Recommended minimums:

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| Memory | 1 GB | 2–4 GB |
| CPU | 1 core | 2 cores |
| Disk (data volume) | 500 MB | 2+ GB (grows with sessions/skills) |

Browser automation (Playwright/Chromium) is the most memory-hungry feature. If you don't need browser tools, 1 GB is sufficient. With browser tools active, allocate at least 2 GB.

Set limits in Docker:

```sh
docker run -d \
  --name openzuma \
  --restart unless-stopped \
  --memory=4g --cpus=2 \
  -v ~/.openzuma:/opt/data \
  nousresearch/openzuma-agent gateway run
```

## What the Dockerfile does

The official image is based on `debian:13.4` and includes:

- Python 3 with all Openzuma dependencies (`pip install -e ".[all]"`)
- Node.js + npm (for browser automation and WhatsApp bridge)
- Playwright with Chromium (`npx playwright install --with-deps chromium`)
- ripgrep and ffmpeg as system utilities
- The WhatsApp bridge (`scripts/whatsapp-bridge/`)

The entrypoint script (`docker/entrypoint.sh`) bootstraps the data volume on first run:
- Creates the directory structure (`sessions/`, `memories/`, `skills/`, etc.)
- Copies `.env.example` → `.env` if no `.env` exists
- Copies default `config.yaml` if missing
- Copies default `SOUL.md` if missing
- Syncs bundled skills using a manifest-based approach (preserves user edits)
- Then runs `openzuma` with whatever arguments you pass

## Upgrading

Pull the latest image and recreate the container. Your data directory is untouched.

```sh
docker pull nousresearch/openzuma-agent:latest
docker rm -f openzuma
docker run -d \
  --name openzuma \
  --restart unless-stopped \
  -v ~/.openzuma:/opt/data \
  nousresearch/openzuma-agent gateway run
```

Or with Docker Compose:

```sh
docker compose pull
docker compose up -d
```

## Skills and credential files

When using Docker as the execution environment (not the methods above, but when the agent runs commands inside a Docker sandbox), Openzuma automatically bind-mounts the skills directory (`~/.openzuma/skills/`) and any credential files declared by skills into the container as read-only volumes. This means skill scripts, templates, and references are available inside the sandbox without manual configuration.

The same syncing happens for SSH and Modal backends — skills and credential files are uploaded via rsync or the Modal mount API before each command.

## Troubleshooting

### Container exits immediately

Check logs: `docker logs openzuma`. Common causes:
- Missing or invalid `.env` file — run interactively first to complete setup
- Port conflicts if running with exposed ports

### "Permission denied" errors

The container runs as root by default. If your host `~/.openzuma/` was created by a non-root user, permissions should work. If you get errors, ensure the data directory is writable:

```sh
chmod -R 755 ~/.openzuma
```

### Browser tools not working

Playwright needs shared memory. Add `--shm-size=1g` to your Docker run command:

```sh
docker run -d \
  --name openzuma \
  --shm-size=1g \
  -v ~/.openzuma:/opt/data \
  nousresearch/openzuma-agent gateway run
```

### Gateway not reconnecting after network issues

The `--restart unless-stopped` flag handles most transient failures. If the gateway is stuck, restart the container:

```sh
docker restart openzuma
```

### Checking container health

```sh
docker logs --tail 50 openzuma          # Recent logs
docker run -it --rm nousresearch/openzuma-agent:latest version     # Verify version
docker stats openzuma                    # Resource usage
```
