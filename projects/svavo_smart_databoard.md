# svavo_smart_databoard

## 项目定位

SVAVO Smart Databoard 是一款面向厕所设备的监控与告警中后台系统，专注解决设备状态实时追踪、异常告警以及管理效率问题。系统支持单管理员登录，围绕设备录入、实时轮询、快照存储、告警规则、告警邮件通知以及按厕所分组的总览看板等核心功能，形成从数据采集到运维通知的闭环。

当前交付形态为前后端分离，后端提供 REST API 和轮询调度，前端为 React 单页应用，数据库使用 PostgreSQL，所有组件可通过 Docker Compose 统一编排。

## 技术栈

- **后端**：Go 1.24（模块 `svavo_smart_databoard`），HTTP 路由自行组织，使用 `pgx/v5` 连接 PostgreSQL，`golang.org/x/crypto` 处理密码，JWT 签权。
- **前端**：React 19 + Vite 7，TypeScript 6.x，状态管理 `zustand`，路由 `react-router-dom`，数据请求 `axios` 与 `@tanstack/react-query`，可视化 `echarts` + `echarts-for-react`，扫码 `@zxing` 与 `qr-scanner`，样式 `TailwindCSS 3`，构建使用 Vite。
- **数据库**：PostgreSQL 16（Alpine 镜像）。
- **容器化**：Docker + Docker Compose，提供本地开发用 `docker-compose.yml` 与生产用 `docker-compose.prod.yml`。
- **静态文件/反向代理**：前端构建产物由 nginx 1.27 (Alpine) 托管；生产环境可配合外部 nginx 网关或 frp 内网穿透。
- **辅助运维**：Supervisor 管理后端进程（示例配置 `deploy/hybrid/svavo.supervisor.conf`），systemd 服务文件（`deploy/systemd/svavo-alert.service`），postfix 邮件转发示例（`deploy/postfix/main.cf.example`），frp 示例（`deploy/frp/example-frpc.toml`）。

## 目录和入口

关键目录与文件概览：

```
svavo_smart_databoard
├── cmd/server/                # 后端主程序入口
├── internal/                  # Go 内部包
│   ├── router/                # 路由注册
│   ├── handler/               # HTTP 控制器
│   ├── service/               # 业务逻辑（轮询、告警、种子初始化等）
│   ├── database/              # PostgreSQL 连接与迁移
│   ├── model/                 # 核心数据结构
│   ├── middleware/            # JWT 鉴权中间件
│   └── errcode/               # 统一响应格式
├── frontend/                  # React 前端项目
│   ├── src/                   # 前端源码
│   ├── nginx/default.conf     # 前端 nginx 配置（生产）
│   ├── Dockerfile             # 多阶段构建（Node 构建 → nginx 运行）
│   ├── vite.config.ts         # Vite 配置（API 代理等）
│   └── package.json           # 脚本与依赖
├── deploy/                    # 部署相关配置
│   ├── docker/README.md       # Docker Compose 部署详细说明
│   ├── hybrid/                # 混合部署示例（nginx、Supervisor、环境变量）
│   ├── nginx-gateway/         # 网关 nginx 示例
│   ├── frp/                   # frpc 示例
│   ├── postfix/               # postfix 配置示例
│   ├── systemd/               # systemd 服务示例
│   └── supervisor/            # Supervisor 配置示例
├── docker-compose.yml         # 本地开发 PostgreSQL 服务
├── docker-compose.prod.yml    # 生产全栈 Compose（镜像构建与部署）
├── Dockerfile.backend         # 后端生产镜像构建文件（如有）
├── go.mod                     # Go 模块依赖
└── .env.production.example    # 生产环境变量模板
```

**后端入口**：`cmd/server/main.go`（推测），启动 HTTP 服务并注册 `/api` 路由。  
**前端入口**：`frontend/src/main.tsx`，构建后由 nginx 提供静态文件，并反向代理 `/api` 到后端。  
**API 基路径**：所有接口统一在 `/api/` 下，如 `/api/health`、`/api/auth/login` 等。

## 运行与构建

### 本地开发

