# iNtercom_http_service

## 项目定位

基于 Go 语言开发的楼宇对讲后端服务，提供视频通话、设备联动（智能门锁）、门禁控制和紧急情况处理能力。系统通过 RESTful API 与 MQTT 实时消息配合，支撑访客呼叫、居民接听、设备控制与告警联动等场景。支持阿里云 RTC 和腾讯云 TRTC 两种音视频通道，实际部署以腾讯云 TRTC 为主。系统设计为容器化交付，可借助 Docker Compose 快速搭建运行环境。

## 技术栈

- **语言与运行时**：Go 1.23
- **HTTP 框架**：Gin v1.10
- **ORM**：GORM v1.25（驱动 `gorm.io/driver/mysql`）
- **MQTT 客户端**：Eclipse Paho MQTT v1.5
- **缓存**：Redis 7.0（客户端 `github.com/go-redis/redis/v8`）
- **鉴权**：JWT (`github.com/golang-jwt/jwt/v4`)
- **音视频 RTC**：腾讯云 TRTC（SDK `github.com/tencentyun/tls-sig-api-v2-golang`）
- **数据库**：MySQL 8.0
- **消息代理**：Eclipse Mosquitto 2.0（或其他兼容 MQTT 3.1.1/5.0 的 broker）
- **容器化**：Docker + Docker Compose（多阶段构建，vendor 模式零网络依赖）
- **辅助工具**：frp（内网穿透，可选）

## 目录和入口

项目采用清晰的分层架构，主入口为 `cmd/server`：

```
intercom_http_service/
├── cmd/
│   └── server/            # 应用入口 (main.go)
├── internal/
│   ├── app/
│   │   ├── controllers/   # 请求处理
│   │   ├── middleware/     # 中间件（认证、缓存、限流）
│   │   └── routes/        # 路由注册
│   ├── domain/
│   │   ├── models/        # 数据模型（GORM）
│   │   └── services/      # 业务逻辑层
│   │       └── container/ # 服务容器/依赖注入
│   ├── error/
│   │   ├── code/          # 错误码
│   │   └── response/      # 统一响应结构
│   ├── infrastructure/
│   │   ├── config/        # 配置加载（godotenv）
│   │   ├── database/      # 数据库连接池
│   │   └── mqtt/          # MQTT 连接与配置
│   └── test/
│       └── benchmark/     # 性能测试
├── pkg/
│   ├── logger/            # 日志工具
│   ├── utils/             # 通用工具
│   └── validator/         # 输入校验
├── docs/                  # API 文档、部署文档、Swagger 定义
├── scripts/
│   ├── deploy/            # 部署脚本（deploy_to_server.sh 等）
│   ├── migrate/           # 备份/迁移/回滚脚本
│   └── lint.sh            # 代码检查
├── logs/                  # 应用日志目录
├── Dockerfile
├── docker-compose.yml
├── go.mod
├── go.sum
└── .env.example / .env    # 环境变量模板
```

编译入口：`cmd/server` 下的 `main.go`，构建产物为 `main`，运行时依赖于 `.env` 中的配置（通过 `godotenv` 加载）。

## 运行与构建

### 本地构建（二进制）

```bash
# 进入项目根目录
go build -mod=vendor -ldflags="-s -w" -o main ./cmd/server
./main
```

构建采用 `-mod=vendor` 模式，要求仓库中已包含完整的 `vendor` 目录。Go 版本要求 1.23。

### 容器化构建（推荐）

Dockerfile 采用多阶段构建，最终镜像仅保留二进制、文档、CA 证书：

```bash
docker build -t intercom_http_service .
```

构建基础镜像：`golang:1.23.0-alpine`（构建阶段）→ `alpine:latest`（运行阶段）。  
运行容器可用 `docker run` 挂载 `.env` 并暴露端口，或配合 `docker-compose` 管理依赖。

### Docker Compose 环境

仓库提供的 `docker-compose.yml` 定义了基础依赖服务，未包含应用本身的服务定义：

- **MySQL 8.0**（容器名 `intercom_mysql`），端口映射 `3310:3306`，持久化卷 `intercom_mysql_data`。
- **Redis 7.0-alpine**（容器名 `intercom_redis`），端口映射 `6380:6379`，持久化卷 `intercom_redis_data`。
- **frpc**（内网穿透客户端），依赖自定义配置文件 `./frp/frpc.toml`。

应用容器需单独启动或通过部署脚本编排。部署脚本 `scripts/deploy/deploy_to_server.sh` 可用于自动化部署整个系统（包括应用、MQTT、Nginx 等）。

### 健康检查

- 应用容器内：`wget -qO- http://localhost:8080/api/ping`（Dockerfile 声明 `HEALTHCHECK`）。
- MySQL 容器：`mysqladmin ping`。
- Redis 容器：`redis-cli ping`。
- 部署后外部检查：`curl http://<服务器IP>:20033/api/ping`（根据部署文档，HTTP 服务对外暴露端口为 `20033`）。

### 端口说明

