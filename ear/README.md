# 祖马耳朵模块 (EAR)

语音交互模块，让祖马能"听"和"说"。

## 架构

```
麦克风录音 → 能量检测 → 小米AI语音识别 → 大模型回复 → TTS播放
```

## 文件结构

```
ear/
├── main.py              # 主程序
├── config.py            # 配置文件
├── start.sh             # 启动脚本
├── stop.sh              # 停止脚本
├── README.md            # 本文件
└── voice_assistant_v3_backup.py  # 旧版备份
```

## 使用方法

```bash
# 前台运行（可看日志，Ctrl+C退出）
python3 ~/openzuma/ear/main.py

# 后台运行
~/openzuma/ear/start.sh --bg

# 查看日志
tail -f /data/data/com.termux/files/usr/tmp/ear.log

# 停止
~/openzuma/ear/stop.sh
```

## 配置说明

编辑 `config.py` 可调整：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| ENERGY_THRESHOLD | 80 | 能量阈值，越小越灵敏 |
| SILENCE_DURATION | 2.0 | 静音多久算说完（秒） |
| MAX_RECORD | 15 | 最长录音秒数 |
| LLM_MODEL | mimo-v2.5-pro | 对话大模型 |
| LLM_MAX_TOKENS | 200 | 回复最大长度 |
| TTS_RATE | 1.3 | 语速 |

## 依赖

- Termux + Termux:API
- ffmpeg（音频格式转换）
- termux-microphone-record（录音）
- termux-tts-speak（语音播放）
- 小米 API（XIAOMI_API_KEY + XIAOMI_BASE_URL）

## 工作流程

1. **监听**：每秒录一段1秒音频，计算能量值
2. **检测**：能量 > 阈值 → 检测到说话
3. **录音**：持续录音，静音2秒自动停止
4. **识别**：ffmpeg转WAV → 小米mimo-v2-omni识别文字
5. **回复**：文字发给mimo-v2.5-pro大模型生成回复
6. **播放**：termux-tts-speak语音播放回复

## 注意事项

- 小米设备上 `termux-speech-to-text` 不可用（超级小爱不兼容）
- 语音识别使用小米mimo-v2-omni模型，需要联网
- 对话历史保留最近20条，重启后清空
