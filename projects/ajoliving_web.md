# ajoliving_web 项目文档

## 项目定位

AJOLiving Web 是一个面向海外/国内社区生活服务的全栈应用，提供前端展示、用户认证、社区管理、支付（EASYLINK）、POS 对接、阿里云 OSS 资源存储及邮件通知等能力。项目由 Go 后端（Gin + GORM）和 Vue 3 + TypeScript + Vite 前端组成，通过一套 Bash 脚本实现生产环境的编译、推送、零停机滚动部署与数据库备份。

## 技术栈

| 层次       | 技术选型                                                                                       |
| -------- | ------------------------------------------------------------------------------------------ |
| 后端语言/运行时 | Go 1.24.3                                                                                  |
| HTTP 框架  | Gin                                                                                        |
| ORM      | GORM（主要使用 PostgreSQL，兼容 SQLite 用于测试/本地场景）                                                   |
| 数据库      | PostgreSQL 16（生产，通过 Docker Compose 本地模拟）；实际部署在应用服务器的容器内                                      |
| 认证       | JWT（golang-jwt/jwt/v5），对称密钥，字段：`JWT_SECRET`                                                  |
| 加密       | 通用加密密钥 `ENCRYPTION_KEY`                                                                     |
| 支付       | EASYLINK 支付网关（支持微信 H5/APP、支付宝 H5/APP、云闪付等），通过环境变量管理多套凭证                                      |
| POS 对接   | 通过 HTTP API 与第三方 POS 系统交互，使用用户名/密码登录，字段见配置章节                                               |
| 对象存储     | 阿里云 OSS（通过 ali-oss-go-sdk-v2），支持 CNAME、预签名 URL、回调                                                  |
| 邮件       | SMTP 发送（`MAIL_ENABLED` 控制开关）                                                                 |
| 定时任务     | 内置过期清理 ticker（`ENABLE_EXPIRE_TICKER`）                                                          |
| 前端框架     | Vue 3（Composition API + `<script setup>`）                                                   |
| 构建工具     | Vite 8，后端静态资源由 Vite 打包                                                                     |
| 路由/状态管理  | Vue Router 4，Pinia 3                                                                       |
| 国际化      | vue-i18n 11                                                                                |
| 动效       | GSAP 3 + Lenis 平滑滚动                                                                        |
| CSS 方案   | Tailwind CSS 3 + SCSS                                                                      |
| QR 码生成   | qrcode 库                                                                                   |
| 代理       | 开发环境 Vite 代理 `/api/v1` → 后端 `http://127.0.0.1:8080`（可通过 `VITE_API_PROXY_TARGET` 修改）          |
| 部署       | Bash 脚本 + SSH/SCP + rsync；服务器侧通过时间戳 release 目录 + 符号链接实现原子切换；可选 SSL 证书自动管理                        |

## 目录和入口

```
ajoliving_web/
├── deploy-ajoliving.sh          # 生产部署主脚本（构建、推送、切换、备份）
├── http_service/                # Go 后端
│   ├── cmd/
│   │   ├── server/              # 主服务入口 → 编译产物 ajoliving_server
│   │   └── oss-cors/            # OSS CORS 配置工具 → 编译产物 oss-cors
│   ├── docker-compose.yml      # 本地开发 PostgreSQL 容器
│   ├── .env                     # 环境变量（敏感信息，不提交至版本库）
│   ├── .env.example             # 环境变量模板（无敏感值）
│   ├── go.mod / go.sum
│   └── internal/                # 业务代码
├── web/                         # Vue 3 前端
│   ├── package.json
│   ├── vite.config.ts           # Vite 配置（别名、代理、vendor 分包）
│   ├── tsconfig.json / tsconfig.app.json
│   ├── public/                  # 直接复制的静态文件
│   ├── src/
│   └── index.html
└── doc copy/                    # 辅助文档（含部署提示）
```

