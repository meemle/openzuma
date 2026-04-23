# OpenZuma

一个完整的Android应用项目，可以在安卓手机上部署运行。

## 项目简介

OpenZuma 是一个功能丰富的开源Android应用，采用现代化的Android开发技术栈，包括Kotlin、MVVM架构、Jetpack组件等。项目设计注重代码质量、可维护性和用户体验。

## 项目特点

- 🚀 **现代化架构**：采用MVVM架构，使用Kotlin开发
- 🎨 **Material Design 3**：遵循最新的Material Design设计规范
- 🔧 **多模块化**：清晰的项目结构，便于维护和扩展
- 📱 **多屏幕适配**：支持各种屏幕尺寸和分辨率
- 🔐 **权限管理**：完善的权限请求和处理机制
- 🌐 **网络请求**：集成Retrofit + OkHttp进行网络通信
- 💾 **本地存储**：使用Room数据库进行数据持久化
- 🖼️ **图片加载**：集成Glide进行图片加载和缓存

## 技术栈

- **开发语言**: Kotlin 100%
- **架构模式**: MVVM (Model-View-ViewModel)
- **UI框架**: Jetpack Compose + XML布局
- **网络层**: Retrofit2 + OkHttp3 + Gson
- **数据库**: Room
- **图片加载**: Glide
- **依赖注入**: Hilt
- **导航**: Navigation Component
- **异步处理**: Coroutines + Flow
- **测试框架**: JUnit4 + Espresso

## 快速开始

### 环境要求

- Android Studio 2022.3.1 或更高版本
- Java 17 或 Kotlin 1.9.20
- Android SDK 34
- Gradle 8.2

### 构建步骤

1. **克隆项目**
   ```bash
   git clone https://gitee.com/your-username/openzuma.git
   cd openzuma
   ```

2. **使用Android Studio打开**
   - 打开Android Studio
   - 选择 "Open an Existing Project"
   - 选择项目目录

3. **构建项目**
   - 等待Gradle同步完成
   - 点击 "Build" → "Make Project"

4. **运行应用**
   - 连接Android设备或启动模拟器
   - 点击 "Run" → "Run 'app'"
   - 选择目标设备

### 构建APK

**调试版本:**
```bash
./gradlew assembleDebug
```
APK位置: `app/build/outputs/apk/debug/app-debug.apk`

**发布版本:**
```bash
./gradlew assembleRelease
```
APK位置: `app/build/outputs/apk/release/app-release.apk`

## 项目结构

```
openzuma/
├── app/                                 # 主应用模块
│   ├── src/main/
│   │   ├── java/com/example/openzuma/   # Kotlin源代码
│   │   │   ├── MainActivity.kt          # 主活动
│   │   │   ├── ui/                      # 界面组件
│   │   │   ├── viewmodel/               # ViewModel层
│   │   │   ├── repository/              # 数据仓库层
│   │   │   ├── database/                # 数据库层
│   │   │   ├── network/                 # 网络层
│   │   │   └── utils/                   # 工具类
│   │   ├── res/                         # 资源文件
│   │   │   ├── layout/                  # 布局文件
│   │   │   ├── drawable/                # 图片资源
│   │   │   ├── values/                  # 字符串、颜色等
│   │   │   └── xml/                     # XML配置文件
│   │   └── AndroidManifest.xml          # 清单文件
│   └── build.gradle                     # 模块配置
├── gradle/                              # Gradle包装器
├── build.gradle                         # 项目配置
├── settings.gradle                      # 项目设置
├── gradle.properties                    # Gradle属性
├── LICENSE                              # 许可证文件
└── README.md                            # 项目说明
```

## 功能模块

### 1. 核心功能
- ✅ 用户认证（登录/注册）
- ✅ 个人资料管理
- ✅ 设置页面
- ✅ 消息通知

### 2. 媒体功能
- ✅ 拍照和录像
- ✅ 图片选择
- ✅ 文件上传
- ✅ 多媒体播放

### 3. 工具功能
- ✅ 二维码扫描
- ✅ 位置服务
- ✅ 天气查询
- ✅ 计算器

### 4. 社交功能
- ✅ 好友管理
- ✅ 消息聊天
- ✅ 动态分享
- ✅ 评论点赞

## 配置说明

### 1. 修改应用信息
在 `app/build.gradle` 中修改：
```gradle
defaultConfig {
    applicationId "com.example.openzuma"  # 包名
    versionCode 1                         # 版本号
    versionName "1.0"                     # 版本名称
}
```

### 2. 修改API配置
创建 `app/src/main/res/values/config.xml` 并添加：
```xml
<string name="api_base_url">https://api.example.com</string>
<string name="api_key">your_api_key_here</string>
```

### 3. 修改应用图标
替换 `app/src/main/res/mipmap-*/ic_launcher.png` 文件

## 开发指南

### 代码规范
- 使用Kotlin优先
- 遵循Google的Kotlin风格指南
- 使用有意义的变量名和函数名
- 添加必要的注释
- 编写单元测试

### 添加新功能
1. 在 `ui` 包下创建新的功能模块
2. 添加对应的布局文件
3. 创建ViewModel处理业务逻辑
4. 在导航图中配置路由
5. 添加单元测试

## 部署到Gitee

### 1. 初始化Git仓库
```bash
cd openzuma
git init
git add .
git commit -m "Initial commit: OpenZuma Android project"
```

### 2. 推送到Gitee
```bash
# 添加远程仓库（替换为你的Gitee用户名）
git remote add origin https://gitee.com/your-username/openzuma.git

# 推送到主分支
git push -u origin master
```

### 3. 在Gitee上创建项目
1. 登录Gitee.com
2. 点击右上角"+"号，选择"新建仓库"
3. 填写仓库信息：
   - 仓库名称：openzuma
   - 仓库介绍：一个功能丰富的开源Android应用
   - 选择语言：Kotlin
   - 添加许可证：MIT License
4. 点击"创建"

## 常见问题

### Q: 构建失败，提示SDK版本不匹配
A: 检查并修改 `app/build.gradle` 中的 `compileSdk` 和 `targetSdk` 版本

### Q: 运行时权限被拒绝
A: 确保在 `AndroidManifest.xml` 中声明了所需权限，并在运行时请求权限

### Q: 网络请求失败
A: 检查网络连接，确认API地址正确，并添加网络权限

### Q: 数据库迁移失败
A: 增加数据库版本号，并实现Migration策略

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 作者：[你的名字]
- 邮箱：[你的邮箱]
- Gitee: [你的Gitee主页]

## 更新日志

### v1.0.0 (2026-04-23)
- ✅ 项目初始化
- ✅ 基础架构搭建
- ✅ 核心功能实现
- ✅ 首次发布