# ILock_http_service

## 项目定位

iLock 智能门禁系统后端 HTTP 服务，提供门禁控制、视频通话信令、紧急事件处理等业务 API。系统面向小区/楼宇场景，支持管理员、物业人员、居民等多角色权限管理，集成阿里云 RTC 与腾讯云 TRTC 实现音视频通话，并通过 MQTT 实时推送设备控制、通话状态等消息。本项目以容器化方式交付，供运维团队通过 Docker Compose 一键部署。

- 内部代号：ILock_http_service
- 镜像仓库：`stonesea/ilock-http-service:2.3.0`
- 代码仓库：`https://github.com/The-Healthist/iNtercom_http_service`（origin）
- 最近提交：`9f0fc86` – 修复与整理提交

## 技术栈

- **语言 / 运行时**：Go (go.mod 声明 `go 1.23.0`，构建镜像使用 Go 1.21 alpine)
- **Web 框架**：Gin (`github.com/gin-gonic/gin`)
- **ORM**：GORM (`gorm.io/gorm`)，驱动：`gorm.io/driver/mysql`
- **数据库**：MySQL 8.0
- **缓存**：Redis 7.0（通过 `go-redis/redis/v8` 访问）
- **消息队列**：Eclipse Mosquitto 2.0（MQTT 协议），客户端库 `github.com/eclipse/paho.mqtt.golang`
- **认证**：JWT（`github.com/golang-jwt/jwt/v4`）
- **视频通话**：阿里云 RTC（SDK 未在 go.mod 显式列出，但环境变量存在），腾讯云 TRTC（`github.com/tencentyun/tls-sig-api-v2-golang` 用于签名）
- **文档**：Swagger（`github.com/swaggo/gin-swagger`）
- **部署**：Docker + Docker Compose，多阶段 Dockerfile，辅助 Shell 脚本

## 目录和入口

```
ILock_http_service/
├── cmd/server/                  # 应用入口，主程序 main
├── internal/
│   ├── app/
│   │   ├── controllers/         # HTTP 控制器
│   │   ├── middleware/          # 中间件（认证、限流、缓存等）
│   │   └── routes/              # 路由注册
│   ├── domain/
│   │   ├── models/              # GORM 数据模型
│   │   └── services/            # 业务服务层
│   │       └── container/       # 服务容器/依赖注入
│   ├── error/
│   │   ├── code/                # 错误码定义
│   │   └── response/            # 统一响应格式
│   ├── infrastructure/
│   │   ├── config/              # 配置加载（从 .env 读取）
│   │   ├── database/            # MySQL 连接池初始化
│   │   └── mqtt/                # MQTT 客户端配置及本地 broker 配置文件、数据、证书
│   └── test/benchmark/          # 性能测试
├── pkg/
│   ├── logger/                  # 日志工具
│   ├── utils/                   # 通用函数
│   └── validator/               # 请求校验
├── docs/                        # 文档、Swagger 规范、API 说明
├── scripts/
│   ├── deploy/                  # 部署脚本（build_and_push.sh, deploy_to_server.sh）
│   ├── migrate/                 # 数据迁移脚本（备份、迁移、回滚）
│   └── lint.sh                  # 代码检查
├── docker-compose.yml
├── Dockerfile
├── go.mod / go.sum
└── .env                         # 本地/生产环境变量（敏感，不入库）
```

- **编译入口**：`cmd/server/main.go`（程序包路径 `./cmd/server`），通过 `go build -o main ./cmd/server` 生成二进制。
- **运行时入口**：容器内 `/app/cmd/server/main`。

## 运行与构建

### 构建制品

- **本地编译**：在项目根目录执行
  ```bash
  go build -o main ./cmd/server
  ```
  需要 Go 1.21+ 环境及配置好依赖代理（如 `GOPROXY=https://goproxy.cn,direct`）。