**入口文件**：
- 后端二进制：`ajoliving_server`（`cmd/server`）
- OSS CORS 工具：`oss-cors`（`cmd/oss-cors`）
- 前端生产构建输出：`web/dist/`（Vite 构建产物，部署时由脚本推送至目标服务器 Web 目录）
- 开发模式前端：`npm run dev`（`web/vite.config.ts` 定义代理规则）

## 运行与构建

### 本地开发

**后端**：
1. 启动 PostgreSQL 容器：
   ```bash
   cd http_service
   docker compose up -d
   ```
2. 复制环境变量模板并填写真实值：
   ```bash
   cp .env.example .env
   # 编辑 .env 填入数据库连接、OSS、支付等配置
   ```
3. 运行服务：
   ```bash
   go run ./cmd/server
   ```
   或编译后执行：
   ```bash
   go build -o ajoliving_server ./cmd/server && ./ajoliving_server
   ```

**前端**：
```bash
cd web
npm install
npm run dev   # 默认访问 http://localhost:5173，API 代理至 127.0.0.1:8080
```
可通过环境变量 `VITE_API_PROXY_TARGET` 修改代理目标。

**类型检查**：
```bash
npm run typecheck   # 使用 vue-tsc 检查 .ts/.vue 文件，配置见 tsconfig.app.json
```

### 生产构建

**前端**：
```bash
cd web
npm run build    # 自动先执行 typecheck，然后 vite build
```
产物输出至 `web/dist/`，同时保留 `public/` 中的静态资源一同部署。

**后端**：
```bash
cd http_service
GO111MODULE=on go mod download
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o ajoliving_server ./cmd/server
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o oss-cors ./cmd/oss-cors
```
生成静态链接的 Linux amd64 二进制文件，用于生产服务器。

**部署**：
- 使用 `deploy-ajoliving.sh` 一键完成构建、推送、远程安装、数据库备份、版本切换。
- 脚本支持丰富的环境变量控制行为（详见“配置和密钥”一节）。
- 部署目标：
  - **应用服务器**：`47.239.117.108`，运行 Go 后端、PostgreSQL 容器，托管前端静态文件（通过反向代理对外）。
  - **网关服务器**：`47.83.21.100`，负责 HTTPS 终止、域名路由等（具体配置需补充）。
- 部署流程：
  1. 校验本地 `.env` 存在。
  2. 本地构建前后端。
  3. （可选）若启用数据库恢复，则在本地 PostgreSQL 容器导出转储。
  4. 将编译产物和 `public/`、`dist/` 等资源上传至远程临时目录。
  5. 远程执行脚本：创建带时间戳 release 目录，备份生产数据库（可选），更新符号链接实现切流，重启服务。
  6. 清理旧版 release，保留配置数量（`KEEP_RELEASES` 默认 5）。

### 主要运行脚本速览

- `web/package.json`
  - `dev`: `vite`
  - `build`: `npm run typecheck && vite build`
  - `preview`: `vite preview`
  - `typecheck`: `vue-tsc --noEmit -p tsconfig.app.json`

## 配置和密钥

本节仅列出需要配置的**变量键名**，不包含任何真实值、密码或 Token。所有敏感值应在部署前通过安全渠道注入。

分类依据源码中出现的环境变量（来自 `.env`、`.env.example`、`deploy-ajoliving.sh`、`vite.config.ts`）。

### 应用基本配置

- `APP_ENV` — 运行环境（如 `production`、`development`）
- `APP_PORT` — 后端监听端口
- `APP_PUBLIC_BASE_URL` — 前端公开访问基 URL（如 `https://ajoliving.skylinedances.com`）
- `APP_API_PUBLIC_BASE_URL` — 后端 API 公开访问基 URL（如 `https://ajoliving.server.skylinedances.com`）
- `BOOTSTRAP_STAFF_PHONES` — 初始管理员手机号（逗号分隔）
- `SEED_COMMUNITIES` — 预置社区数据（格式待确认）

### 数据库

