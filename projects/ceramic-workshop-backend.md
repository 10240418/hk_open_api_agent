# ceramic-workshop-backend

## 项目定位
陶瓷车间数字大屏的后端服务，负责从西门子 S7-1200 PLC 采集料仓、辊道窑、SCR/风机等设备的实时运行数据，经解析转换后存入 InfluxDB 时间序列数据库，并通过 REST API 供 Flutter 前端大屏消费。

## 技术栈

| 层级 | 技术/组件 | 版本/说明 |
|---|---|---|
| 语言 | Python | 3.11 |
| Web 框架 | FastAPI | 推测自 `/docs` 端点 |
| 数据库 | InfluxDB | 2.7 |
| 工业通信 | python-snap7（推测） | 与 S7-1200 PLC 通讯，读取 DB8/9/10 |
| 容器化 | Docker + Docker Compose |  |
| 基础镜像 | python:3.11-slim |  |

## 目录和入口

- **容器工作目录**：`/app`
- **服务入口**：`main.py`（启动 FastAPI 应用）
- **核心依赖定义**：`requirements.txt`
- **离线 pip 包**：`python_packages/`（Linux 预编译包，用于离线安装）
- **PLC 模块推测**：源码中应包含 PLC 数据块解析、转换器、InfluxDB 写入、API 路由等模块（`parser`, `converter`, `routes` 等），详参 `ceramic-workshop-backend` 仓库。
- **其他文件**：
  - `Dockerfile`
  - `docker-compose.yml`
  - `README.md`

## 运行与构建

### 本地快速启动（直连 PLC）
```bash
docker-compose up -d
pip install -r requirements.txt
python3 main.py
```
服务监听 `http://localhost:8080`，API 文档 `http://localhost:8080/docs`。

### 仅供开发/测试的不连 PLC 模式
设置环境变量 `MOCK_MODE=true`（默认值），后端将不尝试连接真实 PLC，可独立验证 API 逻辑。

### 容器化构建
```bash
docker-compose build
```
Dockerfile 使用离线 pip 包目录 `python_packages/` 安装依赖，构建过程无需外网。

### 容器运行
```bash
docker-compose up -d
```
- `ceramic-influxdb` 容器暴露 `8086`（InfluxDB HTTP API）
- `ceramic-backend` 容器暴露 `8080`（应用 API）

## 配置和密钥

### 必需的环境变量

| 变量 | 说明 | 示例值/来源 |
|---|---|---|
| `INFLUX_URL` | InfluxDB 服务地址 | `http://influxdb:8086`（容器内）<br>`http://localhost:8086`（宿主机） |
| `INFLUX_TOKEN` | InfluxDB 管理员令牌 | *已脱敏，请从安全存储获取* |
| `INFLUX_ORG` | InfluxDB 组织名 | `ceramic-workshop` |
| `INFLUX_BUCKET` | InfluxDB 桶名 | `sensor_data` |
| `PLC_IP` | 西门子 S7-1200 PLC IP 地址 | `192.168.50.223`（根据现场网络调整） |
| `MOCK_MODE` | 是否使用模拟模式（免连 PLC） | `true` 或 `false` |

### Docker Compose 中的密钥
`docker-compose.yml` 中定义了 InfluxDB 初始化凭据：

- `DOCKER_INFLUXDB_INIT_USERNAME=admin`
- `DOCKER_INFLUXDB_INIT_PASSWORD=<redacted>`
- `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=<redacted>`

*真实值不应出现在本文档中。复刻时请在本地安全存储（如 `private/env-backup/`）中查阅，或从 InfluxDB 管理员处获取。*

### 电流变比（非环境变量，业务影响数据精度）
- 辊道窑（DB9）电表电流变比：**60**
- 料仓/SCR/风机（DB8, DB10）电表电流变比：**20**
  实际一次侧电流 = PLC 读取值 × 0.1 × 变比。

## 外部依赖

| 依赖 | 类型 | 通信方向 | 说明 |
|---|---|---|---|
| Siemens S7-1200 PLC | 工业设备 | 本服务向 PLC 发起连接 | 读取 DB8（9料仓）、DB9（辊道窑6温区）、DB10（2SCR+2风机） |
| InfluxDB 2.7 | 数据库 | 本服务写入 & 读取 | 存储传感器时序数据，提供 API 查询 |
| Docker 引擎 | 基础设施 | 运行容器 |  |
| GitHub 仓库 | 代码仓库 | 拉取 | `origin https://github.com/10240418/ceramic-workshop-backend.git` |

