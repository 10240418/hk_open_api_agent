# HarmonyOS_Wanderlogue

## 项目定位
Wanderlogue 是一款面向旅行爱好者的 HarmonyOS 原生日记应用，提供多媒体日记编辑、卡片式排版、地图标记、时间轴回顾、加密保护、数据备份与长截图分享等核心功能。项目以 ArkTS 开发，适配华为原生鸿蒙设备。

## 技术栈
- **语言**: ArkTS (声明式 UI)  
- **框架**: HarmonyOS SDK (API version ≥ 9)  
- **构建工具**: hvigor  
- **IDE**: DevEco Studio  
- **依赖管理**: ohpm  
- **运行时**: HarmonyOS 设备或模拟器

## 目录和入口

### 关键模块
```
HarmonyOS_Wanderlogue/
├── AppScope/
│   └── app.json5                     # 应用全局配置
├── entry/                            # 主模块
│   ├── src/main/ets/
│   │   ├── entryability/
│   │   │   └── EntryAbility.ets      # 应用主入口
│   │   ├── pages/                    # 页面层（Index/Main/Home/Detail/Edit/Map/Profile/Settings）
│   │   ├── components/               # UI 组件层（DiaryCard/TimelineItem/TextCard/ImageCard/VideoCard 等）
│   │   ├── services/                 # 业务逻辑服务层（Database/File/Security/Backup/Map/Share）
│   │   ├── models/                   # 数据模型层（Diary/Card/Location/Template/Constants）
│   │   ├── utils/                    # 工具层（Date/File/Image/Logger）
│   │   └── common/                   # 公共模块（AppStorage/Router/Theme）
│   └── resources/                    # 资源文件（base/dark/rawfile）
```

### 路由与入口
- 页面注册在 `entry/src/main/resources/base/profile/main_pages.json`。
- 启动入口为 `EntryAbility.ets`，初始页面通常为 `pages/Index.ets`。

## 运行与构建
项目依赖 DevEco Studio 和 HarmonyOS SDK 完成构建与调试。

- **本地构建**：用 DevEco Studio 打开工程，自动安装 hvigor 依赖后，点击 Build → Build Hap(s)/APP(s)。
- **命令行构建**（如已配置环境变量）：
  ```bash
  cd HarmonyOS_Wanderlogue
  hvigorw assembleHap
  ```
- **调试运行**：连接真机或启动模拟器，在 DevEco Studio 中点击 Run 'entry'。

暂无 `package.json` 或 Node.js 脚本，所有构建流程由 hvigor 接管。

## 配置和密钥
- 应用全局配置：`AppScope/app.json5` 定义了 bundleName、version 等。
- 模块级配置：`entry/src/main/module.json5` 包含 abilities、permissions 等。
- 环境特定配置：未发现 `.env` 文件，配置以 JSON5 形式嵌入。
- **需要关注的密钥/签名**：
  - 应用签名指纹（用于华为账号、地图等服务鉴权）。
  - 若使用华为地图服务，需在 `AppGallery Connect` 中开启并配置 `client_id`（存放在代码或配置文件中，具体位置待确认）。
  - 若使用华为云备份或其他联网服务，需提供 API 密钥，目前代码中未明确暴露。

**重要**：所有密钥、签名信息不得写入本文档。实际部署时，请从 `private/env-backup/`（若存在）获取或登录 AppGallery Connect 控制台下载。

## 外部依赖
| 依赖项 | 用途 | 说明 |
|--------|------|------|
| HarmonyOS 基础能力（@ohos.*） | 系统 API（文件、数据库、通知等） | 系统内置 |
| 华为地图服务（Map Kit） | 地图展示与 POI 标记 | 需要在 AppGallery Connect 开通 |
| 数据库（关系型/键值型） | 本地数据持久化 | HarmonyOS 内置 |
| 文件存储（FileIO） | 图片、视频文件管理 | 系统 API |
| 备份服务（可选） | 数据导入/导出 | 本地 JSON 或云端（待确认） |

## 部署线索
- 目标平台：HarmonyOS NEXT 或 HarmonyOS 3.0/4.0。
- 分发渠道：华为应用市场（AppGallery）。
- 部署步骤：
  1. 在 DevEco Studio 中生成签名 App（p12、csr、cer 等）。
  2. 在 AppGallery Connect 中创建应用，填写包名，上传签名指纹。
  3. 开启所需服务（如地图、分析、推送等），获取对应的配置文件 JSON 并放入工程。
  4. 构建 Release Hap，通过 AppGallery Connect 上传并提审。
- 回调域名：无 Web 回调，暂不涉及。
- 端口监听：本地应用无服务端，不监听端口。

## 复刻检查清单
1. 克隆仓库：
   ```bash
   git clone <repo-url>
   cd HarmonyOS_Wanderlogue
   ```
   当前远端为 `https://github.com/10240418/HarmonyOS_Wanderlogue.git`（公开可见）。
2. 安装 DevEco Studio 及对应 HarmonyOS SDK（最低 API 9）。
3. 在 DevEco Studio 中打开工程，等待 hvigor 同步完成。
4. 检查编译环境：
   - 确认 SDK 路径、ohpm 配置正确。
   - 若有自定义插件，需额外安装。
5. 申请华为开发者账号，创建应用并完成签名配置。
6. 启用所需云端服务（地图等），将生成的配置文件（如 `agconnect-services.json`）放入工程指定位置。
7. 用真机或模拟器运行，验证主流程。
8. 若需启用备份功能，确认权限与存储路径。

## 待补充信息
- 包名（bundleName）的具体值（`AppScope/app.json5` 中定义）。
- 华为地图、备份等服务是否已集成，以及对应的 `agconnect-services.json` 存放位置。
- 是否使用了华为统一认证或其他需要 AppID 的服务。
- 数据库表结构与字段说明（后续可补入开发文档）。
- 长截图分享的实现方式（是否依赖第三方 SDK）。
- 加密算法及密钥管理方式（用于日记加密的对称/非对称方案）。
- CI/CD 集成方案（若存在）。

如需更详细的部署指导，请参照项目仓库中的 README.md 及华为官方文档。
