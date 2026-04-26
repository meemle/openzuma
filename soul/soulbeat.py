"""
Openzuma Soul - 灵魂跳动引擎 v2
定时主动发言，让openzuma有自主"灵魂跳动"

v2 改造重点：
- 废弃硬编码话题库，改用大模型实时生成话题
- 结合实时财经数据（Sina Finance API）+ 当前时间/季节
- 每次跳动生成全新内容，杜绝重复
- 静默时段（23:00-07:00）不推送
- 话题风格：投资专家视角，带信息增量，简洁不废话
"""

import random
import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Callable, Optional, List, Dict, Any

logger = logging.getLogger("openzuma.soul")

# ====== 静默时段配置 ======
SILENT_HOUR_START = 23  # 23:00开始静默
SILENT_HOUR_END = 7     # 07:00结束静默


def _is_silent_hours() -> bool:
    """判断当前是否在静默时段"""
    hour = datetime.now().hour
    if SILENT_HOUR_START <= hour or hour < SILENT_HOUR_END:
        return True
    return False


def _fetch_market_snapshot() -> str:
    """从Sina Finance API获取实时市场快照，作为话题生成的素材"""
    try:
        import requests
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'}
        
        codes = {
            '上证指数': 'sh000001',
            '深证成指': 'sz399001',
            '创业板': 'sz399006',
            '恒生指数': 'rt_hsi',
            '道琼斯': 'gb_dji',
            '纳斯达克': 'gb_ixic',
            '黄金': 'hf_GC',
            '原油': 'hf_CL',
        }
        
        code_str = ','.join(codes.values())
        r = requests.get(f'https://hq.sinajs.cn/list={code_str}', headers=headers, timeout=8)
        
        lines = r.text.strip().split('\n')
        snapshot_parts = []
        for line in lines:
            line = line.strip()
            if not line or '=' not in line:
                continue
            try:
                code_part = line.split('=')[0].split('_')[-1]
                data = line.split('"')[1]
                if not data:
                    continue
                fields = data.split(',')
                
                # 找到对应名称
                name = None
                for n, c in codes.items():
                    if c == code_part:
                        name = n
                        break
                if not name:
                    continue
                
                # 不同品种解析方式不同
                if code_part.startswith('hf_'):
                    # 国际期货: field[0]=现价, field[3]=昨结算
                    price = float(fields[0])
                    prev = float(fields[3]) if fields[3] else price
                    change_pct = ((price - prev) / prev) * 100 if prev else 0
                    snapshot_parts.append(f"{name}: {price} ({change_pct:+.2f}%)")
                elif code_part.startswith(('gb_', 'rt_')):
                    # 港美股: field[1]=现价, field[3]=昨收
                    price = float(fields[1])
                    prev = float(fields[3]) if fields[3] else price
                    change_pct = ((price - prev) / prev) * 100 if prev else 0
                    snapshot_parts.append(f"{name}: {price} ({change_pct:+.2f}%)")
                else:
                    # A股指数: field[1]=现价, field[2]=昨收
                    price = float(fields[1])
                    prev = float(fields[2]) if fields[2] else price
                    change_pct = ((price - prev) / prev) * 100 if prev else 0
                    snapshot_parts.append(f"{name}: {price:.2f} ({change_pct:+.2f}%)")
            except (IndexError, ValueError):
                continue
        
        return '；'.join(snapshot_parts) if snapshot_parts else "市场数据暂不可用"
    except Exception as e:
        logger.debug(f"获取市场快照失败: {e}")
        return "市场数据暂不可用"


