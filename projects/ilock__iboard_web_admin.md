# ilock__iboard_web_admin

## 项目定位

iBoard Web 管理后台前端工程。为 iBoard 产品线提供基于浏览器的管理控制台（Admin Console），采用 Vue 3 + Vite + TypeScript 技术栈，配合 Ant Design Vue 组件库，实现业务配置、数据查看等管理功能。

## 技术栈

- **语言**：TypeScript (~5.6)，少量 JavaScript
- **框架**：Vue 3.5（Composition API + `<script setup>` SFC）
- **构建工具**：Vite 6
- **UI 库**：Ant Design Vue 4.x
- **状态管理**：Pinia 2.3
- **路由**：Vue Router 4
- **HTTP 客户端**：Axios 1.7
- **CSS 预处理**：Sass 1.83
- **代码质量**：ESLint 9、vue-tsc 2.1
- **组件按需加载**：unplugin-vue-components（配合 AntDesignVueResolver）
- **容器化**：Docker 多阶段构建（Node LTS → Nginx Stable）

## 目录和入口

- 本地路径：`/Users/yangliu/Documents/Code/ilock/iboard_web_admin`
- 仓库内相对路径：`ilock/iboard_web_admin`
- 当前分支：`carousel_version`
- 最近提交：`11c8170` (2026-04-25) “feat: update Docker and Nginx configurations for improved deployment”

典型目录结构（基于源码信号与 Vite/Vue 惯例推断）：

```
.
├── nginx/
│   └── default.conf          # Nginx 部署配置
├── public/                   # 不参与编译的静态资源
├── src/                      # 应用源码
│   ├── main.ts               # 应用入口
│   ├── App.vue               # 根组件
│   ├── router/               # Vue Router 路由定义
│   ├── stores/               # Pinia 状态管理
│   ├── views/                # 页面组件
│   ├── components/           # 公共/业务组件
│   └── assets/               # 样式、图片等
├── Dockerfile                # 容器构建定义
├── package.json              # 依赖与脚本
├── vite.config.ts            # Vite 配置
├── tsconfig.json             # TypeScript 配置
└── .env                      # 环境变量（值不入库）
```

应用入口为 `src/main.ts`，Vite 构建后静态资源基础路径为 `/admin/`。

## 运行与构建

### 本地开发

```bash
yarn install
yarn dev
```

- 开发服务器监听 `0.0.0.0:8082`（可配置于 `vite.config.ts`）。
- 所有 `/api` 请求通过 Vite 内置代理转发到后端 API 服务（目标环境见配置章节，不同环境指向不同后端）。
- 支持 HMR。

### 生产构建

```bash
yarn build
```

执行 `vue-tsc -b && vite build`，产物输出至 `dist/`。

### 本地预览构建结果

```bash
yarn preview
```

### Docker 构建

- **Dockerfile 多阶段构建**：第一阶段使用 `node:lts-alpine` 安装依赖并构建；第二阶段从 `nginx:stable-alpine` 复制 `dist` 目录并注入 Nginx 配置。
- 容器暴露端口 **9002**。
- 多平台构建示例（来自 Dockerfile 注释）：
  ```bash
  docker buildx build --platform linux/amd64,linux/arm64 -t <registry>/<image>:<tag> .
  ```

镜像标签、仓库地址由 `.env` 变量注入，不应硬编码。

## 配置和密钥

### 环境变量（`.env`）

以下仅列出 **键名**，实际值存放在安全位置（如 `private/env-backup/` 或密钥管理系统），**绝不写入本文档**。

| 变量名           | 用途说明                                  |
| ---------------- | ----------------------------------------- |
| `APP_PORT`       | 应用端口（可能用于本地或部署标识）        |
| `DOCKER_REGISTRY`| 镜像仓库地址（如   `registry.example.com`)|
| `IMAGE_NAME`     | 镜像名称                                  |
| `IMAGE_TAG`      | 镜像标签                                  |
| `NODE_ENV`       | 运行环境（development / production）      |

注意：这些变量大概率仅用于构建或部署流程，**不会被直接注入前端 bundle**。

### Vite 配置（`vite.config.ts`）

- **静态资源基础路径**：`base: '/admin/'`  
  所有部署后的资源 URL 均以此为前缀，网关/Nginx 必须相应配置。