- **Docker 镜像构建**：使用根目录 Dockerfile，两阶段构建：
  1. `golang:1.21.0-alpine` 编译，开启 `CGO_ENABLED=0`，最终产物带 `-ldflags="-s -w"` 压缩。
  2. 运行阶段基于 `alpine:latest`，安装 ca-certificates、tzdata、curl，暴露 20033，启动命令：`/app/cmd/server/main`。
  构建命令：
  ```bash
  docker build -t stonesea/ilock-http-service:2.3.0 .
  ```

### 运行环境

- **容器化运行**：整体通过 `docker-compose.yml` 定义，包含 `app`、`db`、`redis`、`mqtt` 四个服务，使用自定义网络 `ilock_network`，并挂载必要卷。
- **应用服务**：
  - 端口映射：`20033:20033`
  - 挂载 `./.env` 到容器内 `/app/.env`，以及 `./logs` 到 `/app/logs`。
  - 环境变量：见配置章节；通过 `ENV_TYPE=SERVER` 控制为服务端模式。
  - 健康检查：`curl -f http://localhost:20033/api/health`，每 30 秒执行一次。
- **数据库**：
  - MySQL 8.0，端口映射 `3310:3306`，数据卷 `ilock_mysql_data` 挂载至 `/var/lib/mysql`。
  - 启动参数：`max_connections=1000`，`innodb_buffer_pool_size=1G`。
  - 健康检查：`mysqladmin ping`。
- **缓存**：
  - Redis 7.0-alpine，端口映射 `6380:6379`，数据卷 `ilock_redis_data`，持久化开启 AOF，最大内存 512MB，淘汰策略 `allkeys-lru`。
  - 健康检查：`redis-cli ping`。
- **消息队列**：
  - Eclipse Mosquitto 2.0，端口映射 `1884:1883`（MQTT）、`8883:8883`（MQTT over TLS）、`9001:9001`（WebSocket）。
  - 配置文件、数据、日志、证书从 `internal/infrastructure/mqtt/` 下的对应目录挂载。
  - 健康检查：通过 `mosquitto_sub` 检测 `$SYS/#` 主题。
- **启动与停止**：
  ```bash
  docker-compose up -d      # 启动全部服务
  docker-compose down       # 停止并移除容器
  ```
- **本地调试**：可单独启动 `go run ./cmd/server`，但需自行提供 MySQL、Redis、MQTT 实例，并在 `.env` 中配置连接信息（如 `LOCAL_DB_HOST` 等）。

## 配置和密钥

所有敏感值均存储于 `.env` 文件（未纳入版本控制）。本节仅列出环境变量 key 名称及用途，**不包含任何 secret value**。真实凭据请从私密备份 `private/env-backup/` 获取。

### 全局 / 运行模式

- `ENV_TYPE`：运行环境，取值 `SERVER` 代表生产/服务器模式。
- `TZ`：时区设置。

### 数据库

**本地 / 开发环境（LOCAL_*）**

- `LOCAL_DB_HOST`
- `LOCAL_DB_PORT`
- `LOCAL_DB_USER`
- `LOCAL_DB_PASSWORD`
- `LOCAL_DB_NAME`
- `LOCAL_DB_TIMEZONE`
- `LOCAL_DB_MIGRATION_MODE`：数据库迁移策略（例如 auto/alter/drop）

**服务器 / 生产环境（SERVER_*）**

- `SERVER_DB_HOST`
- `SERVER_DB_PORT`
- `SERVER_DB_USER`
- `SERVER_DB_PASSWORD`
- `SERVER_DB_NAME`
- `SERVER_DB_TIMEZONE`
- `SERVER_DB_MIGRATION_MODE`

**MySQL 容器用**

- `MYSQL_ROOT_PASSWORD`：MySQL root 密码（敏感）
- `MYSQL_DATABASE`：自动创建的数据库名

### Redis

- `LOCAL_REDIS_HOST` / `LOCAL_REDIS_PORT`
- `SERVER_REDIS_HOST` / `SERVER_REDIS_PORT`
- `REDIS_PASSWORD`（敏感）
- `REDIS_DB`

### MQTT

