#!/bin/bash
# Docker/Podman entrypoint: bootstrap config files into the mounted volume, then run openzuma.
set -e

OPENZUMA_HOME="${OPENZUMA_HOME:-/opt/data}"
INSTALL_DIR="/opt/openzuma"

# --- Privilege dropping via gosu ---
# When started as root (the default for Docker, or fakeroot in rootless Podman),
# optionally remap the openzuma user/group to match host-side ownership, fix volume
# permissions, then re-exec as openzuma.
if [ "$(id -u)" = "0" ]; then
    if [ -n "$OPENZUMA_UID" ] && [ "$OPENZUMA_UID" != "$(id -u openzuma)" ]; then
        echo "Changing openzuma UID to $OPENZUMA_UID"
        usermod -u "$OPENZUMA_UID" openzuma
    fi

    if [ -n "$OPENZUMA_GID" ] && [ "$OPENZUMA_GID" != "$(id -g openzuma)" ]; then
        echo "Changing openzuma GID to $OPENZUMA_GID"
        # -o allows non-unique GID (e.g. macOS GID 20 "staff" may already exist
        # as "dialout" in the Debian-based container image)
        groupmod -o -g "$OPENZUMA_GID" openzuma 2>/dev/null || true
    fi

    actual_openzuma_uid=$(id -u openzuma)
    if [ "$(stat -c %u "$OPENZUMA_HOME" 2>/dev/null)" != "$actual_openzuma_uid" ]; then
        echo "$OPENZUMA_HOME is not owned by $actual_openzuma_uid, fixing"
        # In rootless Podman the container's "root" is mapped to an unprivileged
        # host UID — chown will fail.  That's fine: the volume is already owned
        # by the mapped user on the host side.
        chown -R openzuma:openzuma "$OPENZUMA_HOME" 2>/dev/null || \
            echo "Warning: chown failed (rootless container?) — continuing anyway"
    fi

    echo "Dropping root privileges"
    exec gosu openzuma "$0" "$@"
fi

# --- Running as openzuma from here ---
source "${INSTALL_DIR}/.venv/bin/activate"

# Create essential directory structure.  Cache and platform directories
# (cache/images, cache/audio, platforms/whatsapp, etc.) are created on
# demand by the application — don't pre-create them here so new installs
# get the consolidated layout from get_openzuma_dir().
# The "home/" subdirectory is a per-profile HOME for subprocesses (git,
# ssh, gh, npm …).  Without it those tools write to /root which is
# ephemeral and shared across profiles.  See issue #4426.
mkdir -p "$OPENZUMA_HOME"/{cron,sessions,logs,hooks,memories,skills,skins,plans,workspace,home}

# .env
if [ ! -f "$OPENZUMA_HOME/.env" ]; then
    cp "$INSTALL_DIR/.env.example" "$OPENZUMA_HOME/.env"
fi

# config.yaml
if [ ! -f "$OPENZUMA_HOME/config.yaml" ]; then
    cp "$INSTALL_DIR/cli-config.yaml.example" "$OPENZUMA_HOME/config.yaml"
fi

# SOUL.md
if [ ! -f "$OPENZUMA_HOME/SOUL.md" ]; then
    cp "$INSTALL_DIR/docker/SOUL.md" "$OPENZUMA_HOME/SOUL.md"
fi

# Sync bundled skills (manifest-based so user edits are preserved)
if [ -d "$INSTALL_DIR/skills" ]; then
    python3 "$INSTALL_DIR/tools/skills_sync.py"
fi

# Final exec: two supported invocation patterns.
#
#   docker run <image>                 -> exec `openzuma` with no args (legacy default)
#   docker run <image> chat -q "..."   -> exec `openzuma chat -q "..."` (legacy wrap)
#   docker run <image> sleep infinity  -> exec `sleep infinity` directly
#   docker run <image> bash            -> exec `bash` directly
#
# If the first positional arg resolves to an executable on PATH, we assume the
# caller wants to run it directly (needed by the launcher which runs long-lived
# `sleep infinity` sandbox containers — see tools/environments/docker.py).
# Otherwise we treat the args as a openzuma subcommand and wrap with `openzuma`,
# preserving the documented `docker run <image> <subcommand>` behavior.
if [ $# -gt 0 ] && command -v "$1" >/dev/null 2>&1; then
    exec "$@"
fi
exec openzuma "$@"
