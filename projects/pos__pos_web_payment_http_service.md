# pos_web_payment_http_service

## 项目定位

面向 EasyLink 支付的 H5 收银台后端服务，纯 Go 实现。

- 仅处理微信、支付宝的 H5 支付场景，暴露 `/api/payments/h5/*` 接口。
- 完全适配前端下单 → EasyLink 网关 → 异步回调 → 业务写回的完整链路。
- 内部调用 EasyLink 网关的 `unifiedOrder`、`query`、`close`、`cancel` 接口。
- 回调成功后自动调用 `report-payment` 完成业务钩子，失败时返回 `fail` 让网关重试。
- 同步将订单快照、`report_payment_data` 持久化到 MySQL，并支持建立订单时携带业务参数与网关参数覆盖。

## 技术栈

- **语言**：Go (go 1.24.3)
- **Web 框架**：未使用第三方路由/Web 框架，基于 Go 标准库自建 HTTP 服务
- **数据库驱动**：`github.com/go-sql-driver/mysql v1.8.1`
- **数据存储**：MySQL 8.4（通过 Docker Compose 提供本地环境）
- **运行时**：Go native binary，无容器运行时约束
- **部署线索**：目前仅有用于本地开发数据库的 `docker-compose.yml`；服务本身可通过编译后直接运行

## 目录和入口

- **本地路径**：`/Users/yangliu/Documents/Code/pos/pos_web_payment_http_service`
- **源码入口**：
  - `main.go`（根目录直接运行 `go run .`）
  - 兼容旧式入口 `cmd/server/` 启动方式（`go run ./cmd/server` 亦可用）
- **关键文件**：
  - `go.mod` – 依赖声明
  - `docker-compose.yml` – 本地 MySQL 环境
  - `README.md` – 运行与接口说明
  - `.env` – 环境变量配置（敏感信息已脱敏，真实文件不进入版本库）
- **分支信息**：当前分支 `main`，最新提交 `22ea765`，描述为 `feat: add order record synchronization and event streaming capabilities`

## 运行与构建

### 构建

无需特殊构建系统，标准 Go 编译即可：

```bash
go build -o payment_service .
```

### 本地运行

服务会按以下优先级加载环境变量文件（优先级从高到低）：

1. `$PAYMENTS_ENV_FILE` 指定的文件
2. `./.env.easylink.local`
3. `./.env`
4. `../pos_web/.env.easylink.local`

启动命令：

```bash
# 推荐方式
go run .
# 或明确指定 main.go
go run main.go
# 兼容旧入口
go run ./cmd/server
```

服务默认监听 `127.0.0.1:20034`，可通过环境变量 `PAYMENTS_HTTP_ADDR` 修改。

首次启动前需确保 MySQL 已运行且数据库可访问，服务会自动建表（表名由 `PAYMENTS_MYSQL_TABLE` 控制，默认 `payment_orders`）。若仍配置了 `PAYMENTS_STORE_DRIVER`，其值必须为 `mysql`，否则启动失败。

### 本地 MySQL 准备

```bash
docker compose up -d
```

使用服务前确认 MySQL 容器的健康检查通过（`docker compose ps`）。

## 配置和密钥

所有配置均以环境变量形式注入，严禁将实际值提交至仓库或本文档。以下列出当前使用的变量名及用途，敏感变量已明确标注，其值需从私有安全渠道获取。

### EasyLink 支付通道配置（通用）

| 环境变量 | 用途 | 敏感 |
| :--- | :--- | :--- |
| `EASYLINK_ENV` | 网关环境标识（如 `prod` / `sandbox`） | 否 |
| `EASYLINK_MCH_NO` | 商户号 | 否 |
| `EASYLINK_NOTIFY_URL` | EasyLink 异步回调地址，指向本服务的 `/api/payments/h5/notify/easylink` | 否 |
| `EASYLINK_RETURN_BASE_URL` | 支付完成后的前端跳转基础 URL | 否 |
| `EASYLINK_EXPIRED_SECONDS` | 订单过期时间（秒） | 否 |
| `EASYLINK_TIMEOUT_MS` | 调用 EasyLink 网关的请求超时（毫秒） | 否 |

### 支付宝通道配置