- `MQTT_BROKER_URL`：消息队列地址，如 `tcp://mqtt:1883`
- `MQTT_CLIENT_ID`
- `MQTT_USERNAME` / `MQTT_PASSWORD`（敏感）
- `MQTT_USE_TLS`
- `MQTT_TLS_SKIP_VERIFY`
- `MQTT_CONNECT_TIMEOUT`
- `MQTT_KEEP_ALIVE`
- `MQTT_RECONNECT_INTERVAL`

### JWT 与安全

- `JWT_SECRET_KEY`：用于 JWT 签名（敏感）
- `DEFAULT_ADMIN_PASSWORD`：默认管理员初始密码（敏感）

### 第三方 RTC 服务

**阿里云 RTC**

- `ALIYUN_ACCESS_KEY`（敏感）
- `ALIYUN_RTC_APP_ID`
- `ALIYUN_RTC_REGION`

**腾讯云 TRTC**

- `TENCENT_RTC_ENABLED`：是否启用腾讯云 TRTC
- `TENCENT_SDKAPPID`
- `TENCENT_SECRET_KEY`（敏感）

### 服务器端口

- `LOCAL_SERVER_PORT`：应用监听端口（如 20033）
- `SERVER_SERVER_PORT`：生产环境应用端口

### Docker 部署辅助

- `DOCKER_USERNAME`：用于推送镜像的 Docker Hub 用户名

## 外部依赖

- **MySQL 8.0**（必需）：存储所有业务数据，通过 GORM 管理表结构，应用启动时可自动执行数据库迁移（根据 `*_DB_MIGRATION_MODE` 配置）。
- **Redis 7.0**（必需）：用于缓存、限流、会话等场景。
- **Eclipse Mosquitto 2.0**（必需）：MQTT broker，负责实时消息推送、设备控制指令和视频通话信令；需要提供 ACL 和认证配置（见 `internal/infrastructure/mqtt/config/`）。
- **阿里云 RTC**（可选）：提供音视频通话能力，需有效的 AccessKey、AppId。
- **腾讯云 TRTC**（可选）：与阿里云 RTC 互备，需 SDKAppID 和 SecretKey。
- **Docker Hub**：拉取预构建镜像 `stonesea/ilock-http-service:2.3.0`，或从本仓库自建。
- **Gin Swagger**：API 文档由 Swagger UI 提供，`docs/` 下的 swagger 文件需随镜像一同部署。

## 部署线索

### 基础架构

- 所有服务均通过 `docker-compose.yml` 编排，网络名称：`ilock_network`（bridge）。
- 应用依赖数据库、Redis、MQTT 的健康检查（`depends_on condition: service_healthy`）后才启动。
- 数据持久化依赖命名卷 `ilock_mysql_data` 和 `ilock_redis_data`，需注意备份，迁移时参考 `scripts/migrate/` 中的脚本。

### 端口映射（宿主机 -> 容器）

| 服务 | 宿主机端口 | 容器端口 | 说明 |
|------|------------|----------|------|
| app  | 20033      | 20033    | HTTP API / Swagger |
| db   | 3310       | 3306     | MySQL 外部连接 |
| redis| 6380       | 6379     | Redis 外部连接 |
| mqtt | 1884       | 1883     | MQTT TCP |
|      | 8883       | 8883     | MQTT over TLS |
|      | 9001       | 9001     | MQTT WebSocket |

实际部署时请根据网络安全策略开放相应端口，生产环境建议只对外暴露 `20033` 及 MQTT 相关端口（如有设备直连需求）。

### 部署操作

- **快速部署**（已有镜像）：在项目根目录备好 `.env` 文件，执行：
  ```bash
  docker-compose up -d
  ```
- **自构建并推送**：编辑 `scripts/deploy/build_and_push.sh`，设置 Docker Hub 用户等信息后执行。
- **远程服务器部署**：使用 `scripts/deploy/deploy_to_server.sh -s <server-ip> -u root`，脚本会同步配置、拉起服务。详细步骤见同目录下的《原有数据卷保留部署指南》。
- **首次部署后验证**：
  ```bash
  curl http://<server-ip>:20033/api/health
  curl http://<server-ip>:20033/api/ping
  ```
  浏览器访问 `http://<server-ip>:20033/swagger/index.html` 确认 API 文档可用。