- `DB_DRIVER` — 驱动（如 `postgres`）
- `DB_DSN` — 连接字符串（可替代细分配置）
- `POSTGRES_DB` — 数据库名
- `POSTGRES_USER` — 用户名
- `POSTGRES_PASSWORD` — （**敏感**）数据库密码
- `POSTGRES_PORT` — 端口（默认 `5432`，本地 dev 可通过映射暴露）

### 支付（EASYLINK）

- `EASYLINK_ENV` — 环境标识（如 `sandbox` / `production`）
- `EASYLINK_BASE_URL` — 网关基地址（来自 `.env.example`，`.env` 中未列但可能必需）
- `EASYLINK_MCH_NO` — 商户号
- `EASYLINK_TIMEOUT_MS` — 请求超时（毫秒）
- `EASYLINK_EXPIRED_SECONDS` — 订单过期秒数
- `EASYLINK_ALI_H5_APP_ID` — 支付宝 H5 应用 ID
- `EASYLINK_ALI_H5_APP_SECRET` — （**敏感**）
- `EASYLINK_ALI_H5_WALLET_TYPE` — 钱包类型
- `EASYLINK_ALI_QR_PAY_DATA_TYPE` — 支付宝扫码支付数据类型
- `EASYLINK_WX_H5_APP_ID` — 微信 H5 应用 ID
- `EASYLINK_WX_H5_APP_SECRET` — （**敏感**）
- `EASYLINK_WX_QR_PAY_DATA_TYPE` — 微信扫码支付数据类型
- `EASYLINK_UP_OP_APP_ID` — 银联 APP 应用 ID
- `EASYLINK_UP_OP_APP_SECRET` — （**敏感**）
- `EASYLINK_YSF_QR_PAY_DATA_TYPE` — 云闪付扫码支付数据类型
- `EASYLINK_YSF_QR_APP_ID` — 云闪付 APP ID（可能于 `.env.example` 中有对应 secret）
- `EASYLINK_YSF_QR_APP_SECRET` — （**敏感**）
- `EASYLINK_H5_APP_ID` / `EASYLINK_H5_APP_SECRET` — 通用 H5 应用 ID/Secret（`.env.example` 中简写）

### OSS（阿里云对象存储）

- `OSS_PROVIDER` — 固定值（如 `aliyun`）
- `OSS_ENDPOINT` — OSS 终端节点
- `OSS_BUCKET` — Bucket 名称
- `OSS_REGION` — 区域
- `OSS_ACCESS_KEY_ID` — （**敏感**）
- `OSS_ACCESS_KEY_SECRET` — （**敏感**）
- `OSS_SESSION_TOKEN` — STS 临时 Token（可选）
- `OSS_USE_CNAME` — 是否使用自定义域名（`1`/`0`）
- `OSS_MEDIA_BASE_URL` — 资源访问基 URL（如 CDN 地址）
- `OSS_PRESIGN_EXPIRES` — 预签名 URL 有效期
- `OSS_DISABLE_SSL` — 是否禁用 SSL
- `OSS_ALLOWED_ORIGINS` — 允许的跨域来源（部署时用于 CORS 配置）
- `OSS_CALLBACK_ENABLED` — 是否启用上传回调
- `OSS_CALLBACK_URL` — 回调地址（会组合 `APP_API_PUBLIC_BASE_URL`）

### 安全与加密

- `JWT_SECRET` — （**敏感**）JWT 签名密钥
- `ENCRYPTION_KEY` — （**敏感**）通用加密密钥

### 邮件（SMTP）

- `MAIL_ENABLED` — 是否启用邮件发送
- `SMTP_HOST` — 邮件服务器地址
- `SMTP_PORT` — 端口
- `SMTP_USERNAME` — 用户名
- `SMTP_PASSWORD` — （**敏感**）
- `SMTP_FROM` — 发件人地址
- `SMTP_HELLO_NAME` — HELO/EHLO 主机名
- `SMTP_TO` — 默认收件人（测试或通知）

### OTP（一次性密码）

