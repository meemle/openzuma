# OpenZuma - Termux 移动端 AI 智能助手

牵来一匹始祖马，
潜心修炼御马术；
待到驾轻就熟时，
祖马一跃胜赤兔。

## 🚀 项目简介

OpenZuma 是专为 **Termux (Android)** 环境优化的 AI 智能助手系统，一部手机就是一台完整的 AI 服务器。

核心能力：
- 微信平台接入（通过 clawbot 对接）
- 丰富的工具集（终端、文件操作、网络搜索、代码执行等）
- 技能系统（可扩展的功能模块）
- 定时任务调度
- 多模型支持（Claude、GPT、DeepSeek、GLM 等）
- 灵魂跳动引擎（Soul 模块，AI 自主主动交互）
- **语音交互（EAR 模块，录音→识别→大模型→语音回复）**

基于学习借鉴 Hermes Agent，希望能更加简化易用、智能进化与主动交互等。

## 📱 为什么选择 Termux？

- **零成本部署**：不需要云服务器，旧手机就能跑
- **24小时在线**：配合 termux-wake-lock + 电池优化豁免，持续运行
- **随时随地管理**：微信直接对话，不需要 SSH
- **省电省流量**：相比 Docker/云方案，资源消耗极低

## 📁 项目结构

```
openzuma/
├── run_agent.py          # AIAgent 核心类 - 对话主循环
├── model_tools.py        # 工具编排，函数调用分发
├── toolsets.py           # 工具集定义
├── toolset_distributions.py  # 工具集分发配置
├── cli.py                # 命令行界面（486KB，核心大文件）
├── openzuma_state.py     # 会话数据库（SQLite + FTS5 搜索）
├── openzuma_constants.py # 常量定义
├── openzuma_logging.py   # 日志系统
├── openzuma_time.py      # 时间工具
├── utils.py              # 通用工具函数
├── agent/                # Agent 内部模块
│   ├── prompt_builder.py     # 系统提示词组装
│   ├── context_compressor.py # 上下文自动压缩
│   ├── memory_manager.py     # 记忆管理
│   ├── skill_commands.py     # 技能斜杠命令
│   └── ...
├── tools/                # 工具实现（每文件一个工具）
│   ├── registry.py           # 工具注册中心
│   ├── terminal_tool.py      # 终端执行
│   ├── file_tools.py         # 文件操作
│   ├── web_tools.py          # 网络搜索
│   └── ...
├── ear/                  # 🎤 EAR 语音交互模块
│   ├── main.py            # 主程序（录音→STT→LLM→TTS）
│   ├── config.py          # 配置（阈值、模型、语速）
│   ├── start.sh           # 启动脚本（支持 --bg）
│   ├── stop.sh            # 停止脚本
│   └── README.md          # 模块说明
├── gateway/              # 消息平台网关
│   ├── run.py            # 网关主循环、消息分发
│   ├── config.py         # 网关配置
│   ├── session.py        # 会话持久化
│   ├── channel_directory.py  # 频道目录管理
│   └── platforms/        # 平台适配器（微信等）
├── soul/                 # 灵魂跳动引擎
│   ├── soulbeat.py       # SoulBeat 核心 - 定时跳动与大模型话题生成
│   ├── integration.py    # Gateway 集成 - 配置加载与消息推送
│   └── __init__.py
├── cron/                 # 定时任务调度
├── plugins/              # 插件系统（memory, context_engine 等）
├── skills/               # 内置技能
└── openzuma_cli/         # CLI 子命令和配置
```

## 🔧 快速开始（Termux）