- 应用服务：Dockerfile 中 `EXPOSE 8080`，部署文档外部访问使用 `20033`（可能通过反向代理或 frp 映射）。
- MySQL：对外 `3310`（内部 `3306`）。
- Redis：对外 `6380`（内部 `6379`）。
- MQTT：通常需要 `1883`（TCP）、`8883`（SSL）、`9001`（WebSocket），需单独部署 Mosquitto 或使用云端 broker。

## 配置和密钥

应用通过 `.env` 文件配置，使用 `github.com/joho/godotenv` 加载。仓库中不应包含真实凭据，所有敏感值均需在部署时注入。以下为 `.env` 包含的变量 **名称**，不写入任何值：

| 变量名 | 用途 | 敏感性 |
|--------|------|--------|
| `APP_ENV_TYPE` | 应用环境标识（如 `production`, `development`） | 否 |
| `APP_MQTT_BROKER_URL` | MQTT broker 连接地址 | 否 |
| `APP_MQTT_CA_CERT_PATH` | MQTT CA 证书路径（TLS 时使用） | 否 |
| `APP_MQTT_SSL_ENABLED` | 是否启用 MQTT SSL | 否 |
| `APP_SERVER_DB_HOST` | 主数据库地址 | 否 |
| `APP_SERVER_DB_NAME` | 主数据库名 | 否 |
| `APP_SERVER_DB_PASSWORD` | 主数据库密码 | **高度敏感** |
| `APP_SERVER_DB_PORT` | 主数据库端口 | 否 |
| `APP_SERVER_DB_USER` | 主数据库用户名 | 否 |
| `DEFAULT_ADMIN_PASSWORD` | 默认管理员密码 | **敏感** |
| `ENV_TYPE` | 环境类型（可能同 `APP_ENV_TYPE`） | 否 |
| `LOCAL_DB_HOST` | 本地数据库地址（开发/迁移用） | 否 |
| `LOCAL_DB_NAME` | 本地数据库名 | 否 |
| `LOCAL_DB_PASSWORD` | 本地数据库密码 | **敏感** |
| `LOCAL_DB_PORT` | 本地数据库端口 | 否 |
| `LOCAL_DB_USER` | 本地数据库用户名 | 否 |
| `LOCAL_REDIS_HOST` | 本地 Redis 地址 | 否 |
| `LOCAL_REDIS_PORT` | 本地 Redis 端口 | 否 |
| `LOCAL_SERVER_PORT` | 应用监听端口（可能覆盖默认） | 否 |
| `MQTT_BROKER_URL` | MQTT broker URL（可能与应用变量重复） | 否 |
| `MQTT_CLIENT_ID` | MQTT 客户端 ID | 否 |
| `MQTT_PASSWORD` | MQTT 连接密码 | **敏感** |
| `MQTT_QOS` | MQTT 服务质量等级 | 否 |
| `MQTT_SSL_ENABLED` | MQTT 是否启用 SSL | 否 |
| `MQTT_USERNAME` | MQTT 连接用户名 | 否 |
| `MYSQL_DATABASE` | Docker Compose 中 MySQL 默认数据库（由 `docker-compose.yml` 传递） | 否 |
| `MYSQL_ROOT_PASSWORD` | Docker Compose 中 MySQL root 密码 | **高度敏感** |
| `TENCENT_RTC_ENABLED` | 是否启用腾讯云 TRTC | 否 |
| `TENCENT_SDKAPPID` | 腾讯云 TRTC 应用 ID | 否（但需保密） |
| `TENCENT_SECRET_KEY` | 腾讯云 TRTC 密钥 | **高度敏感** |

**特别注意**：
- 生产环境严禁在版本控制中提交 `.env`。建议使用密钥管理服务（如 HashiCorp Vault）或 CI/CD 注入变量。
- `MYSQL_ROOT_PASSWORD` 同时出现在 `docker-compose.yml` 的环境变量及 healthcheck 命令中，需保持一致。
- 数据库密码、MQTT 密码、TRTC 密钥必须替换为强随机字符串，默认值或示例密码一律禁用。

## 外部依赖

| 依赖项 | 版本/镜像 | 用途 | 必选 |
|--------|-----------|------|------|
| MySQL | 8.0（镜像 `mysql:8.0`） | 业务数据持久化 | 是 |
| Redis | 7.0-alpine（`redis:7.0-alpine`） | 缓存与会话（连接池、限流、中间件） | 是 |
| MQTT Broker | Eclipse Mosquitto 2.0 或兼容服务 | 实时消息推送、视频通话信令 | 是（如需实时通信） |
| 腾讯云 TRTC | 通过 SDK 调用 | 音视频通话能力 | 可选（`TENCENT_RTC_ENABLED=true` 时启用） |
| frp | `fatedier/frpc:latest` | 内网穿透（可选，用于开发或私有化部署） | 否 |

所有依赖均可通过 Docker Compose 启动，MQTT broker 需单独提供部署配置（`docker-compose.yml` 中未包含 Mosquitto 服务定义）。

## 部署线索

### 仓库信息

- **上游仓库**：`https://github.com/The-Healthist/iNtercom_http_service.git`
- **当前扫描分支**：`main`（commit `0a216d2`，2026-05-01）
- **目录位置**：`intercom/iNtercom_http_service`
- 工作区整洁，无未提交改动。

