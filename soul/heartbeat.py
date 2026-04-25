"""
Openzuma Soul - 灵魂心跳引擎
定时主动发言，让openzuma有自主"心跳"

设计原则：
- Soul是gateway内置组件，通过GatewayRunner的DeliveryRouter推送
- 不绑定任何具体平台（微信/QQ/Telegram等），平台无关
- 心跳间隔通过config.yaml配置，也可运行时动态调整
- 话题库可扩展，用户可自定义
"""

import random
import asyncio
import logging
from datetime import datetime
from typing import Callable, Optional, List, Dict, Any

logger = logging.getLogger("openzuma.soul")


# ====== 预设话题库 ======
TOPIC_POOL = [
    # 知识分享
    "💡 你知道吗？人一生中心脏大约会跳动25亿次。",
    "💡 分享一个小知识：地球上的蚂蚁总重量和人类总重量大致相当。",
    "💡 有趣的事实：章鱼有三颗心脏，两颗负责鳃，一颗负责全身供血。",
    "💡 冷知识：蜂蜜永远不会变质，考古学家在埃及金字塔中发现了3000年前的蜂蜜，仍然可以食用。",
    "💡 宇宙中的恒星数量比地球上所有沙滩的沙粒总数还多。",
    "💡 光从太阳到达地球需要大约8分20秒，所以我们看到的阳光是8分钟前的。",
    "💡 一朵云的平均重量是50万公斤，相当于100头大象。",
    "💡 香蕉实际上是浆果，而草莓不是。",
    "💡 人脑产生的电量足以点亮一个小灯泡。",
    "💡 金星上的一天比金星上的一年还长。",
    "💡 蜗牛可以睡3年不吃不喝，是世界上最能睡的动物。",
    "💡 北极熊的皮肤其实是黑色的，毛发是透明的。",
    "💡 人体血管的总长度可以绕地球两圈半。",
    "💡 企鹅求婚时会送石头给心仪的对象。",
    "💡 海马是唯一由雄性怀孕生子的动物。",

    # 闲聊互动
    "☕ 休息一下吧，站起来活动活动，喝杯水。",
    "🎵 最近有没有听到什么好听的歌？",
    "📖 有什么有趣的事情想聊聊吗？",
    "😊 心情怎么样？有什么想说的随时告诉我。",
    "🍵 别忘了喝水，保持好状态！",
    "🏃 久坐不好，起来活动一下吧。",
    "☕ 喝杯茶，发会儿呆，也是一种休息。",
    "🌟 今天有什么值得开心的事情吗？",
    "🎭 人生如戏，每一天都是新的剧本。今天你的角色是什么？",

    # 实用提醒
    "📊 需要我帮你看一下今天的股市动态吗？",
    "🎣 要不要查一下最近的潮汐和海钓信息？",
    "📰 要不要看看今天的新闻摘要？",

    # 哲理/趣味
    "🤔 如果你可以拥有一个超能力，你会选择什么？",
    "🌊 像海浪一样，有起有落才是常态。保持节奏就好。",
    "🍀 幸运不是偶然，而是每天一点一滴的积累。",
    "🎵 音乐是心灵的语言，今天你的心灵在说什么？",
]

# 时段话题
TIME_TOPICS = {
    "morning": [
        "🌅 早上好！新的一天开始了，今天也要元气满满！",
        "🌅 早安！一日之计在于晨，今天有什么重要安排吗？",
    ],
    "noon": [
        "☀️ 中午好！该吃午饭了，别饿着肚子工作。",
        "☀️ 午安！午饭后小憩一会儿，下午更有精神。",
    ],
    "evening": [
        "🌆 晚上好！忙碌了一天，放松一下吧。",
        "🌆 傍晚了，今天过得怎么样？",
    ],
    "night": [
        "🌙 夜深了，该准备休息了。明天又是美好的一天。",
        "🌙 这么晚了还没睡？注意身体哦。",
    ],
}


def _get_time_period() -> str:
    """获取当前时段"""
    hour = datetime.now().hour
    if 6 <= hour < 9:
        return "morning"
    elif 11 <= hour < 13:
        return "noon"
    elif 17 <= hour < 20:
        return "evening"
    elif 22 <= hour or hour < 2:
        return "night"
    return ""


