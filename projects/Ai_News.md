# Ai_News – 项目知识库

## 项目定位
一个现代化 AI 新闻聚合前端平台，提供多语言、深/浅主题、粒子背景的新闻展示与浏览体验。当前阶段仅包含前端，新闻数据来源及后端服务尚未明确。

## 技术栈
- **语言**：TypeScript、JavaScript
- **框架**：React 18
- **构建工具**：react-scripts (Create React App)
- **UI 库**：Material-UI (MUI) v7，包含 `@mui/material`、`@emotion/react`、`@emotion/styled`
- **国际化**：i18next、react-i18next
- **动画**：react-particles、tsparticles
- **测试**：Jest（react-scripts 内置）
- **代码规范**：ESLint（react-app 配置）
- **容器化**：Docker、Docker Compose
- **Web 服务器（生产）**：Nginx

## 目录与入口
项目根目录为 `Ai_News`，前端代码集中于 `web/` 子目录。

```
Ai_News
└── web/                     # 前端应用
    ├── public/              # 静态资源（CRA 约定）
    ├── src/                 # 源代码
    │   ├── components/      # React 组件
    │   │   ├── Header/
    │   │   ├── Footer/
    │   │   ├── Hero/
    │   │   └── News/
    │   ├── context/         # React Context
    │   ├── i18n/            # 多语言翻译文件
    │   ├── styles/          # 样式
    │   └── assets/          # 静态资源
    ├── Dockerfile           # 生产镜像构建
    ├── docker-compose.yml   # 开发/生产容器编排
    ├── deploy.sh            # 部署脚本（内容待核实）
    ├── nginx.conf           # Nginx 配置
    └── package.json         # 依赖与脚本定义
```

**入口文件**：CRA 默认 `src/index.tsx` 或 `src/index.js`（具体需核实，扫描未提供索引文件信息）。

## 运行与构建

### 本地开发
```bash
cd web
npm install
npm run start      # 或 npm run dev，等价于 react-scripts start
```
开发服务器默认监听 `http://localhost:3000`。

### 生产构建
```bash
cd web
npm run build      # 输出至 web/build/
```

### 测试
```bash
cd web
npm test           # 使用 react-scripts test (Jest)
```

### Docker 部署（基于 docker-compose）
```bash
cd web

# 开发环境（热重载，挂载源码）
docker-compose up dev

# 生产环境（Nginx 静态服务）
docker-compose up prod -d
```
- `dev` 服务使用 `node:18-alpine`，映射端口 `3000`。
- `prod` 服务使用 `nginx:alpine`，映射端口 `80`，依赖提前执行 `build` 服务生成的 `build` 目录。

**独立 Dockerfile 构建**（不使用 compose）：
```bash
cd web
docker build -t ai-news-hub .
docker run -p 80:80 ai-news-hub
```
Dockerfile 采用多阶段构建，先将源码编译为生产包，再由 Nginx 提供服务。

## 配置与密钥
- **显式 .env 文件**：未检出任何 `.env` / `.env.*` 文件。
- **Docker Compose 环境变量**：仅设置了 `NODE_ENV=development` 和 `CHOKIDAR_USEPOLLING=true`（开发用，无敏感信息）。
- **潜在密钥需求**：
  - 新闻数据源可能依赖外部 API（如 NewsAPI 等），若存在，需要 `REACT_APP_NEWS_API_KEY` 之类的环境变量。目前源码中未发现调用，**待补充**。
  - 部署时可能需要配置 Nginx 反向代理或后端服务地址。
- 密钥维护方式：通常通过 CRA 环境变量 `REACT_APP_*` 注入，应在部署系统（如 CI/CD）中安全注入，或通过 `web/.env.production` 维护（不提交至仓库）。当前本地备份位于 `private/env-backup/`（如存在）。

## 外部依赖
- **运行依赖**：
  - React、ReactDOM
  - MUI 组件库及 Emotion 引擎
  - i18next / react-i18next 国际化
  - react-particles / tsparticles 粒子效果
  - web-vitals 性能监控
- **构建与开发依赖**：
  - react-scripts (内含 webpack、babel、postcss 等)
- **容器依赖**：
  - Node.js 18 + Alpine Linux
  - Nginx Alpine
- **外部服务**（待明确）：
  - 新闻内容 API（域名、端口、认证方式）
  - 推荐系统或个性化 API
  - 邮件/消息通知服务（若有）

## 部署线索
1. 项目仓库：`https://github.com/10240418/Ai_News.git`，默认分支 `main`。
2. 部署方式：推荐 Docker Compose 或 Dockerfile 构建镜像后运行。
3. 关键部署文件：
   - `web/docker-compose.yml`：定义了 dev、build、prod 三个服务，prod 依赖 `web/build` 目录和 `nginx.conf`。
   - `web/Dockerfile`：支持独立构建镜像。
   - `web/nginx.conf`：Nginx 配置（需确认是否包含 API 代理规则）。
   - `web/deploy.sh`：自定义部署脚本，可能包含构建、推送镜像、重启容器等逻辑，内容需查看该文件。
4. 网络端口暴露：
   - 开发环境占用 3000
   - 生产环境占用 80
5. 持久化存储：无数据库/状态存储，仅静态文件。
6. 集成建议：如果后续引入后端 API，需在 Nginx 中增加 `proxy_pass` 或通过环境变量注入后端地址。

## 复刻检查清单
从零搭建可运行环境：

- [ ] 克隆仓库：`git clone https://github.com/10240418/Ai_News.git && cd Ai_News/web`
- [ ] 确认 Node.js 版本 ≥ 18，npm 或 yarn 可用
- [ ] 安装依赖：`npm install`
- [ ] 检查是否需要 `.env` 文件（若无，使用默认配置可能仅展示静态示例数据，或从 `private/env-backup/` 获取模板）
- [ ] 本地开发运行：`npm start`，验证页面渲染正常
- [ ] 执行测试：`npm test`，确保测试通过
- [ ] 生产构建：`npm run build`，检查 `build/` 目录生成
- [ ] Docker 方式部署（二选一）：
  - 使用 `docker-compose up prod -d`，确保 `build` 目录已存在（可先运行 `build` 服务）
  - 或使用 `docker build -t ai-news-hub . && docker run -p 80:80 ai-news-hub`
- [ ] 配置反向代理/域名（如有）：修改 `nginx.conf`，添加对应 server_name 和 proxy 规则
- [ ] 更新部署清单：在 `inventory/projects.yaml` 和 `deployments/` 记录本次部署信息

## 待补充信息
1. **新闻数据源**：前端如何获取新闻？是否为静态 JSON 或动态调用 API？API 端点、认证方式、请求频率限制需明确。
2. **环境变量清单**：若有 `REACT_APP_*` 变量，需列出 key 名称及用途（如 `REACT_APP_API_BASE_URL`、`REACT_APP_NEWS_API_KEY`）。
3. **后端/API 项目**：是否关联独立后端服务？如有，请提供仓库路径、技术栈、部署说明。
4. **生产域名与端口**：实际部署使用的域名、HTTPS 证书管理方式。
5. **监控与日志**：是否集成 Sentry、LogRocket 等前端监控？
6. **deploy.sh 内容**：该脚本具体做了什么，依赖哪些外部参数。
7. **国际化配置完成度**：翻译文件是否完备，语言切换逻辑是否依赖外部服务。
8. **设计资产**：定制图标、品牌资源的来源与替换方式。
9. **贡献指南合规**：仓库中是否已配置 CI（GitHub Actions 等），测试覆盖要求。
