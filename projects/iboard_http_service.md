# iboard_http_service

## 项目定位
iBoard 智能楼宇管理系统后端服务。基于 Go 实现，提供楼宇通知、广告管理、设备控制等功能的 RESTful API，并与旧系统 iSmart 进行通知数据同步。主要面向内部运营团队，支持超级管理员和楼宇管理员两级角色，通过 JWT 进行认证。

## 技术栈
- **语言**：Go 1.23
- **Web 框架**：Gin
- **ORM**：GORM (MySQL 驱动)
- **数据库**：MySQL 8.0
- **缓存**：Redis 7.4
- **认证**：JWT (`golang-jwt/jwt/v4`)
- **API 文档**：Swagger/OpenAPI (`swaggo`)
- **邮件**：go-gomail (SMTP)
- **密码处理**：golang.org/x/crypto
- **配置**：godotenv 加载 `.env`
- **部署**：Docker + Docker Compose (多阶段构建)

## 目录和入口
```
iboard_http_service/
├── cmd/server/          # 应用入口 (main.go)
├── internal/
│   ├── app/             # 控制器、中间件、路由
│   ├── domain/          # 数据模型、业务服务、服务容器
│   ├── error/           # 错误码、统一响应
│   └── infrastructure/  # 配置、数据库、Redis 初始化
├── pkg/                 # 可共享的工具包
├── docs/                # 文档 (API 文档、部署文档、错误说明)
├── scripts/             # 部署、迁移、更新脚本
├── migrations/          # 数据库迁移文件
├── mysql/               # MySQL 自定义镜像 (备份导入)
├── redis/               # Redis 自定义镜像 (持久化数据)
├── .env                 # 环境变量配置 (不进入版本控制)
├── docker-compose.yml
├── Dockerfile
├── go.mod
└── README.md
```
- 主程序入口：`cmd/server/main.go`
- 路由注册在 `internal/app/router` 中，API 前缀 `/api`
- 数据库模型位于 `internal/domain/models`
- 基础设施初始化在 `internal/infrastructure/config`、`database`、`redis`

## 运行与构建
### 本地开发和测试
依赖 Go 1.23+、MySQL、Redis 运行实例，并准备好 `.env` 文件。
```bash
# 安装依赖
go mod download

# 运行
go run ./cmd/server
```
服务默认监听 `10031` 端口（由 `SERVER_PORT` 或 `HTTP_HOST` 环境变量控制）。

### Docker 构建
使用多阶段构建，最终镜像基于 alpine，注入版本标签。
```bash
# 构建，可指定 VERSION 参数
docker build --build-arg VERSION=1.1.8 -t stonesea/iboard_http_service:1.1.8 .
```
构建产物中会复制 `.env` 文件到容器内 `/app/.env`。

### Docker Compose 部署
提供两套 Compose 文件：
- `docker-compose.yml`：使用项目自维护的镜像 `stonesea/iboard_http_service:1.1.8`、`stonesea/iboard-mysql:1.1.2`、`stonesea/iboard-redis:1.1.2`。MySQL 数据卷已命名。
- `10.7/docker-compose.yml`：使用官方镜像 `mysql:8.0`、`redis:7.4.1`，并挂载初始化脚本和 Redis 配置文件，适合自定义部署。

启动命令 (以根目录 Compose 为例)：
```bash
docker-compose up -d
```
服务监听端口映射：`10031:10031`，MySQL 对外 `3308:3306`，Redis `6379:6379`。

### 自动部署脚本
脚本 `docs/docs_deploy/deploy.sh` 以及 `scripts/deploy/` 下的脚本可用于自动部署、迁移和更新，需提前配置目标服务器信息。

## 配置和密钥
所有配置通过环境变量注入，敏感信息不硬编码。本地开发从 `.env` 文件加载，生产环境通过 Docker Compose `environment` 或容器编排平台密钥管理注入。

