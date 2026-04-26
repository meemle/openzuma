# OpenZuma - 智能助手源码

牵来一匹始祖马，
潜心修炼御马术；
待到驾轻就熟时，
祖马一跃胜赤兔。

## 🚀 项目简介

OpenZuma  是一个功能强大的AI智能助手系统，支持：
- 多平台接入（微信、QQ、Telegram、Discord、Slack等）
- 丰富的工具集（终端、文件操作、网络搜索、代码执行等）
- 技能系统（可扩展的功能模块）
- 定时任务调度
- 多模型支持（Claude、GPT、DeepSeek等）
- 灵魂跳动引擎（Soul模块，AI自主主动交互）

基于学习借鉴Hermes Agent，希望能更加简化易用、智能进化与主动交互等。

## 📁 项目结构

```
openzuma/
├── run_agent.py          # AIAgent核心类
├── model_tools.py        # 工具编排
├── toolsets.py           # 工具集定义
├── cli.py                # 命令行界面
├── openzuma_state.py       # 会话数据库
├── agent/                # 代理内部模块
├── tools/                # 工具实现
├── gateway/              # 消息平台网关
├── soul/                 # 灵魂跳动引擎
│   ├── soulbeat.py       # SoulBeat核心 - 定时跳动与大模型话题生成
│   ├── integration.py    # Gateway集成 - 配置加载与消息推送
│   └── __init__.py       # 模块入口
├── ui-tui/               # 终端用户界面
├── tui_gateway/          # TUI JSON-RPC后端
├── acp_adapter/          # ACP服务器
├── cron/                 # 定时任务调度
├── tests/                # 测试套件
└── batch_runner.py       # 批量处理
```

## 🔧 快速开始

### 安装依赖
```bash
pip install -e .
```
### 查看OpenZuma版本
```bash
openzuma --version
```
### 运行OpenZuma
```bash
openzuma #即可进入交互式对话界面
```
### 配置
1. 复制 `config.yaml.example` 为 `~/.openzuma/config.yaml`
2. 配置API密钥和模型设置
3. 根据需要配置平台适配器

## 🌐 支持的平台

- **CLI**: 本地命令行界面
- **微信**: 通过clawbot对接
- **QQ**: 官方QQBot API
- **Telegram**: 官方Bot API
- **Discord**: Bot集成
- **Slack**: App集成
- **WhatsApp**: 通过WhatsApp Business API
- **Signal**: 通过signal-cli

## 🛠️ 工具集

OpenZuma 支持丰富的工具集：
- ✅ 终端命令执行
- ✅ 文件读写操作
- ✅ 网络搜索和内容提取
- ✅ 代码执行和调试
- ✅ 技能管理系统
- ✅ 定时任务调度
- ✅ 记忆和会话搜索
- ✅ 多代理协作

## 💗 灵魂跳动引擎（Soul模块）

Soul模块是OpenZuma的核心创新——让AI助手拥有"自主灵魂"，能够定时主动发言，不再只是被动等待用户提问。

### 核心特性
- **🧠 大模型实时话题生成**：废弃硬编码话题库，每次跳动由大模型结合实时数据生成全新话题，杜绝重复
- **📊 实时财经数据融合**：集成新浪财经API，自动获取A股、港股、美股、黄金、原油等市场行情，以投资专家视角输出有信息增量的分析
- **🌙 智能静默时段**：内置23:00-07:00静默模式，夜间不推送，不打扰休息
- **⏱️ 可配置跳动间隔**：通过`config.yaml`灵活设置间隔时长（默认30分钟）
- **🌐 全平台推送**：通过Gateway的DeliveryRouter，自动推送到微信、QQ、Telegram等任何已连接的平台

### 配置示例
```yaml
soul:
  enabled: true
  interval_minutes: 30
  model: google/gemini-2.0-flash-001    # 话题生成模型
  base_url: https://openrouter.ai/api/v1  # 可选
  api_key: sk-xxx                        # 可选，默认读取环境变量
```

### 架构
```
soul/
├── soulbeat.py       # SoulBeat核心引擎
│   ├── 定时跳动循环
│   ├── 静默时段判断
│   ├── 实时市场数据获取（Sina Finance）
│   └── 大模型话题生成与推送
├── integration.py    # Gateway集成层
│   ├── 配置加载（load_soul_config）
│   ├── SoulBeat实例创建（create_soulbeat）
│   └── 消息推送（soulbeat_deliver_via_gateway）
└── __init__.py
```

## 📚 文档

详细文档请参考：
- `AGENTS.md` - 开发指南
- `README_DEV.md` - 开发者文档
- `docs/` - 完整文档

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

致敬OpenClaw、Hermes、Evolver等等。

## 📞 联系

如有问题，请通过GitHub Issues反馈。:)