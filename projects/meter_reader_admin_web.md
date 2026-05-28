# meter_reader_admin_web

## 项目定位

本仓库是 **meter_reader（读表）系统** 的前端管理后台，基于 Vuestic Admin 模板定制。提供仪表数据查看、配置管理等功能，面向内部运维或管理员使用。系统整体采用微服务架构，前端通过反向代理与后端 HTTP 服务通信，后端再连接 MySQL、InfluxDB、Redis 以及内部 gRPC 服务。

## 技术栈

- **语言**: TypeScript + JavaScript
- **前端框架**: Vue 3.3（Composition API）
- **构建工具**: Vite 4
- **状态管理**: Pinia 2
- **UI 组件库**: Vuestic UI 1.9
- **样式方案**: Tailwind CSS 3 + Sass
- **图表**: Chart.js 4 + vue-chartjs + chartjs-chart-geo
- **国际化**: vue-i18n 9
- **HTTP 客户端**: axios
- **路由**: vue-router 4
- **代码检查**: ESLint + Prettier + TypeScript
- **测试/文档**: Storybook 7
- **包管理**: npm（`package-lock.json` 存在，但 Dockerfile 使用 `yarn`）
- **容器化**: Docker（多阶段构建），生产使用 Nginx 提供静态文件
- **编排（本地全套环境）**: Docker Compose（包含 MySQL、InfluxDB、Redis、后端微服务等）

## 目录和入口

源码目录未完整扫描，基于标准 Vite + Vue 项目和现有文件列出关键路径：

```
meter_reader_admin_web/
├── .env.example                 # 环境变量模板（前端构建时使用）
├── package.json                 # 项目元信息与脚本
├── vite.config.ts               # Vite 构建配置（含代理、路径别名、base）
├── tsconfig.json / tsconfig.*   # TypeScript 配置（推断存在）
├── tailwind.config.js           # Tailwind CSS 配置（推断存在）
├── postcss.config.js            # PostCSS 配置（推断存在）
├── Dockerfile                   # 生产镜像构建文件
├── docker-compose.yaml          # 本地完整环境编排（含后端及基础设施）
├── nginx/
│   └── default.conf             # Nginx 站点配置（用于 Docker 部署）
├── src/
│   ├── main.ts                  # 应用入口（推断）
│   ├── App.vue                  # 根组件（推断）
│   ├── router/                  # 路由配置（推断）
│   ├── stores/                  # Pinia 状态（推断）
│   ├── components/              # 公共组件（推断）
│   ├── views/                   # 页面组件（推断）
│   ├── i18n/                    # 国际化资源
│   │   └── locales/             # 语言文件（推断，被 Vite 插件引用）
│   └── ...
├── public/                      # 静态资源（直接拷贝到 dist）
└── ...
```

**入口模块**: 由 Vite 根据 `index.html` 加载 `src/main.ts`，引入 Vue 实例、路由、状态、UI 库等。

## 运行与构建

### 本地开发

```bash
npm install          # 安装依赖
npm run dev          # 启动 Vite 开发服务器，默认监听 0.0.0.0，热重载
```

Vite 开发服务器配置了代理：`/api` → `http://localhost:8080/`，方便本地调试后端。

### 生产构建

```bash
npm run build        # lint + vue-tsc 类型检查 + vite build，产出在 dist/
npm run preview      # 本地预览生产产物（使用 vite preview）
npm run build:ci     # CI 环境构建，跳过 lint 与类型检查
npm run start:ci     # 使用 serve 提供服务，监听 dist/ 目录
```

### Storybook

```bash
npm run storybook    # 启动 Storybook 开发服务器，端口 6006
npm run build-storybook  # 构建 Storybook 静态站点
```

### Docker 构建与运行

**构建 web 镜像**：
```bash
docker build -t idreamsky/meter-reader-web-admin .
```
Dockerfile 采用多阶段构建：第一阶段用 `node:lts-alpine` 执行 `yarn` 和 `yarn build`；第二阶段用 `nginx:stable-alpine`，将 `dist/` 拷贝到 `/usr/share/nginx/html`，并注入 `nginx/default.conf`，暴露 80 端口。