### 环境变量清单
以下列出所有已知变量的 **名称**，具体值仅配置于目标环境，不在本文档中公开。部分变量在 `docker-compose.yml` 中直接使用 `${VAR}` 引用 `.env` 文件或外部环境。

#### 数据库
- `DB_HOST` – MySQL 主机名（容器内一般为 `mysql`）
- `DB_PORT` – MySQL 端口（默认 3306）
- `DB_USER` – 数据库用户名（root）
- `DB_PASSWORD` – 数据库密码 **(敏感)**
- `DB_NAME` – 数据库名称 (`iboard_db`)
- `DB_TIMEZONE` – 数据库时区 (`Asia/Shanghai`)

#### Redis
- `REDIS_HOST` – Redis 主机名（容器内一般为 `redis`）
- `REDIS_PORT` – Redis 端口（默认 6379）
- `REDIS_PASSWORD` – Redis 密码 **(敏感)**
- `REDIS_DB` – Redis 数据库编号（例如 `0`）

#### 服务端口
- `SERVER_PORT` 或 `HTTP_HOST` – 服务监听地址/端口（容器内默认 `:10031`）

#### 文件/对象存储（推断为 OSS/S3）
- `ACCESS_KEY_ID` – 云存储 AccessKey ID **(敏感)**
- `ACCESS_KEY_SECRET` – 云存储 Secret Key **(敏感)**
- `HOST` – 存储服务 Endpoint（可能用于文件上传）  
- `CALLBACK_URL` – 文件上传回调地址
- `CALLBACK_URL_SYNC` – 文件同步回调地址

#### 邮件通知 (SMTP)
- `SMTP_ADDR` – SMTP 服务器地址
- `SMTP_PORT` – SMTP 端口
- `SMTP_USER` – SMTP 认证用户
- `SMTP_PASS` – SMTP 密码 **(敏感)**

#### 业务相关
- `DEVICE_HEALTH_TIMEOUT` – 设备健康超时
- `NOTICE_SYNC_INTERVAL` – 通知同步间隔
- `NOTICE_SYNC_BUILDING_CACHE_DURATION`
- `NOTICE_SYNC_CACHE_DURATION`
- `NOTICE_SYNC_COUNT_CACHE_DURATION`
- `LOG_FILE` – 日志文件路径

> 总计 27 个变量，其中 7 个为敏感凭证。所有敏感变量均以环境变量形式传入，未在 Compose 文件中明文硬编码（真实值时已使用 `<redacted>` 占位或通过外部注入）。

### 自定义 Docker 镜像中的固定凭证
- MySQL 容器需要 `MYSQL_ROOT_PASSWORD` 和 `MYSQL_DATABASE`。
- Redis 可能通过持久化文件初始化，但也支持 `REDIS_PASSWORD` 环境变量。

## 外部依赖
| 依赖 | 用途 | 备注 |
|------|------|------|
| MySQL 8.0 | 主业务数据库 | 使用 GORM 自动迁移，或通过 `migrations/` 手动管理。自定义镜像 `stonesea/iboard-mysql` 包含备份导入。 |
| Redis 7.4 | 缓存、通知同步去重、建筑物缓存 | 使用 `go-redis/v8`。自定义镜像 `stonesea/iboard-redis` 包含 `dump.rdb` 数据。 |
| 云对象存储 (推测阿里云 OSS 或 S3 兼容) | 文件上传（广告素材等） | 通过 `ACCESS_KEY_ID`、`ACCESS_KEY_SECRET`、`HOST` 连接。上传后由 `CALLBACK_URL` 通知。 |
| SMTP 邮件服务 | 邮件发送（告警等） | 使用 `gopkg.in/gomail.v2`。 |
| iSmart 旧系统 | 通知数据同步 | 系统内部定时和手动触发的通知同步，依赖旧系统 API（未在文档中明确 URL）。 |

