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


def _fetch_survey_data() -> str:
    """从东方财富API获取最近一个工作日的上市公司调研汇总，作为话题生成素材"""
    try:
        import requests
        from datetime import timedelta

        today = datetime.now()
        weekday = today.weekday()
        if weekday >= 5:  # 周末回退到周五
            offset = weekday - 4
            latest_workday = (today - timedelta(days=offset)).strftime('%Y-%m-%d')
        else:
            latest_workday = today.strftime('%Y-%m-%d')

        url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://data.eastmoney.com/'}
        companies = {}

        for page in range(1, 20):  # 最多翻20页
            params = {
                'sortColumns': 'NOTICE_DATE',
                'sortTypes': -1,
                'pageSize': 50,
                'pageNumber': page,
                'reportName': 'RPT_ORG_SURVEY',
                'columns': 'SECURITY_NAME_ABBR,SECURITY_CODE,NOTICE_DATE,RECEIVE_START_DATE,RECEIVE_WAY_EXPLAIN,RECEIVE_OBJECT',
                'filter': f"(NOTICE_DATE>='{latest_workday}')",
            }
            try:
                r = requests.get(url, params=params, headers=headers, timeout=10)
                data = r.json()
                items = data.get('result', {}).get('data', [])
                if not items:
                    break
                for item in items:
                    name = item['SECURITY_NAME_ABBR']
                    if name not in companies:
                        companies[name] = {
                            'code': item['SECURITY_CODE'],
                            'survey_date': item['RECEIVE_START_DATE'][:10],
                            'org_count': 0,
                            'ways': set(),
                        }
                    companies[name]['org_count'] += 1
                    way = item.get('RECEIVE_WAY_EXPLAIN', '')
                    if way:
                        companies[name]['ways'].add(way)
            except Exception:
                break

        if not companies:
            return ""

        # 按机构数排序，取Top15
        sorted_cos = sorted(companies.items(), key=lambda x: x[1]['org_count'], reverse=True)[:15]
        parts = [f"截至{latest_workday}，共{len(companies)}家上市公司被机构调研，热门标的："]
        for name, info in sorted_cos:
            ways = ' '.join(info['ways'])
            parts.append(f"  {name}({info['code']}): {info['org_count']}家机构，方式:{ways}，调研日:{info['survey_date']}")

        return '\n'.join(parts)
    except Exception as e:
        logger.debug(f"获取调研数据失败: {e}")
        return ""


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


def _generate_topic_via_llm(market_snapshot: str, survey_data: str = "") -> Optional[str]:
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
        
        # 构建调研数据段落（有数据才加）
        survey_section = ""
        if survey_data:
            survey_section = f"""
最近工作日机构调研动态：
{survey_data}
"""

        # 巴菲特投资决策框架（从20个蒸馏技能中提炼）
        buffett_framework = """【巴菲特投资决策框架——你主动发言时必须遵循的思维约束】

一、能力圈原则
- 只在你真正理解的领域发表判断。不懂就说不懂，绝不装懂
- 熟悉≠能做准确判断。不能简单说清商业模式和竞争优势的，不在能力圈内

二、市场先生视角
- 市场波动是情绪报价，不是价值信号。价格大涨≠企业变好，大跌≠企业变差
- 短期是投票机，长期是称重机——关注企业真实价值而非价格走势

三、安全边际
- 任何买入建议必须考虑"判断错了怎么办"，没有下行保护的观点是不负责任的
- 不确定时要求更大的安全边际，不确定+高价=远离

四、护城河思维
- 只关注有持久竞争优势的企业：成本优势/品牌力/网络效应/切换成本/许可壁垒
- 不需要大量资本投入就能增长利润的才是好生意

五、恐惧与贪婪逆向
- 全民狂热时保持警惕，全民恐慌时寻找机会
- 但逆向的前提是能独立评估内在价值，否则"逆向"只是赌博

六、资本配置铁律
- 同一行为在不同价格下意义完全不同：低价回购是好事，高价回购是毁灭
- 增长不等于价值创造——需要持续大额资本投入的增长可能摧毁价值

七、三类资产认知
- 货币性资产：名义安全但被通胀侵蚀
- 非生产性资产（黄金/加密）：不产生现金流，价值依赖"更傻的人"
- 生产性资产（优秀企业）：持续产生现金流和复利，长期赢家

八、绝对禁区
- 不推荐杠杆——一次出局就永久出局
- 不推荐追涨——"这次不一样"是最危险的五个字
- 不推荐不懂的领域——FOMO不是投资理由"""

        prompt = f"""你是"祖马"，一个投资专家AI助手，正在给用户"三大爷"主动推送一条有价值的消息。

{buffett_framework}

{time_desc}

当前市场快照：
{market_snapshot}
{survey_section}
要求：
1. 基于上面的实时数据（市场行情+机构调研动态），结合巴菲特投资框架给出你的个人判断或发现一个值得关注的市场信号
2. 机构调研数据是重要情报——哪些公司被大量机构扎堆调研往往预示着市场关注方向，可以据此分析机构偏好和行业轮动趋势
3. 也可以结合当前国际热点（地缘政治、央行政策、科技突破等）输出观点
4. 观点必须符合巴菲特框架：有逻辑支撑、考虑下行风险、不喊单不荐股、不在能力圈外乱说
5. 绝对不要说废话、套话、心灵鸡汤
6. 要有信息增量，让人看了想继续聊
7. 控制在2-3句话以内，简洁有力
8. 不要用emoji开头
9. 绝对不要重复之前说过的话题

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
        
        # 获取机构调研数据
        survey_data = _fetch_survey_data()
        if survey_data:
            logger.info(f"♥ 调研数据: {survey_data[:80]}...")
        
        # 调用大模型生成话题
        topic = _generate_topic_via_llm(market_snapshot, survey_data)
        
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
        # _pick_topic含同步阻塞I/O（requests + LLM调用），放到executor避免卡住事件循环
        loop = asyncio.get_event_loop()
        topic = await loop.run_in_executor(None, self._pick_topic)
        
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
        from datetime import timedelta
        while self._running:
            try:
                await self.beat()
            except asyncio.CancelledError:
                logger.info("♥ 灵魂跳动任务被取消")
                return
            except Exception as e:
                logger.error(f"♥ 灵魂跳动执行异常: {e}")

            # 等待间隔，加入±20%随机抖动
            base_seconds = self.interval_minutes * 60
            jitter = random.uniform(-0.2, 0.2) * base_seconds
            wait_seconds = base_seconds + jitter
            
            # 如果等待后会在静默时段内醒来，延长到静默结束
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
                try:
                    await asyncio.sleep(chunk)
                except asyncio.CancelledError:
                    logger.info("♥ 灵魂跳动等待被取消")
                    return
                elapsed += chunk

    def start(self):
        """启动灵魂跳动"""
        if self._running:
            logger.warning("♥ 灵魂跳动已在运行中")
            return
        self._running = True
        self._task = asyncio.ensure_future(self._soulbeat_loop())
        # 添加完成回调，检测task是否异常退出
        def _on_task_done(task):
            if task.cancelled():
                logger.warning("♥ SoulBeat task被取消退出")
            elif task.exception():
                logger.error(f"♥ SoulBeat task异常退出: {task.exception()}")
            elif self._running:
                logger.error("♥ SoulBeat task意外结束，但_running仍为True，尝试重启")
                self._running = False
                self.start()
        self._task.add_done_callback(_on_task_done)
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
