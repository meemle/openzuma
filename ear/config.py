#!/usr/bin/env python3
"""
祖马耳朵模块 (EAR) - 配置文件
"""
import os

# ── 音频配置 ─────────────────────
ENERGY_THRESHOLD = 80     # 能量阈值（越小越灵敏，环境噪音大就调高）
SILENCE_DURATION = 2.0    # 静音多久算说完（秒）
MAX_RECORD = 15           # 最长录音秒数
MONITOR_SEC = 1           # 监听每段秒数（最小1）
SAMPLE_RATE = 16000       # 采样率
# ─────────────────────────────────

# ── API 配置 ─────────────────────
TMP_DIR = "/data/data/com.termux/files/usr/tmp"

# 自动从 .env 读取
API_KEY = ""
API_BASE = ""
_env_path = os.path.expanduser("~/.openzuma/.env")
if os.path.exists(_env_path):
    for line in open(_env_path).read().split("\n"):
        if line.startswith("XIAOMI_API_KEY="):
            API_KEY = line.split("=", 1)[1]
        if line.startswith("XIAOMI_BASE_URL="):
            API_BASE = line.split("=", 1)[1]
# ─────────────────────────────────

# ── 大模型配置 ───────────────────
STT_MODEL = "mimo-v2-omni"       # 语音识别模型
LLM_MODEL = "mimo-v2.5-pro"      # 对话大模型
LLM_MAX_TOKENS = 200             # 回复最大长度
LLM_TEMPERATURE = 0.7            # 回复创造性（0-1）
SYSTEM_PROMPT = "你是祖马，一个智能语音助手。用户通过语音和你对话，你需要简洁、自然地回复。回答要简短（1-2句话），适合语音播放。不要用markdown格式，不要用emoji。"
# ─────────────────────────────────

# ── TTS 配置 ─────────────────────
TTS_RATE = 1.3                   # 语速
TTS_LANG = "zh"                  # 语言
# ─────────────────────────────────

# ── 对话历史 ─────────────────────
MAX_HISTORY = 20                 # 保留最近N条消息
# ─────────────────────────────────
