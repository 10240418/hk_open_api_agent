# Intercom Web Admin

## 项目定位

Intercom Web Admin 是一个基于 Vue 3 构建的现代化 Web 管理前端，用于提供内部管理界面。项目采用前后端分离架构，本仓库为前端应用，通过 Axios 调用远端 API（可能为 Go 后端）实现数据交互。命名与提交信息表明其管辖范围包括用户管理、消息处理或系统配置等管理功能。

## 技术栈

- **前端框架**：Vue 3 (Composition API)  
- **构建工具**：Vite 6  
- **语言**：TypeScript（主要）  
- **样式方案**：TailwindCSS v4 + Element Plus 组件库  
- **路由**：Vue Router 4  
- **状态管理**：Pinia  
- **HTTP 客户端**：Axios  
- **测试**：Vitest（单元测试）、Playwright（端到端测试）  
- **代码规范**：ESLint、Prettier、Oxlint  

此外，本地环境含有 Go 运行时及 GORM 依赖，暗示后台服务可能为 Go 语言实现，但此类依赖不在本前端仓库构建范围内。

## 目录和入口

基于 README 描述的项目结构：

```text
├── public/                 # 静态资源（不经过构建工具处理）
├── src/
│   ├── assets/            # 资源文件（图片、字体等）
│   ├── components/        # Vue 公共组件
│   ├── views/             # 页面级视图组件
│   ├── router/            # 路由配置
│   ├── stores/            # Pinia 状态管理
│   └── main.js            # 应用入口（实际应为 main.ts 或 main.js）
├── e2e/                  # Playwright 端到端测试
├── tailwind.config.js    # TailwindCSS 配置（v4 可能已简化为 CSS 导入）
├── postcss.config.js     # PostCSS 配置
├── vite.config.js        # Vite 配置
└── package.json
```

入口文件 `src/main.js` 负责挂载 Vue 应用实例，初始化路由和状态管理。

## 运行与构建

所有脚本均通过 package.json 定义，使用 pnpm 作为包管理器。

- **安装依赖**  
  ```bash
  pnpm install
  ```

- **启动开发服务器**  
  ```bash
  pnpm dev
  ```
  对应命令：`vite`，启动 Vite Dev Server，支持 HMR。

- **生产构建**  
  ```bash
  pnpm build
  ```
  对应命令：`vite build`，输出产物至默认 `dist/` 目录。

- **预览生产构建**  
  ```bash
  pnpm preview
  ```
  对应命令：`vite preview`，用于本地预览构建结果。

- **单元测试**  
  ```bash
  pnpm test:unit
  ```
  对应命令：`vitest`。

- **端到端测试**  
  ```bash
  pnpm test:e2e
  ```
  对应命令：`playwright test`。

- **代码检查与格式化**  
  - `pnpm lint`：并行运行 ESLint 和 Oxlint  
  - `pnpm format`：使用 Prettier 格式化代码

## 配置和密钥

- 未在仓库中发现 `.env` 或 `.env.*` 文件。  
- 前端实际运行时可能需要在开发环境提供环境变量，例如 API 基础地址（如 `VITE_API_BASE_URL`）。根据最近提交 `feat: update API base URL and improve error handling in axios responses`，推测存在用于指定 API 基地址的变量。  
- 所有密钥、后端数据库密码等均不在此仓库中，由后端服务管理。  
- 复刻时请参考团队内部私有配置备份，路径 `private/env-backup/`（若存在）。

## 外部依赖

### 核心运行依赖

| 包名 | 用途 |
|------|------|
| `vue` ^3.5.16 | 前端框架 |
| `vue-router` ^4.5.1 | 客户端路由 |
| `pinia` ^3.0.2 | 状态管理 |
| `axios` | HTTP 客户端 |
| `element-plus` | UI 组件库 |
| `@element-plus/icons-vue` | 图标库 |
| `dayjs` | 日期处理 |
| `tailwindcss` ^4.1.8 | 原子化 CSS 框架 |
| `@tailwindcss/typography` ^0.5.16 | 排版插件 |