- `OTP_PROVIDER` — 提供方（如 `mock`）
- `OTP_MOCK_CODE` — 当 provider 为 mock 时使用的固定验证码

### POS 对接

- `POS_API_BASE_URL` — POS 系统 API 基地址
- `POS_API_LOGIN_TYPE` — 登录方式标识
- `POS_LOGIN_URL` — 登录端点
- `POS_API_USERNAME` — 用户名
- `POS_API_PASSWORD` — （**敏感**）
- `POS_LOGIN_USERNAME_FIELD` — 登录请求中用户名字段名
- `POS_LOGIN_PASSWORD_FIELD` — 密码字段名
- `POS_LOGIN_TIMEOUT` — 登录超时

### 钱包充值

- `WALLET_RECHARGE_ENABLED` — 是否开启钱包充值功能
- `WALLET_RECHARGE_NOTIFY_URL` — 充值回调通知地址
- `WALLET_RECHARGE_RETURN_BASE_URL` — 充值完成后跳转地址

### 定时任务

- `ENABLE_EXPIRE_TICKER` — 是否开启过期清理 Ticker
- `EXPIRE_TICKER_INTERVAL` — 执行间隔

### 部署脚本专用变量（通过环境传入）

- `APP_SERVER` — 应用服务器 IP（`47.239.117.108`）
- `GATEWAY_SERVER` — 网关服务器 IP（`47.83.21.100`）
- `PROJECT` — 项目标识（`ajoliving`）
- `APP_DOMAIN` — 后端域名（`ajoliving.server.skylinedances.com`）
- `WEB_DOMAIN` — 前端域名（`ajoliving.skylinedances.com`）
- `APP_PORT` / `WEB_PORT` / `DB_PORT` — 服务端口
- `APP_PUBLIC_BASE_URL` / `APP_API_PUBLIC_BASE_URL` — 同应用配置
- `OSS_CALLBACK_ENABLED` / `OSS_CALLBACK_URL` / `OSS_ALLOWED_ORIGINS` — 部署时覆盖
- `BACKUP_DB` — 是否备份生产数据库（`1`/`0`）
- `DB_BACKUP_KEEP` — 保留备份数量
- `RESTORE_DB` — 是否从本地 dump 恢复数据库（`0` 默认关闭，需二次确认）
- `RESTORE_DB_CONFIRM` — 恢复数据库的安全确认短语 `RESTORE_PRODUCTION_AJOLIVING`
- `APPLY_NETWORK` / `APPLY_SSL` / `APPLY_OSS_CORS` — 是否应用网络/SSL/OSS CORS 配置
- `VERIFY_DEPLOY` / `VERIFY_HTTPS` — 部署后验证开关
- `SYNC_ENV` — 是否同步本地 `.env` 到服务器
- `KEEP_RELEASES` — 保留的旧 release 数量
- `CERTBOT_EMAIL` — SSL 证书申请邮箱
- `RELEASE_ID` — 手动指定发布 ID（默认时间戳）
- `ENV_FILE` — 环境变量文件路径（默认 `http_service/.env`）

### 前端构建时变量

- `VITE_API_PROXY_TARGET` — Vite 开发服务器代理目标（用于 `vite.config.ts`）
- `VITE_API_BASE_URL` — 生产构建时注入的 API 基地址（部署脚本中设置 `VITE_API_BASE_URL="$APP_API_PUBLIC_BASE_URL/api/v1"`）

## 外部依赖

### 基础设施与服务

- **PostgreSQL 16**：主数据存储，生产环境在应用服务器上通过容器运行；本地开发通过 `docker-compose.yml` 提供。
- **阿里云 OSS**：用户资源存储、媒体文件托管，支持 CNAME 和回调。
- **EASYLINK 支付平台**：聚合支付，处理微信、支付宝、云闪付等多渠道支付，需配置商户号、应用 ID、回调等。
- **SMTP 服务**：用于发送邮件通知，需提供参数（Host/Port/User/Password）。
- **POS 系统**：第三方 HTTP API，需对接登录和数据交互。
- **Let's Encrypt / acme.sh**：SSL 证书自动管理（脚本可选启用）。
- **域名解析**：
  - `ajoliving.skylinedances.com` → 前端
  - `ajoliving.server.skylinedances.com` → 后端 API

