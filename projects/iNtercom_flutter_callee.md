# iNtercom_flutter_callee 工程文档

## 项目定位

基于腾讯云 TRTC 的智能门禁通话系统，包含：

- Flutter 实现的住户端应用（被叫端 callee），提供音视频通话能力；
- Web 端发起通话演示程序（门禁设备端），纯前端静态页面；
- TRTC Web SDK 包装库 `TrtcWrapper`，用于 Flutter Web 平台集成。

项目以 TRTC Flutter SDK 示例代码为基础进行定制，面向门禁/可视对讲场景。

## 技术栈

- 移动端：Flutter (Dart)，集成 `tencent_rtc_sdk` (trtc_cloud)
- Web 端：原生 HTML/JavaScript，可直接在浏览器运行或部署至静态服务器
- Web SDK 包装：TypeScript + Webpack，封装 `trtc-cloud-js-sdk` 及美颜、音频混音插件
- 构建工具：Node.js / npm，Webpack，Flutter CLI
- 代码辅助：ESLint + Prettier（Web 部分）
- 语言：Dart、TypeScript、JavaScript、少量 Python（用于简易 HTTP 服务器示例）

## 目录和入口

```
.
├── lib/                    # Flutter 应用主模块（callee 业务逻辑）
├── example/                # TRTC Flutter 官方示例代码（调试参考）
├── android/                # Android 平台工程
├── ios/                    # iOS 平台工程
├── web/                    # Web SDK 包装库及依赖
│   ├── package.json        # Web 构建脚本与依赖管理
│   ├── dist/               # 构建产物（bundle.js）
│   └── README.md           # 包装库说明
├── caller_demo/            # Web 端发起通话演示（门禁设备端）
│   ├── index.html          # 单页应用入口
│   └── README.md           # 使用说明与 API 约定
├── pubspec.yaml            # Flutter 项目描述与依赖
└── README.md               # TRTC Flutter SDK 通用说明（上游官方文档）
```

关键入口文件：
- Flutter 主入口：`lib/main.dart`（需确认）
- Flutter 示例入口：`example/lib/main.dart`
- Web 包装库入口：`web/src/*.ts`（webpack 编译入口）
- Web 演示入口：`caller_demo/index.html`
- TRTC 用户签名生成（仅用于调试）：`lib/debug/GenerateTestUserSig.dart`

## 运行与构建

### Flutter 应用（住户端）

```bash
flutter pub get
flutter run
```

平台要求：Flutter >=2.0，Android Studio >=3.5 / Xcode >=11.0，设备系统 Android >=4.1 / iOS 需有效签名。

iOS 注意：需在 `ios/Runner/Info.plist` 中将 `io.flutter.embedded_views_preview` 设为 `YES`。

### Web SDK 包装库

位于 `web/` 目录：

```bash
npm install
npm run build          # 生产构建
npm run dev            # 开发构建（watch）
```

构建产物位于 `web/dist/`，需在 Flutter Web 的 `index.html` 中引入：

```html
<script src="TrtcWrapper.[version].bundle.js" type="application/javascript"></script>
<script src="BeautyManagerWrapper.[version].bundle.js" type="application/javascript"></script>
```

### Web 发起端演示

位于 `caller_demo/`，为纯静态页面，部署方式任选：

- 直接双击 `index.html` 在浏览器打开；
- 使用简易 HTTP 服务器：

```bash
# Node.js
npx serve .
# Python 3
python -m http.server 8080
```

- 部署至任意 Web 服务器根目录。

运行后需在页面配置后端 API 地址和门禁设备 ID。

## 配置和密钥

### TRTC 应用凭证

该工程依赖腾讯云 TRTC 应用，需要以下两个关键配置项（**严禁硬编码在生产客户端**）：

- 环境变量/代码中使用的 key 名称：`SDKAPPID`（数字）、`SECRETKEY`（字符串）
- 调试示例中用于本地生成 `UserSig` 的文件：`example/lib/debug/GenerateTestUserSig.dart` 或 `lib/debug/GenerateTestUserSig.dart`

官方示例在客户端直接填入 `SDKAPPID` 和 `SECRETKEY`，**仅用于本地调试，严禁上线**。正式环境必须将 `UserSig` 计算逻辑迁移至后台服务器，通过 API 下发。

### Web 发布脚本凭证

`web/package.json` 中定义了发布至腾讯云 TOX 平台的脚本，使用了两个参数：

