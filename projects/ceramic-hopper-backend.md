# ceramic-hopper-backend

## 项目定位

陶瓷车间数字大屏后端服务，负责采集 PLC S7-1200 设备数据，经解析与转换后存入 InfluxDB，并通过 RESTful API 向 Flutter 大屏客户端提供实时监控数据。

核心数据流：  
`PLC S7-1200 (DB8/DB9/DB10) → Parser → Converter → InfluxDB → REST API → Flutter`

## 技术栈

- 运行时：Python 3.11
- Web 框架：FastAPI
- 数据库：InfluxDB 2.7
- 工业通信：与 Siemens S7-1200 PLC 交互（推测使用 `python-snap7` 或类似库）
- 部署：Docker Compose（含 InfluxDB 与应用服务），Dockerfile
- 离线依赖：预打包的 Linux Python 包目录（`python_packages_linux`）

## 目录和入口

- 应用入口：`main.py`
- 依赖声明：`requirements.txt`
- 离线依赖包目录：`python_packages_linux`
- Docker 构建文件：`Dockerfile`
- 服务编排：`docker-compose.yml`
- 项目说明：`README.md`

> 注：完整源码目录结构当前扫描未获取，待补充。推测包含模块：`parser`、`converter`、API 路由、PLC 驱动等。

## 运行与构建

### 使用 Docker Compose（推荐）

```bash
docker-compose up -d
```

该命令将启动 InfluxDB 容器及应用容器，应用监听端口 `8080`，InfluxDB 监听 `8086`。

### 本地开发运行

```bash
pip install -r requirements.txt
python main.py
```

如果本地不便安装工业通信库，可启用 Mock 模式（`MOCK_MODE=true`）跳过 PLC 连接。

访问 API 文档：http://localhost:8080/docs

### 启动前须知

- 若使用 `docker-compose`，InfluxDB 容器会通过环境变量完成初始化配置（组织、存储桶、admin token 等），无需手动介入。
- 默认 `MOCK_MODE` 为 `true`，生产环境应显式设置为 `false`，并需确保 PLC 可达。
- 构建镜像时，依赖安装采用本地离线包（`python_packages_linux`），若该目录缺失或不全，需先执行依赖准备步骤（待补充）。

## 配置和密钥

所有运行时配置通过环境变量注入。**严禁在文档或仓库中记录真实值**。

| 环境变量 | 用途 | 来源 / 备注 |
|----------|------|-------------|
| `INFLUX_URL` | InfluxDB 服务地址 | Docker Compose 内网为 `http://influxdb:8086`；本地调试通常为 `http://localhost:8086` |
| `INFLUX_TOKEN` | InfluxDB 认证令牌 | 由 InfluxDB 初始化生成，对应 `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` |
| `INFLUX_ORG` | InfluxDB 组织名 | `ceramic-workshop` |
| `INFLUX_BUCKET` | InfluxDB 存储桶 | `sensor_data` |
| `PLC_IP` | Siemens S7-1200 控制器 IP 地址 | **当前 `docker-compose.yml` 未暴露此变量，需补充**。物理网络 IP，例如 `192.168.50.223` |
| `MOCK_MODE` | 是否绕过 PLC 通信使用模拟数据 | `true` / `false`，默认 `true` |
| `PYTHONUNBUFFERED` | Python 输出不缓冲 | 固定设为 `1` |
| `TZ` | 容器时区 | `Asia/Shanghai` |
| `DOCKER_INFLUXDB_INIT_*` 系列变量 | InfluxDB 容器首次启动初始化用 | 包含用户名、密码、组织、存储桶、admin token，密码与 token 均为敏感信息，生产环境应从外部安全注入 |

### 电流变比配置（业务参数）

电表读取值需乘以电流变比得到一次侧实际电流，逻辑硬编码于转换模块：

| 设备类型 | 变比 | 计算式 |
|----------|------|--------|
| 辊道窑 (roller_kiln) | 60 | 一次侧电流 = PLC 读取值 × 0.1 × 60 |
| 料仓 / SCR / 风机 | 20 | 一次侧电流 = PLC 读取值 × 0.1 × 20 |

若变比调整需修改代码。

## 外部依赖

### 运行时依赖

