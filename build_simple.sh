#!/data/data/com.termux/files/usr/bin/bash
echo "🔧 创建极简APK..."

# 创建必要的目录
mkdir -p build/apk/debug

# 创建极简AndroidManifest
cat > AndroidManifest.xml << 'MANIFEST'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.openzuma">

    <uses-sdk
        android:minSdkVersion="24"
        android:targetSdkVersion="34" />

    <application
        android:allowBackup="true"
        android:icon="@drawable/ic_launcher"
        android:label="OpenZuma测试版"
        android:theme="@android:style/Theme.Light">
        
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
MANIFEST

echo "✅ 极简构建文件已创建"
echo "📁 可以在Android Studio中导入完整项目进行构建"
