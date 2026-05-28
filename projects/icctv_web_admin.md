# icctv_web_admin 项目文档

## 项目定位

`icctv_web_admin` 是 iCCTV 系统的 Web 管理后台，采用 Vue 3 + TypeScript + Vite 构建。项目为运维人员提供视频监控设备管理、数据看板、报表导出等功能界面，前端通过 API 与后端服务交互，最终以 Nginx 静态资源服务的形式部署。

## 技术栈

- **语言**：TypeScript（~5.9.3）
- **UI 框架**：Vue 3（Composition API + `<script setup>`）
- **构建工具**：Vite（通过 rolldown-vite 7.2.2 提供）
- **状态管理**：Pinia（^2.3.1）
- **路由**：Vue Router（^4.6.3）
- **UI 组件库**：Ant Design Vue（^4.2.6）
- **样式方案**：Tailwind CSS 4（已启用 Just-in-Time 引擎，通过 `@tailwindcss/vite` 插件集成）
- **HTTP 客户端**：axios（^1.13.2）
- **图表**：ECharts（5.6.0），通过 `vue-echarts`（6.7.3）封装为 Vue 组件
- **电子表格**：exceljs（^4.4.0），用于前端导出 Excel
- **工具库**：dayjs（^1.11.19）处理日期
- **包管理**：Yarn（^1.22.22），通过 `packageManager` 字段锁定版本
- **代码检查**：vue-tsc（^3.1.3）用于类型检查

## 目录和入口

（源码目录结构未提供，下列描述基于常规 Vue 3 + Vite 项目约定）

- `src/` – 主源码目录
  - `main.ts`：应用入口，创建 Vue 实例，挂载路由、状态管理、Ant Design Vue 等
  - `App.vue`：根组件
  - `router/`：路由配置
  - `stores/`：Pinia 状态仓库
  - `views/`：页面组件（如 `orangepi/` 目录下的 `useOrangePi.ts` 可能包含地图或设备相关逻辑）
  - `components/`：可复用组件
- `public/`：静态资源
- `vite.config.ts`：Vite 配置，含 `@` 别名指向 `src`
- `tsconfig.json` / `tsconfig.*.json`：TypeScript 配置，可能继承自 `@vue/tsconfig`
- `package.json`：依赖与脚本声明
- `docker-compose.yml`、`Dockerfile`、`nginx.conf`：部署相关文件

**关键入口文件线索**：
- 从 Dockerfile 中 `cat src/views/orangepi/useOrangePi.ts | grep publicToken` 可知，项目内存在与 OrangePi（可能为某款开发板/边缘设备）相关的功能，且使用了 `publicToken`（疑似高德地图、百度地图等第三方服务的公共 token）。

## 运行与构建

### 本地开发

```bash
yarn install        # 安装依赖
yarn dev            # 启动开发服务器（vite）
```

开发服务器默认端口及代理规则需查阅 `vite.config.ts`（源码中未提供，可能需要补充）。

### 类型检查

```bash
yarn typecheck      # 仅运行 vue-tsc 类型检查，不产生输出
```

### 生产构建

```bash
yarn build          # 先执行 vue-tsc 类型检查，再通过 vite build 生成 dist
```

构建产物位于 `dist/` 目录。

### 构建产物预览

```bash
yarn preview        # 本地预览生产构建
```

### Docker 构建与运行

项目内提供 `docker-compose.yml` 可直接启动完整服务：

```bash
docker compose up -d
```

该命令会：
1. 基于 `Dockerfile` 构建镜像，传入构建参数 `VITE_API_BASE_URL=/api`。
2. 创建并启动容器 `icctv-web-admin`，将容器 80 端口映射到宿主机 3000 端口。
3. 自动加入 `icctv-network` 桥接网络。

单独构建镜像：

```bash
docker build \
  --build-arg VITE_API_BASE_URL=/api \
  -t icctv-web-admin .
```

## 配置和密钥

### 环境变量

- **`VITE_API_BASE_URL`**：后端 API 的基础路径，在构建阶段会被 Vite 内联到产物中。当前 `docker-compose.yml` 中设置为 `/api`，通常配合 Nginx 反向代理将 `/api` 转发至实际后端。

注意：未在项目根目录发现 `.env` 或 `.env.*` 文件，所有配置可能直接通过 Docker 构建参数注入或硬编码。

### 第三方密钥线索

- 在 `src/views/orangepi/useOrangePi.ts` 中出现 `publicToken` 标识，可能为高德地图、百度地图或其他服务的公共令牌。此项 **不在此文档展示具体值**，复刻时需要向项目负责人获取并在该文件中替换或通过环境变量传入（当前未发现从环境变量读取该 token 的逻辑，可能需要代码改造）。

## 外部依赖

### 后端 API

- 项目依赖一个未知的后端服务，通过 `VITE_API_BASE_URL` 指定的路径访问。根据 Docker 部署方式，预期后端与前端处于同一 `icctv-network`，且 Nginx 配置中会将 `/api` 代理至后端。真实后端地址、端口、认证方式需要补充。

