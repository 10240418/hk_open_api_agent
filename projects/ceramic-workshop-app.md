# ceramic-workshop-app

## 项目定位
陶瓷工作坊辅助移动应用（Flutter 跨平台实现），目标平台包含 iOS 与 Android。扫描未发现服务端代码，Python 运行时可能用于本地工具脚本或数据预处理，待确认是否为独立后端服务。

## 技术栈
- **主语言**：Dart（Flutter）
- **辅助/工具语言**：Python（运行时已配置，但未检出明确的项目脚本，需进一步确认用途）
- **UI 框架**：Flutter
- **平台**：iOS、Android
- **包管理与构建**：pubspec.yaml（Dart 侧）；未检测到 `requirements.txt` 或 `Pipfile`（Python 侧）

## 目录和入口
- **入口文件**（惯例）：`lib/main.dart`（Dart 应用启动点）
- **依赖声明**：`pubspec.yaml`
- **iOS 工程**：`ios/Runner.xcworkspace`，包含启动图等资源（`ios/Runner/Assets.xcassets/LaunchImage.imageset/`）
- **Android 工程**：预期在 `android/` 目录下（标准 Flutter 项目结构）
- **Python 相关代码**：未在源码扫描中捕获相关文件夹或脚本，建议检查仓库根目录、`tools/`、`scripts/` 等位置

## 运行与构建
- **准备工作**
  - 安装 Flutter SDK（参考 [Flutter 官方安装指引](https://docs.flutter.dev/get-started/install)）
  - 安装 Dart 插件（随 Flutter SDK）
  - 如使用 Python 工具，请准备 Python 3 环境（版本待补充）
- **获取依赖**
  ```bash
  flutter pub get
  ```
- **开发运行**
  ```bash
  # 连接设备或启动模拟器后
  flutter run
  ```
  - 目标平台可通过 `-d` 参数指定，例如 `flutter run -d <device_id>`
- **构建生产包**
  - iOS：`flutter build ios`（进一步打包需 Xcode，签名配置需 Apple Developer 账号）
  - Android：`flutter build apk` 或 `flutter build appbundle`
- **注意**：项目未包含 `package.json`，无 npm 相关构建流程；Python 侧无明确运行入口，如有需求请调查是否存在 Fastlane、辅助脚本或 Django/Flask 后端

## 配置和密钥
- **环境变量文件**：未检测到 `.env`、`.env.*`、`*.env` 文件。
- **可能需要的密钥种类**（根据应用特征推测，请核实）：
  - 若接入后端 API，可能需要 `API_BASE_URL`、`AUTH_TOKEN` 等
  - 若使用第三方服务（如地图、支付、推送），可能涉及 `GOOGLE_MAPS_API_KEY`、`STRIPE_PUBLISHABLE_KEY` 等
- **管理建议**：
  - 所有密钥和配置不应硬编码在源码中，可使用 Flutter 的 `--dart-define` 或专用 env 包（如 `flutter_dotenv`）在构建时注入
  - 敏感凭证必须存放于内部密钥管理服务（Vault/Secrets Manager），禁止提交至仓库
  - 目前未检出任何环境变量 key 名称，待后续开发或逆向确认后补充到本文档

## 外部依赖
- **Flutter 包**：具体列表见 `pubspec.yaml` 中的 `dependencies` 节。常见可能包括网络、状态管理、UI 组件等。
- **本机平台能力**：依据 `pubspec.yaml` 和源码引用，可能依赖相机、定位、通知等原生插件（需检查 `ios/Runner/Info.plist` 中权限描述）
- **Python 依赖**：未检出依赖文件，若项目包含 Python 工具，请补充 `requirements.txt` 或 `pyproject.toml` 并列出关键库
- **外部服务**：无法从现有信号推断，需补充（例如后端 API 地址、数据库、认证服务、存储桶等）

## 部署线索
- **移动端部署**：本应用为 Flutter 前端，无独立服务端，部署即为发布到应用商店
  - **iOS App Store**：需 Xcode 构建归档，上传至 App Store Connect，配置证书与描述文件
  - **Google Play**：需生成签名的 App Bundle 或 APK，上传至 Google Play Console
- **可能存在后端/辅助服务**：扫描发现 Python 运行时，但无服务端代码线索，如存在后端，需补充：
  - 后端项目地址或所在目录
  - 部署方式（容器、云函数、VPS 等）
  - 暴露端口、域名、健康检查端点
- **缺省**：当前无任何运行时端口、域名、TLS 配置信息

## 复刻检查清单
1. 克隆仓库并切换到 `main` 分支（注意工作区有未提交改动，建议先 `git stash` 或提交）
2. 安装 Flutter 并确认 `flutter doctor` 无严重报错
3. 执行 `flutter pub get` 拉取 Dart 依赖
4. 检查是否存在 Python 工具：
   - 查找 `requirements.txt`、`setup.py`、`pyproject.toml` 等
   - 如有，创建虚拟环境并安装依赖
5. 按需补齐环境变量：
   - 若使用 `flutter_dotenv`，在项目根创建 `.env` 文件（模板需从开发者或文档获取）
   - 若使用 `--dart-define`，整理所需变量名并将值注入构建命令
6. 在模拟器或真机上运行 `flutter run` 验证基础功能
7. 配置 iOS/Android 的证书与签名，进行发布构建测试
8. 如果依赖后端服务，请确保后端已部署并能连通，并在应用配置中指向正确的地址

## 待补充信息
- Python 运行时的具体用途及对应脚本位置
- 是否有后端服务，若有请提供接口契约、域名、认证方式
- 应用所需的环境变量 key 列表及其作用
- 用到的第三方 SDK（如 Firebase、微信/支付宝支付、推送服务）及配置方式
- 完整的应用功能描述与产品文档链接
- iOS 的 Bundle ID、Android 的 Application ID
- 签名证书管理策略（使用 Fastlane Match 还是手动管理）
- 项目未提交的本地改动内容，评估是否需要合并
