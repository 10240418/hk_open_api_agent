# iNtercom_flutter_caller

## 项目定位
本项目是基于腾讯云实时音视频（TRTC）服务实现的 Flutter 通话发起端应用。仓库整合了 TRTC Flutter SDK 的主体逻辑、Web 端音视频包装库（TrtcWrapper）、标准 API 示例应用，以及一个面向门禁/呼叫场景的纯前端演示程序（caller_demo）。核心用途是展示如何在 Flutter 中集成 TRTC 完成音视频通话的发起与控制，并为对接现有 MQTT 后端提供无后端依赖的 Web 发起端参考。

## 技术栈
- **Flutter（Dart）**：跨平台移动/桌面/Web 应用框架
- **JavaScript / TypeScript**：用于 Web 端 TRTC 包装库及 caller_demo
- **Node.js & Webpack**：构建 Web 端 TRTC bundle 及 caller_demo 开发工具链
- **Python**：辅助脚本（如 HTTP 静态服务器）
- **腾讯云 TRTC Web SDK（trtc-cloud-js-sdk）**：浏览器端实时音视频
- **rtc-audio-mixer、rtc-beauty-plugin、rtc-detect**：音效、美颜与设备检测
- **ESLint + Prettier**：代码规范与格式化
- **Tox**：内部发布工具（`tox:publish` 脚本）

## 目录和入口
```
.
├── README.md                        # TRTC Flutter SDK 整体说明
├── pubspec.yaml                     # Flutter 项目依赖入口
├── lib/                             # Flutter 核心代码
├── example/                         # TRTC 标准 Demo 应用（含 Android、iOS 配置）
├── web/                             # TrtcWrapper —— Web 端 TRTC 包装库
│   ├── package.json                 # Web 端构建与发布脚本
│   ├── README.md                    # TrtcWrapper 说明
│   └── dist/                        # 构建产物（TrtcWrapper.bundle.js 等）
├── caller_demo/                     # 纯前端通话发起端 Demo
│   ├── README.md                    # 使用说明与接口文档
│   └── index.html                   # 发起端页面
└── ...
```
- **Flutter 应用入口**：按标准 Flutter 项目结构位于 `lib/main.dart`，具体入口文件需从源码确认。
- **Web 包装库入口**：`web/src` 下的 TypeScript 源码，由 Webpack 打包。
- **caller_demo**：无构建过程，直接使用 `index.html`。
- **示例应用入口**：`example/lib/main.dart`。

## 运行与构建
### Flutter 应用（含示例）
```bash
cd <项目根目录>
flutter pub get
# 运行 Android 模拟器或设备
flutter run
# 构建 APK
flutter build apk
# 构建 iOS（需 macOS + Xcode）
flutter build ios
```

### Web 端 TrtcWrapper 构建
```bash
cd web
npm install
# 开发模式（未压缩）
npm run dev
# 生产模式（压缩）
npm run build
```
构建产物：
- `dist/TrtcWrapper.[version].bundle.js` —— TRTC 基础库
- `dist/BeautyManagerWrapper.[version].bundle.js` —— 美颜插件
- `dist/JSGenerateTestUserSig.[version].bundle.js` —— 本地 UserSig 生成（仅调试用）

### caller_demo（通话发起端）
无需构建，直接通过 HTTP 服务器访问：
```bash
cd caller_demo
# Node.js 简易服务器
npx serve .
# 或使用 Python
python -m http.server 8080
```
也可直接双击 `index.html` 在浏览器中打开（但某些 API 调用可能要求 HTTP 协议环境）。

### 发布（仅 Web 产物）
`web/package.json` 提供了 Tox 发布脚本：
- 测试环境：`npm run tox:publish@dev`
- 生产环境：`npm run tox:publish@master`
发布目标为 `viktest/myapp`，需要提供 `SecretId` 和 `SecretKey`（见配置与密钥）。

## 配置和密钥
### 腾讯云 TRTC 凭证
**必需配置项（通过代码或环境变量注入）**：
- `SDKAPPID`：腾讯云 TRTC 应用 ID
- `SECRETKEY`：用于生成 UserSig 的密钥
- `userSig`：由 SDKAppID 和 SecretKey 计算出的动态签名