- **MQTT 配置**：确保 `internal/infrastructure/mqtt/config/mosquitto.conf` 以及 ACL 文件已准备，若需 TLS 则需要证书文件。

### 运维注意事项

- 数据库 root 密码和 MQTT 用户凭证需与 `.env` 中定义一致，修改后需同步更新 docker-compose.yml 中的环境变量占位符或直接引用 `.env` 变量。
- `ENV_TYPE=SERVER` 会控制应用读取 `SERVER_*` 系列变量，确保 docker-compose 中已注入该变量。
- 容器日志挂载在本地 `./logs`，可配合日志收集系统。
- Swagger JSON/YAML 文件位于 `docs/`，镜像内放置于 `/app/docs`，应用启动时会自动加载。

## 复刻检查清单

1. **获取代码**：`git clone <repo-url> && cd ILock_http_service`
2. **准备私密配置**：
   - 从 `private/env-backup/` 恢复 `.env` 文件，或根据章节“配置和密钥”创建 `.env`，填入所有必需变量（包括数据库、Redis、MQTT、JWT、RTC 等凭据）。
   - （可选）若需推送镜像，准备 `DOCKER_USERNAME` 并在构建脚本中配置 Docker Hub 认证。
3. **MQTT 配置检查**：确认 `internal/infrastructure/mqtt/config/` 下存在有效的 `mosquitto.conf`、`acl.conf`，如需 TLS 则提供证书到 `certs/` 目录。
4. **审查 docker-compose.yml**：根据目标环境调整端口映射、数据卷名称、环境变量引用（例如 `MYSQL_ROOT_PASSWORD` 是否从 `.env` 读取）。
5. **构建镜像（可选）**：若使用自建镜像，执行 `docker build -t stonesea/ilock-http-service:2.3.0 .`，并可运行 `scripts/deploy/build_and_push.sh` 推送至仓库。
6. **启动服务**：`docker-compose up -d`
7. **验证状态**：
   - 各容器健康检查通过（`docker-compose ps`）
   - `curl localhost:20033/api/health` 返回正常
   - 访问 Swagger 文档：`http://<host>:20033/swagger/index.html`
8. **初始化管理员**：使用环境变量 `DEFAULT_ADMIN_PASSWORD` 登录，或根据业务逻辑创建初始管理员账号。
9. **网络与安全**：配置防火墙仅放通所需端口；如有公网访问需求，部署反向代理并配置域名及 SSL。
10. **数据备份**：设置定期备份 MySQL 数据和 Redis AOF 文件，可结合 `scripts/migrate/backup.sh` 思路。

## 待补充信息

- **生产域名与 SSL 证书**：目前未发现配置，若提供外部访问需补充域名、TLS 证书及反向代理（如 Nginx）设置。
- **阿里云 RTC / 腾讯云 TRTC 详细参数**：如回调地址、录制配置等业务细节未在文档中体现。
- **MQTT 主题与 ACL 完整设计**：当前文档仅列主题示例，完整 ACL 规则需从 `internal/infrastructure/mqtt/config/acl.conf` 确认。
- **数据库初始化数据**：是否包含默认楼栋、设备、管理员账号等种子数据，迁移策略（alter/drop）对生产环境的影响需明确。
- **日志与监控**：容器日志仅本地挂在 `./logs`，建议接入集中日志系统（ELK/Loki）和监控告警（Prometheus 指标目前未暴露）。
- **CI/CD 流水线**：仓库未提供 GitHub Actions 或其他 CI 配置，自动化构建、测试、部署需另行搭建。
- **扩展性**：若计划横向扩展 app 实例，需评估数据库、Redis、MQTT 的水平扩展方案及会话亲和性策略。