| 环境变量 | 用途 | 敏感 |
| :--- | :--- | :--- |
| `EASYLINK_ALI_APP_ID` | 支付宝应用 ID | 是 |
| `EASYLINK_ALI_APP_SECRET` | 支付宝应用密钥 | **是** |
| `EASYLINK_ALI_H5_APP_ID` | 支付宝 H5 应用 ID | 是 |
| `EASYLINK_ALI_H5_APP_SECRET` | 支付宝 H5 应用密钥 | **是** |
| `EASYLINK_ALI_H5_BIZ_PAY_METHOD` | 支付宝 H5 业务支付方式编码 | 否 |
| `EASYLINK_ALI_QR_APP_ID` | 支付宝扫码应用 ID | 是 |
| `EASYLINK_ALI_QR_APP_SECRET` | 支付宝扫码应用密钥 | **是** |
| `EASYLINK_ALI_QR_BIZ_PAY_METHOD` | 支付宝扫码业务支付方式编码 | 否 |

### 微信通道配置

| 环境变量 | 用途 | 敏感 |
| :--- | :--- | :--- |
| `EASYLINK_WX_APP_ID` | 微信支付应用 ID | 是 |
| `EASYLINK_WX_APP_SECRET` | 微信支付应用密钥 | **是** |
| `EASYLINK_WX_H5_APP_ID` | 微信 H5 支付应用 ID | 是 |
| `EASYLINK_WX_H5_APP_SECRET` | 微信 H5 支付应用密钥 | **是** |
| `EASYLINK_WX_H5_BIZ_PAY_METHOD` | 微信 H5 业务支付方式编码 | 否 |
| `EASYLINK_WX_QR_APP_SECRET` | 微信扫码支付应用密钥 | **是** |
| `EASYLINK_WX_QR_BIZ_PAY_METHOD` | 微信扫码业务支付方式编码 | 否 |
| `EASYLINK_WX_QR_PAY_DATA_TYPE` | 微信扫码支付数据类型 | 否 |

### 银联及 Nuvei 通道配置

| 环境变量 | 用途 | 敏感 |
| :--- | :--- | :--- |
| `EASYLINK_UP_APP_ID` | 银联应用 ID | 是 |
| `EASYLINK_UP_APP_SECRET` | 银联应用密钥 | **是** |
| `EASYLINK_UP_EXPRESS_APP_ID` | 银联小额快捷应用 ID | 是 |
| `EASYLINK_UP_EXPRESS_APP_SECRET` | 银联小额快捷应用密钥 | **是** |
| `EASYLINK_UP_OP_APP_ID` | 银联 OP 应用 ID | 是 |
| `EASYLINK_UP_OP_APP_SECRET` | 银联 OP 应用密钥 | **是** |
| `EASYLINK_NUVEI_H5_APP_ID` | Nuvei H5 应用 ID | 是 |
| `EASYLINK_NUVEI_H5_APP_SECRET` | Nuvei H5 应用密钥 | **是** |

### 银联云闪付扫码配置

| 环境变量 | 用途 | 敏感 |
| :--- | :--- | :--- |
| `EASYLINK_YSF_QR_BIZ_PAY_METHOD` | 云闪付扫码业务支付方式编码 | 否 |

### 服务自身配置

| 环境变量 | 用途 | 敏感 |
| :--- | :--- | :--- |
| `PAYMENTS_HTTP_ADDR` | HTTP 服务监听地址，默认 `127.0.0.1:20034` | 否 |
| `PAYMENTS_DEV_PORT` | 开发环境端口（用途视内部代码而定） | 否 |
| `PAYMENTS_ENABLE_SIMULATE` | 是否开启模拟模式（非生产使用） | 否 |
| `PAYMENTS_MYSQL_DSN` | MySQL 连接串，含用户名、密码、地址和库名 | **是** |
| `PAYMENTS_MYSQL_TABLE` | 订单表名，默认 `payment_orders` | 否 |
| `PAYMENTS_STORE_DRIVER` | 存储驱动（仅允许 `mysql`，否则启动失败） | 否 |
| `PAYMENTS_ENV_FILE` | 指定另外的 env 文件路径 | 否 |

> **重要**：所有标记为“是”的变量均包含凭证或密钥，**严禁**写入文档、日志或版本控制。实际部署时应从公司密钥管理服务注入或通过加密配置文件提供。

## 外部依赖

- **MySQL 8.4**：存储支付订单快照、业务回调数据。本地通过 `docker-compose.yml` 启动，生产需提供高可用 MySQL 实例。
- **EasyLink 支付网关**：核心外部服务，本服务通过 HTTP 与其通信。须确保网络可达，且 `EASYLINK_ENV` 对应的环境端点正确。
- **report-payment 业务服务**：回调成功后调用的下游服务（HTTP 调用）。需确认其接口与本服务约定一致，且本服务可访问其内部地址。
- **网络**：需要出站访问 EasyLink 网关，入站需能接收 EasyLink 的异步回调通知（通常由反向代理或负载均衡转发）。

## 部署线索