def _generate_topic_via_llm(market_snapshot: str) -> Optional[str]:
    """调用本地大模型生成一个有深度的话题"""
    try:
        from openai import OpenAI
        
        # 读取配置获取API信息
        config_path = os.path.expanduser("~/.openzuma/config.yaml")
        api_key = os.environ.get("OPENAI_API_KEY", "")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        model = os.environ.get("SOUL_MODEL", "google/gemini-2.0-flash-001")
        
        # 尝试从config.yaml读取（优先soul段，其次model段）
        try:
            import yaml
            if os.path.exists(config_path):
                with open(config_path) as f:
                    cfg = yaml.safe_load(f) or {}
                # 先读soul专属配置
                soul_cfg = cfg.get("soul", {})
                # 再读model段配置作为兜底
                model_cfg = cfg.get("model", {})
                model = soul_cfg.get("model", model_cfg.get("default", model))
                api_key = soul_cfg.get("api_key") or model_cfg.get("api_key") or api_key
                base_url = soul_cfg.get("base_url") or model_cfg.get("base_url") or base_url
        except Exception:
            pass
        
        if not api_key:
            logger.warning("♥ SoulBeat: 无API key，无法调用大模型生成话题")
            return None
        
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        now = datetime.now()
        time_desc = f"现在是{now.year}年{now.month}月{now.day}日 {now.hour}:{now.minute:02d}，{['周一','周二','周三','周四','周五','周六','周日'][now.weekday()]}"
        
        prompt = f"""你是"祖马"，一个投资专家AI助手，正在给用户"三大爷"主动推送一条有价值的消息。

{time_desc}

当前市场快照：
{market_snapshot}

要求：
1. 基于上面的实时数据，给出你的个人投资判断或发现一个值得关注的市场信号
2. 也可以结合当前国际热点（地缘政治、央行政策、科技突破等）输出观点
3. 绝对不要说废话、套话、心灵鸡汤
4. 要有信息增量，让人看了想继续聊
5. 控制在2-3句话以内，简洁有力
6. 不要用emoji开头
7. 绝对不要重复之前说过的话题

直接输出内容，不要加任何前缀或标签。"""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.9,
        )
        
        topic = response.choices[0].message.content.strip()
        return topic if topic else None
        
    except Exception as e:
        logger.error(f"♥ LLM话题生成失败: {e}")
        return None