### 客户端依赖（NPM）

前端 `package.json` 列出的核心运行依赖：
- `vue`, `vue-router`, `pinia`, `vue-i18n`, `axios`
- `gsap`, `@studio-freight/lenis`（动画与平滑滚动）
- `qrcode`, `@types/qrcode`
- 开发依赖：`vite`, `@vitejs/plugin-vue`, `typescript`, `tailwindcss`, `sass`, `postcss`, `autoprefixer`, `@vue/tsconfig`, `vue-tsc`

### Go 模块依赖

由 `go.mod` 列出的主要直接依赖：
- `github.com/gin-gonic/gin`
- `github.com/golang-jwt/jwt/v5`
- `gorm.io/gorm`, `gorm.io/driver/postgres`, `gorm.io/driver/sqlite`
- `github.com/aliyun/alibabacloud-oss-go-sdk-v2`
- `github.com/joho/godotenv`（加载 .env）
- `github.com/oklog/ulid/v2`（唯一 ID 生成）

## 部署线索

1. **部署目标**：
   - **应用服务器**（`47.239.117.108`）：运行 Go 服务（二进制）和 PostgreSQL 容器，同时托管前端静态文件。
   - **网关服务器**（`47.83.21.100`）：负责 HTTPS 卸载、域名路由，推测运行 Nginx/HAProxy（具体配置待补充）。
2. **服务端口约定**：
   - 后端 API：`APP_PORT`（默认 `20042`）
   - 前端静态：`WEB_PORT`（默认 `20041`）
   - PostgreSQL：`DB_PORT`（默认 `45432`，对外映射）
3. **目录结构**（远程主机）：
   - `/home/admin/$PROJECT/server/` — 后端目录，内含 `releases/` 及当前版本符号链接 `current`。
   - `/home/admin/$PROJECT/web/` — 前端目录，同样使用 `releases/` 与符号链接。
   - `/home/admin/$PROJECT/db/` — 存放数据库备份。
4. **零停机切换**：每次部署创建 `releases/$RELEASE_ID` 目录，分别放置后端 binary 及前端 `dist/`、`public/` 资源，更新 `current` 符号链接后重启后端服务（或前端 Web 服务）。
5. **数据库运维**：
   - 备份：执行 `pg_dump` 并保留最近若干份。
   - 恢复：仅在显式设置 `RESTORE_DB=1` 并确认短语后，从本地 dump 文件恢复到生产数据库（极少使用）。
   - 迁移：后端使用 GORM 自动迁移（AutoMigrate），部署后自动执行字段/表变更。
6. **环境变量同步**：`SYNC_ENV=1` 时，部署脚本会将本地 `.env` 推送到远程 `$APP_RELEASE_DIR/ajoliving.env`，服务启动时读取。
7. **SSL 证书**：`APPLY_SSL=1` 时，脚本会在网关服务器上通过 certbot 或类似工具为 `$APP_DOMAIN` 和 `$WEB_DOMAIN` 申请证书。
8. **OSS CORS 配置**：构建的 `oss-cors` 工具会被推送并在远程执行，配置存储桶的 CORS 规则，允许 `$OSS_ALLOWED_ORIGINS` 和回调。
9. **部署后验证**：脚本支持调用健康检查端点，确保服务启动正常。

## 复刻检查清单

若要在新环境完全复刻该项目并投入生产，请按以下步骤逐项确认：

