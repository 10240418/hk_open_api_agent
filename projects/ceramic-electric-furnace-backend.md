# ceramic-electric-furnace-backend

## 项目定位
陶瓷电炉监控系统后端服务。以西门子 S7-1200 PLC 作为主控数据源，通过 Modbus RTU 采集料仓称重仪表数据，将所有时序数据写入 InfluxDB，对外提供实时状态、历史查询、报警与蝶阀状态队列等 RESTful API。面向工控机环境，支持容器化部署和 Windows 服务托管，为 Flutter 前端提供数据支撑。

## 技术栈
- 语言：Python  
- Web 框架：FastAPI  
- 时序数据库：InfluxDB 2.7  
- PLC 协议：S7（python-snap7）  
- 现场总线：Modbus RTU（pyserial／pymodbus）  
- 容器化：Docker + Docker Compose  
- 配置驱动：YAML 配置文件  
- 运行环境：Windows（工控机），可选 Linux  
- 辅助脚本：PowerShell（串口桥接、进程看门狗）

## 目录和入口
```
.
├── app/
│   ├── core/                # InfluxDB 客户端、报警存储
│   ├── plc/                 # PLC 解析器（DB1/DB30/DB32/DB41）、连接管理
│   ├── services/            # 双速轮询服务、投料计算、Modbus 重量读取
│   ├── routers/             # API 路由（控制、实时、历史、状态、蝶阀、报警）
│   └── tools/               # 物理量转换、Modbus 读取工具
├── configs/                 # PLC 模块定义、DB 结构 YAML
├── deploy/                  # 各版本部署包、docker-compose、监控脚本
│   ├── 1.1.0/ … 1.1.8/     # 历史版本部署
│   └── production/          # 宿主机直接运行模式示例
├── main.py                  # 应用入口
├── Dockerfile               # 容器构建文件
├── docker-compose.yml       # 多 profile 编排（mock / production）
└── requirements.txt         # Python 依赖（内容待补充）
```
**入口文件**：`main.py`，基于 FastAPI 启停，启动后不自动开启轮询，需前端通过 API 触发。

## 运行与构建
### 容器方式（推荐）
- 构建镜像：
  ```powershell
  docker build -t furnace-backend:<tag> .
  ```
- 启动（Mock 模式，开发测试）：
  ```bash
  docker compose --profile mock up -d --build
  ```
- 启动（生产模式，连接真实 PLC 和 Modbus）：
  ```bash
  docker compose --profile production up -d --build
  ```
  实际部署时通常使用 `docker compose up -d`（具体 profile 依据 `docker-compose.yml` 中设置）。

  生产模式需要在宿主机侧启动串口网桥（如果 Modbus 设备使用物理串口且后端位于容器内），详见部署线索。

### 宿主机直接运行（备选）
  ```powershell
  pip install -r requirements.txt
  # 确保 .env 已就位
  python main.py
  # 或使用 uvicorn
  uvicorn main:app --host 0.0.0.0 --port 8082
  ```
  此方式可直接访问 COM 口，无需串口网桥。可将后端注册为 Windows 服务（借助 NSSM）或启用工业看门狗脚本实现进程守护。

## 配置和密钥
项目通过 `.env` 文件注入运行时配置。预定义的环境变量（按作用域分类）：

### PLC 连接
| 变量名 | 说明 |
|--------|------|
| `PLC_IP` | S7-1200 PLC IP 地址 |
| `PLC_PORT` | S7 协议端口（通常 102） |
| `PLC_RACK` | 机架号 |
| `PLC_SLOT` | 插槽号 |

### Modbus RTU（料仓重量）
| 变量名 | 说明 |
|--------|------|
| `MODBUS_PORT` | 串口设备路径（宿主机直接运行）或 TCP 转发地址（如 `socket://host.docker.internal:7777`） |
| `MODBUS_BAUDRATE` | 波特率（默认 19200） |

### InfluxDB
| 变量名 | 说明 |
|--------|------|
| `INFLUX_URL` | InfluxDB 服务地址，例如 `http://furnace-influxdb:8086` |
| `INFLUX_TOKEN` | **敏感** — InfluxDB 认证令牌 |
| `INFLUX_ORG` | 组织名称 |
| `INFLUX_BUCKET` | 数据桶名称 |

### 应用与电气参数
| 变量名 | 说明 |
|--------|------|
| `MOCK_MODE` | 是否启用模拟数据（`true`/`false`） |
| `ENABLE_POLLING` | 启动时是否自动开启轮询（建议由 API 控制，默认关闭） |
| `POLLING_INTERVAL` | 常规轮询间隔（秒） |
| `SERVER_HOST` / `SERVER_PORT` | API 监听地址与端口（容器内通常 `0.0.0.0:8080`） |
| `DEBUG` | 调试模式开关 |
| `CT_RATIO` / `PT_RATIO` | 电流互感器/电压互感器变比（用于电表数据转换） |
| `DB30_NUMBER` / `DB30_SIZE` | DB30 数据块编号及字节大小 |
| `DB32_NUMBER` / `DB32_SIZE` | DB32 数据块编号及字节大小 |
| `DB33_NUMBER` / `DB33_SIZE` | DB33 电表数据块编号及字节大小（预留） |

**敏感变量处理**：  
- `INFLUX_TOKEN` 及 InfluxDB 管理密码等绝不能硬编码或提交至仓库。  
- 部署时需从安全渠道获取真实令牌，并写入生产环境 `.env`（该文件应被 `.gitignore` 排除）。  
- 建议在工控机上通过文件权限限制对 `.env` 的读取。

