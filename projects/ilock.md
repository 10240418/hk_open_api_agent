# ilock 项目工程文档

## 项目定位

`ilock` 是一个基于 Go 的后端服务与 Vue3 前端组成的智能锁/物联网管理平台。项目通过 HTTP API 对外提供业务能力，内部集成 MQTT、时序数据库、缓存与关系型数据库，主要负责设备通信、数据采集与管理后台呈现。当前仓库包含核心服务、管理前端以及相关部署编排资源。

## 技术栈

- **语言**：Go、TypeScript/JavaScript、少量 Python
- **后端框架**：Gin（HTTP）、GORM（ORM）
- **前端框架**：Vue 3 + Vite（两个独立前端应用）
  - `ilock-http-frontend`：Element Plus
  - `iboard_web_admin`：Ant Design Vue + Pinia 状态管理
- **关键依赖库**：
  - JWT 鉴权、密码哈希（golang-jwt, crypto）
  - MySQL 驱动、Redis 客户端、MQTT 客户端、InfluxDB 客户端
- **构建工具**：Vite、vue-tsc
- **运行时**：Go、Node.js、Python（可能用于脚本或部署辅助）
- **容器化与编排**：Docker、Docker Compose、nginx

## 目录和入口

项目根目录下主要模块：

- `ilock_http_service/` — 核心后端服务（Go）
  - `go.mod` 声明模块 `ilock_http_service`
  - `ilock-http-frontend/` — 面向 C 端/设备管理的前端界面（Vue3 + Element Plus）
  - `deploy/emqx/` — EMQX MQTT Broker 集群配置
  - `docker-compose.yml` — 服务编排定义
- `iboard_web_admin/` — 管理后台前端（Vue3 + Ant Design Vue + Pinia）
  - 独立构建与 nginx 配置（`nginx/default.conf`、`Dockerfile`）
- `doc/` — 部署相关文档，如 `server-deployment-ai-prompt.md`
- `tmp/` — 实验性/原型工作区（非生产代码）

**入口线索**：

- 后端入口未在扫描中直接给出，通常为 `ilock_http_service/main.go` 或 `cmd/` 下程序，监听 HTTP API 端口（需确认）。
- 前端入口分别为两个 Vite 项目下的 `index.html` 及 `src/` 目录。

## 运行与构建

### 前端构建

**`ilock-http-frontend`** (位于 `ilock_http_service/ilock-http-frontend`)：
- 安装依赖：`npm install`（或 `pnpm`/`yarn`）
- 开发模式：`npm run dev`
- 生产构建：`npm run build`
- 预览生产构建：`npm run preview`

**`iboard_web_admin`** (位于 `iboard_web_admin`)：
- 安装依赖：`npm install`
- 开发模式：`npm run dev`
- 生产构建（包含类型检查）：`npm run build` （执行 `vue-tsc -b && vite build`）
- 预览：`npm run preview`

### 后端构建

Go 服务基于模块 `ilock_http_service`，使用 Go 1.26。
- 依赖下载：`go mod download`
- 构建：`go build ./...` 或指定 `cmd` 目录生成二进制文件
- 运行：直接执行编译产物或 `go run` 指令

### Docker 相关

- 服务通过 `ilock_http_service/docker-compose.yml` 编排，可能包含 Go 应用、EMQX、MySQL、Redis 等服务容器。
- `iboard_web_admin` 提供独立 `Dockerfile`，结合 `nginx/default.conf` 构建前端镜像。

## 配置和密钥

各个组件通过环境变量配置，切勿将真实值硬编码或提交至仓库。

### ilock-http-frontend

- **`ilock_http_service/ilock-http-frontend/.env.production`**
  - `VITE_API_BASE_URL`
  - `VITE_PROXY_TARGET`（疑似敏感）
- **`ilock_http_service/ilock-http-frontend/.env.development`**
  - `VITE_API_BASE_URL`
  - `VITE_PROXY_TARGET`（疑似敏感）

这些变量用于配置前端请求的后端 API 地址及开发代理目标。

### iboard_web_admin

- **`iboard_web_admin/.env`**
  - `APP_PORT`
  - `DOCKER_REGISTRY`
  - `IMAGE_NAME`
  - `IMAGE_TAG`
  - `NODE_ENV`

无直接标记为敏感，但 `DOCKER_REGISTRY` 可能包含私有仓库地址。

### 后端服务

