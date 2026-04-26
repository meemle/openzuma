"""
Openzuma Soul - Gateway集成 v2
将soul模块集成到GatewayRunner中，大模型驱动的话题生成

v2 改造：
- 话题不再从预设库抽取，而是大模型实时生成
- 配置新增: model, base_url, api_key（用于话题生成LLM）
- 静默时段(23:00-07:00)内置在soulbeat.py中
"""

import logging
from typing import Optional, Dict, Any, List

from .soulbeat import SoulBeat

logger = logging.getLogger("openzuma.soul.integration")


def load_soul_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    从config.yaml加载soul配置
    
    v2 配置格式:
        soul:
          enabled: true
          interval_minutes: 30
          model: google/gemini-2.0-flash-001    # 话题生成用的模型
          base_url: https://openrouter.ai/api/v1  # 可选，覆盖默认
          api_key: sk-xxx                        # 可选，覆盖环境变量
          custom_topics: []                       # v2中弃用，保留兼容
    """
    soul_cfg = config.get("soul", {})
    result = {
        "enabled": soul_cfg.get("enabled", False),
        "interval_minutes": soul_cfg.get("interval_minutes", 30),
        "model": soul_cfg.get("model", ""),
        "base_url": soul_cfg.get("base_url", ""),
        "api_key": soul_cfg.get("api_key", ""),
        "custom_topics": soul_cfg.get("custom_topics", []),
    }
    
    # v2: 如果配置了model，设置环境变量供soulbeat使用
    if result["model"]:
        import os
        os.environ["SOUL_MODEL"] = result["model"]
    if result["base_url"]:
        import os
        os.environ["SOUL_BASE_URL"] = result["base_url"]
    if result["api_key"]:
        import os
        os.environ["SOUL_API_KEY"] = result["api_key"]
    
    return result


def create_soulbeat(
    deliver_func,
    config: Optional[Dict[str, Any]] = None,
) -> Optional[SoulBeat]:
    """
    根据配置创建SoulBeat v2实例
    """
    if config is None:
        config = {"enabled": False, "interval_minutes": 30}
    
    if not config.get("enabled", False):
        logger.info("♥ Soul模块未启用（soul.enabled未设为true）")
        return None
    
    soulbeat = SoulBeat(
        deliver_func=deliver_func,
        interval_minutes=config.get("interval_minutes", 30),
    )
    
    logger.info("♥ SoulBeat v2 模块已创建（大模型实时话题生成模式）")
    return soulbeat


async def soulbeat_deliver_via_gateway(gateway_runner, message: str) -> bool:
    """
    SoulBeat的推送函数 - 通过GatewayRunner向所有活跃session推送
    （保持不变，平台无关）
    """
    from gateway.delivery import DeliveryTarget
    from gateway.platforms.base import Platform
    
    try:
        targets = []
        
        if hasattr(gateway_runner, 'session_store'):
            sessions = gateway_runner.session_store.list_sessions()
            for session_key in sessions:
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
        
        if not targets and hasattr(gateway_runner, 'adapters'):
            for platform, adapter in gateway_runner.adapters.items():
                default_chat = getattr(adapter, 'default_chat_id', None) or \
                              getattr(adapter, 'home_chat_id', None)
                if default_chat:
                    targets.append(DeliveryTarget(
                        platform=platform,
                        chat_id=default_chat,
                    ))
        
        if not targets:
            logger.warning("♥ 没有可推送的目标，灵魂跳动消息跳过")
            return False
        
        results = await gateway_runner.delivery_router.deliver(
            content=message,
            targets=targets,
            job_name="openzuma-soul",
        )
        
        success = any(r.get("success") for r in results.values())
        if success:
            logger.info(f"♥ 灵魂跳动已推送到 {len(results)} 个目标")
        else:
            logger.warning(f"♥ 灵魂跳动推送全部失败: {results}")
        return success
        
    except Exception as e:
        logger.error(f"♥ 灵魂跳动推送异常: {e}")
        return False
