#!/bin/bash
# 使用系统Gradle构建

echo "使用系统Gradle构建..."

# 设置环境
export GRADLE_HOME=/usr/share/gradle
export PATH=$GRADLE_HOME/bin:$PATH

if command -v gradle &> /dev/null; then
    echo "✅ 系统Gradle可用"
    gradle --version | head -5
    
    # 直接构建
    gradle clean assembleDebug
else
    echo "❌ 系统Gradle不可用"
    exit 1
fi
