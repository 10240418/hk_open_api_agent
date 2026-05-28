# yls_databoard

## 项目定位

`yls_databoard` 是一个轻量级 Web 仪表盘（dashboard），用于展示 **ylsCode** 的使用数据。项目当前处于初始化阶段，提供基于 Node.js 的简单 HTTP 服务，通过脚本直接启动，无前端构建流程。

## 技术栈

- 语言：JavaScript（ES2022+）
- 运行时：Node.js >= 18
- 框架：待补充（推测可能使用 Express 或内置 `http` 模块，需查看 `server.js` 具体实现）
- 包管理工具：未显式声明（`package.json` 未包含 `packageManager` 字段，本地可能使用 npm 或 pnpm）

## 目录和入口

- 项目根入口文件：`server.js`
- 主要配置文件：`package.json`、`.env`
- 源码目录：当前仅包含根级别文件，项目结构极简，未发现独立的 `src/`、`views/` 或 `public/` 目录（需补充实际目录树）

## 运行与构建

无构建步骤，仅通过 Node.js 直接启动服务。

| 环境 | 命令 | 说明 |
|------|------|------|
| 开发 | `npm run dev` | 执行 `node server.js`，启动服务 |
| 生产 | `npm run start` | 与 `dev` 相同，执行 `node server.js` |
| 测试 | 未定义 | `package.json` 中无 `test` 脚本 |

启动后，服务将监听某个端口（未在已扫描文件中明确，需检查代码或 `.env` 中的 `PORT` 变量）。

## 配置和密钥

项目通过环境变量文件 `.env` 管理配置。已扫描到以下变量（仅保留键名）：

- `api_key`（疑似敏感，实际值已脱敏，不写入本文档）

该变量可能用于对外部 API 的认证（例如 ylsCode API）。请确认：
- 该密钥对应的服务商及权限范围
- 是否有对应的 `PORT`、`HOST` 等网络配置变量（未在扫描中列出，可能是缺失或后续添加）

**重要**：真实 `.env` 内容不纳入知识库。复刻前应从 `private/env-backup/` 获取本地备份，或通过安全渠道注入环境变量。

## 外部依赖

项目 `package.json` 中 **未声明任何第三方依赖**（`dependencies` 和 `devDependencies` 字段为空或缺失）。当前服务可能完全基于 Node.js 内置模块，或依赖清单未纳入扫描结果。

**需要进一步确认**：
- `server.js` 中是否使用了 `express`、`axios`、`dotenv` 等库
- 安装所需的精确依赖列表（`npm ls --depth=0` 或对应锁文件）

若 `server.js` 实际引入了未声明的模块，需补充 `package.json` 中的依赖声明，并重新生成锁文件。

## 部署线索

- **代码仓库**：`https://github.com/myclain/yls_databoard.git`（`origin` 远端）
- **默认分支**：`main`
- **最近提交**：`a84c73c` - `2026-04-28 16:13:00 +0800` - `feat: init`
- **部署平台**：待补充（未在代码中检测到 `Dockerfile`、`Procfile`、CI 配置或云平台部署模板）
- **域名与端口**：待补充（可能配置在 `.env` 或服务器硬编码，需查看 `server.js`）
- **持久化存储**：无迹象表明需要数据库，若后续引入需补充连接字符串与迁移指南
- **健康检查端点**：未提供，建议实现一个基础 `/health` 路由

如需在 Hermes/Codex 上自动部署，需补充：
- 目标运行环境（如 Docker 镜像、PM2 配置或 systemd 服务文件）
- 环境变量注入方式（平台变量、Secrets Manager 等）
- 反向代理配置（如 Nginx 路由规则）

## 复刻检查清单

在另一台机器或环境复刻此项目时，请按顺序完成：

1. **拉取仓库**
   ```bash
   git clone https://github.com/myclain/yls_databoard.git
   cd yls_databoard
   git checkout main
   ```
2. **安装 Node.js 版本**
   确保本地 Node.js 版本 ≥ 18，建议使用 `fnm` 或 `nvm` 管理。
3. **获取环境变量文件**
   从安全备份位置（如 `private/env-backup/`）复制 `.env` 到项目根目录，或手动创建并填入所需值（`api_key` 等）。
4. **检查实际依赖**
   若 `package.json` 中无依赖，但代码需要第三方库，需手动补全 `dependencies` 并执行 `npm install`。
   - 先阅读 `server.js` 确认使用的模块。
   - 通过 `npm init -y` 方式重新声明或手动添加。
5. **启动服务**
   ```bash
   npm run dev   # 或 npm start
   ```
6. **验证运行**
   根据 `.env` 或代码中定义的端口访问，确认仪表盘页面可正常加载。
7. **记录部署信息**
   更新 `inventory/projects.yaml` 与 `deployments/` 目录下的部署记录，包括主机、端口、访问域名等。

## 待补充信息

以下关键信息在本次扫描中缺失，需要项目负责人或进一步分析代码后填入：

- [ ] **框架/库具体清单**：`server.js` 实际依赖的 Node.js 包（如 express, dotenv, node-fetch 等）
- [ ] **网络配置**：监听端口、绑定的 IP 地址
- [ ] **API 认证细节**：`api_key` 的使用方式（请求头名称、目标 API Base URL）
- [ ] **完整目录结构**：`views`、`static`、`assets` 等目录是否存在
- [ ] **部署方案**：目标云服务商、CI/CD 流程、反向代理/SSL 终止配置
- [ ] **监控与日志**：是否已有日志记录方案（如 winston、morgan）
- [ ] **测试脚本**：无测试命令，若后续添加请提供 `test` 脚本及测试框架
- [ ] **环境变量完整性**：`.env` 示例文件（`.env.example`）用于本地开发模板

待以上信息收集完整后，本文档可更新为自动化部署可直接引用的权威说明。
