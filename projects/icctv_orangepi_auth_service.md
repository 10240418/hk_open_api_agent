# icctv_orangepi_auth_service

## 项目定位

部署在 OrangePi 的高性能认证网关，负责对接 iSmart Token、校验建筑与频道粒度的权限，为 MediaMTX 的 WebRTC、RTSP、录像功能提供安全代理，并通过 HTTP API 暴露设备管理与远程维护能力。

核心职责：

- 接收上游 iSmart 签发的 Token，校验合法性及可访问的 building/channel；
- 反向代理 MediaMTX 的 WebRTC 与 RTSP 流，根据校验结果放行或拒绝；
- 管理 MediaMTX 的流路径（path）与录像配置；
- 通过 FRPC 提供公网可达的维护通道，支持远程更新 FRPC 端口映射；
- 提供设备信息、健康检查等运维接口。

项目对应的远端仓库：`https://github.com/The-Healthist/icctv_orangepi_auth_service.git`。

## 技术栈

- 语言：Python
- Web 框架：FastAPI
- 运行时：python（基于 Python 3.11-slim 镜像）
- 容器化：Docker，多阶段构建
- 编排：Docker Compose
- 流媒体：MediaMTX（bluenviron/mediamtx:latest-ffmpeg）
- 内网穿透：FRP（snowdreamtech/frpc:latest 作为客户端，fatedier/frps 作为服务端）
- 目标平台：linux/arm64（OrangePi）

## 目录和入口

项目仓库关键路径一览：

```
icctv_orangepi_auth_service/
├── auth_service/                  # Python 认证服务源码
│   ├── Dockerfile                 # 多阶段构建，目标架构 arm64
│   ├── app.py                     # 应用主入口
│   └── requirements.txt           # Python 依赖清单
├── config/                        # 按部署目标分组的配置文件
│   ├── orangepi29005/
│   │   └── docker-compose.yml     # OrangePi 29005 部署编排
│   ├── orangepi29006/
│   │   └── docker-compose.yml     # OrangePi 29006 部署编排
│   └── server/
│       └── docker-compose.yml     # FRP 服务端 (frps) 编排
├── docker-compose.yml             # 根级编排（开发/本地测试）
└── README.md
```

服务入口：`auth_service/app.py`（由 Docker 镜像的 `CMD ["python", "app.py"]` 启动）。

## 运行与构建

### 1. 构建认证服务镜像

在 `auth_service/` 目录下执行（确保构建上下文为项目根目录或 auth_service 目录）：

```bash
docker buildx build --platform linux/arm64 -t icctv-auth-service:<version> .
```

示例版本号见现有部署：`1.1.1` 或 `1.1.2`。镜像构建后会用于 `docker-compose.yml` 中的 `icctv_orangepi_service` 服务，部署时需传入对应 tag 并设置 `pull_policy: never`（表明镜像已存在本地）。

### 2. 部署到 OrangePi 设备

每个 OrangePi 实例对应一组固定的公网端口，部署时需选定对应的 `docker-compose.yml` 并准备以下配置文件：

- `config/mediamtx.yml` – MediaMTX 全局配置（监听端口、鉴权回调 URL 等）
- `config/frpc.toml` – FRPC 客户端配置（包含与服务端的连接凭据、端口映射规则）

在目标设备上创建目录结构（以 OrangePi 29005 为例）：

```
~/icctv/
├── docker-compose.yml   # 从 config/orangepi29005/docker-compose.yml 复制
├── config/
│   ├── mediamtx.yml
│   └── frpc.toml
└── recordings/          # 录像存储卷
```

执行启动：

```bash
cd ~/icctv
docker compose up -d
```

### 3. 部署 FRP 服务端

在具有公网 IP 的服务器上，使用 `config/server/docker-compose.yml`，并准备 `config/frps.toml`（绑定端口、认证令牌等）。启动方式同上。

## 配置和密钥

### 环境变量

认证服务（`ismart_auth_service` 容器）通过环境变量控制行为，以下为完整列表（敏感值使用 `<REDACTED>` 占位）：

