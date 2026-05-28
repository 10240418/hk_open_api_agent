# POS Web

## 项目定位
POS Web 是面向健康管理或零售场景的收银系统前端，支持商品展示、订单管理和 H5 在线支付。  
项目采用 Vue 3 + TypeScript + Vite 构建，并配套一个 Go 编写的本地支付后端服务，用于对接 EasyLink 支付网关，提供下单、查单、结果回写等接口。  
该仓库同时包含面向 AI 辅助开发的 UI 主题规范和 Figma 插件，用于保持页面和交互的一致性。

## 技术栈
- **前端**  
  - 语言：TypeScript / JavaScript  
  - 框架：Vue 3 (Composition API)  
  - 构建工具：Vite (v8)  
  - UI 库：Vant  
  - 状态管理：Pinia  
  - 路由：Vue Router  
  - 国际化：vue-i18n  
  - HTTP 客户端：axios  
  - 二维码生成：qrcode  
  - 测试：Vitest + happy-dom  
  - 类型检查：vue-tsc  
- **支付后端服务** (位于 `../pos_web_payment_http_service`)  
  - 语言：Go  
  - 关键依赖：gopkg.in/yaml.v3, google.golang.org/protobuf, edwards25519 等（详见 go.mod）  
- **辅助工具**  
  - Figma 插件 (TypeScript/JSON)  
  - AI 开发提示词与 Skill 规范 (Markdown)

## 目录和入口
- **根目录关键文件**  
  - `package.json` — 脚本、依赖声明  
  - `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json` — TypeScript 配置  
  - `.env.easylink.example` — 支付环境变量模板  
- **`src/` — 前端源码主目录**  
  - 入口：由 `vite.config.ts` 定义，通常为 `src/main.ts`  
  - 文档：`src/doc/pos-web-current-feature-summary-*.md`、`pos-web-theme-system-v1.md` 等  
- **`skills/pos-web-theme/SKILL.md`** — AI 开发主题技能规范  
- **`tmp/figma-native-plugin-v2/`** — Figma 插件“POS Mobile Native Builder V2”  
- **支付后端入口**（外部仓库）  
  - Go 服务：`../pos_web_payment_http_service/cmd/server`  
  - Node 参考实现：`scripts/easylink_dev_server.mjs`
- **启动入口说明**  
  - 前端 Dev Server：`npm run dev`  
  - 支付后端 (Go)：`npm run payments:dev`  
  - 支付后端 (Node 参考)：`npm run payments:dev:node`

## 运行与构建
### 本地开发
1. **安装依赖**  
   ```bash
   npm install
   ```
2. **启动前端**  
   ```bash
   npm run dev
   ```  
   默认监听 `http://127.0.0.1:5173`。

3. **支付联调（可选）**  
   需要同级仓库 `pos_web_payment_http_service`，并确保已安装 Docker。  
   ```bash
   cd ../pos_web_payment_http_service && docker compose up -d   # 启动 MySQL (127.0.0.1:3311, 库名 pos_payments)
   cd ../pos_web
   cp .env.easylink.example .env.easylink.local              # 根据模板填写本地支付配置
   npm run payments:dev                                       # 启动 Go 支付服务 (默认 127.0.0.1:20034)
   ```  
   Vite 开发代理会将 `/api/payments/h5/*` 转发到本机 Go 服务，其余 `/api/*` 仍走原后端（需另行配置或确保可访问）。  
   如需使用旧的 Node 支付模拟，可执行 `npm run payments:dev:node`。

4. **模拟支付进度**  
   如果暂无真实的支付回调，可通过 API 模拟状态推进：  
   `POST /api/payments/h5/orders/{mchOrderNo}/simulate`

### 构建
- **类型检查**  
  ```bash
  npm run typecheck
  ```
- **生产构建**  
  ```bash
  npm run build
  ```  
  实际执行：`vue-tsc --noEmit -p tsconfig.app.json && vite build`，产物输出到 `dist/`。

- **预览生产构建**  
  ```bash
  npm run preview
  ```

