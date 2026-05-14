#!/bin/bash
# 祖马耳朵模块 - 启动脚本
# 用法：
#   ./start.sh          # 前台运行
#   ./start.sh --bg     # 后台运行

EAR_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="/data/data/com.termux/files/usr/tmp/ear.log"
PID_FILE="/data/data/com.termux/files/usr/tmp/ear.pid"

if [ "$1" = "--bg" ]; then
    # 检查是否已在运行
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "⚠️  耳朵模块已在运行 (PID: $(cat "$PID_FILE"))"
        exit 1
    fi

    echo "🎙️  启动耳朵模块（后台模式）..."
    cd "$EAR_DIR"
    nohup python3 -u main.py > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "✅ 耳朵模块已启动 (PID: $!)"
    echo "📋 日志: tail -f $LOG_FILE"
    echo "🛑 停止: $EAR_DIR/stop.sh"
else
    echo "🎙️  启动耳朵模块（前台模式）..."
    cd "$EAR_DIR"
    python3 -u main.py
fi
