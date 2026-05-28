# iboard_flutter

## 项目定位

`iboard_flutter` 是一个基于 Flutter 框架开发的移动端应用，项目代号 / 名称推断为 **iBoard**。从 Git 提交历史中的 `“feat: Update app version to 1.2.15 and enhance live monitor widget”` 可看出，该应用具备**实时监测面板（Live Monitor）**功能，可能用于健康、运动或设备数据的实时展示与仪表盘控制。仓库公开托管于 GitHub（`The-Healthist/iboard_flutter`），定位偏向健康管理或状态监测的移动工具。

## 技术栈

| 层级 | 技术/工具 | 备注 |
|------|-----------|------|
| 框架 | Flutter (>=3.x) | 跨平台移动 UI 框架 |
| 语言 | Dart | 主要应用逻辑语言 |
| 辅助脚本 | Python *(检测到运行时)* | 具体用途待确认，可能用于本地工具、数据预处理或自动化；未扫描到 Python 脚本文件 |
| 平台目标 | iOS、Android | 项目包含 `ios/`、`android/` 标准目录 |

## 目录和入口

本项目遵循 Flutter 标准目录结构（未提供完整树，以下基于骨架和常识推断，需核对实际仓库）：

```
iboard_flutter/
├── android/                  # Android 原生工程
├── ios/                      # iOS 原生工程
├── lib/                      # Dart 应用主代码
│   └── main.dart             # 预期应用入口
├── test/                     # 单元/组件测试
├── assets/                   # 图片、字体等静态资源
├── pubspec.yaml              # 依赖与元数据声明
├── README.md                 # 项目简介
└── ...                       # 其他（如 analysis_options.yaml）
```

- **入口文件**：`lib/main.dart`（按 Flutter 惯例，需实际确认）
- **启动图资源说明**：`ios/Runner/Assets.xcassets/LaunchImage.imageset/` 提供了 iOS 启动图自定义方式（参照其中的 README）

## 运行与构建

### 本地开发环境准备

1. **安装 Flutter SDK**：确保已安装与 `pubspec.yaml` 声明的 Flutter 版本兼容的 SDK。
2. **获取依赖**：在项目根目录执行：
   ```bash
   flutter pub get
   ```
3. **运行应用**：
   ```bash
   # 连接设备或启动模拟器，执行：
   flutter run
   ```
   - 可通过 `-d` 参数指定目标设备。

### 构建产物

- **Android APK**：`flutter build apk` （或 `appbundle`）
- **iOS**：`flutter build ios` 并通过 Xcode 打包（需 macOS 及有效苹果开发者证书）

### Python 脚本

若仓库内存在 Python 脚本（未发现，但环境信息提及 Python 运行时），可能需要额外步骤（如安装 `requirements.txt` 依赖），详情待补充。

## 配置和密钥

- **环境变量文件**：仓库内未发现 `.env`、`.env.*` 或 `*.env` 模板文件。
- **配置方式**：当前判断无典型环境变量注入机制。若应用需连接后端 API 或第三方服务，相关 Base URL、令牌等可能硬编码在 Dart 源码中，或通过 Android/iOS 原生配置文件（如 `strings.xml`、`Info.plist`）管理。
- **密钥安全要求**：
  - **禁止**将真实密钥（API Key、Token、证书密码等）写入本文档。
  - 如需复刻，请查阅团队内部安全的凭据共享渠道（如私有备份目录 `private/env-backup/` 或凭据管理服务）。
  - 关键的配置项 Key 名称（如 `API_BASE_URL`、`WS_URL`）尚未识别，待补充。

## 外部依赖

主要依赖声明在 `pubspec.yaml` 中（具体列表缺失）。从功能线索推测可能包括：

- 图表/仪表盘库（`fl_chart`、`syncfusion_flutter_gauges` 等）
- WebSocket 或 HTTP 客户端（`web_socket_channel`、`dio`）
- 状态管理（如 `provider`、`riverpod`、`bloc`）
- 平台专属插件（`permission_handler`、`health`、`bluetooth` 等，视监测数据类型）

需由开发者从 `pubspec.yaml` 提取完整依赖并补充至此。

## 部署线索

- **代码仓库**：`https://github.com/The-Healthist/iboard_flutter.git`（公开）
- **当前分支**：`carousel_fix`（修复轮播相关）
- **最近提交**：`dd88c78`（版本 1.2.15，增强 live monitor widget）
- **部署方式**：推测为标准移动应用发布流程：
  1. **Android**：生成签名 APK/AAB，上传至 Google Play 或内部分发平台。
  2. **iOS**：通过 Xcode Archive 发布到 TestFlight / App Store（需 Apple Developer 账号及签名配置）。
- **CI/CD**：未在仓库中检测到 `fastlane/`、`.github/workflows/` 等自动化配置，部署脚本与流程需团队补充。
- **后端依赖**：若应用依赖后端服务，需提供服务地址及对应环境配置，目前无任何信息。

## 复刻检查清单

1. **克隆项目**：
   ```bash
   git clone https://github.com/The-Healthist/iboard_flutter.git
   cd iboard_flutter
   git checkout carousel_fix   # 按需切换分支
   ```
2. **Flutter 环境**：确认 `flutter doctor` 通过，SDK 版本与 `pubspec.yaml` 兼容。
3. **安装依赖**：`flutter pub get`
4. **恢复凭据/配置**：
   - 查找本地备份 `private/env-backup/` 或团队凭据管理工具，获取必需的 Key、后端地址等（不得写入本仓库明文）。
   - 若存在硬编码的敏感值，替换为外部配置注入方式。
5. **原生工程配置**：
   - **Android**：准备 `android/key.properties`（签名所需），或使用调试模式。
   - **iOS**：打开 `ios/Runner.xcworkspace` 设置 Team 和 Bundle ID。
6. **连接必要外设/服务**：如有蓝牙或受信网络，请确保设备已授权。
7. **运行验证**：`flutter run` 或使用 IDE 调试。
8. **生产打包**：
   - Android：`flutter build apk --release` （或 `appbundle`）
   - iOS：`flutter build ios` 然后在 Xcode 中 Archive 并分发。
9. **更新部署记录**：成功部署后，更新 `inventory/projects.yaml` 及 `deployments/` 下的对应记录。

## 待补充信息

- [ ] `pubspec.yaml` 中的完整依赖项列表
- [ ] Python 脚本的具体用途、触发方式及所需环境
- [ ] 后端 API 地址（如 REST/WebSocket 端点）
- [ ] 第三方服务商（如健康数据源、支付、邮件等）及其认证方式
- [ ] Android 签名证书指纹与分发渠道
- [ ] iOS 开发者团队与 Bundle ID
- [ ] 是否存在 CI/CD 流水线（如 GitHub Actions、Codemagic）
- [ ] 配置文件模板与需注入的环境变量键名
- [ ] 项目完整的目录结构快照（`tree` 输出）
- [ ] 是否有其他分支承担不同环境（如 `dev`、`staging`）
