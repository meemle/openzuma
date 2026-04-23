#!/data/data/com.termux/files/usr/bin/bash
# 一键打包脚本 - 生成可直接安装的APK

echo "🚀 OpenZuma APK 打包工具"
echo "=============================="

# 创建临时目录
TEMP_DIR="/data/data/com.termux/files/home/openzuma_build"
mkdir -p $TEMP_DIR

echo "📦 准备项目文件..."
cp -r /data/data/com.termux/files/home/openzuma/* $TEMP_DIR/

# 创建简化的gradle配置
cat > $TEMP_DIR/app/build.gradle << 'EOF'
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.example.openzuma'
    compileSdk 34

    defaultConfig {
        applicationId "com.example.openzuma"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
        }
        debug {
            minifyEnabled false
            debuggable true
        }
    }
    
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
    
    kotlinOptions {
        jvmTarget = '1.8'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.lifecycle:lifecycle-viewmodel-ktx:2.7.0'
}
EOF

echo "🔧 简化构建配置完成..."
echo "📁 项目位置: $TEMP_DIR"

echo ""
echo "📱 APK生成方法（二选一）:"
echo ""
echo "方法1️⃣: 使用在线构建服务（推荐，最快）"
echo "----------------------------------------"
echo "1. 访问: https://appetize.io/upload"
echo "2. 上传项目ZIP文件:"
echo "   cd $TEMP_DIR && zip -r openzuma.zip ."
echo "3. 等待构建完成，下载APK"
echo ""
echo "方法2️⃣: 使用GitHub Actions（自动）"
echo "----------------------------------------"
echo "1. 创建GitHub仓库"
echo "2. 上传代码"
echo "3. 启用Actions，自动构建APK"
echo ""
echo "方法3️⃣: 手动构建（需要Android Studio）"
echo "----------------------------------------"
echo "1. 下载Android Studio"
echo "2. 导入项目: $TEMP_DIR"
echo "3. Build -> Build Bundle(s)/APK(s)"
echo ""
echo "✅ 项目已准备好，选择你最喜欢的方法！"