## 部署线索

### 网络
- Docker 网络：`ceramic-network`（内部通信）
- 对外端口映射：
  - 后端 API：`8080`（可自定义）
  - InfluxDB HTTP：`8086`

### 数据持久化
`docker-compose.yml` 中为 InfluxDB 挂载了两个 Windows 本地路径：
- `D:/data/influxdb_data` → `/var/lib/influxdb2`（数据）
- `D:/data/influxdb_config` → `/etc/influxdb2`（配置）

**注意**：跨平台部署时需将 `D:/data/...` 调整为当前宿主机的有效路径。

### 健康检查
- `GET /api/health` （应用整体健康）
- `GET /api/health/plc` （PLC 连接状态）

### 配置管理
- `PUT /api/config/plc` 可动态更新 PLC 配置（可能需要重启或应用生效）
- `POST /api/config/plc/test` 测试配置连接

### 部署后动作
1. 确认 InfluxDB `sensor_data` 桶已创建，Token 有效。
2. 若生产环境不使用模拟模式，将 `MOCK_MODE` 设为 `false` 并确保网络可达 PLC。
3. 部署成功后，按内部流程更新 `inventory/projects.yaml` 及 `deployments/` 下的对应部署记录。
4. 检查电流变比配置是否正确，必要时在源码常量中校对。

## 复刻检查清单

- [ ] 获取 `ceramic-workshop-backend` 仓库代码（`git clone` 并切换到期望分支/提交）。
- [ ] 确保目标环境已安装 Docker 和 Docker Compose。
- [ ] 准备安全的密钥存储，导出或配置以下变量（且绝不写入文档）：
  - `DOCKER_INFLUXDB_INIT_PASSWORD`
  - `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`
  - `INFLUX_TOKEN`（应与上面的 admin token 一致或创建 read/write token）
- [ ] 检查并修改 `docker-compose.yml` 中 InfluxDB 数据卷路径为本地有效目录。
- [ ] （可选）若网络受限，预先将 Linux 兼容的 Python 依赖包放入 `python_packages/` 目录，并确保 `requirements.txt` 版本匹配。
- [ ] 根据是否连接真实 PLC 设定 `MOCK_MODE` 环境变量。
- [ ] 设置 `PLC_IP` 为实际 PLC 的 IP 地址（若非模拟模式）。
- [ ] 执行 `docker-compose up -d` 启动所有服务。
- [ ] 调用 `http://<host>:8080/api/health` 验证后端正常。
- [ ] 若连有 PLC，调用 `http://<host>:8080/api/health/plc` 确认 PLC 通讯正常。
- [ ] 验证核心批量接口：
  - `/api/hopper/realtime/batch`
  - `/api/roller/realtime/formatted`
  - `/api/scr-fan/realtime/batch`
- [ ] 检查 InfluxDB UI（如 `http://localhost:8086`）中 `sensor_data` 桶有数据流入。
- [ ] 部署记录归档，更新 `inventory/projects.yaml`。

## 待补充信息

- **认证与授权**：API 端点目前未提及任何认证机制（JWT、OAuth2 或其他），生产环境需评估是否需要增加访问控制。
- **PLC 连接安全性**：未发现 TLS/VPN 配置，PLC 与后端使用内网明文 S7 协议通信，需结合现场网络隔离状况评估风险。
- **日志与监控**：未描述集中日志收集、指标暴露（如 Prometheus）方案，缺少异常报警配置。
- **持久化备份**：InfluxDB 数据备份策略未定义，需确认是否为时间序列数据配置自动备份。
- **依赖清单**：`requirements.txt` 具体内容未知，建议团队补录依赖名称及版本锁定信息。
- **多环境支持**：开发/测试/生产环境差异仅通过环境变量控制，未发现多套 Docker Compose 覆盖文件，部署时需注意隔离。
- **PLC 数据块结构**：DB8/9/10 的详细地址映射与字段类型需在内部文档维护，便于现场调试和数据一致性校验。