1. **环境变量**  
   复制模板并修改敏感项：
   ```bash
   cp .env.example .env
   ```
   必需的最小变量集见 [配置和密钥](#配置和密钥)，其它参数均有默认值。

2. **启动 PostgreSQL**
   ```bash
   docker compose up -d postgres
   ```

3. **启动后端**
   ```bash
   set -a && source .env && set +a
   go run ./cmd/server
   ```
   默认监听 `:8080`（通过 `HTTP_ADDR` 可修改）。

4. **启动前端**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Vite 开发服务器默认 `http://127.0.0.1:5173`，并自动代理 `/api` 到后端地址（由 `VITE_API_PROXY_TARGET` 控制）。

### 构建验证

- **后端测试**（如果有）：
  ```bash
  go test ./...
  ```
- **前端构建**：
  ```bash
  cd frontend
  npm run build     # 包含类型检查
  # 或跳过类型检查快速构建：
  npm run build:fast
  ```
  构建结果输出到 `frontend/dist/`。

- **前端预览**（本地静态文件服务，不含后端代理）：
  ```bash
  npm run preview
  ```

- **Go 二进制构建**（非容器环境）：
  ```bash
  go build -o svavo-server ./cmd/server
  ```

### 代码质量

- 前端 Lint：`cd frontend && npm run lint`
- 前端类型检查：`npm run typecheck`（分别对 app 与 node 配置执行 `tsc --noEmit`）

## 配置和密钥

以下列出系统定义的环境变量，**严禁在本文档中记录任何实际值**。所有敏感变量仅保留名称，实际值需从安全存储或本地 `private/env-backup/` 中获得。

### 后端必需配置（来源：`.env` / `.env.production.example` / `deploy/hybrid/.env.server.example`）

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `JWT_SECRET` | 是 | JWT 签名密钥，用于管理员会话 |
| `ADMIN_USERNAME` | 是 | 管理员登录用户名 |
| `ADMIN_PASSWORD` | 是 | 管理员密码（bcrypt 哈希或不加密视实现而定） |
| `POSTGRES_DB` | 是 | 数据库名（默认 `svavo_databoard`） |
| `POSTGRES_USER` | 是 | 数据库用户（默认 `svavo`） |
| `POSTGRES_PASSWORD` | 是 | 数据库密码 |
| `POSTGRES_HOST` | 否 | 数据库主机（默认 `localhost`？实际由 Compose 提供服务名） |
| `POSTGRES_PORT` | 否 | 数据库端口（默认 `5432`，本地映射可设为 `35432`） |
| `SVAVO_ACCESS_ID` | 是 | SVAVO 设备 API 认证 ID |
| `SVAVO_ACCESS_SECRET` | 是 | SVAVO 设备 API 认证密钥 |
| `SVAVO_API_BASE_URL` | 否 | SVAVO API 基础地址，有默认值 |
| `APP_ENV` | 否 | 运行环境标识（如 `production`） |
| `HTTP_ADDR` | 否 | 后端 HTTP 监听地址，默认 `:8080` |
| `MAIL_ENABLED` | 否 | 是否启用邮件告警，默认 `false`/`true` 视部署 |

### 前端构建/运行时变量

| 变量名 | 说明 |
|--------|------|
| `VITE_DEV_SERVER_PORT` | Vite 开发服务器端口，默认 `5173` |
| `VITE_API_PROXY_TARGET` | 开发时代理 `/api` 的目标地址，默认 `http://127.0.0.1:8080` |

### PostgreSQL Docker 环境（`docker-compose.yml`）

仅作为示例，实际通过 `.env` 传入：

```
POSTGRES_DB=${POSTGRES_DB:-svavo_databoard}
POSTGRES_USER=${POSTGRES_USER:-svavo}
POSTGRES_PASSWORD=<redacted>
```

> 注意：生产 Compose 中后端和前端容器也会读取同一个 `.env` 文件，所有敏感配置通过该文件统一管理。

## 外部依赖

### 第三方 API
- **SVAVO 设备平台**：系统通过 `SVAVO_ACCESS_ID` / `SVAVO_ACCESS_SECRET` 调用其接口进行设备轮询和快照获取，基地址由 `SVAVO_API_BASE_URL` 指定。接口文档未收入本仓库，需联系 SVAVO 提供方获取。

### 邮件服务
- 告警邮件由后端内部邮件模块发送，参考配置 `deploy/postfix/main.cf.example`，实际部署需提供 SMTP 服务器地址、端口、认证信息，或使用本地 postfix 中继。

### 数据库
- PostgreSQL 16，连接参数均由环境变量提供，支持容器化部署和独立实例。

### NPM 依赖（前端运行时）
详见 `frontend/package.json`，关键依赖包括 `react`、`react-dom`、`@tanstack/react-query`、`axios`、`react-router-dom`、`echarts`、`zustand`、`@zxing/library` 等。

### Go 模块依赖
- `github.com/jackc/pgx/v5`：PostgreSQL 驱动
- `golang.org/x/crypto`：密码处理相关

### 部署基础设施
- Docker & Docker Compose
- Nginx（含前端镜像内嵌的 nginx，以及可选的外部网关 nginx）
- 可选：Supervisor / systemd、frp 内网穿透

## 部署线索

以下线索来源于仓库内已有的部署文档和模板，实际部署时请替换示例中的域名、IP 和端口。

### 生产 Compose 部署（推荐）

1. **准备环境文件**  
   将 `.env.example` 或 `.env.production.example` 复制为 `.env`，填写所有必需变量（特别是 `JWT_SECRET`、管理员密码、数据库密码、SVAVO 凭证）。

2. **构建镜像**  
   ```bash
   docker compose -f docker-compose.prod.yml --env-file .env build
   ```
   后端镜像标签：`svavo-smart-databoard-backend`  
   前端镜像标签：`svavo-smart-databoard-frontend`

3. **导出镜像用于离线部署**  
   ```bash
   docker save svavo-smart-databoard-backend | gzip > svavo-backend.tar.gz
   docker save svavo-smart-databoard-frontend | gzip > svavo-frontend.tar.gz
   docker save postgres:16-alpine | gzip > svavo-postgres.tar.gz
   ```

4. **传输至目标服务器**（示例 IP `47.239.117.108`，实际需替换）  
   上传镜像、`docker-compose.prod.yml` 与 `.env` 文件。

   ```bash
   scp svavo-*.tar.gz user@target-server:/path/to/deploy/
   scp docker-compose.prod.yml .env user@target-server:/path/to/deploy/
   ```

5. **导入镜像并启动**
   ```bash
   ssh user@target-server "cd /path/to/deploy && \
     docker load < svavo-backend.tar.gz && \
     docker load < svavo-frontend.tar.gz && \
     docker load < svavo-postgres.tar.gz && \
     docker compose -f docker-compose.prod.yml --env-file .env up -d"
   ```

6. **验证**
   ```bash
   # 检查容器状态
   docker compose -f docker-compose.prod.yml ps
   # 健康检查（后端默认端口 32081，前端 32080，可按需调整）
   curl -I http://127.0.0.1:32081/api/health
   curl -I http://127.0.0.1:32080
   ```

7. **回滚**
   ```bash
   docker compose -f docker-compose.prod.yml down
   ```

### 混合部署（非容器化后端/前端）

部署配置示例位于 `deploy/hybrid/`：
- `svavo.frontend.nginx.conf` / `svavo.web.ssl.nginx.conf`：前端 nginx 配置（HTTP/HTTPS）
- `svavo.api.ssl.nginx.conf`：后端 API 代理配置
- `svavo.supervisor.conf`：后端进程守护
- `.env.server.example`：后端环境变量模板
- `svavo.run.sh`：启动脚本示例

此类部署需要自行管理 Go 二进制构建、nginx 安装与证书，不在此详细介绍。

### 反向代理与域名

- 外部 nginx 网关示例：`deploy/nginx-gateway/example.conf`，可配置域名、SSL 终结及 upstream 指向应用服务器。
- 内网穿透：`deploy/frp/example-frpc.toml` 展示如何通过 frp 暴露本地服务。

### 邮件通知配置

若启用邮件告警（`MAIL_ENABLED=true`），需配置后端 SMTP 连接或使用本地 postfix（参考 `deploy/postfix/main.cf.example`）。具体 SMTP 凭据需从运维侧获取。

### 数据库初始化

服务启动时会自动执行数据库迁移（表创建、种子数据导入，如设备型号初始化），无需手动执行 SQL。

## 复刻检查清单

从零开始复刻完整生产环境，请逐项确认：

- [ ] 获取 SVAVO 设备 API 的 `ACCESS_ID` 和 `ACCESS_SECRET`
- [ ] 准备 PostgreSQL 实例（外部或容器内）并确认连接信息
- [ ] 创建 `.env` 文件，设置所有标记为“必需”的变量（尤其 `JWT_SECRET`、管理员密码、数据库密码）
- [ ] 准备邮件 SMTP 服务器信息，若启用告警则填写相关配置
- [ ] 确定部署方式（Docker Compose 或混合部署），准备 Docker 或 nginx/Go 运行时
- [ ] 构建或拉取后端/前端镜像（或编译二进制）
- [ ] 配置外部反向代理规则（域名、SSL 证书、端口映射）
- [ ] 如需内网穿透，参照 frp 示例配置 frpc
- [ ] 部署后验证：
    - 后端健康检查 `GET /api/health` 返回 200
    - 前端页面可访问，登录成功
    - 设备轮询功能正常（种子数据已初始化）
    - 告警规则可创建，邮件可达（若启用）
- [ ] 更新 `inventory/projects.yaml` 和 `deployments/` 下的部署记录
- [ ] 建立数据备份策略（PostgreSQL dump）

## 待补充信息

以下条目对完整运维和持续集成至关重要，但当前仓库中未明确或缺失：

- **生产环境实际域名** 与 SSL 证书的申请/更新方式
- **邮件 SMTP 服务器地址、端口、认证方式**（目前仅有 postfix 转发示例，无明确凭据管理说明）
- **SVAVO API 的详细文档**（接口说明、频率限制、错误码）
- **CI/CD 流程** 是否已建立（目前未见 GitHub Actions 或其他 CI 配置）
- **日志收集与监控方案**（容器日志、应用日志的汇聚与报警）
- **数据库备份策略**（定时任务或工具）
- **前后端版本发布规范** 与回滚流程细节
- **多环境支持**（如 staging、production）在 Compose 或配置层面的切换方式
- **性能测试与容量规划** 依据
- **第三方依赖升级策略**（Go/CVE 扫描、npm audit）