| 变量名 | 说明 | 备注 |
|--------|------|------|
| `TZ` | 时区 | 固定为 `Asia/Shanghai` |
| `PORT` | 服务监听端口 | 容器内默认 `8889` |
| `DEBUG` | 调试模式 | `true` / `false` |
| `SECRET_KEY` | JWT 签名密钥 | 必填，需妥善保管，**严禁硬编码在公开配置中**。当前镜像内可能以环境变量传入，生产部署应从密钥管理服务或安全挂载获取。示例值已打码：`<REDACTED>` |
| `MEDIAMTX_HOST` | MediaMTX API 地址 | 容器内为 `mediamtx` 或 `127.0.0.1`（根据网络模式） |
| `MEDIAMTX_PORT` | MediaMTX 访问端口 | `8890` |
| `MEDIAMTX_API_PORT` | MediaMTX API 端口 | `9997` |
| `FRPC_CONFIG_PATH` | frpc.toml 路径 | 挂载后的容器内路径，一般为 `/app/config/frpc.toml` |
| `DOCKER_SOCK_PATH` | Docker socket 路径 | 用于控制 frpc 容器重启 |
| `FRPC_SERVICE_NAME` | frpc 容器名 | `frpc` |
| `DISABLE_TOKEN_AUTH` | 是否禁用Token校验 | `false` |
| `TOKEN_MODE` | Token 模式 | `simple` |
| `WEBRTC_PUBLIC_IP` | WebRTC 公网 IP | 对应 FRP 映射的公网地址 |
| `WEBRTC_PUBLIC_PORT` | WebRTC 公网端口 | 如 `32005`、`32006` |
| `HTTP_PROXY`、`HTTPS_PROXY` 等 | 代理设置 | 均强制置空，避免影响容器间通信 |

MediaMTX 容器还需设置 `MTX_WEBRTCADDITIONALHOSTS` 与 `MTX_WEBRTCICEHOSTNAT1TO1IPS`，指向公网 IP，并清除代理。

### 敏感凭据清单

以下凭据未在文档中显示实际值，复刻时需从受控存储中获取：

- **SECRET_KEY** – 认证服务 Token 签名密钥。
- **FRPC/FRPS 认证令牌** – `frpc.toml` 与 `frps.toml` 中配置的 `token`。
- **iSmart 对接凭据**（如存在）– 用于向 iSmart 服务校验 Token 的密钥或证书。
- **docker-compose 中硬编码密钥** – 现有 YAML 文件中 `SECRET_KEY` 以明文形式暴露，生产环境需改用 Docker secrets 或外部变量注入。

### 配置文件说明

- **`mediamtx.yml`**：定义 RTSP/WebRTC 监听端口、鉴权回调地址（指向 `ismart_auth_service:8889` 的特定端点）、录像路径等。
- **`frpc.toml`**：声明与服务端的连接信息、本地服务到公网端口的映射（如将本地 `8889` 映射到公网 `29005`，SSH 端口等）。
- **`frps.toml`**（服务端）：绑定服务端监听端口、认证令牌等。

## 外部依赖

- **iSmart Token 签发与校验服务** – 上游身份体系，认证服务依赖其提供 Token 验证能力，具体集成方式见 `TOKEN_MODE=simple` 及内部实现。
- **MediaMTX** – 流媒体服务器，通过 HTTP API（`http://mediamtx:9997`）管理流路径与配置。
- **FRP 服务端** – 运行在公网可达主机上（已知 `39.108.49.167` 或其它 IP），为 OrangePi 设备提供反向代理。
- **Docker 守护进程** – 挂载 `/var/run/docker.sock` 以实现对 `frpc` 容器的远程重启。
- **外部 DNS** – 某些部署配置中为 MediaMTX 容器指定了公共 DNS（`8.8.8.8`、`114.114.114.114` 等），用于解决 DDNS 解析问题。

## 部署线索

