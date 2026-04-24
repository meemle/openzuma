"""
Shared platform registry for Openzuma Agent.

Single source of truth for platform metadata consumed by both
skills_config (label display) and tools_config (default toolset
resolution).  Import ``PLATFORMS`` from here instead of maintaining
duplicate dicts in each module.
"""

from collections import OrderedDict
from typing import NamedTuple


class PlatformInfo(NamedTuple):
    """Metadata for a single platform entry."""
    label: str
    default_toolset: str


# Ordered so that TUI menus are deterministic.
PLATFORMS: OrderedDict[str, PlatformInfo] = OrderedDict([
    ("cli",            PlatformInfo(label="🖥️  CLI",            default_toolset="openzuma-cli")),
    ("telegram",       PlatformInfo(label="📱 Telegram",        default_toolset="openzuma-telegram")),
    ("discord",        PlatformInfo(label="💬 Discord",         default_toolset="openzuma-discord")),
    ("slack",          PlatformInfo(label="💼 Slack",           default_toolset="openzuma-slack")),
    ("whatsapp",       PlatformInfo(label="📱 WhatsApp",        default_toolset="openzuma-whatsapp")),
    ("signal",         PlatformInfo(label="📡 Signal",          default_toolset="openzuma-signal")),
    ("bluebubbles",    PlatformInfo(label="💙 BlueBubbles",     default_toolset="openzuma-bluebubbles")),
    ("email",          PlatformInfo(label="📧 Email",           default_toolset="openzuma-email")),
    ("homeassistant",  PlatformInfo(label="🏠 Home Assistant",  default_toolset="openzuma-homeassistant")),
    ("mattermost",     PlatformInfo(label="💬 Mattermost",      default_toolset="openzuma-mattermost")),
    ("matrix",         PlatformInfo(label="💬 Matrix",          default_toolset="openzuma-matrix")),
    ("dingtalk",       PlatformInfo(label="💬 DingTalk",        default_toolset="openzuma-dingtalk")),
    ("feishu",         PlatformInfo(label="🪽 Feishu",          default_toolset="openzuma-feishu")),
    ("wecom",          PlatformInfo(label="💬 WeCom",           default_toolset="openzuma-wecom")),
    ("wecom_callback", PlatformInfo(label="💬 WeCom Callback",  default_toolset="openzuma-wecom-callback")),
    ("weixin",         PlatformInfo(label="💬 Weixin",          default_toolset="openzuma-weixin")),
    ("qqbot",          PlatformInfo(label="💬 QQBot",           default_toolset="openzuma-qqbot")),
    ("webhook",        PlatformInfo(label="🔗 Webhook",         default_toolset="openzuma-webhook")),
    ("api_server",     PlatformInfo(label="🌐 API Server",      default_toolset="openzuma-api-server")),
])


def platform_label(key: str, default: str = "") -> str:
    """Return the display label for a platform key, or *default*."""
    info = PLATFORMS.get(key)
    return info.label if info is not None else default