**启动本地全套服务**（在仓库根目录）：
```bash
docker-compose up -d
```
这会启动 MySQL、InfluxDB、Redis、driver、scheduler、backend 以及 web 容器（如果你定义了 web 服务，但当前 `docker-compose.yaml` 未明确包含 web，仅在后端调用；若需启动 web 前端，需补充 web 服务定义）。

## 配置和密钥

### 前端构建时环境变量

在项目根目录创建 `.env` 文件（参考 `.env.example`），支持以下变量。这些变量会在 Vite 构建时通过 `import.meta.env` 暴露给客户端代码，**不要存放生产密钥**。

| 变量名 | 用途 | 备注 |
|--------|------|------|
| `VITE_APP_BUILD_VERSION` | 应用构建版本号 | 非敏感 |
| `VITE_APP_GTM_KEY` | Google Tag Manager 容器 ID | 敏感，如需使用 GTM 请提供真实 key |
| `VITE_APP_INCLUDE_DEMOS` | 是否包含示例页面 | 非敏感 |
| `VITE_APP_ROUTER_MODE_HISTORY` | 路由模式（history/hash） | 非敏感，与部署时的路径重写有关 |

`.env` 文件不可提交到版本库，`.env.example` 作为模板提供。

### 后端服务敏感变量（docker-compose 中定义）

`docker-compose.yaml` 中定义了全套后端环境所需的敏感信息，用于本地开发与测试。**这些值严禁公开**，在复刻部署时必须替换为自己的凭据。

涉及的密钥变量名如下（具体值已从本文档脱敏）：

- MySQL：`MYSQL_ROOT_PASSWORD`
- InfluxDB：`DOCKER_INFLUXDB_INIT_PASSWORD`、`DOCKER_INFLUXDB_INIT_ADMIN_TOKEN`、`INFLUX_TOKEN`
- SMTP 邮件服务：`SMTP_PASS`（发件邮箱 `sky@skylinedances.com` 的密码）
- 其他后端变量：`DB_PASS`（MySQL root 密码，文件内直接写有值，同样需替换）

在实际部署时，应通过 Docker Compose 的 `env_file` 或集群 Secret 管理机制注入这些值。

### Nginx 配置

`nginx/default.conf` 提供生产环境的 Web 服务器配置，应包含：
- 静态文件服务根路径指向 `/usr/share/nginx/html`
- 针对 Vue Router `history` 模式的回退规则（尝试文件，不存在时返回 index.html）
- 如有反向代理 `/api` 到后端的需求，也应在此文件配置（但目前构建只用于前端，代理可能由外部网关处理）

具体配置内容应检查该文件并适配实际部署架构。

## 外部依赖

### 服务依赖

前端运行本身不直接连接数据库等后端设施，但需要以下服务提供 API：

| 服务 | 地址（本地示例） | 说明 |
|------|------------------|------|
| HTTP API 服务（backend） | `http://localhost:8080` | 提供 RESTful API（通过 `/api` 前缀代理） |
| InfluxDB | `http://influx:8086`（Docker 网络内） | 时间序列数据库，存储读数数据 |
| MySQL | `mysql:3306` | 关系型数据库，存储业务数据 |
| Redis | `redis:6379` | 缓存、会话或队列 |
| gRPC 服务（driver/scheduler） | 各在 `50051` | 底层读数采集与任务调度，前端不直接访问 |
| SMTP 服务 | smtp.exmail.qq.com:465 | 邮件发送（密码、用户等已脱敏） |

### 第三方库（主要）

- 图表：chart.js, vue-chartjs, chartjs-chart-geo
- UI 组件：vuestic-ui, epic-spinners, flag-icons, ionicons
- 工具：moment, medium-editor, @vueuse/core, register-service-worker
- GTM：@gtm-support/vue-gtm
- 国际化：vue-i18n, @intlify/unplugin-vue-i18n

## 部署线索