| 部署目标 | 认证端口 | SSH 端口 | WebRTC 端口 | 网络模式 | 特殊说明 |
|----------|----------|----------|-------------|----------|----------|
| orangepi29005 | 29005 | 30005 | 32005 | host | `network_mode: host`，MEDIAMTX_HOST 设为 `127.0.0.1` |
| orangepi29006 | 29006 | 30006 | 32006 | bridge（默认） | 端口映射直接暴露，MEDIAMTX_HOST 为 `mediamtx` |
| 本地开发（根 docker-compose） | 29001 | 未知 | 32004 | bridge | 用于调试，`WEBRTC_PUBLIC_PORT=32004` |

公网入口 IP 均为 `117.72.193.54`（开发/测试环境），实际生产可能不同。

设备内部 IP 示例：`192.168.50.175`（orangepi29006），具体以实际网络为准。

目录布局标准化：每台设备的 `~/icctv/` 下包含 `docker-compose.yml`、`config/mediamtx.yml`、`config/frpc.toml`、`recordings/`。

## 复刻检查清单

从零复刻本服务到新 OrangePi 设备时，按以下步骤操作：

1. **克隆仓库**  
   `git clone https://github.com/The-Healthist/icctv_orangepi_auth_service.git`

2. **获取/生成机密**  
   - `SECRET_KEY`（用于 JWT 签名）  
   - FRPC 与 FRPS 的 `token`  
   - 如有 iSmart 对接凭据，从安全存储获取

3. **准备 ARM64 Docker 环境**  
   在构建机或 OrangePi 上安装 Docker，开启 buildx 并支持 `linux/arm64`。

4. **构建认证镜像**  
   在 `auth_service/` 目录执行：  
   `docker buildx build --platform linux/arm64 -t icctv-auth-service:<版本> .`  
   将镜像推送至私有仓库或直接加载到目标设备。

5. **创建部署目录**  
   在目标设备上按“部署线索”中的路径结构准备目录，复制对应设备的 `docker-compose.yml`，并根据端口规划调整 `WEBRTC_PUBLIC_PORT` 等变量。

6. **准备配置文件**  
   - `config/mediamtx.yml`：确保鉴权回调地址指向 `http://localhost:8889` 或相应容器名。  
   - `config/frpc.toml`：填入正确的 FRP 服务端地址、端口和 token，以及需要映射的本地端口。  
   - 服务端 `frps.toml`（如有需要）配置监听的端口和 token。

7. **启动服务**  
   ```bash
   cd ~/icctv
   docker compose up -d
   ```

8. **验证**  
   - 检查 `docker compose ps` 所有服务均为 running  
   - 访问 `http://<设备IP>:8889/health`，确保返回 healthy  
   - 通过 FRP 公网端口（如 `http://117.72.193.54:29005/health`）验证连通性  
   - 调用 `/api/auth/generate-token` 生成测试 Token，并尝试访问受保护接口

9. **更新资产清单**  
   部署成功后，同步更新内部 `inventory/projects.yaml` 及 `deployments/` 下的部署记录。

## 待补充信息

- **`requirements.txt` 具体依赖** – 文档未收录，需从仓库中获取并记录用于环境复现。
- **`mediamtx.yml` 完整模板** – 仅提及概念，缺少可运行的配置样例，尤其是鉴权回调路径和录像策略。
- **`frpc.toml` / `frps.toml` 模板** – 缺少端口映射关系、认证字段等关键示例，应补充脱敏版本。
- **iSmart Token 验证接口细节** – 对接 iSmart 的请求格式、响应校验规则尚未文档化，对集成至关重要。
- **生产环境凭据管理方案** – 当前 `SECRET_KEY` 明文嵌入 YAML，需说明如何通过 Docker secrets、环境变量注入或 Vault 加固。
- **设备指纹与注册流程** – `device_id` 的生成逻辑及与 iSmart/中心服务的关联规则。
- **录像存储与清理策略** – `recordings` 卷的管理、保留周期。
- **灰度与监控集成** – 健康检查端点已存在，但未提及 Prometheus 指标、日志聚合等生产运维配置。
- **本地开发/测试的 frpc 配置** – 根 `docker-compose.yml` 依赖的 `frpc.toml` 模板未提供。

以上信息建议优先从源码、内部文档或直接与开发团队沟通后补充完整。