### 容器化部署核心

- `Dockerfile`：多阶段构建，产物仅含 `main` 二进制、`docs/`、CA 证书；运行用户 root（生产可考虑非 root）。
- `docker-compose.yml`：启动 MySQL + Redis + frpc，网络 `intercom_network`。
- 完整部署需额外启动 Mosquitto 容器或指向外部 MQTT 地址。

### 部署脚本

- `scripts/deploy/deploy_to_server.sh`：自动化部署入口，需编辑脚本中的服务器 IP、用户等信息。
- 迁移脚本：`scripts/migrate/backup.sh`、`migrate.sh`、`rollback.sh` 用于数据搬迁与回滚。

### 端口与访问

- 应用 HTTP：Dockerfile `EXPOSE 8080`，部署后外部访问端口 `20033`（由部署脚本或反向代理提供）。
- Swagger UI：`http://<IP>:20033/swagger/index.html`（部署成功后）。
- API 健康检查：`/api/ping` 和 `/api/health/status`。
- JWT 鉴权端点：`/api/auth/login`。

### 数据库迁移

项目支持 GORM AutoMigrate，启动时自动创建/更新表结构。首次部署后应检查默认管理员账号的创建逻辑（`DEFAULT_ADMIN_PASSWORD`）。

## 复刻检查清单

从零复刻该服务并运行至可用状态，需按顺序完成以下步骤：

1. **克隆仓库**  
   ```bash
   git clone https://github.com/The-Healthist/iNtercom_http_service.git
   cd intercom_http_service
   git checkout main
   ```

2. **准备环境配置文件**  
   - 复制 `.env.example`（或新建 `.env`），填入上述所有变量。  
   - 至少补全数据库、MQTT、腾讯云TRTC（如需）及管理员密码相关变量。  
   - 确认 `MYSQL_ROOT_PASSWORD` 与 `docker-compose.yml` 中一致。

3. **启动基础依赖**  
   ```bash
   docker-compose up -d
   ```
   等待 `db`、`redis`、`frpc`（可选）健康检查通过。

4. **部署 MQTT Broker**（若未用外部 broker）  
   - 使用 `eclipse-mosquitto:2.0` 镜像启动，配置匿名访问或用户名密码，并与应用中的 `MQTT_USERNAME`/`MQTT_PASSWORD` 匹配。  
   - 公开端口 `1883`、`8883`、`9001`，加入同一 Docker 网络或可被应用访问。

5. **构建并启动应用**  
   - 若采用脚本部署：执行 `./scripts/deploy/deploy_to_server.sh -s <服务器IP> -u <用户>`（需提前配置脚本内的路径、端口等）。  
   - 若手动：构建镜像后运行容器，挂载 `.env`，确保网络连通，或直接运行二进制。

6. **验证服务**  
   - `curl http://<IP>:20033/api/ping` 应返回成功。  
   - 通过 Swagger (`/swagger/index.html`) 测试登录接口，确认数据库表已自动创建。

7. **检查日志与监控**  
   - `docker-compose logs app` 或容器日志查看启动错误。  
   - 确保 MQTT 客户端成功连接，RabbitMQ 类错误需检查 broker 地址及证书。

8. **补充管理员账号**（若未自动创建）  
   - 可能需要通过数据库手动插入或执行初始化脚本。

9. **配置 TRTC**（可选）  
   - 在腾讯云控制台获取 `SDKAppID` 和 `SecretKey`，填入 `.env`，设置 `TENCENT_RTC_ENABLED=true`。

10. **更新部署文档**  
    - 将实际使用的域名、证书路径、回调地址写入运维手册。

## 待补充信息

- **MQTT broker 部署细节**：`docker-compose.yml` 中无 Mosquitto 服务定义，需要提供的 `mosquitto.conf` 及 ACL 配置未在仓库中展示，部署时需自行准备或使用云服务。
- **应用监听端口与外部端口的映射**：Dockerfile 暴露 `8080`，部署文档使用 `20033`，中间是否存在 Nginx/HAProxy 或 frp 转发规则，需从部署脚本或运维配置中获得，当前未明确。
- **生产环境域名和 HTTPS**：文档未提及域名、SSL 证书配置及 API 回调域名（如 TRTC 回调），生产部署时需补充。
- **TRTC 回调地址和权限**：若启用腾讯云 TRTC，需配置回调服务地址，相关实现细节（如接收 TRTC 事件的端点）在代码中是否完整未核实。
- **数据库初始化数据**：除自动建表外，是否存在初始管理员账号或其他必需种子数据？文档提及 `DEFAULT_ADMIN_PASSWORD`，但创建逻辑未描述。
- **持久化卷管理**：生产环境 MySQL 和 Redis 的备份策略、持久化卷挂载路径与宿主机映射，需根据实际部署规划。
- **CI/CD 集成**：未提供持续集成配置，自动化构建和部署流程需从零建立。
- **安全加固建议**：容器以 root 运行、MySQL root 密码明文传递，生产环境需调整用户权限并使用 secrets 管理。