### 开发与构建依赖

| 包名 | 用途 |
|------|------|
| `vite` ^6.3.5 | 构建工具 |
| `@vitejs/plugin-vue` | Vite 的 Vue 插件 |
| `@vitejs/plugin-vue-jsx` | Vue JSX 支持 |
| `typescript` ^5.8.3 | 类型系统 |
| `eslint`、`oxlint`、相关插件 | 代码检查 |
| `prettier` | 代码格式化 |
| `vitest`、`@vue/test-utils`、`jsdom` | 单元测试 |
| `@playwright/test` | 端到端测试 |
| `autoprefixer`、`postcss` | CSS 后处理 |

### 后端间接依赖（本地缓存可见）

项目本地 `pkg/mod` 中存在以下 Go 模块，表明与之配合的后端可能用到这些组件，但不属于本前端仓库的直接依赖：

- `gorm.io/gorm`、`gorm.io/driver/mysql`：ORM 及 MySQL 驱动  
- `gopkg.in/yaml.v3`：YAML 解析  
- `google.golang.org/protobuf`：Protobuf 序列化  
- `golang.org/x/sync`、`golang.org/x/crypto`：Go 扩展库  

这些信息仅用于说明整体技术生态，对本前端的构建无直接影响。

## 部署线索

- 生产构建产物为静态文件（`dist/` 目录），可部署到任何静态服务器（Nginx、CDN、Vercel 等）。  
- 需要确保前端可访问后端 API 地址，通常在构建时通过环境变量注入，例如 `VITE_API_BASE_URL`。  
- 最近提交对 API 基础 URL 和 Axios 错误处理进行了更新，说明部署前必须核对正确的 API 地址。  
- 未发现 Dockerfile 或 CI/CD 配置文件，部署方式待人工补充。  
- 远端仓库信息：  
  - `origin`: `https://github.com/10240418/iNtercom_web_admin.git`  
  - `upstream`: `https://github.com/The-Healthist/iNtercom_web_admin.git`  

## 复刻检查清单

复刻并运行本项目的步骤：

1. 克隆仓库并切换到 `main` 分支。  
2. 确认 Node.js 和 pnpm 已安装（推荐使用 Node.js 18+）。  
3. 执行 `pnpm install` 安装前端依赖。  
4. 检查是否存在 `.env` 文件（若无，请根据团队内部文档创建，至少需配置 `VITE_API_BASE_URL` 指向正确的后端服务）。  
5. 运行 `pnpm dev` 启动开发服务器，验证页面能否正常加载并与后端交互。  
6. 如果开发通过，运行 `pnpm build` 生成生产包，确保构建无报错。  
7. 将 `dist/` 目录部署到目标服务器，并配置反向代理（如 Nginx）将 API 请求转发到后端或直接依赖环境变量中的绝对地址。  
8. 更新仓库的 `inventory/projects.yaml` 和 `deployments/` 下的部署记录，标记此次部署信息。  

## 待补充信息

- **后端服务详细信息**：仓库地址、部署方式、数据库类型及连接配置（MySQL？）、Protobuf 协议定义文件位置。  
- **环境变量清单**：完整的必需环境变量及可选变量（例如 `VITE_API_BASE_URL`、可能存在的认证相关变量）。  
- **生产部署域名与端口**：前端访问域名、后端 API 域名，以及 HTTPS 配置策略。  
- **CI/CD 流程**：当前未见 `.github/workflows` 或其他 CI 配置，需确认是否有自动化构建部署流程。  
- **权限与认证**：前端是否依赖 Cookie/Token 认证，与后端如何协同。  
- **监控与日志**：前端错误监控方案（如 Sentry）的集成情况。  

本知识文档后续应随项目演进持续更新，特别是环境变量、部署细节及后端依赖的具体版本。