class SoulBeat:
    """
    openzuma的灵魂跳动 v2 - 大模型驱动的实时话题生成
    
    改造点：
    - 不再用硬编码话题库
    - 每次跳动调用大模型+实时市场数据生成全新话题
    - 静默时段(23:00-07:00)自动跳过
    - 记录历史话题避免重复
    """

    def __init__(
        self,
        deliver_func: Optional[Callable] = None,
        interval_minutes: int = 30,
        topic_pool: Optional[List[str]] = None,  # v2中保留参数但不再使用
    ):
        self.deliver_func = deliver_func
        self.interval_minutes = interval_minutes
        # v2: 话题历史记录，用于防重复
        self._topic_history: List[str] = []
        self._max_history = 50  # 保留最近50条话题历史
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._beat_count = 0
        logger.info(f"♥ SoulBeat v2 初始化: 间隔={interval_minutes}分钟, 大模型实时生成模式")

    def _pick_topic(self) -> Optional[str]:
        """v2: 通过大模型+实时数据生成话题"""
        # 检查静默时段
        if _is_silent_hours():
            logger.info("♥ 静默时段(23:00-07:00)，跳过本次跳动")
            return None
        
        # 获取市场快照
        market_snapshot = _fetch_market_snapshot()
        logger.info(f"♥ 市场快照: {market_snapshot[:80]}...")
        
        # 调用大模型生成话题
        topic = _generate_topic_via_llm(market_snapshot)
        
        if not topic:
            # LLM失败时，用市场数据拼一条简报
            if market_snapshot and market_snapshot != "市场数据暂不可用":
                topic = f"📊 市场速递：{market_snapshot}"
            else:
                logger.warning("♥ 话题生成失败且无市场数据，跳过本次跳动")
                return None
        
        # 检查是否与历史重复
        if topic in self._topic_history:
            logger.info("♥ 话题与历史重复，跳过本次跳动")
            return None
        
        # 记录到历史
        self._topic_history.append(topic)
        if len(self._topic_history) > self._max_history:
            self._topic_history = self._topic_history[-self._max_history:]
        
        return topic

    async def beat(self) -> Optional[str]:
        """跳动一次 - 生成话题并推送"""
        self._beat_count += 1
        topic = self._pick_topic()
        
        if not topic:
            logger.info(f"♥ 第{self._beat_count}次灵魂跳动: 无话题生成，跳过")
            return None
        
        logger.info(f"♥ 第{self._beat_count}次灵魂跳动: {topic[:50]}...")

        if self.deliver_func:
            try:
                await self.deliver_func(topic)
                logger.info("♥ 灵魂跳动消息推送成功")
            except Exception as e:
                logger.error(f"♥ 灵魂跳动消息推送失败: {e}")
        else:
            logger.warning("♥ 未配置deliver_func，灵魂跳动消息未推送")

        return topic

    async def _soulbeat_loop(self):
        """灵魂跳动循环（异步）"""
        while self._running:
            try:
                await self.beat()
            except Exception as e:
                logger.error(f"♥ 灵魂跳动执行异常: {e}")

            # 等待间隔，加入±20%随机抖动
            base_seconds = self.interval_minutes * 60
            jitter = random.uniform(-0.2, 0.2) * base_seconds
            wait_seconds = base_seconds + jitter
            
            # 如果等待后会在静默时段内醒来，延长到静默结束
            from datetime import timedelta
            wake_time = datetime.now() + timedelta(seconds=wait_seconds)
            if SILENT_HOUR_START <= wake_time.hour or wake_time.hour < SILENT_HOUR_END:
                # 计算到早上7点的秒数
                target = wake_time.replace(hour=SILENT_HOUR_END, minute=0, second=0, microsecond=0)
                if target <= wake_time:
                    target = target + timedelta(days=1)
                wait_seconds = (target - datetime.now()).total_seconds() + random.uniform(0, 300)
                logger.info(f"♥ 下一次跳动调整到静默时段结束后: {wait_seconds:.0f}秒后")

            logger.info(f"♥ 下一次灵魂跳动: {wait_seconds:.0f}秒后")

            # 分段等待，以便能及时响应stop()
            elapsed = 0
            while elapsed < wait_seconds and self._running:
                chunk = min(10, wait_seconds - elapsed)
                await asyncio.sleep(chunk)
                elapsed += chunk

    def start(self):
        """启动灵魂跳动"""
        if self._running:
            logger.warning("♥ 灵魂跳动已在运行中")
            return
        self._running = True
        self._task = asyncio.ensure_future(self._soulbeat_loop())
        logger.info(f"♥♥♥ 灵魂跳动v2启动！每{self.interval_minutes}分钟生成一次话题 ♥♥♥")

    def stop(self):
        """停止灵魂跳动"""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = None
        logger.info("♥ 灵魂跳动已停止")

    def set_interval(self, minutes: int):
        """动态调整跳动间隔"""
        self.interval_minutes = minutes
        logger.info(f"♥ 灵魂跳动间隔已调整为 {minutes}分钟")

    def add_topic(self, topic: str):
        """v2保留兼容接口，实际不再需要"""
        logger.info("♥ v2模式: 话题由大模型实时生成，add_topic已弃用")

    def remove_topic(self, topic: str):
        """v2保留兼容接口"""
        pass

    @property
    def status(self) -> Dict[str, Any]:
        """获取灵魂跳动状态"""
        return {
            "running": self._running,
            "version": "v2-llm-driven",
            "interval_minutes": self.interval_minutes,
            "beat_count": self._beat_count,
            "topic_history_size": len(self._topic_history),
            "last_topic": self._topic_history[-1] if self._topic_history else None,
        }

    def __repr__(self):
        state = "跳动中" if self._running else "静止"
        return f"<SoulBeat-v2 {state} 间隔={self.interval_minutes}min 跳动={self._beat_count}次>"