## 配置和密钥
- 仓库根目录未检出 `.env` 文件，所有环境变量需根据模板手工创建。
- 支付联调需要文件 `.env.easylink.local`，其键名可参考 `.env.easylink.example`。  
  已知环境变量 key（仅名称，无实际值）：
  - `VITE_ENABLE_ORDER_RECORD_SNAPSHOT_SYNC` — 为 `true` 时将订单快照同步到后端 `POST /api/payments/order-records/bulk`
  - `EASYLINK_ENABLE_REPORT_PAYMENT` — 为 `true` 时 Go 服务会在支付成功后调用 report-payment hook
  - 支付网关相关密钥（如 EasyLink 商户号、API 密钥、回调地址 `notifyUrl` 等）按 `example` 文件提示填写
- **安全声明**：本文档不包含任何 Secret、密码、Token 或 API Key 的实际值。

## 外部依赖
- **前端 NPM 包**  
  `vue`, `vue-router`, `pinia`, `vue-i18n`, `vant`, `axios`, `qrcode`, `vite`, `@vitejs/plugin-vue`, `typescript`, `vue-tsc`, `vitest`, `happy-dom`, `@vue/test-utils`, `rolldown` 等。
- **支付后端 Go 依赖**  
  `gopkg.in/yaml.v3`, `google.golang.org/protobuf`, `filippo.io/edwards25519`, `golang.org/x/text`, `golang.org/x/sys` 等（见 go.mod）。
- **外部服务**  
  - MySQL 数据库（本地通过 Docker Compose 管理，端口 3311，数据库名为 `pos_payments`）  
  - EasyLink 支付网关（H5 支付，异步通知 + 轮询查单）  
  - 前端额外依赖的“原后端”服务（处理 `/api/*` 非支付请求），其定义未包含在本仓库内。
- **开发工具**  
  - Figma 桌面端（加载 `tmp/figma-native-plugin-v2` 插件）

## 部署线索
1. **前端**  
   - 执行 `npm run build`，将 `dist/` 部署到任意静态服务器（Nginx、CDN 等）。  
   - SPA 路由需配置 fallback 到 `index.html`。  
   - 生产环境需在构建时注入 `VITE_*` 变量（如 `VITE_ENABLE_ORDER_RECORD_SNAPSHOT_SYNC`），这些变量会在构建期固化到产物中。
2. **支付后端**  
   - 对 Go 服务执行 `go build ./cmd/server`，推送二进制至服务器。  
   - 通过环境变量注入 EasyLink 商户凭证、数据库 DSN、回调域名 `notifyUrl` 等。  
   - 确保 MySQL 实例可达，且支付回调端点可从公网访问。
3. **反向代理**  
   - 生产环境需配置将 `/api/payments/h5/*` 流量转发至支付后端服务地址，其余 `/api/*` 转发至主业务后端。  
   - 开发环境中 Vite 代理仅用于本地，不可用于生产。

## 复刻检查清单
- [ ] 克隆 `pos_web` 及 `pos_web_payment_http_service` 仓库至同级目录  
- [ ] 安装 Node.js（版本 ≥ 20.19 或 ≥ 22.12）  
- [ ] 在 `pos_web` 目录执行 `npm install`  
- [ ] 复制 `.env.easylink.example` 为 `.env.easylink.local`，按实际凭据填写（不含值泄露）  
- [ ] 安装 Docker，在 `pos_web_payment_http_service` 执行 `docker compose up -d` 启动 MySQL  
- [ ] 运行 `npm run payments:dev` 启动 Go 支付服务（或 `payments:dev:node` 使用 Node 模拟）  
- [ ] 运行 `npm run dev` 启动前端，验证基本页面与支付流程模拟  
- [ ] 执行 `npm run typecheck` 和 `npm run build`，确保构建成功  
- [ ] 准备生产环境：  
  - 配置前端的 VITE 环境变量（如需要）并重新构建  
  - 编译并部署支付后端，设置环境变量  
  - 在反向代理层添加正确的转发规则  
- [ ] 验证支付回调、订单同步等完整链路  
- [ ] 更新部署记录与 inventory 文件（如 `inventory/projects.yaml`）

## 待补充信息
- `.env.easylink.example` 中每一项变量的用途说明和是否必填  
- 原后端服务的地址、接口约定及认证方式  
- 生产数据库的 DSN 格式及密码存储方案（如 Secrets Manager）  
- EasyLink 商户注册、凭证申请及回调域名白名单指引  
- 日志与监控方案（支付流水、前端异常）  
- 容器化部署资料（Dockerfile 编写、docker-compose 生产化）  
- 主题系统详细用法和 AI Skill 在生产中的使用流程  
- Figma 插件在切图与设计交付中的具体角色
