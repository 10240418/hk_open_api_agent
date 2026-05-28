# Arti 项目文档

## 项目定位

Arti 仓库包含一个名为 `letter-exchange-app` 的私有 Web 应用，基于 Next.js 构建，初步定位为「书信交换」相关的前端项目。当前版本 `0.1.0`，处于早期开发阶段，工作区存在未提交的改动。

## 技术栈

- 语言：TypeScript（JavaScript）
- 运行时：Node.js
- 前端框架：React 19、Next.js 15.3.5（App Router）
- 样式方案：Tailwind CSS v4、`tailwind-merge`、`clsx`
- UI 组件：Radix UI（Avatar、Dialog、DropdownMenu、Toast）
- 表单与验证：React Hook Form + Zod
- 动画：Framer Motion
- 图标：Lucide React
- 状态管理：Zustand
- 日期处理：date-fns
- 开发工具：TypeScript、ESLint（`eslint-config-next`）
- 构建工具：Next.js（开发模式启用 Turbopack）
- 包管理器：待确认（`package.json` 未锁定管理器）

## 目录和入口

仓库根目录为 `Arti`，应用代码集中在子目录 `letter-exchange-app/`，目录结构示意：

```
Arti/
└── letter-exchange-app/
    ├── app/
    │   ├── layout.tsx          # 根布局（推断）
    │   └── page.tsx            # 首页入口（README 提及）
    ├── package.json            # 依赖与脚本
    ├── next.config.*           # Next.js 配置（可能存在于仓库）
    └── ...                     # 其他源码与配置文件
```

- 主入口：`letter-exchange-app/app/page.tsx`（可从浏览器直接访问）
- 环境变量备份路径：`private/env-backup/`（位于仓库外，仅本地可用）

## 运行与构建

所有命令需在 `letter-exchange-app/` 目录内执行。

### 安装依赖

首先根据实际情况选择包管理器（npm/yarn/pnpm），示例：

```bash
cd letter-exchange-app
npm install
```

### 开发服务器

```bash
npm run dev
# 实际命令：next dev --turbopack
# 默认监听 http://localhost:3000
```

### 生产构建

```bash
npm run build
# 执行 next build
```

### 启动生产服务

```bash
npm run start
# 执行 next start，端口 3000（可通过 PORT 环境变量调整）
```

### 代码检查

```bash
npm run lint
# 执行 next lint
```

## 配置和密钥

- 仓库中 **未发现** 任何 `.env`、`.env.*` 或 `*.env` 文件。
- 本地存在环境变量备份目录 `private/env-backup/`，复刻或部署时需从此目录恢复对应的 `.env` 文件到 `letter-exchange-app/`。
- 所需的**环境变量 key 名称及用途目前未记录**。常见 Next.js 项目可能包含：
  - `NEXT_PUBLIC_*` 前缀的客户端变量
  - 服务端 API 地址、数据库连接字符串等
- 本文档绝不记录任何 secret、密码、token 的具体值。

> 下一步：从备份恢复 `.env` 后，请整理出所有环境变量 key 并补充到本文档的「待补充信息」章节。

## 外部依赖

从 `letter-exchange-app/package.json` 中提取的典型依赖和用途：

| 类别 | 核心包 | 说明 |
|------|--------|------|
| 框架 | `next`, `react`, `react-dom` | Next.js + React 19 前端框架 |
| 样式 | `tailwindcss`, `@tailwindcss/postcss`, `tailwind-merge`, `clsx` | 原子化 CSS 与类名合并 |
| UI 基础 | `@radix-ui/react-avatar`, `@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`, `@radix-ui/react-toast` | 无样式交互组件 |
| 动画 | `framer-motion` | 声明式动效 |
| 图标 | `lucide-react` | SVG 图标集 |
| 表单处理 | `react-hook-form`, `@hookform/resolvers`, `zod` | 表单状态管理与 schema 验证 |
| 状态管理 | `zustand` | 轻量全局状态 |
| 工具 | `date-fns` | 日期操作 |
| 开发依赖 | `typescript`, `eslint`, `eslint-config-next`, 各类 `@types/*` | 类型检查与代码规范 |

未发现数据库驱动、ORM、邮件/支付等 SDK，推测该项目为纯前端应用或依赖外部 API。后端服务（如存在）尚未在本仓库中体现。

## 部署线索

- **推荐平台**：Vercel（README 明确提及，且为 Next.js 官方推荐）
- 也支持任何能运行 Node.js 的服务器或 Docker 环境。
- 部署流程概要：
  1. 恢复环境变量文件（`private/env-backup/` 或 CI 密钥管理）。
  2. 安装依赖并执行 `next build`。
  3. 使用 `next start` 启动生产服务，或将构建产物直接部署至 Vercel。
- 默认端口：`3000`，可通过 `PORT` 环境变量调整。
- 仓库内未发现 `Dockerfile`、`docker-compose.yml` 或自定义服务器代码。
- **缺失信息**：生产域名、SSL 证书、回调域名、持久化存储等，均需后续补充。

## 复刻检查清单

以下步骤用于从零复刻并验证项目：

- [ ] 确认拥有 `private/env-backup/` 访问权限，获取所需环境变量文件。
- [ ] 克隆仓库：`git clone https://github.com/10240418/Arti.git`，进入 `Arti` 目录。
- [ ] 进入应用目录 `cd letter-exchange-app`。
- [ ] 根据锁定文件（`package-lock.json` / `yarn.lock` / `pnpm-lock.yaml`）确定包管理器并安装依赖。
- [ ] 将环境变量文件放至 `letter-exchange-app/` 根目录（如 `.env.local`、`.env.production`）。
- [ ] 运行 `npm run dev`，在浏览器访问 `http://localhost:3000`，验证基本功能。
- [ ] 执行 `npm run build`，确保无构建错误。
- [ ] （可选）使用 `npm run start` 测试生产模式。
- [ ] 若部署至 Vercel 或其他平台，配置对应的环境变量并触发部署。
- [ ] 更新 `inventory/projects.yaml` 和 `deployments/` 运维记录。

## 待补充信息

以下关键信息尚缺失，请项目负责人在后续更新中补充：

- 环境变量列表：
  - 每个变量的 key 名称、是否必填、用途说明及示例格式
- 后端服务：
  - API 基地址、接口文档链接、鉴权方式
- 数据库（若有）：
  - 类型、版本、连接配置方式
- 第三方服务集成：
  - 是否涉及邮件、支付、OAuth 等，若有请提供服务商、回调域名、所需要的密钥名称
- 生产环境：
  - 域名、SSL 方案、端口设置、反向代理配置
- CI/CD：
  - 使用的平台和流水线配置（如 GitHub Actions、Vercel 自动部署）
- 包管理器：
  - 明确使用 npm / yarn / pnpm 及其版本
- 应用功能：
  - 完整的业务描述、核心用户流程、关键页面说明
