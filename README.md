# Hermes Agent - 智能助手源码

这是完整的 Hermes Agent 智能助手系统源码。

## 🚀 项目简介

Hermes Agent 是一个功能强大的AI智能助手系统，支持：
- 多平台接入（微信、Telegram、Discord、Slack等）
- 丰富的工具集（终端、文件操作、网络搜索、代码执行等）
- 技能系统（可扩展的功能模块）
- 定时任务调度
- 多模型支持（Claude、GPT、DeepSeek等）

## 📁 项目结构

```
hermes-agent/
├── run_agent.py          # AIAgent核心类
├── model_tools.py        # 工具编排
├── toolsets.py           # 工具集定义
├── cli.py                # 命令行界面
├── hermes_state.py       # 会话数据库
├── agent/                # 代理内部模块
├── tools/                # 工具实现
├── gateway/              # 消息平台网关
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
pip install -r requirements.txt
```

### 运行CLI版本
```bash
python -m hermes_agent.cli.main
```

### 配置
1. 复制 `config.yaml.example` 为 `~/.hermes/config.yaml`
2. 配置API密钥和模型设置
3. 根据需要配置平台适配器

## 🌐 支持的平台

- **CLI**: 本地命令行界面
- **微信**: 通过clawbot对接
- **Telegram**: 官方Bot API
- **Discord**: Bot集成
- **Slack**: App集成
- **WhatsApp**: 通过WhatsApp Business API
- **Signal**: 通过signal-cli

## 🛠️ 工具集

Hermes 支持丰富的工具集：
- ✅ 终端命令执行
- ✅ 文件读写操作
- ✅ 网络搜索和内容提取
- ✅ 代码执行和调试
- ✅ 技能管理系统
- ✅ 定时任务调度
- ✅ 记忆和会话搜索
- ✅ 多代理协作

## 📚 文档

详细文档请参考：
- `AGENTS.md` - 开发指南
- `README_DEV.md` - 开发者文档
- `docs/` - 完整文档

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系

如有问题，请通过GitHub Issues反馈。