- **容器化**：当前仓库仅有 `docker-compose.yml` 用于本地 MySQL，未提供服务的 Dockerfile。生产容器化需自行编写，或直接将编译后的二进制部署至虚拟机/裸机。
- **服务监听**：默认 `127.0.0.1:20034`，生产环境建议置于反向代理（如 Nginx）后方，通过域名对外暴露 `/api/payments/h5/*`。
- **回调域名**：EasyLink 的 `notifyUrl` 必须能够访问服务端真实地址，需在环境变量 `EASYLINK_NOTIFY_URL` 中配置完整回调 URL（可能包含域名或内网地址，取决于网关位置）。
- **持久化**：依赖 MySQL 存储，生产环境需提供独立的数据库实例，并在 `PAYMENTS_MYSQL_DSN` 中配置正确的连接信息。确保数据库用户具有建表、读写权限。
- **启动参数**：除了环境变量，无额外启动参数。服务启动后自动建表（如不存在）。
- **运行用户**：建议以非 root 用户运行二进制，确保拥有对所在目录的读权限（读 env 文件）和网络监听权限。

## 复刻检查清单

在新环境克隆并部署前，请确认以下步骤全部完成：

1. **代码拉取**
   - `git clone https://github.com/The-Healthist/pos_web_payment_http_service.git`
   - 切换到目标分支（通常是 `main`）。

2. **Go 环境准备**
   - 安装 Go 1.24.3 或更高版本。
   - 执行 `go mod download` 确保依赖缓存。

3. **MySQL 准备**
   - 提供 MySQL 8.4 实例（可通过 `docker compose up -d` 启动本地库，或连接已有实例）。
   - 创建数据库（本地 docker-compose 已创建 `pos_payments`）。
   - 创建用户并授权（本地默认用户 `pos_payments`，密码需从私有源获取）。
   - 确认 `PAYMENTS_MYSQL_DSN` 可正常连接，且用户有建表权限。

4. **环境变量配置**
   - 从安全渠道获取所有敏感变量的值（参照“配置和密钥”章节）。
   - 按优先级准备 `.env` 或 `PAYMENTS_ENV_FILE` 指定的文件，确保包含所有必需变量（特别是 EasyLink 各通道凭证、MYSQL_DSN）。
   - 验证 `EASYLINK_NOTIFY_URL` 指向本服务的正确回调路径。
   - 若无需某些通道，可删除对应变量，但服务代码可能会因缺失配置而失败，建议按实际支付场景保留需要的通道。

5. **启动服务**
   - 通过 `go run .` 或编译后运行二进制。
   - 检查启动日志，确认监听地址及数据库连接正常，无致命错误。

6. **功能验证**
   - 调用 `POST /api/payments/h5/orders` 创建测试订单（可启用 `PAYMENTS_ENABLE_SIMULATE` 模拟）。
   - 检查 MySQL 中 `payment_orders` 表是否有数据。
   - 如有条件，使用 EasyLink 沙箱环境完成完整支付回调验证。

7. **反向代理 / 负载均衡配置（生产）**
   - 将服务端口通过 Nginx/网关对外暴露。
   - 设置健康检查端点（可使用 `/health` 或根路径，需确认服务是否内置），确保流量调度正常。

8. **监控与日志**
   - 收集服务日志，确保能看到 EasyLink 调用详情及错误信息。
   - 监控 `report-payment` 调用成功率，发现失败及时排查。

## 待补充信息

- **EasyLink 网关具体端点及 API 文档**：需确认不同环境（沙箱/生产）的域名和路径，以便在代码中配置或在 env 内显式指定（若代码依赖 SDK 可能需要额外配置）。
- **report-payment 服务接口定义**：当前仅提及自动调用，未记录请求格式、地址获取方式（是配置文件、服务发现还是固定 URL），需补充相关接口契约及目标地址配置项。
- **服务健康检查端口/路径**：未明确是否有 `/healthz` 等端点，需验证后补充，便于生产探活。
- **生产部署架构**：缺失生产环境的部署方式（如 Kubernetes Deployment 描述、虚拟机 systemd unit 等），也无 CI/CD 配置。
- **数据库迁移策略**：目前启动时自动建表，若后续表结构变更，是否需手动执行变更或引入 migration 工具需明确。
- **日志级别与输出格式**：未说明，生产环境可能需要调整为 JSON 格式并指定日志级别。
- **安全加固**：服务监听地址是否应改为 `0.0.0.0` 由网络策略控制；回调接口是否有签名验证或 IP 白名单；敏感配置的保护机制等需在正式上线前确认。
- **依赖的具体版本和兼容性**：EasyLink 网关 SDK 或 API 版本未声明，`report-payment` 依赖的版本也未提及。
