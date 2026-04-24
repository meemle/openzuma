"""
Openzuma Heart - 心脏模块
让openzuma拥有自主心跳，定时主动发言

Heart是gateway的内置组件，通过DeliveryRouter推送消息，
对接微信、QQ、Telegram等任何已连接的adapter。
"""

from .heartbeat import Heartbeat

__all__ = ["Heartbeat"]
