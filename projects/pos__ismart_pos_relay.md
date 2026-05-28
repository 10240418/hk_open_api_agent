# ismart_pos_relay

## 项目定位
ismart_pos_relay 是一个用 Go 语言编写的 HTTP 中继服务，基于 Gin 框架，集成了 JWT 认证能力。从模块名 `ismartposrelay` 推断，它可能负责在 POS 系统组件之间转发请求、校验身份或聚合数据，定位为轻量级、可容器化部署的业务网关或 relay 层。

## 技术栈
- 语言：Go 1.22+
- 框架：Gin (github.com/gin-gonic/gin)
- 认证：golang-jwt/v4
- JSON 处理：goccy/go-json，sonic，标准 encoding/json 并存
- 校验：go-playground/validator/v10
- 其它：golang.org/x/crypto，ugorji/go/codec，protobuf 等间接依赖
- 容器化：多阶段 Docker 构建，构建阶段使用 `golang:1.24-alpine`，运行阶段使用 `alpine:3.14`
- GOPROXY：构建时指定为 `https://goproxy.cn,direct`

## 目录和入口
- 本地工作副本路径：`/Users/yangliu/Documents/Code/pos/ismart_pos_relay`
- Git 分支：`master`（最后提交 `d407785`，信息 `feat：last`）
- 工作区无未提交改动
- 源码布局（根据 Dockerfile 推理）：
  - 根目录存在 `main.go`（或类似入口），编译产出为 `main` 二进制
  - 存在 `.conf/` 目录，存放配置文件，构建时随产物一同打包至镜像的 `/app/.conf`
- 项目模块名：`ismartposrelay`（go.mod）

## 运行与构建
### 本地构建
```bash
go build -o main .
```
要求 Go 1.22+，依赖自动通过 `go.mod` 下载。

### Docker 构建
```bash
docker build -t ismart-pos-relay .
```
多阶段构建说明：
- Stage 1 (`build-stage`)：在 `golang:1.24-alpine` 中执行 `go build -o main .`，代理地址为 `GOPROXY=https://goproxy.cn,direct`
- Stage 2 (`release-stage`)：基于 `alpine:3.14`，复制二进制 `main` 和配置目录 `.conf` 到 `/app`
- 暴露端口：`8080`（容器内）
- 启动命令：`/app/main`

### 启动服务
默认监听 HTTP 端口 8080。工作目录需要包含 `.conf` 子目录，否则服务可能因缺少配置而失败。容器启动示例：
```bash
docker run -p 8080:8080 ismart-pos-relay
```
如需覆盖或挂载外部配置，应挂载到 `/app/.conf`。

## 配置和密钥
- **未发现 `.env`、`.env.*` 或 `*.env` 文件**，项目不从环境文件读取配置。
- 配置来源：`./.conf` 目录（内嵌于镜像）。该目录的具体内容未在源码信号中公开，推测包含 JSON/YAML 格式的服务端口号、日志等级、上游端点、JWT 配置等。
- **密钥与敏感信息**：
  - 项目使用了 JWT 签名（`golang-jwt`），必然存在签名密钥。其存放位置大概率在上述 `.conf` 目录的某个文件中，或通过环境变量导入（未发现相关库）。
  - 严禁在本文档中记录任何密钥值。实际部署时，需从内部凭据管理系统（如 `private/env-backup/`）获取对应的 JWT secret 等敏感配置，并在不泄密的前提下注入应用。
- **可保留的环境变量 KEY 名称（推断）**：这类变量可能用于覆盖配置，如 `JWT_SECRET`、`LISTEN_PORT`、`UPSTREAM_URL` 等，但源码中未直接体现，需查阅 `.conf` 文件细节。

## 外部依赖
- 运行时无外部数据库、缓存或消息队列依赖（go.mod 中未见相关驱动）。
- 依赖全部为 Go 第三方库，包括 Gin、JWT、JSON 解析器、校验器等，无专有服务 SDK。
- 与外部交互可能通过 HTTP 调用上游业务服务（未在源码信号中暴露具体地址），需结合 `.conf` 中的 URL 配置确定。

## 部署线索
- **代码仓库**：`https://github.com/The-Healthist/pos_ismart_relay.git`（唯一远端 origin）
- **当前部署形态**：仅提供了 Dockerfile，无 Helm、docker-compose 或 Kubernetes 清单。
- **推荐部署流程**：
  1. 从仓库 `master` 分支拉取代码（commit `d407785`）
  2. 确保 `.conf` 目录中的配置文件已填写正确的生产参数（重点替换本地密钥、上游地址等）
  3. 执行 `docker build -t <registry>/ismart-pos-relay:<tag> .` 并推送
  4. 在目标环境以容器方式运行，映射 8080 端口，并配置健康检查端点（待确认）
- **端口**：容器内服务监听 `8080`，TLS 终结或外部路由需由反向代理（如 Nginx、Traefik）处理。
- **配置注入**：若需将配置文件外置，可将宿主机目录挂载到容器的 `/app/.conf`；注意镜像已自带一份默认配置，挂载会覆盖。

## 复刻检查清单
1. 克隆仓库并切换到 `master` 分支
2. 获取内部 `.conf` 配置模板，根据部署环境填入必要的密钥与地址（JWT secret、upstream URL 等），但切勿入库
3. 确认 Go 版本不低于 1.22，或直接使用 Docker 构建
4. 构建镜像：`docker build -t ismart-pos-relay .`
5. 运行容器，检查 stdout 日志确认启动成功，尝试访问 `http://localhost:8080` 的健康探测或已知端点
6. 配置反向代理（80/443 → 8080）和证书（如需要）
7. 记录本次部署使用的镜像 tag、配置版本，更新 `inventory/projects.yaml` 及 `deployments/` 部署记录

## 待补充信息
- `.conf` 目录下的具体文件列表及其配置项含义（包含但不限于：JWT 密钥字段名、监听端口是否可配、上游服务域名/路径）
- 服务提供的 HTTP 端点路由（健康检查、业务转发、JWT 签发/校验等）
- 是否依赖外部认证服务或需白名单 IP/域名
- 构建时的 Go 代理如需切换内网代理的说明
- 日志、监控与链路追踪的实现方式（若存在）
- 生产环境预设的资源限制与自动伸缩策略
- 本地开发 / 灰度 / 生产环境的配置差异对照
