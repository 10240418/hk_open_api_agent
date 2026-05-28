# ilock_http_service

## 项目定位
智能锁管理系统的 HTTP 服务与 Web 管理前端。

- **后端** (Go)：基于 Gin 提供 RESTful API，通过 MQTT 与智能锁设备双向通信，使用 MySQL 存储业务数据，Redis 实现缓存与会话管理，InfluxDB 记录时序指标。
- **前端** (Vue 3)：可视化设备管理界面，通过 Vite 构建，与后端 API 交互。
- **目标部署形式**：后端二进制 + 前端静态资源，配合 Docker Compose 运行的所有中间件。

## 技术栈
- **后端语言**：Go (go 1.26+)
- **Web 框架**：Gin
- **ORM**：GORM (MySQL 驱动)
- **认证**：JWT (golang-jwt)
- **加密**：golang.org/x/crypto (含 AES)
- **消息通信**：Eclipse Paho MQTT Client
- **时序数据库**：InfluxDB Client v2
- **缓存 / 状态**：Redis (go-redis)
- **前端框架**：Vue 3 + Element Plus + Axios + Vue Router
- **前端构建工具**：Vite
- **基础中间件**：MySQL, Redis, EMQX (MQTT Broker), InfluxDB 2.x
- **容器编排**：Docker Compose

## 目录和入口
- 项目根：Go 后端工程，包含 `main.go`（推测入口文件）、`go.mod`、`config.example.yaml`（配置模板）。
- `ilock-http-frontend/`：Vue 3 前端工程，包含 `package.json`、`vite.config.ts`、`.env.*`。
- `deploy/emqx/cluster.hocon`：EMQX 集群配置。
- `docker-compose.yml`：基础服务编排。

**入口点**：
- 后端启动：`go run .`（默认监听 8080 端口，见 `config.example.yaml`）。
- 前端开发：`cd ilock-http-frontend && npm run dev`，Vite 开发服务器自动代理 `/api` 请求到后端。
- 前端生产构建：`cd ilock-http-frontend && npm run build`，产出静态资源位于 `dist/`。

## 运行与构建
### 1. 启动依赖服务
执行 `docker-compose up -d` 启动下列服务：

| 服务 | 容器名 | 主机端口 | 容器端口 | 说明 |
|------|--------|---------|---------|------|
| MySQL | docker-mysql | 3307 | 3306 | 数据持久化，root 密码通过环境变量设置 |
| Redis | my-redis | 6379 | 6379 | 无密码（可配置） |
| EMQX | my-emqx | 1883, 18083 | 1883, 18083 | MQTT Broker 及 Dashboard |
| InfluxDB | influxdb2 | 8086 | 8086 | 首次启动自动初始化组织、桶和 Token |

> 注意：InfluxDB 初始化参数通过环境变量注入，首次启动后需确保 Token 等信息与 `config.yaml` 匹配。

### 2. 后端
- 复制 `config.example.yaml` → `config.yaml`。
- 修改 `config.yaml`，填入数据库密码、MQTT 凭证、InfluxDB Token、JWT/AES 密钥，确保地址指向本机映射端口（如 `127.0.0.1:3307`）。
- 运行：`go run .` 或编译：`go build -o ilock_http_service . && ./ilock_http_service`。
- 若有数据库 schema 迁移，需在启动前执行（项目未提供 SQL 脚本时，GORM AutoMigrate 可能在代码中自动执行）。

### 3. 前端开发
- `cd ilock-http-frontend`
- 确保 `.env.development` 中 `VITE_API_BASE_URL` 和 `VITE_PROXY_TARGET` 配置正确（典型值为 `VITE_API_BASE_URL=/api`，`VITE_PROXY_TARGET=http://127.0.0.1:8080`）。
- `npm install && npm run dev`

### 4. 生产部署
- **前端**：`npm run build` 产出静态文件，部署至 Nginx 或由 Go 后端静态文件服务提供。
- **API 代理**：若使用 Nginx，将 `/api` 路径反向代理到后端 `127.0.0.1:8080`。
- **后端**：编译二进制，通过 systemd/supervisor 等守护进程运行，`config.yaml` 中的外部地址应指向实际网络可访问的中间件。

## 配置和密钥
以下列出所有需要提供的配置项键名，**实际值必须通过安全渠道获取，严禁提交到版本控制或写入本文档**。

### 后端配置 (`config.yaml`，模板见 `config.example.yaml`)

| 配置路径 | 环境变量 / 键名 | 说明 |
|----------|----------------|------|
| 服务器 | `server.port` | HTTP 监听端口 |
| 安全 | `server.jwt_secret` | JWT 签名密钥 |
| 安全 | `server.aes_secret` | AES 加密密钥（32 字节） |
| 数据库 | `database.dsn` | MySQL 连接串，格式：`user:password@tcp(host:port)/db?params` |
| Redis | `redis.addr` | 地址，如 `127.0.0.1:6379` |
| Redis | `redis.password` | 密码（若无则留空） |
| Redis | `redis.db` | 数据库编号 |
| MQTT | `mqtt.broker` | Broker 地址，如 `tcp://127.0.0.1:1883` |
| MQTT | `mqtt.username` | 连接用户名 |
| MQTT | `mqtt.password` | 连接密码 |
| MQTT | `mqtt.api_url` | EMQX HTTP API 地址，如 `http://127.0.0.1:18083/api/v5` |
| MQTT | `mqtt.api_key` | EMQX API Key |
| MQTT | `mqtt.api_secret` | EMQX API Secret |
| InfluxDB | `influxdb.url` | InfluxDB 地址，如 `http://127.0.0.1:8086` |
| InfluxDB | `influxdb.token` | 访问 Token |
| InfluxDB | `influxdb.org` | 组织名 |
| InfluxDB | `influxdb.bucket` | Bucket 名称 |