- **InfluxDB 2.7**：时序数据库，存储传感器数据
- **Siemens S7-1200 PLC**：现场数据源，通过工业以太网通信
- **PLC 通信库**：具体库名未在扫描件中给出，推测为 `python-snap7` 或类似（待补充 `requirements.txt` 内容确认）

### 构建依赖

- 离线 Python 包目录：`./python_packages_linux`，要求包含 `requirements.txt` 声明所有包的 `.whl` 或 `.tar.gz` 离线文件
- Docker 基础镜像：`python:3.11-slim`

## 部署线索

### 容器服务

`docker-compose.yml` 定义两个服务：

- **influxdb**  
  - 镜像：`influxdb:2.7`  
  - 卷挂载路径为 Windows 风格（`D:/data/…`），部署至 Linux 主机时需改为合适的 Linux 路径  
  - 通过环境变量完成首次初始化，重启后数据持久化  
  - 连接至自定义网络 `ceramic-network`

- **backend**  
  - 使用当前目录的 `Dockerfile` 构建  
  - 挂载主机源码目录至容器 `/app`（开发模式，生产建议移除卷挂载或仅挂载配置）  
  - 环境变量中缺少 `PLC_IP`，需补充  
  - 依赖 `influxdb` 服务

### 网络

自定义桥接网络 `ceramic-network`，容器间通过服务名通信。

### 端口暴露

- `8086`：InfluxDB HTTP API
- `8080`：应用 FastAPI 服务

### 生产部署建议

- 移除后端服务的源码卷挂载，改用构建镜像中包含代码的方式
- 所有凭据（token、密码）应通过 Docker secret、Vault 或 K8s Secret 注入，不应明码写入 `docker-compose.yml`
- 将 PLC IP 等环境特定配置外部化（例如 `.env` 文件，不提交至版本控制）
- 根据目标主机操作系统调整 InfluxDB 卷路径

## 复刻检查清单

从零复刻本服务至新环境时，请逐项确认：

- [ ] 克隆仓库，确认包含 `python_packages_linux` 目录（若为空或缺失，需参照 `requirements.txt` 重新准备离线包）
- [ ] 准备目标 Linux 主机并安装 Docker 及 Docker Compose
- [ ] 创建 InfluxDB 数据持久化目录（如 `/data/influxdb_data`、`/data/influxdb_config`），并修改 `docker-compose.yml` 中 `volumes` 为正确的 Linux 路径
- [ ] 生成安全的 InfluxDB admin token、密码，用占位符替换 `docker-compose.yml` 中的示例值（或通过 `.env` 引用，但确保 `.env` 不入库）
- [ ] 确认 PLC 网络可达，获取 PLC IP 地址，并在 `docker-compose.yml` 的 `backend` 环境变量中添加 `PLC_IP=<实际IP>`
- [ ] 将 `MOCK_MODE` 设置为 `false`（如果需连接真实 PLC）
- [ ] 启动服务：`docker-compose up -d`
- [ ] 检查容器日志：`docker logs ceramic-backend`，确认 InfluxDB 连接正常、PLC 连接正常（或 Mock 模式生效）
- [ ] 访问 `http://<host>:8080/docs` 验证 API 可用
- [ ] 验证大屏客户端能正常拉取数据
- [ ] 配置 InfluxDB 自动导入或创建任务（如有保留策略、连续查询需求，待补充）
- [ ] 配置监控告警（容器状态、PLC 离线等）

## 待补充信息

- **`requirements.txt` 完整内容**：明确 PLC 通信库及版本，确认离线包完整性
- **源码目录树**：各模块代码组织（parser、converter、API 路由、PLC 驱动等）
- **PLC 连接参数细节**：端口（默认 102？）、机架/插槽号、DB 块布局文档
- **API 鉴权机制**：当前描述为开放接口，生产是否需要 API token 或 CORS 策略限制定
- **InfluxDB 备份与恢复策略**：无备份配置说明
- **日志收集与处理**：当前无集中日志方案
- **Mock 数据生成方式**：模拟数据的格式、数量，以便离线演示
- **CI/CD 流程**：如何自动构建 Docker 镜像并推送至镜像仓库
- **变比等业务配置外移**：是否有计划将电流变比等配置转为环境变量或配置文件，减少代码修改
- **运维手册**：日常巡检、PLC 断线重连策略、InfluxDB 存储估算等
