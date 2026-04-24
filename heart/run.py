#!/usr/bin/env python3
"""
Openzuma Heart 启动脚本
让openzuma定时主动发言，推送到微信对话

用法:
  python -m heart.run                    # 默认每10分钟
  python -m heart.run --interval 5       # 每5分钟
  python -m heart.run --interval 15      # 每15分钟
"""

import argparse
import logging
import signal
import sys
import os

# 确保可以导入openzuma模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from heart.heartbeat import Heartbeat

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("heart.run")


def send_via_clawbot(message: str):
    """通过微信clawbot发送消息到对话"""
    try:
        # 方法1: 调用openzuma gateway的内部推送接口
        import requests
        gateway_url = os.environ.get("OPENZUMA_GATEWAY_URL", "http://127.0.0.1:8742")
        api_key = os.environ.get("OPENZUMA_API_KEY", "")

        # 尝试通过gateway的推送接口发送
        resp = requests.post(
            f"{gateway_url}/api/send",
            json={"message": message, "platform": "weixin"},
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
            timeout=10
        )
        if resp.status_code == 200:
            logger.info("♥ 消息已通过gateway推送")
            return

        # 方法2: 直接使用Hermes的send_message工具
        logger.warning(f"♥ Gateway推送返回 {resp.status_code}，尝试备用方式")
    except ImportError:
        logger.warning("♥ requests未安装，尝试备用发送方式")
    except Exception as e:
        logger.warning(f"♥ Gateway推送失败: {e}")

    # 备用方式: 写入消息队列文件，由cron任务拾取
    try:
        queue_dir = os.path.expanduser("~/.openzuma/heart_queue")
        os.makedirs(queue_dir, exist_ok=True)
        import time
        queue_file = os.path.join(queue_dir, f"msg_{int(time.time())}.txt")
        with open(queue_file, "w", encoding="utf-8") as f:
            f.write(message)
        logger.info(f"♥ 消息已写入队列: {queue_file}")
    except Exception as e:
        logger.error(f"♥ 备用发送方式也失败了: {e}")


def main():
    parser = argparse.ArgumentParser(description="Openzuma Heart - 心脏模块")
    parser.add_argument("--interval", type=int, default=10, help="心跳间隔（分钟），默认10")
    parser.add_argument("--dry-run", action="store_true", help="仅打印不发送，用于测试")
    args = parser.parse_args()

    send_func = lambda msg: print(f"[心跳] {msg}") if args.dry_run else send_via_clawbot

    heart = Heartbeat(send_func=send_func, interval_minutes=args.interval)

    def shutdown(signum, frame):
        logger.info("收到停止信号，心脏正在停止...")
        heart.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info(f"♥♥♥ Openzuma Heart 启动！间隔: {args.interval}分钟 ♥♥♥")
    if args.dry_run:
        logger.info("⚠️ 干运行模式，仅打印不发送")

    heart.start()

    # 主线程保持运行
    try:
        signal.pause()
    except AttributeError:
        # Android/Termux 没有 signal.pause()
        import time
        while True:
            time.sleep(60)


if __name__ == "__main__":
    main()
