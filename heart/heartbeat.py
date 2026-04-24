"""
Openzuma Heart - 心跳引擎
定时主动发言，让openzuma有自主"心跳"
"""

import random
import time
import threading
import logging
from datetime import datetime

logger = logging.getLogger("openzuma.heart")

# 预设话题库 - 多样化的主动发言内容
TOPIC_POOL = [
    # 知识分享
    "💡 你知道吗？人一生中心脏大约会跳动25亿次，今天你的心脏已经跳了多少次了？",
    "💡 分享一个小知识：地球上的蚂蚁总重量和人类总重量大致相当。",
    "💡 有趣的事实：章鱼有三颗心脏，两颗负责鳃，一颗负责全身供血。",
    "💡 冷知识：蜂蜜永远不会变质，考古学家在埃及金字塔中发现了3000年前的蜂蜜，仍然可以食用。",
    "💡 你知道吗？宇宙中的恒星数量比地球上所有沙滩的沙粒总数还多。",
    "💡 分享：光从太阳到达地球需要大约8分20秒，所以我们看到的阳光是8分钟前的。",
    "💡 有趣的事实：一朵云的平均重量是50万公斤，相当于100头大象。",
    "💡 冷知识：香蕉实际上是浆果，而草莓不是。",
    "💡 你知道吗？人脑产生的电量足以点亮一个小灯泡。",
    "💡 分享：金星上的一天比金星上的一年还长。",

    # 闲聊互动
    "🌤 今天天气怎么样？有没有出去走走？",
    "☕ 休息一下吧，站起来活动活动，喝杯水。",
    "🎵 最近有没有听到什么好听的歌？可以推荐给我。",
    "📖 有什么有趣的事情想聊聊吗？",
    "🌙 已经很晚了，注意休息哦。",
    "🎯 今天有什么计划或者目标吗？",
    "😊 心情怎么样？有什么想说的随时告诉我。",
    "🍵 别忘了喝水，保持好状态！",
    "🏃 久坐不好，起来活动一下吧。",
    "🌟 今天有什么值得开心的事情吗？",

    # 实用提醒
    "📊 需要我帮你看一下今天的股市动态吗？",
    "🎣 要不要查一下曹妃甸最近的潮汐和海钓信息？",
    "📋 有什么待办事项需要提醒你的吗？",
    "🔔 提醒：定期保存你的工作成果，避免意外丢失。",
    "📰 要不要看看今天的新闻摘要？",

    # 哲理/趣味
    "🤔 如果你可以拥有一个超能力，你会选择什么？",
    "🧩 思考题：如果机器能思考，它会不会也无聊？",
    "🎭 人生如戏，每一天都是新的剧本。今天你的角色是什么？",
    "🌊 像海浪一样，有起有落才是常态。保持节奏就好。",
    "🍀 幸运不是偶然，而是每天一点一滴的积累。",
]

# 特殊时段话题
MORNING_TOPICS = [
    "🌅 早上好！新的一天开始了，今天也要元气满满！",
    "🌅 早安！一日之计在于晨，今天有什么重要安排吗？",
    "🌅 早上好！记得吃早餐，美好的一天从早餐开始。",
]

NOON_TOPICS = [
    "☀️ 中午好！该吃午饭了，别饿着肚子工作。",
    "☀️ 午安！午饭后小憩一会儿，下午更有精神。",
]

EVENING_TOPICS = [
    "🌆 晚上好！忙碌了一天，放松一下吧。",
    "🌆 傍晚了，今天过得怎么样？",
]

NIGHT_TOPICS = [
    "🌙 夜深了，该准备休息了。明天又是美好的一天。",
    "🌙 这么晚了还没睡？注意身体哦，早睡早起精神好。",
]


class Heartbeat:
    """openzuma的心脏 - 定时主动发言引擎"""

    def __init__(self, send_func=None, interval_minutes=10, topic_pool=None):
        """
        Args:
            send_func: 发送消息的函数，接收一个字符串参数
            interval_minutes: 心跳间隔（分钟），默认10分钟
            topic_pool: 自定义话题库，为None则使用默认话题库
        """
        self.send_func = send_func
        self.interval_minutes = interval_minutes
        self.topic_pool = topic_pool or TOPIC_POOL.copy()
        self._timer = None
        self._running = False
        self._last_topic = None
        self._beat_count = 0
        logger.info(f"♥ Heart 初始化完成，间隔: {interval_minutes}分钟，话题库: {len(self.topic_pool)}条")

    def _get_time_aware_topics(self):
        """根据当前时段获取额外话题"""
        hour = datetime.now().hour
        if 6 <= hour < 9:
            return MORNING_TOPICS
        elif 11 <= hour < 13:
            return NOON_TOPICS
        elif 17 <= hour < 20:
            return EVENING_TOPICS
        elif 22 <= hour or hour < 2:
            return NIGHT_TOPICS
        return []

    def _pick_topic(self):
        """随机挑选一个话题，避免连续重复"""
        candidates = self.topic_pool + self._get_time_aware_topics()
        if self._last_topic and len(candidates) > 1:
            candidates = [t for t in candidates if t != self._last_topic]
        topic = random.choice(candidates)
        self._last_topic = topic
        return topic

    def beat(self):
        """跳动一次 - 发送一条主动消息"""
        self._beat_count += 1
        topic = self._pick_topic()
        logger.info(f"♥ 第{self._beat_count}次心跳: {topic[:30]}...")

        if self.send_func:
            try:
                self.send_func(topic)
                logger.info("♥ 心跳消息发送成功")
            except Exception as e:
                logger.error(f"♥ 心跳消息发送失败: {e}")
        else:
            logger.warning("♥ 未配置send_func，心跳消息未发送")

        return topic

    def _heartbeat_loop(self):
        """心跳循环"""
        if not self._running:
            return
        self.beat()
        # 安排下一次心跳
        self._schedule_next()

    def _schedule_next(self):
        """安排下一次心跳"""
        if not self._running:
            return
        interval_seconds = self.interval_minutes * 60
        # 加入±20%的随机抖动，避免太机械
        jitter = random.uniform(-0.2, 0.2) * interval_seconds
        next_interval = interval_seconds + jitter
        logger.info(f"♥ 下一次心跳将在 {next_interval:.0f}秒后 ({self.interval_minutes}分钟±抖动)")
        self._timer = threading.Timer(next_interval, self._heartbeat_loop)
        self._timer.daemon = True
        self._timer.start()

    def start(self):
        """启动心脏"""
        if self._running:
            logger.warning("♥ 心脏已在运行中")
            return
        self._running = True
        logger.info(f"♥♥♥ 心脏启动！每{self.interval_minutes}分钟跳动一次 ♥♥♥")
        self._schedule_next()

    def stop(self):
        """停止心脏"""
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None
        logger.info("♥ 心脏已停止")

    def set_interval(self, minutes):
        """动态调整心跳间隔"""
        self.interval_minutes = minutes
        logger.info(f"♥ 心跳间隔已调整为 {minutes}分钟")
        # 如果正在运行，重新安排下一次心跳
        if self._running:
            if self._timer:
                self._timer.cancel()
            self._schedule_next()

    def add_topic(self, topic):
        """添加自定义话题"""
        self.topic_pool.append(topic)
        logger.info(f"♥ 新话题已添加，当前话题库: {len(self.topic_pool)}条")

    def remove_topic(self, topic):
        """移除话题"""
        if topic in self.topic_pool:
            self.topic_pool.remove(topic)
            logger.info(f"♥ 话题已移除，当前话题库: {len(self.topic_pool)}条")

    @property
    def status(self):
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