- `--sid=<SecretId>`
- `--skey=<SecretKey>`

实际值**必须在 CI/CD 环境中通过安全变量注入**，严禁写入代码仓库。脚本仅运维人员或 CI 系统可执行。

### 后端 API 端点（Web 演示用）

`caller_demo` 需要配置以下两个 API 端点（具体地址由部署时填入）：

- 发起呼叫：`POST {API_BASE}/mqtt/call`，携带 `device_device_id` 和 `timestamp`
- 挂断呼叫：`POST {API_BASE}/mqtt/controller/device`，携带呼叫动作信息

生产环境 API 地址和鉴权方式需向服务端团队确认。

## 外部依赖

### Flutter 依赖

由 `pubspec.yaml` 管理，核心依赖为腾讯云 TRTC SDK（包名 `tencent_rtc_sdk` 或 `trtc_cloud`，以实际声明为准）。

### Web 包装库运行时依赖

- `trtc-cloud-js-sdk`：TRTC Web SDK
- `rtc-beauty-plugin`：美颜插件（基础美颜功能）
- `rtc-audio-mixer`：音频混音插件
- `rtc-detect`：浏览器能力检测

开发依赖：TypeScript、Webpack、ESLint、Prettier 等参见 `web/package.json`。

### 后端服务

Web 发起端依赖一个后端服务来转发呼叫信令，该服务应至少提供 `/mqtt/call` 和 `/mqtt/controller/device` 接口，并完成与住户端 App 的 MQTT 推送。

## 部署线索

1. **Flutter 住户端 App**：构建 Android APK/AAB 及 iOS IPA，通过应用商店或企业分发渠道下发。
2. **Flutter Web（可选）**：若启用 Web 平台，需将 `flutter build web` 产物与 `TrtcWrapper` bundle 一起部署到静态资源服务器，并在 `index.html` 中正确引入 JS 文件。
3. **Web 发起端演示**：`caller_demo/index.html` 可直接部署至任何静态 Web 服务器，或嵌入门禁设备前端；需在运行时填写后端 API 地址和设备 ID。
4. **TrtcWrapper 静态资源**：从 `web/dist/` 目录取出 bundle 文件，放置于 Flutter Web 构建产物或 CDN，确保版本一致。
5. **TRTC 应用配置**：无论是客户端还是服务端生成 `UserSig`，均需提前在腾讯云 TRTC 控制台创建应用，获取 `SDKAppID` 与 `SecretKey`。

## 复刻检查清单

- [ ] 克隆代码库，确认分支为 `main`。
- [ ] 在腾讯云 TRTC 控制台创建应用，获取 `SDKAppID` 和 `SecretKey`。
- [ ] 搭建后端签名服务（或部署已有的 `UserSig` 生成服务），禁止客户端硬编码 `SecretKey`。
- [ ] 修改调试文件 `lib/debug/GenerateTestUserSig.dart`，填入本地调试用的 `SDKAPPID` 和 `SECRETKEY`（仅开发用途，勿提交真实值）。
- [ ] Flutter 环境准备：安装 Flutter SDK，执行 `flutter pub get`。
- [ ] iOS 项目需确认 `Info.plist` 中 `io.flutter.embedded_views_preview` 为 `YES`，并配置开发者签名。
- [ ] Android 清单文件可能需增加 `tools:replace="android:label"` 避免合并冲突。
- [ ] Web 包装库准备：进入 `web/`，执行 `npm install && npm run build`，将产物复制至 Flutter Web 资源目录或 CDN。
- [ ] 将 `caller_demo/index.html` 部署至目标环境，配置正确的后端 API 地址。
- [ ] 运行 Flutter 应用及 Web 发起端，进行端到端通话测试。
- [ ] 完成部署后更新 `inventory/projects.yaml` 及 `deployments/` 下的部署记录。

## 待补充信息

- Flutter 应用的主入口文件具体路径和业务模块划分。
- 生产环境 `UserSig` 生成服务的部署地址及鉴权方式。
- 后端服务与 MQTT 推送的详细协议和数据格式。
- 门禁设备端和住户端在真实场景下的身份标识映射关系。
- CI/CD 流程中安全注入 `TOX` 凭据的具体方式和变量名。
- 若项目有其他环境变量文件（如 `.env`），请提供环境变量 key 列表（不提供值）。
- 各个模块的生产环境访问域名或 IP 地址。
