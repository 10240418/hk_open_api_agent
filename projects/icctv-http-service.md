# icctv-http-service

## 项目定位
OrangePi 后台管理系统 HTTP 服务端，提供管理员、建筑、NVR、OrangePi 设备管理及绑定等 RESTful API，同时管理设备公网配置与远程端口更新。服务面向内部运维与设备集成，需要管理员认证（JWT）和长期/永久 Token 机制。

## 技术栈
- 语言：Go 1.24.5
- Web 框架：标准库（net/http）为主，依赖注入自行实现
- ORM：GORM（支持 MySQL 与 SQLite 驱动）
- 认证：JWT（golang-jwt/jwt/v5），bcrypt 密码哈希（golang.org/x/crypto）
- 配置：godotenv 加载 `.env`
- 数据库：MySQL（生产）或 SQLite（本地开发）
- 容器化：Docker，Docker Compose

## 目录和入口
- 入口：`main.go`（编译为单一二进制文件）
- 配置文件：`.env`、`.env.production`
- 容器编排：`docker-compose.yml`、`Dockerfile`
- 数据库初始化脚本：`sql/00_init_user.sh`
- 依赖管理：`go.mod`、`go.sum`
- API 文档：`README.md`

## 运行与构建

### 本地开发（无容器）
1. 准备环境变量：复制 `.env` 并根据需要修改 `DB_DRIVER`、`DB_HOST`、`DB_USER`、`DB_PASS`、`DB_NAME`、`HTTP_ADDR` 等。
2. 运行：
   ```bash
   go run main.go
   ```
   服务将监听 `HTTP_ADDR` 指定的地址（默认 `:8080`）。

### 容器化运行
1. 准备环境变量文件 `.env`（参考 `.env.production` 模板）。
2. 构建并启动：
   ```bash
   docker compose up -d --build
   ```
   服务映射宿主端口 `32001` 到容器 `8080`，MySQL 暴露 `3307` 到宿主。

### 构建二进制
```bash
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o icctv-http-service ./main.go
```

## 配置和密钥

### 环境变量清单
以下 key 出现在 `.env` 或 `docker-compose.yml` 中，**不包含实际值**。

**数据库连接**
- `DB_DRIVER`：数据库驱动，可选 `mysql` 或 `sqlite`
- `DB_HOST`：数据库主机地址（容器内为 `mysql`）
- `DB_PORT`：数据库端口（默认 3306）
- `DB_USER`：数据库用户名
- `DB_PASS`：数据库密码
- `DB_NAME`：数据库名称
- `DATABASE_PATH`：SQLite 文件路径（仅 SQLite 驱动时使用）

**MySQL 容器初始化**
- `MYSQL_ROOT_PASSWORD`：MySQL root 密码
- `MYSQL_DATABASE`：自动创建的数据库名
- `MYSQL_USER`：应用使用的数据库用户
- `MYSQL_PASSWORD`：应用用户的密码

**服务监听**
- `HTTP_ADDR`：HTTP 服务监听地址（默认 `:8080`）

**机密信息处理**
- 所有秘钥、密码、Token 的实际值**严禁**写入本文档。
- 生产环境凭据需从本地安全存储 `private/env-backup/` 中获取，或通过密钥管理服务注入。

## 外部依赖
- **MySQL 8.0**：生产环境首选，通过 `docker-compose.yml` 启动容器。
- **SQLite**：可选本地开发数据库。
- **外部 OrangePi 设备**：服务通过 `/api/orangepi/remote/` 接口与远程 OrangePi 通信（端口更新、信息查询、健康检查），具体设备地址由公网配置 `/api/publicnet/config` 管理。
- **无第三方 SaaS 集成**（无支付、邮件等）。

## 部署线索