**注意**：
- 示例应用中存在本地生成 UserSig 的代码（`example/lib/debug/generate_test_user_sig.dart` 和 Web 端的 `JSGenerateTestUserSig.bundle.js`），仅适用于本地调试。正式上线**必须**将 UserSig 计算逻辑迁移到业务服务器，防止密钥泄露。
- 本仓库未包含 `.env` 文件，复刻时请自行创建（建议使用 `.env.example` 记录所需变量名称）并确保 `.gitignore` 已排除。

### Web 发布凭证
`web/package.json` 中 `tox:publish@dev` 脚本使用占位符：
```
--sid=<SecretId> --skey=<SecretKey>
```
部署时需替换为实际的发布平台（Tox/Vik）密钥对，切记不要将明文密钥提交到仓库。

### caller_demo 后端配置
caller_demo 需要通过 Web 界面配置：
- **API 服务地址**：对接自定义后端服务的完整 URL（示例中的地址可在 `caller_demo/README.md` 查看）。
- **设备 ID**：发起通话的设备标识。

后端需实现的接口参见 `caller_demo/README.md`。

## 外部依赖
| 服务 / 组件 | 用途 | 备注 |
| --- | --- | --- |
| 腾讯云 TRTC | 实时音视频通信 | 需要已创建 TRTC 应用并获取 SDKAppID / SecretKey |
| MQTT 后端服务 | 通话信令中转（caller_demo 使用） | 需独立部署，接口规范见 caller_demo README |
| Tox / Vik 发布系统 | Web 产物分发 | 仅当使用内部发布流程时依赖 |

Web 端 npm 依赖详情见 `web/package.json`，核心运行时包：`trtc-cloud-js-sdk`、`rtc-audio-mixer`、`rtc-beauty-plugin`、`rtc-detect`。

## 部署线索
- **Flutter 跨平台应用**：最终构建为 Android APK / iOS IPA 或 Web 应用。发布前需将 SDKAppID 和 UserSig 获取方式改为从业务服务器动态获取。
- **Web TrtcWrapper**：需先在 `web/` 目录执行构建，然后将生成的 `.bundle.js` 文件部署至 Flutter Web 项目的 `web/` 目录，并在 `index.html` 中引用（参见 `web/README.md` 的引用示例）。
- **caller_demo**：纯静态页面，可部署到 Nginx、CDN 或云存储桶，配置反向代理以指向后端 API。
- **Tox 发布管道**：通过 `tox:publish@master` 将构建产物推送至正式环境，需提前配置`SecretId`、`SecretKey` 与目标路径。

## 复刻检查清单
1. 克隆仓库：`git clone https://github.com/The-Healthist/iNtercom_flutter_caller.git`
2. 安装 Flutter 依赖：`flutter pub get`
3. 安装 Web 依赖：`cd web && npm install`
4. 创建本地配置文件（如 `.env`），记录 `SDKAPPID`、`SECRETKEY` 等密钥（永不提交版本库）。
5. 替换 `example/lib/debug/generate_test_user_sig.dart` 中的占位符值（仅用于本地调试）。
6. 构建 Web 包装库：`cd web && npm run build`
7. 将构建产物复制到 Flutter Web 项目对应目录（若需 Web 平台）。
8. 配置并启动 `caller_demo` 所需的后端 API 服务（或 mock 服务）。
9. 更新 `caller_demo/index.html` 中的默认后端地址。
10. 执行测试：
    - 启动 Flutter 示例应用，验证音视频通话。
    - 打开 caller_demo 页面，测试 API 连接与通话流程。
11. 生产部署：
    - 将 UserSig 生成逻辑迁移至服务器，移除客户端中的 SecretKey。
    - 配置 CI/CD（如 Tox 发布）所需的凭证。

## 待补充信息
- 生产环境腾讯云 TRTC 应用的 `SDKAppID` 及对应的服务器端 UserSig 签发接口地址。
- caller_demo 所对接的后端服务实际部署地址及接口认证方式（如 API Key 或 Token）。
- Tox 发布系统的详细配置说明（`viktest/myapp` 的目标路径定义、权限凭证来源）。
- Flutter 应用主入口文件（`lib/main.dart`）的具体路径及路由结构。
- 是否包含 Android/iOS 原生模块配置（如权限、iOS 的 `io.flutter.embedded_views_preview` 设置）。