1. **应用路径前缀**：Vite 配置中 `base: '/admin/'`，表示应用期望部署在域名的 `/admin/` 路径下。Nginx 或网关需要正确地将 `/admin/` 的请求映射到静态文件目录，并配置回退规则。
2. **构建产物**：运行 `npm run build` 后生成 `dist/` 目录，该目录即为纯静态文件集合，由 Nginx 直接提供服务。
3. **容器化部署**：执行 `docker build`，生成的镜像默认使用 Nginx 提供 `dist/` 内容，暴露 80 端口。可在 Kubernetes 或 Docker Compose 中运行，并通过 Ingress/反向代理挂在 `/admin/` 路径。
4. **API 代理**：生产环境中，前端发出的 `/api` 请求通常需要由反向代理（如 Nginx、Traefik）转发到实际的 HTTP API 服务（backend:8080）。开发时 Vite 自带代理；生产则需在网关或 Nginx 中配置。
5. **环境变量注入**：Vite 的构建时环境变量是在编译阶段固化到 JS 代码中的，因此对每个部署环境（开发、测试、生产）需要提前准备对应的 `.env` 文件并运行 `npm run build`。如需动态注入，可考虑运行时用配置文件替换或使用 nginx 的 SSI/环境变量替换方案（较复杂，不推荐）。
6. **后端依赖**：确保 MySQL、InfluxDB、Redis 及三个后端微服务（driver、scheduler、backend）已就绪，且网络互通，端口一致。前端才能正常工作。

## 复刻检查清单

要从零复刻并部署此项目，请按照以下步骤操作：

- [ ] 克隆仓库 `https://github.com/The-Healthist/meter_reader_admin_web.git`，切换到需要部署的分支（如 `liuyang` 或主分支）。
- [ ] 安装 Node.js 与 npm（版本参考 `package.json` engines，推荐 LTS）。
- [ ] 在项目根目录根据 `.env.example` 创建 `.env` 文件，填入必要的 Vite 环境变量（`VITE_APP_GTM_KEY` 等）。
- [ ] 运行 `npm install` 安装前端依赖。
- [ ] 确认后端 API 地址：本地开发可直接使用 Vite 代理到 `http://localhost:8080`；生产构建需确认最终部署的 API 网关。
- [ ] 运行 `npm run build` 生成 `dist/`；若跳过 lint 和类型检查可用 `npm run build:ci`。
- [ ] 准备 Nginx 配置：确保 `nginx/default.conf` 与部署路径 `/admin/` 匹配，并配有 SPA 回退规则；如需要 API 代理，添加对应 `proxy_pass` 指令。
- [ ] 构建 Docker 镜像（如有需要）：`docker build -t your-registry/meter-reader-web-admin .`，推送至镜像仓库。
- [ ] 部署后端基础设施（可参考仓库中的 `docker-compose.yaml`，但替换所有密钥和凭据）。至少确保 backend HTTP 服务可用。
- [ ] 部署前端容器或静态文件至 Web 服务器，并配置路由 `/admin/*` 指向前端，检查 API 请求路径是否正确转发。
- [ ] 验证页面可访问，登录功能、数据图表展示正常。
- [ ] 如启用了 GTM，确认 `VITE_APP_GTM_KEY` 正确且网站可追踪。
- [ ] 更新内部部署记录（`inventory/projects.yaml` 和 `deployments/` 下的文件）。

## 待补充信息

- [ ] **生产环境域名与 URL**：目前项目无明确文档说明对外提供服务的域名，需要补充。
- [ ] **后端 API 实际地址**：生产环境中 `/api` 代理需要指向的后端服务地址和端口未明确，需从运维配置或后端文档获取。
- [ ] **GTM Key 的实际值**：如需启用 Google Tag Manager，联系营销或产品团队获取容器 ID 并填入 `VITE_APP_GTM_KEY`。
- [ ] **路由模式**：`VITE_APP_ROUTER_MODE_HISTORY` 建议设为 `true` 以使用 history 模式，但需要服务器端支持。确认生产环境 Nginx 或网关已配置相应的回退规则。
- [ ] **身份认证与授权**：项目是否依赖 OAuth2、JWT 或 Session，登录接口地址、Token 刷新策略等需了解清楚并配置。
- [ ] **Storybook 部署**：若需对外展示组件库，需明确是否要单独部署 Storybook。
- [ ] **持续集成配置**：本项目包含 `husky` 和 `lint-staged`，但未见 CI/CD 脚本（如 GitHub Actions），需补充或创建自动化构建流程。
- [ ] **后端密钥管理**：`docker-compose.yaml` 中的明文密钥需迁移至安全保管库（如 Vault、集群 Secrets），并在部署文档中说明如何注入。
- [ ] **许可证**：项目为 MIT 协议（基于 Vuestic Admin），需确认业务代码的合规性及其依赖许可证。
