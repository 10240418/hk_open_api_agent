# ceramic-hopper-app

## 项目定位
基于当前代码库的扫描结果，这是一个**新初始化的 Flutter 移动应用项目**，遵循官方 `flutter create` 生成的默认模板结构，尚未包含业务逻辑与自定义功能。仓库名称 `ceramic-hopper-app` 与 GitHub 组织 `clutchtechnology` 关联，后续将作为特定应用（可能涉及“陶瓷”或“料斗”领域）的开发起点。

## 技术栈
- **语言**：Dart
- **框架**：Flutter（具体版本需从 `pubspec.yaml` 解析，当前未提供）
- **运行时**：Flutter Engine / Dart VM，目标平台待确认（默认支持 Android、iOS，可能扩展至 Web、桌面）
- **构建系统**：Flutter CLI（`flutter build`）
- **包管理**：Dart Pub（`pubspec.yaml`）
- **代码仓库**：`https://github.com/clutchtechnology/ceramic-hopper-app.git`，分支 `main`

## 目录和入口
项目遵循标准 Flutter 目录布局，核心源码位于 `lib/` 目录下：

- **应用入口**：`lib/main.dart` —— 应用程序启动点，现阶段为模板生成代码。
- **平台工程**：`android/`、`ios/`、`web/` 等平台入口目录（默认启用 Android 和 iOS，Web 需查看配置）。
- **依赖声明**：`pubspec.yaml` —— 定义项目元数据、依赖库、资源路径等。
- **其他辅助**：`test/` 目录存放单元测试与 widget 测试入口。
- 完整目录树可通过 `tree` 或 `ls -R` 补充，便于自动部署工具解析。

## 运行与构建
当前项目未提供自定义脚本，所有操作依赖 Flutter 标准工具链。

**开发运行**
```bash
flutter run          # 连接设备或模拟器后启动应用
flutter run -d <id>  # 指定目标设备
```

**依赖安装**
```bash
flutter pub get
```

**构建制品**
```bash
flutter build apk     # Android APK
flutter build ios     # iOS（需 macOS 环境）
flutter build web     # Web（若已启用）
flutter build windows # Windows（若已启用）
```

**测试**
```bash
flutter test
```

**其他常用命令**
```bash
flutter doctor        # 检查开发环境
flutter clean         # 清理构建缓存
```

## 配置和密钥
- 项目未检测到 `.env`、`*.env` 或环境变量配置文件。
- 模板代码中不存在数据库连接、第三方 API Key 等凭据引用。
- 环境变量名称（如后续引入）建议使用类似 `SUPABASE_URL`、`API_ENDPOINT` 等 key，但当前为空白。
- 密钥集中管理方式尚未确定，推荐在实际接入外部服务时使用 `flutter_dotenv` 或编译时注入（`--dart-define`）。

## 外部依赖
- 实际依赖包清单需从 `pubspec.yaml` 获取，当前扫描未解析其内容。
- 可通过下述命令导出完整依赖树：
  ```bash
  flutter pub deps
  ```
- 请将 `pubspec.yaml` 内容与 `pubspec.lock` 一并归档，以便精确复刻。

## 部署线索
- 移动端部署通常经由 App Store Connect（iOS）与 Google Play Console（Android），部署所需签名、证书、配置文件（`key.properties`, `ExportOptions.plist` 等）尚未生成或配置。
- Web 部署可将 `build/web` 产物托管至静态服务（如 GitHub Pages、Cloudflare Pages），但需先确认项目是否已启用 Web 平台。
- 尚无 CI/CD 配置（如 GitHub Actions、Codemagic、Fastlane），后续若需自动化构建请补充相应工作流文件。

## 复刻检查清单
该列表用于新环境搭建、Hermes/Codex 自动部署及运维人员手动复刻。

1. **克隆代码**
   ```bash
   git clone https://github.com/clutchtechnology/ceramic-hopper-app.git
   cd ceramic-hopper-app
   git checkout main
   ```
2. **安装 Flutter SDK**
   - 版本建议与项目锁定版本一致（查看 `pubspec.yaml` 中 `environment.sdk` 约束）。
   - 确保 `flutter doctor` 无关键报错。
3. **安装依赖**
   ```bash
   flutter pub get
   ```
4. **配置环境变量/密钥**
   - 当前无，如后续引入请从安全备份恢复 `.env` 或使用 `flutter run --dart-define=KEY=value`。
   - 若使用 Firebase 等服务，需下载对应平台的 `google-services.json`/`GoogleService-Info.plist` 并置于 `android/app/` 或 `ios/Runner/`。
5. **构建与测试**
   ```bash
   flutter test
   flutter build apk --debug       # 快速验证
   ```
6. **平台特定设置**
   - Android：配置 `key.properties` 签名文件（若发布）。
   - iOS：在 Xcode 中设置 Team、Bundle Identifier，管理证书。
   - Web：确认 `web/index.html` 等文件存在，如有自定义域名需适配。
7. **部署**
   - 按目标平台文档执行制品分发（应用商店上架、Web 部署等）。
   - 部署成功后更新 `inventory/projects.yaml` 及 `deployments/` 目录下的部署记录。

## 待补充信息
为达到可完整复刻和自动化部署的标准，以下内容需人工补充：

- **`pubspec.yaml` 解析**：列出所有依赖及版本，明确环境约束（Dart SDK、Flutter 版本）。
- **项目业务描述**：说明应用功能、目标用户、业务流程。
- **目标平台**：确认是否仅移动端，或包含 Web/Desktop。
- **外部服务集成**：
  - 是否使用后端 API、数据库、认证服务？若有，提供服务商、访问端点（非凭据）及通信协议。
  - 支付、通知等第三方 SDK 的初始化方式与所需标识符（如 APNs Key ID、Firebase Sender ID 等）。
- **CI/CD 方案**：若有自动构建需求，请补充 pipeline 配置（如 `.github/workflows/`）。
- **环境管理**：多环境（dev、staging、prod）的切换机制（若有）。
- **本地密钥备份路径**：提示的 `private/env-backup/` 是否已建立？如已建立，需确认访问授权。