## 部署线索
1. **容器编排**：优先使用提供的 `docker-compose.yml`，后端、MySQL、Redis 组成服务栈，共享 `iboard-network` 桥接网络。
2. **端口映射**：
   - 后端服务：容器 `10031` → 宿主机 `10031`
   - MySQL：容器 `3306` → 宿主机 `3308`（注意并非默认端口，避免冲突）
   - Redis：默认 `6379:6379`
3. **数据持久化**：
   - MySQL 数据：命名卷 `iboard_mysql_data1.1.2`（或 `iboard_mysql_data`）
   - Redis 数据：命名卷 `iboard_redis_data1.1.2`（或 `redis_data`）
   - 应用日志：挂载 `./logs` → 容器 `/app/logs`
4. **镜像来源**：
   - 生产环境可使用 `stonesea/iboard_http_service:1.1.8`
   - MySQL 与 Redis 可使用 `stonesea/iboard-mysql:1.1.2` 和 `stonesea/iboard-redis:1.1.2`，这些镜像预装了初始数据或 RDB 文件。
5. **启动顺序**：后端 `depends_on` mysql 和 redis，确保数据库和缓存先就绪。
6. **反向代理**：服务本身未配置 TLS，若需 HTTPS，建议在前置 Nginx/Caddy 终止 TLS，并将请求转发至 `10031`。
7. **自定义初始化**：`10.7/docker-compose.yml` 中使用了 `mysql_init` 目录和 `redis_config/redis.conf` 自定义初始化，可按需参考。
8. **健康检查**：可通过 `GET /api/ping` 检测服务状态。

## 复刻检查清单
在新环境部署时，请逐项确认：

- [ ] Git 仓库可访问：`origin https://github.com/The-Healthist/iboard_http_service.git`
- [ ] 准备 `.env` 文件（或环境变量注入）补充以下信息：
  - [ ] 数据库连接 (host, port, user, password, dbname)
  - [ ] Redis 连接及密码
  - [ ] 云存储 AccessKey (`ACCESS_KEY_ID`, `ACCESS_KEY_SECRET`, `HOST`)
  - [ ] 回调 URL (`CALLBACK_URL`, `CALLBACK_URL_SYNC`)
  - [ ] SMTP 邮件配置 (addr, port, user, pass)
  - [ ] 其他业务参数（同步间隔等）
- [ ] 选择 Docker Compose 模板（主版本或 `10.7` 自定义版），检查卷定义和端口映射是否与目标环境冲突。
- [ ] 如需自定义数据初始化，准备 MySQL 导入脚本 (`iboard_db_backup.sql`) 和 Redis 持久化文件 (`redis_dump.rdb`)。
- [ ] 确认目标服务器已安装 Docker 和 Docker Compose。
- [ ] 验证目标端口防火墙规则：`10031` (API), `3308` (MySQL, 可选), `6379` (Redis, 可选)
- [ ] 如需访问外部旧系统 iSmart 进行同步，准备 iSmart API 端点及凭据（配置在 `.env` 中或代码内部，需进一步确认）。
- [ ] 部署后执行 `curl http://<server_ip>:10031/api/ping` 验证服务。
- [ ] 检查数据库迁移状态（容器启动后自动迁移，或手动执行迁移脚本）。
- [ ] 配置日志收集（容器内日志输出至挂载卷 `./logs`，可接入日志系统）。

## 待补充信息
- **iSmart 旧系统同步**：同步的具体 API 地址、认证方式及参数未在文档中体现，需从代码或业务方获取。
- **云存储服务商**：`ACCESS_KEY_ID` 等具体指的是阿里云 OSS 还是其他 S3 兼容服务，需要根据实际配置确认。
- **域名与反向代理**：生产环境是否使用域名、HTTPS 证书在哪里管理、是否有 WAF 等，未记录。
- **监控与告警**：目前只有 SMTP 邮件配置，是否接入 Prometheus 或其他监控系统未知。
- **自动化 CI/CD**：未见 CI 配置（如 GitHub Actions），镜像构建和推送流程需补充。
- **高可用与扩展**：MySQL、Redis 是否做了主从或集群，后端是否支持水平扩展，均待明确。