### Docker Compose 关键信息
- MySQL 服务名：`mysql`，容器名 `icctv-mysql`
- MySQL 数据卷：`icctv_mysql_data`
- 健康检查：`mysqladmin ping`（使用 `MYSQL_ROOT_PASSWORD`）
- 应用容器名：`icctv-app`
- 应用镜像：`icctv-http-service:latest`（由 Dockerfile 构建）
- 端口映射：`32001:8080`（宿主→容器）
- 启动依赖：应用等待 MySQL 健康检查通过后启动

### Dockerfile 构建要点
- 基础镜像：`golang:1.24` 构建，最终镜像 `scratch` 仅包含静态二进制
- 构建时关闭外部代理，使用 `GOPROXY=https://mirrors.aliyun.com/goproxy/,direct`
- 目标文件：`/main`，暴露 8080 端口

### 生产部署建议
- 修改 `docker-compose.yml` 中 MySQL 用户的默认密码（当前为空占位）。
- 确保 `.env` 文件安全，不提交到版本控制。
- 如需外部访问，将 `32001` 端口通过反向代理暴露，并配置 TLS。
- 定期备份 `icctv_mysql_data` 数据卷。

## API 概览
（所有接口前缀 `/api/`，除认证接口外均需 `Authorization: Bearer <token>`）

### 认证
- `POST /api/auth/public` – 获取公开 Token（24h），需 `building_id` 和 `channels`
- `POST /api/auth/permanent` – 获取永久 Token，需 `ismartid`，返回关联令牌及设备 URL
- `POST /api/auth/login` – 管理员登录，返回 `accessToken` 和 `expiresAt`

### 管理员
- `GET/POST/PUT/DELETE /api/admin` – 管理员 CRUD

### 建筑
- `GET/POST/PUT/DELETE /api/building` – 建筑信息管理

### 设备
- `GET/POST/PUT/DELETE /api/device` – OrangePi 设备管理

### NVR
- `GET/POST/PUT/DELETE /api/nvr` – NVR 信息管理

### 绑定关系
- `POST/DELETE /api/bind/building-orangepi` – 绑定/解绑 OrangePi 与建筑
- `GET /api/bind/building-orangepi/{building_id}` – 查询建筑关联的 OrangePi
- `POST/DELETE /api/bind/building-nvr` – 绑定/解绑 NVR 与建筑
- `GET /api/bind/building-nvr/{building_id}` – 查询建筑关联的 NVR

### 远程管理
- `POST /api/orangepi/remote/ports` – 远程端口更新
- `GET /api/orangepi/remote/info` – 查询远程设备信息
- `GET /api/orangepi/remote/health` – 远程健康检查

### 汇总与配置
- `GET /api/device/info` – 设备汇总信息
- `GET/PUT /api/publicnet/config` – 公网配置（管理远程设备通信地址）

## 复刻检查清单
1. 克隆仓库并切换至 `main` 分支。
2. 获取或重建 `.env` 文件（参考 `.env.production` 结构，从 `private/env-backup/` 或运维手册获取实际值）。
3. 检查 `docker-compose.yml`，确保 MySQL 环境变量与 `.env` 匹配。
4. 执行构建并启动：
   ```bash
   docker compose up -d --build
   ```
5. 验证 MySQL 健康检查通过，应用容器正常启动。
6. 测试 API 连通性：
   ```bash
   curl http://<host>:32001/api/admin -H "Authorization: Bearer <token>"
   ```
7. 若需持久化数据，确认 `icctv_mysql_data` 卷存在。
8. 更新部署清单 `inventory/projects.yaml` 及 `deployments/` 下的相关记录。

## 待补充信息
- 远程 OrangePi 设备的具体认证机制及端口更新协议。
- 公网配置接口 `GET/PUT /api/publicnet/config` 的数据模型和效果。
- 数据库表结构（GORM AutoMigrate 由代码定义，需结合源码确认模型）。
- SQLite 与 MySQL 双驱动切换时的兼容性差异及迁移步骤。
- 生产环境 MySQL 密码的密钥管理集成方式。
- 是否包含 CI/CD 管道（如 GitHub Actions）以及镜像仓库地址。