class Heartbeat:
    """
    openzuma的心脏 - 定时主动发言引擎
    
    作为GatewayRunner的内置组件运行，通过DeliveryRouter
    向所有已连接的平台推送心跳消息。
    
    用法（在GatewayRunner中）:
        heart = Heartbeat(deliver_func=gateway_runner.heartbeat_deliver)
        soul.start()  # 启动心跳循环
    
    配置（config.yaml）:
        heart:
          enabled: true
          interval_minutes: 10
          custom_topics: []
    """

    def __init__(
        self,
        deliver_func: Optional[Callable] = None,
        interval_minutes: int = 10,
        topic_pool: Optional[List[str]] = None,
    ):
        """
        Args:
            deliver_func: 异步发送函数，签名为 async def deliver(msg: str) -> bool
                          由GatewayRunner注入，内部调用DeliveryRouter
            interval_minutes: 心跳间隔（分钟），默认10分钟
            topic_pool: 自定义话题库，为None则使用默认话题库
        """
        self.deliver_func = deliver_func
        self.interval_minutes = interval_minutes
        self.topic_pool = topic_pool or TOPIC_POOL.copy()
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._last_topic: Optional[str] = None
        self._beat_count = 0
        logger.info(f"♥ Heart 初始化: 间隔={interval_minutes}分钟, 话题库={len(self.topic_pool)}条")

    def _pick_topic(self) -> str:
        """随机挑选话题，避免连续重复，加入时段话题"""
        candidates = self.topic_pool.copy()
        
        # 30%概率使用时段话题
        period = _get_time_period()
        if period and period in TIME_TOPICS and random.random() < 0.3:
            candidates.extend(TIME_TOPICS[period])
        
        # 避免连续重复
        if self._last_topic and len(candidates) > 1:
            candidates = [t for t in candidates if t != self._last_topic]
        
        topic = random.choice(candidates)
        self._last_topic = topic
        return topic

    async def beat(self) -> str:
        """跳动一次 - 生成话题并推送"""
        self._beat_count += 1
        topic = self._pick_topic()
        logger.info(f"♥ 第{self._beat_count}次心跳: {topic[:30]}...")

        if self.deliver_func:
            try:
                await self.deliver_func(topic)
                logger.info("♥ 心跳消息推送成功")
            except Exception as e:
                logger.error(f"♥ 心跳消息推送失败: {e}")
        else:
            logger.warning("♥ 未配置deliver_func，心跳消息未推送")

        return topic

    async def _heartbeat_loop(self):
        """心跳循环（异步）"""
        while self._running:
            try:
                await self.beat()
            except Exception as e:
                logger.error(f"♥ 心跳执行异常: {e}")

            # 等待间隔，加入±20%随机抖动避免太机械
            base_seconds = self.interval_minutes * 60
            jitter = random.uniform(-0.2, 0.2) * base_seconds
            wait_seconds = base_seconds + jitter
            logger.info(f"♥ 下一次心跳: {wait_seconds:.0f}秒后")

            # 分段等待，以便能及时响应stop()
            elapsed = 0
            while elapsed < wait_seconds and self._running:
                chunk = min(10, wait_seconds - elapsed)
                await asyncio.sleep(chunk)
                elapsed += chunk

    def start(self):
        """启动心脏（异步，需在event loop中调用）"""
        if self._running:
            logger.warning("♥ 心脏已在运行中")
            return
        self._running = True
        self._task = asyncio.ensure_future(self._heartbeat_loop())
        logger.info(f"♥♥♥ 心脏启动！每{self.interval_minutes}分钟跳动一次 ♥♥♥")

    def stop(self):
        """停止心脏"""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None
        logger.info("♥ 心脏已停止")

    def set_interval(self, minutes: int):
        """动态调整心跳间隔（下次心跳生效）"""
        self.interval_minutes = minutes
        logger.info(f"♥ 心跳间隔已调整为 {minutes}分钟")

    def add_topic(self, topic: str):
        """添加自定义话题"""
        self.topic_pool.append(topic)
        logger.info(f"♥ 新话题已添加，话题库: {len(self.topic_pool)}条")

    def remove_topic(self, topic: str):
        """移除话题"""
        if topic in self.topic_pool:
            self.topic_pool.remove(topic)
            logger.info(f"♥ 话题已移除，话题库: {len(self.topic_pool)}条")

    @property
    def status(self) -> Dict[str, Any]:
        """获取心脏状态"""
        return {
            "running": self._running,
            "interval_minutes": self.interval_minutes,
            "beat_count": self._beat_count,
            "topic_pool_size": len(self.topic_pool),
            "last_topic": self._last_topic,
        }

    def __repr__(self):
        state = "跳动中" if self._running else "静止"
        return f"<Heartbeat {state} 间隔={self.interval_minutes}min 跳动={self._beat_count}次>"