- **路径别名**：`@` → `src/`  
- **开发代理**：  
  - 前缀 `/api` 的请求被代理到**后端 API 服务**。
  - 代理目标包含多个环境选项（京东云地址、本地地址等），但具体 IP 和端口不在此处公开；部署前需根据环境确认。
- **组件自动导入**：通过 `unplugin-vue-components` 配合 `AntDesignVueResolver`，无需手动注册 Ant Design Vue 组件。

### Nginx 配置（`nginx/default.conf`）

该文件未在源码信号中展示内容。根据镜像结构和 `base: '/admin/'` 的设置，必须确保：

- 根路径正确指向 `/usr/share/nginx/html`。
- 处理 `/admin/` 路由，让 SPA 的 fallback 到 `index.html`。
- 若生产环境不走独立 API 网关，则还需在此文件中配置 `/api` 的反向代理规则，将请求转发至后端服务。

复刻时必须获取或重建该 Nginx 配置。

## 外部依赖

- **后端 API 服务**：管理后台所必需的后端接口，通过 `/api` 路径访问。  
  开发环境使用 Vite 代理转发，生产环境需由 Nginx/Ingress/API Gateway 代理。  
  未发现邮件、支付、第三方 OAuth 等外部服务集成的迹象（源码信号仅含 Axios 调用后端，无额外 SDK）。

## 部署线索

1. **镜像仓库**：通过 `.env` 中的 `DOCKER_REGISTRY`、`IMAGE_NAME`、`IMAGE_TAG` 定义，Dockerfile 注释中曾出现 `idreamsky/iboard-web-admin` 示例标签。
2. **容器端口**：`9002`，需在容器编排或启动时映射。
3. **HTTP 路由**：
   - 前端资源路径前缀：`/admin/`
   - API 代理路径：`/api/` → 后端服务
4. **Git 仓库**：`https://github.com/The-Healthist/iboard_web_admin.git`
5. **部署方式**：适合容器化部署（Kubernetes、Docker Compose 等），结合 Nginx Ingress 或外部负载均衡。
6. **潜在构建方式**：Dockerfile 支持多平台（amd64/arm64），可使用 `docker buildx`。

## 复刻检查清单

- [ ] 克隆仓库并切换至目标分支（如 `carousel_version`）。
- [ ] 补全 `.env` 文件（从安全备份获取真实的 `DOCKER_REGISTRY`、`IMAGE_NAME`、`IMAGE_TAG` 等值）。
- [ ] 安装依赖：`yarn install`。
- [ ] 本地验证：`yarn dev`，确保页面可访问，API 代理连通正常。
- [ ] 获取或编写生产适用的 `nginx/default.conf`（适配 `/admin/` 路由及 `/api` 代理）。
- [ ] 执行 `yarn build` 生成生产包，检查构建日志无错误。
- [ ] 构建 Docker 镜像：
  ```bash
  docker build -t $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG .
  ```
  （如需多平台，使用 `docker buildx build --platform linux/amd64,linux/arm64`）
- [ ] 推送镜像至仓库：
  ```bash
  docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG
- [ ] 部署到目标环境：
  - 配置容器端口映射 (9002)。
  - 配置路由规则，使 `<域名>/admin/` 指向该服务。
  - 配置 `/api` 反向代理至真实后端 API 地址。
- [ ] 部署后验证：
  - 访问 `<域名>/admin/`，确认页面正常渲染。
  - 通过管理后台执行几个关键 API 调用，检查数据返回正确。
- [ ] 更新部署文档：在 `inventory/projects.yaml` 和 `deployments/` 下记录本次部署信息。

## 待补充信息

- `.env` 各变量的实际值（依赖环境备份或保密管理工具）。
- 各环境后端 API 服务的确切地址（开发/测试/预发/生产）。
- `nginx/default.conf` 完整内容，便于准确复刻生产 Nginx 规则。
- 生产环境访问域名及是否启用 HTTPS、CDN 等。
- CI/CD 管道配置（如 GitLab CI、GitHub Actions），触发构建的规则。
- 是否有额外的注入环境变量（例如 Kubernetes ConfigMap/Secret 中定义的 `VITE_*` 变量）。
- 是否有除 REST API 外的其他外部依赖（WebSocket、第三方 SDK 等）。
