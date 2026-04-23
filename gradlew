#!/usr/bin/env bash
# 备用gradlew脚本
# 如果wrapper不可用，使用系统gradle

set -e

# 检查wrapper
if [ -f "gradle/wrapper/gradle-wrapper.jar" ]; then
    # 使用wrapper
    exec java -jar gradle/wrapper/gradle-wrapper.jar "$@"
else
    # 使用系统gradle
    echo "⚠️  gradle-wrapper不可用，尝试系统gradle..."
    if command -v gradle &> /dev/null; then
        exec gradle "$@"
    else
        echo "❌ 错误: 未找到gradle"
        exit 1
    fi
fi
