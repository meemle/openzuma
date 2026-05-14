#!/bin/bash
# 祖马耳朵模块 - 停止脚本

PID_FILE="/data/data/com.termux/files/usr/tmp/ear.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "🛑 停止耳朵模块 (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        # 同时停止可能残留的录音
        termux-microphone-record -q 2>/dev/null
        echo "✅ 耳朵模块已停止"
    else
        echo "⚠️  进程已不存在，清理PID文件"
        rm -f "$PID_FILE"
    fi
else
    echo "⚠️  未找到耳朵模块的PID文件"
    # 尝试通过进程名查找
    PID=$(pgrep -f "ear/main.py" 2>/dev/null)
    if [ -n "$PID" ]; then
        echo "🔍 找到进程 $PID，停止中..."
        kill "$PID" 2>/dev/null
        termux-microphone-record -q 2>/dev/null
        echo "✅ 已停止"
    fi
fi
