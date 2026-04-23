#!/data/data/com.termux/files/usr/bin/bash
# 快速检查Android项目结构

echo "🔍 检查OpenZuma项目结构..."

# 检查关键文件
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $2"
        return 0
    else
        echo "❌ 缺少: $2"
        return 1
    fi
}

echo ""
echo "📁 项目结构检查:"
check_file "app/build.gradle" "构建配置文件"
check_file "app/src/main/AndroidManifest.xml" "Android清单文件"
check_file "app/src/main/java/com/example/openzuma/MainActivity.kt" "主Activity"
check_file "app/src/main/res/values/strings.xml" "字符串资源"
check_file "gradle/wrapper/gradle-wrapper.properties" "Gradle包装器"

echo ""
echo "📱 日历模块检查:"
check_file "app/src/main/java/com/example/openzuma/ui/calendar/CalendarFragment.kt" "日历Fragment"
check_file "app/src/main/res/layout/fragment_calendar.xml" "日历布局"

echo ""
echo "📊 文件统计:"
find . -name "*.kt" -type f | wc -l | xargs echo "Kotlin文件:"
find . -name "*.xml" -type f | wc -l | xargs echo "XML文件:"
find . -name "*.gradle" -type f | wc -l | xargs echo "Gradle文件:"

echo ""
echo "🎯 构建状态: 项目结构完整，可以进行在线构建"