扫描中未直接捕获后端的 `.env` 或配置文件，但根据 `go.mod` 推断，运行时会需要以下环境变量（key 名称常见形式）：
- 数据库连接：`DB_DSN`、`MYSQL_HOST`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DB`
- Redis 连接：`REDIS_ADDR`、`REDIS_PASSWORD`
- MQTT 连接：`MQTT_BROKER`、`MQTT_USER`、`MQTT_PASSWORD`（EMQX 相关）
- InfluxDB 连接：`INFLUXDB_URL`、`INFLUXDB_TOKEN`、`INFLUXDB_ORG`、`INFLUXDB_BUCKET`
- JWT 签名：`JWT_SECRET`
- 服务端口：`PORT` 或 `HTTP_PORT`

> ⚠️ 上述变量名仅为工程习惯推断，具体需查阅 `ilock_http_service` 内部配置加载逻辑（如 `config.yaml` 或 `flag`），并以实际代码为准。

密钥、密码、Token 均不得出现在本文档中。实际部署时从安全存储（Vault、K8s Secrets、或者本地的 `private/env-backup/`）注入。

## 外部依赖

基于代码依赖及部署配置，项目运行时依赖以下外部服务：

| 依赖服务 | 用途 | 说明 |
|----------|------|------|
| MySQL | 业务数据持久化 | GORM + MySQL 驱动 |
| Redis | 缓存与会话管理 | go-redis 客户端 |
| EMQX (MQTT Broker) | 设备消息通信 | `deploy/emqx/cluster.hocon` 提供集群配置，Go 使用 paho.mqtt 客户端 |
| InfluxDB | 时序数据存储 | influxdb-client-go，可能用于设备上报的指标历史 |
| nginx | 前端静态资源服务与反向代理 | `iboard_web_admin/nginx/default.conf` |

> 注意：`go.mod` 中出现了 MongoDB 驱动，但标记为 indirect，可能非项目直接使用，不作为主依赖。

## 部署线索

- **Docker Compose**：主部署文件位于 `ilock_http_service/docker-compose.yml`，推测定义了 Go 应用、EMQX、MySQL、Redis、InfluxDB 等服务。
- **管理前端独立部署**：`iboard_web_admin` 提供 `Dockerfile` 及 nginx 配置，可单独构建镜像运行。
- **EMQX 集群**：`ilock_http_service/deploy/emqx/cluster.hocon` 包含 HOCON 格式的集群配置，部署 EMQX 时应参照该文件。
- **AI 辅助部署提示**：`doc/server-deployment-ai-prompt.md` 可能提供部署步骤说明，可在自动化部署中作为上下文使用。
- **生产环境前端**：构建前端静态资源后由 nginx 托管，API 请求转发到后端。
- Git 远端 `https://github.com/10240418/ilock.git` 为主版本仓库。

## 复刻检查清单

若要在一台新机器上完整复现运行环境，按以下步骤检查并操作：

1. **克隆仓库**：`git clone https://github.com/10240418/ilock.git && cd ilock`
2. **审查私密配置**：查看本地的 `private/env-backup/`（若存在）获取环境变量值，切勿提交。
3. **准备外部依赖**：
   - 启动 MySQL、Redis、EMQX、InfluxDB 实例（可借助 `docker-compose.yml` 或自行部署）。
   - 创建数据库及用户，初始化表结构（可能存在 `migrate` 脚本或 GORM AutoMigrate）。
4. **后端配置**：
   - 为 Go 服务设置所需环境变量（数据库、Redis、MQTT、InfluxDB、JWT Secret、端口等）。
   - 也可通过配置文件加载，参照 `ilock_http_service` 内配置模块。
5. **构建并运行后端**：
   - `cd ilock_http_service && go build -o server ./...` 或 `go run .`
   - 确保端口与前端代理目标一致。
6. **构建前端（两个应用）**：
   - `cd ilock_http_service/ilock-http-frontend && cp .env.production .env && npm install && npm run build`
   - `cd iboard_web_admin && cp .env .env.production && npm install && npm run build`
   - 将构建产物（`dist`）部署至 nginx 或使用各自 Dockerfile 生成镜像。
7. **配置 nginx 反代**：
   - 针对管理后台，`iboard_web_admin/nginx/default.conf` 可作参考。
   - 确保 `/api` 等代理规则指向后端服务地址。
8. **启动 EMQX 集群**：
   - 使用 `deploy/emqx/cluster.hocon` 配置，启动 EMQX 节点（或单节点）。
9. **验证**：确认前端页面能正常访问，API 通信、MQTT 连接及数据存储均正常。
10. **更新部署记录**：在 `inventory/projects.yaml` 和 `deployments/` 下记录本次部署信息。

## 待补充信息

下列信息在复刻或维护时需进一步明确：

- 后端服务的具体入口文件（`main.go` 路径）及监听端口。
- 后端配置加载方式（环境变量、配置文件路径、默认值）。
- 数据库表结构初始化方式（迁移工具或 SQL 文件）。
- EMQX 集群的完整连接凭证（用户名、密码）及 Topic 规范。
- InfluxDB 使用的 bucket 名称及保留策略。
- 前端应用与 API 间的完整路由映射（nginx 配置细节）。
- 各服务的健康检查端点。
- 生产环境域名、SSL 终止等网络架构信息。
- `private/env-backup/` 内容（需安全获取后注入）。
- Python 脚本的具体用途与调用方式。