### 前端环境变量
**`.env.development` / `.env.production`**

| 变量名 | 说明 |
|--------|------|
| `VITE_API_BASE_URL` | API 基础路径（用于代理匹配或生产请求前缀） |
| `VITE_PROXY_TARGET` | Vite Dev Server 代理目标，指向前端开发时的后端地址 |

### 基础设施环境变量 (`docker-compose.yml`)
| 变量名 | 所属服务 | 说明 |
|--------|---------|------|
| `MYSQL_ROOT_PASSWORD` | MySQL | root 用户密码 |
| `DOCKER_INFLUXDB_INIT_USERNAME` | InfluxDB | 初始管理员用户名 |
| `DOCKER_INFLUXDB_INIT_PASSWORD` | InfluxDB | 初始管理员密码 |
| `DOCKER_INFLUXDB_INIT_ORG` | InfluxDB | 初始组织名 |
| `DOCKER_INFLUXDB_INIT_BUCKET` | InfluxDB | 初始 Bucket 名 |
| `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` | InfluxDB | 初始管理员 Token |

> 所有敏感值应通过环境变量注入系统或使用密钥管理服务，本地开发可用 `.env` 文件（确保被 `.gitignore` 排除）。

## 外部依赖
| 依赖 | 用途 | 必要 |
|------|------|------|
| MySQL | 业务数据存储 | 是 |
| Redis | 缓存 / 会话 / 临时状态 | 是 |
| EMQX | MQTT Broker，与智能锁设备通信 | 是 |
| InfluxDB 2.x | 时序数据存储（设备指标、事件）| 是 |
| MongoDB | go.mod 包含 mongo-driver 依赖，但当前基础设施未部署。需确认是否实际使用或未来计划。 | 待定 |

## 部署线索
- **中间件拓扑**：`docker-compose.yml` 描述了单机部署所有依赖，适合开发或小规模测试。
- **应用部署**：项目未提供后端的 Dockerfile，需自行构建镜像或直接部署二进制。前端构建产物为纯静态资源。
- **网络规划**：
  - 前端（浏览器） → Nginx/后端 → 后端 API `:8080`
  - 后端 → MySQL `:3307`、Redis `:6379`、EMQX `:1883/18083`、InfluxDB `:8086`
  - MQTT 设备 → EMQX `:1883`（可能由后端通过 MQTT 协议订阅主题）
- **数据持久化**：MySQL 与 InfluxDB 数据卷挂载，部署时需确保磁盘空间和备份策略。
- **生产加固**：
  - 为 Redis、EMQX、InfluxDB 配置验证和强密码。
  - 考虑开启 TLS（如 EMQX MQTTS、InfluxDB HTTPS）。
  - `jwt_secret` 和 `aes_secret` 使用足够强度的随机字符串。
  - EMQX Dashboard (18083) 和 InfluxDB UI (8086) 应限制公网访问。

## 复刻检查清单
按顺序操作即可从源码重建可运行环境：

1. **克隆仓库**，切换到目标分支（示例 `main`）。
2. **准备配置文件**：根据 `config.example.yaml` 创建 `config.yaml`，填写所有必需凭据和地址（参见配置和密钥章节）。
3. **修改 docker-compose 环境变量**：更新 `docker-compose.yml` 中的 `MYSQL_ROOT_PASSWORD`、InfluxDB 相关密码与 Token，确保与 `config.yaml` 中的值保持一致。
4. **启动依赖服务**：`docker-compose up -d`（所有中间件就绪）。
5. **数据库初始化**：
   - 若项目包含 SQL 迁移文件或种子脚本，按说明执行。
   - 若使用 GORM AutoMigrate，启动后端时会自动建表（需确认）。
6. **启动后端**：在项目根目录执行 `go run .` 或先编译再运行。
7. **启动前端开发模式**：
   - `cd ilock-http-frontend`
   - 复制 `.env.example` 为 `.env.development`（如不存在则直接配置 Vite 代理，参考 `vite.config.ts`）
   - `npm install && npm run dev`
8. **验证连通性**：通过浏览器访问前端，执行基本操作（登录、设备列表等），确认 API 成功返回数据且无 WebSocket/MQTT 错误。
9. **生产构建与部署**：
   - 前端 `npm run build`，将 `dist/` 部署到 Web 服务器。
   - 后端编译为二进制，使用进程守护工具运行，并配置反向代理。
10. **监控**：确认健康检查接口（如有），设置日志收集。

## 待补充信息
- **后端入口确切路径**：`main.go` 所在位置及项目文件结构（是否 `cmd/` 目录）。
- **数据库迁移策略**：是手动 SQL 还是自动迁移，有无版本化管理。
- **EMQX 配置细节**：`deploy/emqx/cluster.hocon` 中是否包含认证/授权插件、MQTT 用户凭证如何与后端同步。
- **MongoDB 使用情况**：`go.mod` 包含 `mongo-driver`，但未在依赖服务中部署，需明确是否废弃或用于特定功能。
- **设备通信协议**：MQTT 主题设计、消息格式、QoS 等，建议提供接口文档。
- **API 文档**：是否有 Swagger/OpenAPI 定义，或 Postman collection。
- **前端路由与权限**：页面清单、角色权限映射。
- **CI/CD**：自动化构建与部署流水线配置（如有）。
- **生产环境配置示例**：去除敏感信息的完整 `config.yaml` 样本，帮助理解各字段含义和格式。
- **监控与日志**：是用标准库还是集成方案，EMQX/InfluxDB 自身的监控端点。
- **许可证**：项目许可类型。

*以上信息需要在真实复刻或交接时向相关开发/运维人员确认。*