- [ ] **代码获取**：`git clone https://github.com/The-Healthist/ajoliving_web.git`，切换到 `main` 分支。
- [ ] **环境变量准备**：基于 `http_service/.env.example` 创建 `.env`，填入所有必需的变量（数据库、支付、OSS、SMTP、JWT 等）。参考“配置和密钥”节中的全部键名。
- [ ] **基础设施准备**：
  - 准备两台 Linux 服务器（可复用现有 IP 或重新绑定域名），配置 SSH 免密登录。
  - 在应用服务器上安装 Docker 及 docker-compose，确保 PostgreSQL 容器可按 `docker-compose.yml` 启动。
  - 配置防火墙，放行 `APP_PORT`、`WEB_PORT`、`DB_PORT`。
  - 设置域名解析，将两个域名分别指向对应的服务器。
- [ ] **外部依赖连通性确认**：
  - EASYLINK 支付：向服务商获取商户号、应用 ID、密钥，确认回调可达。
  - 阿里云 OSS：创建 Bucket，获取 AccessKey，配置 CNAME 和回调地址。
  - SMTP：开通邮件服务，确认发信正常。
  - POS API：获取接口文档，配置登录凭据和端点。
- [ ] **本地开发环境验证**：
  - 启动 Docker PostgreSQL：`cd http_service && docker compose up -d`
  - 启动后端：`go run ./cmd/server`
  - 启动前端：`cd web && npm install && npm run dev`
  - 测试基本功能（登录、页面访问、数据写入等）。
- [ ] **初次生产部署**：
  - 设置部署脚本所需的环境变量（例如 `APP_SERVER`, `GATEWAY_SERVER`, `CERTBOT_EMAIL` 等）。
  - 执行 `bash deploy-ajoliving.sh`，观察输出，按需调整 `APPLY_NETWORK`, `APPLY_SSL` 等开关。
  - 检查远程服务器 release 目录及符号链接是否正确。
- [ ] **功能验证**：
  - 通过浏览器访问 `https://$WEB_DOMAIN` 确认前端正常。
  - 调用 API 端点 `https://$APP_DOMAIN/api/v1/...` 确认接口响应。
  - 触发支付流程（测试环境），验证回调。
  - 上传文件，检查 OSS 存储及 CORS。
- [ ] **监控与备份**：
  - 确认定时器（`ENABLE_EXPIRE_TICKER`）按要求运行。
  - 检查数据库备份脚本配置，确保自动备份和保留策略生效。
  - 将项目信息更新到 `inventory/projects.yaml` 和 `deployments/` 记录。

## 待补充信息

- [ ] **EASYLINK 接入详情**：`EASYLINK_BASE_URL` 的正式生产地址未被记载，且部分支付参数在不同渠道下的差异性未文档化；需提供完整的对接手册。
- [ ] **OSS 回调配置细节**：`OSS_CALLBACK_ENABLED` 启用后，后端如何处理回调、签名验证等信息未在文档中体现。
- [ ] **POS API 对接协议**：请求/响应格式、认证方式具体实现（如 token 刷新）需要补充后台交互文档。
- [ ] **SMTP 服务商**：当前仅给出变量键名，未说明具体使用的邮件服务（如阿里云邮件推送、SendGrid 等）及其限制，生产环境切换需明确。
- [ ] **定时过期任务**：`EXPIRE_TICKER` 清理的对象和业务逻辑不清楚，例如清理订单、会话还是其他数据。
- [ ] **钱包充值流程**：充值渠道、支付方式、与钱包账户的关联逻辑、通知处理未提供。
- [ ] **网关服务器配置**：Nginx/HAProxy 具体配置（vhost、SSL 终结规则、反代设置）未在此文档中列出，复刻时需重建。
- [ ] **数据库迁移策略**：GORM AutoMigrate 是否可满足所有升级？是否需手写迁移脚本？有无数据迁移风险点说明。
- [ ] **后端进程守护**：部署脚本似乎未包含 systemd 服务文件或容器化编排，服务重启策略需明确，避免因进程退出导致服务不可用。
- [ ] **日志与监控**：日志输出位置、格式、集中收集方案未提及。
- [ ] **CI/CD 集成**：因当前通过手动执行部署脚本，是否考虑接入 GitHub Actions 或其他 CI 平台尚未定义。