### NPM 依赖

已通过 `package.json` 锁定，核心依赖已在技术栈中列出。安装时需注意：
- `vite` 版本被重写为 `npm:rolldown-vite@7.2.2`，不是官方 Vite，由 `overrides` 强制指定，确保统一。
- 使用 Yarn v1 作为包管理器，`packageManager` 字段保证协作者使用相同版本。

### Docker 镜像

- **构建镜像**：`swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/node:20-alpine`
- **运行镜像**：`swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/nginx:alpine`
- 两者均来自华为云容器镜像服务，包含 `docker.io` 前缀，实际为代理后的官方镜像。若需在其他环境构建，可替换为 `node:20-alpine` 及 `nginx:alpine`。

## 部署线索

### Docker Compose 部署

- **服务名**：`icctv-web-admin`
- **网络**：`icctv-network`（bridge 模式），需要后端服务加入同一网络。
- **端口映射**：宿主机 3000 → 容器 80
- **重启策略**：`unless-stopped`
- **构建参数**：`VITE_API_BASE_URL` 可依据实际部署环境调整（如生产环境可能为 `https://api.example.com` 或保持相对路径）。

### Nginx 配置

`nginx.conf` 文件内容未提供，需从源码仓库获取。推测其中包含：
- 静态文件根路径指向 `/usr/share/nginx/html`
- 针对 `/api` 的 `proxy_pass` 配置，将请求转发至后端服务地址
- 可能的 Gzip 压缩、缓存控制、前端路由的 fallback 规则（支持 Vue Router 的 history 模式）

### 构建环境注意

- Dockerfile 中主动清除了 `HTTP_PROXY`、`HTTPS_PROXY` 等代理环境变量，并配置 npm/yarn 镜像源为 `https://registry.npmmirror.com`。在内部环境可能需要调整或删除这些步骤。
- 若本地构建非 Docker 环境，请确保可以访问 npm registry，或者配置相同的镜像源。

## 复刻检查清单

1. **获取源码**
   ```bash
   git clone https://github.com/10240418/icctv_web_admin.git
   cd icctv_web_admin
   ```

2. **检查 Node.js 版本**：参考 `node:20-alpine` 镜像，建议使用 Node.js 20.x。

3. **安装依赖**（需 Yarn 1.x）
   ```bash
   yarn install
   ```

4. **补充缺失的环境变量/密钥**
   - 确认 `VITE_API_BASE_URL` 的值（本地开发可在根目录创建 `.env` 文件设置 `VITE_API_BASE_URL`，Vite 会加载）。
   - 获取第三方服务的 `publicToken`（如高德地图 key），并修改对应源码或改造成环境变量注入（当前代码中可能硬编码）。

5. **验证本地开发**
   ```bash
   yarn dev
   ```
   检查控制台无报错，能正常访问并调用后端 API（需确保后端可用或 mock）。

6. **配置 Nginx**：从仓库中提取 `nginx.conf`，根据实际后端地址修改 `/api` 代理目标。如果缺失，需要自行编写 SPA 宿主配置（包含 `try_files` 和 API 代理）。

7. **构建并运行 Docker**
   ```bash
   docker compose up -d --build
   ```
   确保后端服务已在 `icctv-network` 中且 Nginx 能够通过容器名或 IP 访问。

8. **网络与端口**：防火墙或安全组需放通宿主机 3000 端口；若后端也在同一 Docker 网络，检查其容器名或服务名是否与 Nginx 配置中的代理地址一致。

9. **验证部署**：通过浏览器访问 `http://<host>:3000`，确认页面加载、路由跳转正常，API 请求能从 `/api` 正确代理到后端。

10. **更新运维记录**：部署成功后更新 `inventory/projects.yaml` 和 `deployments/` 下的部署记录。

## 待补充信息

- **完整的源码目录结构**：当前仅从 Dockerfile 和配置文件推断，需导出 `src/` 下的完整文件树。
- **nginx.conf 内容**：反向代理规则、后端地址、自定义头部等细节缺失，直接影响部署。
- **后端 API 规格**：API 端点列表、认证方式（是否使用 JWT、Cookie 等）、请求/响应结构，以便前端对接和调试。
- **高德地图或其他第三方 token**：`publicToken` 的来源、用途和申请方式，需记录在内部文档（不公开到本文档）。
- **Vite 开发代理配置**：`vite.config.ts` 中是否含有 `server.proxy` 以解决开发跨域问题。
- **测试及静态资源**：是否包含单元测试（如 Vitest）、E2E 测试；`public/` 下是否有特定配置文件（如 favicon、Web Worker 等）。
- **多环境构建策略**：目前仅有单一的 `VITE_API_BASE_URL` 构建参数，若需区分开发/测试/生产等环境，需补充 `.env.production`、`.env.staging` 等文件及对应的构建命令。
- **CI/CD 流程**：若有自动化构建与发布，需说明流水线配置。