## 外部依赖
- **西门子 S7-1200 PLC**：通过工业以太网与工控机通信，IP、Rack、Slot 须与现场一致。  
- **料仓称重仪表（Modbus RTU）**：通过 RS-232/485 串口连接至工控机（物理端口一般为 COM1）。  
- **InfluxDB 2.7 实例**：可与后端部署在同一 Docker 网络，或独立运行，需预建组织和数据桶，生成读写令牌。  
- **串口－TCP 网桥**（仅容器化部署需要）：将物理 COM 口映射为 TCP 端口供容器访问，常用工具 `tcp_serial_redirect` 或项目自带的 `simple_serial_bridge.py`，监听端口 `7777`。  
- **Flutter 前端 App**：通过 HTTP 调用后端 API，端口 `8082`，前端本身不属于此后端仓库范围。

## 部署线索
### 典型部署流程（工控机 Windows）
1. 在开发机上 `docker build` 并 `docker save -o furnace-backend.tar`。  
2. 将镜像包、对应版本的 `docker-compose.yml`、`.env`（提前填写正确值）复制到工控机部署目录，如 `D:\deploy\<version>\`。  
3. 先启动串口网桥（若 Modbus 需要）：
   ```powershell
   powershell -ExecutionPolicy Bypass -File start_serial_bridge.ps1
   ```
   验证网桥状态：`check_serial_bridge.ps1`。
4. 加载镜像：
   ```powershell
   docker load -i furnace-backend.tar
   ```
5. 启动服务（生产模式）：
   ```powershell
   docker compose up -d
   ```
6. 验证：
   - `docker logs furnace-backend --tail 50` 查看是否成功连接 PLC 与 Modbus。  
   - `curl http://localhost:8082/api/health` 应返回正常。
7. 第一次启动后，需通过 API 开启数据采集：
   ```http
   POST /api/control/start
   Body: { "batch_code": "唯一批次号" }
   ```

### 服务端口
| 服务 | 外部访问端口 | 容器内部端口 | 备注 |
|------|--------------|--------------|------|
| 后端 API | 8082 | 8080 | 工控机对外提供 |
| InfluxDB | 8089 | 8086 | 管理 UI 与查询接口 |
| 串口网桥 | 7777 | - | 仅宿主侧，用于容器访问 COM 口 |

### 进程守护（Windows）
`deploy/1.1.8/` 下提供 `install_industrial_watchdog.ps1` 与 `install_watchdog_fixed.ps1`，可将后端设为 Windows 服务并配合看门狗实现故障自动重启。也可使用 NSSM 手动注册服务（见 `deploy/production/README.md`）。

### 多版本共存
`deploy/` 目录保留多个历史版本（1.1.0～1.1.8），每个版本均有独立 `docker-compose.yml` 和镜像包，支持快速回滚。回滚时只需停止当前版本容器，切换至目标版本目录执行 `docker compose up -d`。

## 复刻检查清单
1. 克隆仓库：
   ```bash
   git clone https://github.com/clutchtechnology/ceramic-electric-furnace-backend.git
   cd ceramic-electric-furnace-backend
   ```
2. 确认 Python 环境（建议 3.10+）并安装依赖：
   ```bash
   pip install -r requirements.txt   # 或使用 Poetry（若有配置）
   ```
3. 准备 InfluxDB：
   - 运行 `influxdb:2.7` 容器，或使用已有实例；  
   - 创建组织、数据桶，生成操作令牌，记录 `INFLUX_URL`、`INFLUX_TOKEN`、`INFLUX_ORG`、`INFLUX_BUCKET`。
4. 根据现场网络配置以下环境变量并写入 `.env`：
   - `PLC_IP`, `PLC_PORT`, `PLC_RACK`, `PLC_SLOT`
   - `MODBUS_PORT`（直接运行填 `COM1`，容器运行填 `socket://host.docker.internal:7777`）
   - `MODBUS_BAUDRATE`
   - InfluxDB 相关变量及 `MOCK_MODE=false`
5. 若使用容器化部署且需要 Modbus：
   - 在工控机上安装/启动串口网桥，确认端口 `7777` 可达。
6. 构建 Docker 镜像：
   ```bash
   docker build -t furnace-backend:latest .
   ```
   或直接使用项目提供的 `docker-compose.yml` 中 `build`。
7. 启动服务：
   ```bash
   docker compose --profile production up -d
   ```
   或宿主机直接运行 `python main.py`。
8. 健康检查：
   ```bash
   curl http://localhost:8082/api/health
   ```
9. 启动数据采集：
   ```bash
   curl -X POST http://localhost:8082/api/control/start -H "Content-Type: application/json" -d "{\"batch_code\": \"TEST001\"}"
   ```
10. 配置自启动/守护：
    - Windows 服务（NSSM）或工业看门狗脚本。  
    - 确保工控机开机后串口网桥和容器均自动运行。
11. 将本次部署记录更新至对应 `deploy/` 目录或内部运维清单。

## 待补充信息
- 确切的 Python 依赖列表（`requirements.txt` 完整内容），用于精确复现环境。  
- 生产环境真实的 PLC IP、Rack/Slot 以及 Modbus 波特率、串口号（示例值不可直接使用）。  
- InfluxDB 认证令牌及管理员密码的获取方式与保管流程。  
- 是否启用 DB33 电表数据采集（当前预留，需确认 CT/PT 变比）。  
- 前端应用部署方式与回调地址（当前为独立 Flutter App，可能需要跨域或反代配置）。  
- `docker-compose.yml` 中各个 profile 的完整定义（mock 与 production 差异、容器名称、网络设置等）。  
- CI/CD 管道是否存在（如 GitHub Actions），如有需补充构建流程与制品位置。  
- 工控机主机名/固定 IP 及操作系统版本，用于网络规划和远程维护。  
- 报警与通知渠道（邮件、短信、Webhook 等）是否已集成，若未集成则视为后续需求。
