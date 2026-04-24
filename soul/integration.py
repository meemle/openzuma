"""
Openzuma Heart - Gateway集成
将heart模块集成到GatewayRunner中，实现平台无关的心跳推送

集成方式：
1. GatewayRunner初始化时创建Heartbeat实例
2. Heartbeat通过DeliveryRouter向所有活跃session推送
3. 配置通过config.yaml的heart字段管理
"""

import logging
from typing import Optional, Dict, Any, List

from .heartbeat import Heartbeat

logger = logging.getLogger("openzuma.soul.integration")


def load_heart_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    从config.yaml加载heart配置
    
    配置格式（config.yaml）:
        heart:
          enabled: true
          interval_minutes: 10
          custom_topics:
            - "🎯 自定义话题1"
            - "💡 自定义话题2"
    
    Returns:
        dict with keys: enabled, interval_minutes, custom_topics
    """
    heart_cfg = config.get("soul", {})
    return {
        "enabled": heart_cfg.get("enabled", False),
        "interval_minutes": heart_cfg.get("interval_minutes", 10),
        "custom_topics": heart_cfg.get("custom_topics", []),
    }


def create_heartbeat(
    deliver_func,
    config: Optional[Dict[str, Any]] = None,
) -> Optional[Heartbeat]:
    """
    根据配置创建Heartbeat实例
    
    Args:
        deliver_func: 异步推送函数，由GatewayRunner注入
        config: heart配置字典（来自load_heart_config）
    
    Returns:
        Heartbeat实例，如果未启用则返回None
    """
    if config is None:
        config = {"enabled": False, "interval_minutes": 10, "custom_topics": []}
    
    if not config.get("enabled", False):
        logger.info("♥ Heart模块未启用（soul.enabled未设为true）")
        return None
    
    topics = None
    if config.get("custom_topics"):
        topics = config["custom_topics"]
    
    heart = Heartbeat(
        deliver_func=deliver_func,
        interval_minutes=config.get("interval_minutes", 10),
        topic_pool=topics,
    )
    
    logger.info("♥ Heart模块已创建并启用")
    return heart


async def heartbeat_deliver_via_gateway(gateway_runner, message: str) -> bool:
    """
    Heartbeat的推送函数 - 通过GatewayRunner向所有活跃session推送
    
    这个函数是平台无关的，会通过DeliveryRouter自动路由到
    微信/QQ/Telegram/Slack等任何已连接的adapter。
    
    Args:
        gateway_runner: GatewayRunner实例
        message: 要推送的心跳消息
    
    Returns:
        是否推送成功
    """
    from gateway.delivery import DeliveryTarget
    from gateway.platforms.base import Platform
    
    try:
        # 收集所有活跃平台的session
        targets = []
        
        # 从session_store获取所有活跃session
        if hasattr(gateway_runner, 'session_store'):
            sessions = gateway_runner.session_store.list_sessions()
            for session_key in sessions:
                # 解析session_key格式: platform:chat_id[:thread_id]
                parts = session_key.split(":")
                if len(parts) >= 2:
                    platform_str = parts[0]
                    chat_id = parts[1]
                    thread_id = parts[2] if len(parts) > 2 else None
                    
                    try:
                        platform = Platform(platform_str)
                        targets.append(DeliveryTarget(
                            platform=platform,
                            chat_id=chat_id,
                            thread_id=thread_id,
                        ))
                    except ValueError:
                        logger.warning(f"♥ 无法识别平台: {platform_str}")
        
        # 如果没有活跃session，尝试向所有已连接adapter的默认chat推送
        if not targets and hasattr(gateway_runner, 'adapters'):
            for platform, adapter in gateway_runner.adapters.items():
                # 获取adapter的默认/主chat_id
                default_chat = getattr(adapter, 'default_chat_id', None) or \
                              getattr(adapter, 'home_chat_id', None)
                if default_chat:
                    targets.append(DeliveryTarget(
                        platform=platform,
                        chat_id=default_chat,
                    ))
        
        if not targets:
            logger.warning("♥ 没有可推送的目标，心跳消息跳过")
            return False
        
        # 通过DeliveryRouter推送
        results = await gateway_runner.delivery_router.deliver(
            content=message,
            targets=targets,
            job_name="openzuma-heart",
        )
        
        success = any(r.get("success") for r in results.values())
        if success:
            logger.info(f"♥ 心跳已推送到 {len(results)} 个目标")
        else:
            logger.warning(f"♥ 心跳推送全部失败: {results}")
        return success
        
    except Exception as e:
        logger.error(f"♥ 心跳推送异常: {e}")
        return False