### 1. 安装 Termux
从 [F-Droid](https://f-droid.org/packages/com.termux/) 下载安装 Termux。

### 2. 安装依赖
```bash
pkg install python git
pip install -e .
```

### 3. 配置
```bash
# 复制配置模板
cp cli-config.yaml.example ~/.openzuma/config.yaml

# 编辑配置，填入 API 密钥
nano ~/.openzuma/.env
```

### 4. 启动网关
```bash
openzuma gateway
```

### 5. 保持后台运行
```bash
# 防止手机休眠杀进程
termux-wake-lock

# 开机自启（需安装 Termux:Boot）
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/openzuma-gateway.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
termux-wake-lock
cd ~/openzuma
source venv/bin/activate
openzuma gateway >> ~/.openzuma/logs/boot.log 2>&1 &
EOF
chmod +x ~/.termux/boot/openzuma-gateway.sh
```

## 🌐 支持的平台

- **CLI**: 本地命令行界面
- **微信**: 通过 clawbot 对接（当前唯一在线平台）

> 其他平台（Telegram、Discord、Slack、QQ 等）已移除，聚焦微信生态深度优化。

## 🛠️ 工具集

- ✅ 终端命令执行
- ✅ 文件读写操作
- ✅ 网络搜索和内容提取
- ✅ 代码执行和调试
- ✅ 技能管理系统
- ✅ 定时任务调度
- ✅ 记忆和会话搜索
- ✅ 多代理协作（子代理委派）
- ✅ 文本转语音
- ✅ 图像分析

## 💗 灵魂跳动引擎（Soul 模块）v2

Soul 模块让 AI 拥有"自主灵魂"，定时主动发言，不再只是被动等待。

### 核心特性
- **🧠 大模型实时话题生成**：每次跳动由大模型结合实时数据生成全新话题
- **📊 实时财经数据融合**：集成新浪财经 API，A 股/港股/美股/黄金/原油行情
- **📰 国际热点新闻抓取**：RSS 源自动抓取（华尔街日报、环球时报、36氪、中国日报、虎嗅、钛媒体、第一财经）
- **🏢 机构调研动态**：东方财富机构调研数据，捕捉市场关注方向
- **🎯 巴菲特投资框架**：主动发言遵循8条投资决策约束（能力圈、安全边际、护城河等）
- **⚡ 话题优先级规则**：重大突发事件 > 市场信号 > 投资洞察
- **🌙 智能静默时段**：23:00-07:00 自动静默，不打扰休息
- **⏱️ 可配置间隔**：通过 `config.yaml` 设置（默认 30 分钟）
- **🔄 多层去重机制**：关键词/字符n-gram/词级n-gram 语义相似度检测 + MD5 hash 新闻去重，重启后历史不丢失
- **💾 持久化存储**：话题历史和新闻 hash 持久化到 `~/.openzuma/state/`，重启不丢记忆
- **📈 市场异动数据**：A股涨跌榜、港股、大宗商品异动，丰富话题素材

### 配置示例
```yaml
soul:
  enabled: true
  interval_minutes: 30
  model: glm-5.1
  api_key: your-api-key
  base_url: https://ark.cn-beijing.volces.com/api/coding/v3
```

### 数据源
| 类型 | 来源 | 内容 |
|------|------|------|
| 市场行情 | 新浪财经 | 上证、深证、创业板、恒生、道琼斯、纳斯达克、黄金、原油 |
| 机构调研 | 东方财富 | 被调研上市公司、机构数量、调研方式 |
|| 国际新闻 | RSS (7源) | 华尔街日报、环球时报、36氪、中国日报、虎嗅、钛媒体、第一财经 |
| 市场异动 | 东方财富 | A股涨跌榜、港股、大宗商品 |

## 🎤 EAR 语音交互模块

EAR 是 OpenZuma 的语音交互模块，让 AI 能"听"能"说"。

### 核心特性
- **🎤 麦克风录音**：通过 `termux-microphone-record` 录音
- **🧠 智能量检测**：只有检测到说话（能量>80）才触发识别，避免误触
- **📝 小米 STT**：使用 `mimo-v2-omni` 模型进行语音识别，无需 Google 服务
- **💬 大模型对话**：识别后自动调用大模型生成回复
- **🔊 语音回复**：通过 `termux-tts-speak` 将回复转为语音播放
- **🔄 连续监听**：识别后自动继续监听，支持连续对话
- **⚙️ 自动启动**：网关启动时耳朵模块自动跟随启动

### 技术方案
```
录音（5s WAV）→ ffmpeg 转码 → 小米 mimo-v2-omni 识别 → mimo-v2.5-pro 回复 → TTS 播放
```

### 配置（~/.openzuma/config.yaml）
```yaml
ear:
  enabled: true
  energy_threshold: 80    # 能量阈值，越低越灵敏
  stt_model: mimo-v2-omni # 语音识别模型
  llm_model: mimo-v2.5-pro # 对话模型
  tts_rate: 1.3           # 语速（0.5-2.0）
```

### 手动控制
```bash
# 启动（前台）
python3 ~/openzuma/ear/main.py

# 启动（后台）
~/openzuma/ear/start.sh --bg

# 停止
~/openzuma/ear/stop.sh
```

### 依赖
- `ffmpeg`：音频转码
- `termux-api`：麦克风录音 + TTS
- 小米 API Key（语音识别 + 大模型对话）

## 📦 已精简模块

本项目聚焦 Termux 移动端部署，已移除以下非必要模块：

| 移除模块 | 说明 |
|---------|------|
| `tests/` | 开发测试套件 |
| `website/` | 文档网站前端 |
| `ui-tui/` + `tui_gateway/` | Ink/React TUI 终端界面 |
| `acp_adapter/` + `acp_registry/` | VS Code/Zed/JetBrains IDE 集成 |
| `environments/` | RL 训练环境（Atropos） |
| `optional-skills/` | 可选技能包模板 |
| `web/` | Web 前端 |
| `Dockerfile` + `docker/` | Docker 构建 |
| `nix/` + `flake.*` | Nix 包管理 |
| `batch_runner.py` | 批量并行处理 |
| `rl_cli.py` | RL 训练命令行 |
| `trajectory_compressor.py` | 轨迹压缩（训练用） |
| `mini_swe_runner.py` | SWE-bench 运行器 |
| `mcp_serve.py` | MCP 服务器 |

节省约 26MB 磁盘空间，保留全部运行时必需模块。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

致敬 OpenClaw、Hermes、Evolver 等等。
