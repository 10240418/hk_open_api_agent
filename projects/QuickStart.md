# QuickStart 项目工程文档

## 项目定位
QuickStart 是 HarmonyOS 入门教学项目（Codelab），通过渐进式的手把手实践案例，引导零基础开发者快速完成首个 HarmonyOS 应用开发，掌握应用的基础构建、UI 开发及多设备部署技能。项目涵盖环境搭建、基础控件使用、多设备适配等典型场景，最终产出可在不同设备形态上运行的应用示例。

## 技术栈
- **目标平台**：HarmonyOS（HMOS）
- **主要语言**：ArkTS（.ets）
- **UI 框架**：ArkUI（声明式 UI）
- **构建系统**：hvigor（对应 `hvigorfile.ts`）
- **包管理器**：ohpm（`oh-package.json5`）
- **运行时**：HarmonyOS Native/ArkRuntime
- **最低 API 版本**：待补充（见 `AppScope/app.json5` 中 `compileSdkVersion` 与 `minAPIVersion`）
- **开发工具**：DevEco Studio

## 目录和入口
项目根目录下包含多个教程阶段对应的子目录，当前扫描聚焦于 `11_DevelopOnceDeployAnywhere`（一次开发，多端部署）阶段，内含两个变体：
- `11_Complete` —— 完整成品项目
- `11_StartPoint` —— 对应阶段的起始脚手架

每个变体均为标准的 HarmonyOS 多模块应用，结构示意如下：
```
11_Complete/ (或 11_StartPoint/)
├── AppScope/                    # 应用全局配置及图标
│   └── app.json5                # 应用包名、版本、图标等
├── build-profile.json5          # 工程级构建配置
├── hvigorfile.ts                # hvigor 构建脚本
├── oh-package.json5             # 工程级依赖与脚本
├── commons/                     # 公共模块（HAR）
│   ├── uicomponents/            # 共享 UI 组件
│   └── utils/                   # 共享工具库
├── features/                    # 业务特性模块（HAR/HSP）
│   ├── learning/
│   ├── map/
│   └── quickstart/
└── products/                    # 产品入口模块（HAP）
    └── default/
        ├── build-profile.json5
        └── hvigorfile.ts
```
**入口点**：`products/default` 模块包含能力(Ability)入口，具体页面路由起始于 `features/quickstart` 等特性模块的 `Index.ets`。应用主配置位于 `AppScope/app.json5`。

## 运行与构建
### 环境准备
1. 安装 **DevEco Studio**（版本与该教学项目匹配的稳定版，建议查阅教程对应版本）。
2. 配置 HarmonyOS SDK（自动下载或手动指定）。
3. 安装 ohpm 包管理器（随 DevEco Studio 提供或独立安装）。

### 获取代码
```bash
git clone https://gitee.com/harmonyos_codelabs/QuickStart.git
cd QuickStart
```

### 构建与运行
1. **使用 DevEco Studio**  
   打开对应阶段文件夹（如 `11_DevelopOnceDeployAnywhere/11_Complete`），点击 `Build -> Build Hap(s)/App(s)` 或直接点击 `Run` 按钮，选择目标设备（模拟器或真机）进行部署调试。

2. **命令行构建（hvigorw）**  
   在对应工程目录下执行：
   ```bash
   hvigorw assembleHap
   ```
   生成 `.hap` 包位于 `products/default/build/outputs/default/` 下，可通过 `hdc install` 部署到设备。

> 注意：项目未提供传统 `package.json` 的 `scripts`，构建完全依赖 hvigor 脚本。

## 配置和密钥
- 未发现 `.env`、`.env.*` 等环境变量文件，无外部密钥注入机制。
- 全局应用标识及版本号定义在 `AppScope/app.json5`（如 `bundleName`、`versionCode`、`versionName`）。
- 编译及签名配置位于 `build-profile.json5` 各层级，具体包括 signingConfigs 等，当前扫描未提取到实际签名信息，需在 DevEco Studio 中配置调试证书（自动生成或手动导入）。
- 所有可变配置直接内嵌于源码或 JSON 配置中，无额外配置中心。

## 外部依赖
- 依赖项声明于各模块的 `oh-package.json5` 中，例如 `commons/uicomponents/oh-package.json5`、`features/quickstart/oh-package.json5` 等。
- 主要依赖为 HarmonyOS 官方 SDK 库（如 `@ohos.*`）和可能的 OpenHarmony 开源组件。
- 目前未发现第三方网络 API、数据库、支付或消息推送服务集成，项目为纯粹本地客户端示例。

## 部署线索
- 部署目标：HarmonyOS 设备（手机、平板等），也可在 DevEco Studio 自带的模拟器上运行。
- 产物形式：`.hap` 包或 `.app` 包（多 HAP 组合）。
- 无需服务器部署，无需域名、端口或数据库等基础设施。
- 若需实际分发，需通过 DevEco Studio 进行签名打包生成正式 release 包，上架至华为应用市场或私有渠道。

## 复刻检查清单
若要完整复刻此工程并成功运行，请逐项确认：
1. ✅ 克隆 `QuickStart` 仓库到本地。
2. ✅ 安装兼容版本的 DevEco Studio 及必需 SDK（API 版本与项目 `AppScope/app.json5` 中的要求一致）。
3. ✅ 打开目标阶段工程目录（如 `11_DevelopOnceDeployAnywhere/11_StartPoint` 或 `11_Complete`）。
4. ✅ 执行 `Sync` 或 `hvigorw assembleHap` 以确保所有依赖下载完毕且无编译错误。
5. ✅ 创建或选择模拟器 / 连接真机，检查 `hdc` 是否可用。
6. ✅ 运行应用，验证主要功能是否正常启动。
7. ✅ 若无签名，DevEco Studio 会自动使用默认调试签名，仅限调试阶段。
8. ✅ 如需多设备部署验证，按照教程指引测试一次开发多端部署效果。
9. ✅ 未涉及外部 API 秘钥，无需配置环境变量。

## 待补充信息
- HarmonyOS API 版本与 SDK 版本具体要求（可从 `app.json5` 或 `build-profile.json5` 提取后补填）。
- 各模块 `oh-package.json5` 中的具体依赖清单与版本范围。
- 签名证书的实际 CN、企ID、aliases（需从 DevEco Studio 签名配置中获取，本文不写入）。
- 教程中其他阶段（01-10）的项目目录结构尚未扫描，可后续按需补充。
- 项目是否涉及 hvigor wrapper 版本配置（`hvigor/hvigor-config.json5` 中 `hvigorVersion` 等）。
- 未发现 CI/CD 或自动化测试脚本。

---
*本文档由工程知识库自动扫描生成人工改写，符合 Hermes/Codex 自动部署与复刻规范，不含任何有效凭据或密码。*
