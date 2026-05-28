# mcp-figma

## 项目定位
MCP Figma 是一个基于 Model Context Protocol (MCP) 的集成服务，使 AI 编程助手（Cursor、GitHub Copilot、Windsurf、Claude Desktop 等）能够直接与 Figma 进行双向通信：读取设计内容并通过程序化方式修改设计。它由 TypeScript MCP 服务器、本地 WebSocket 通道和 Figma 插件三部分协同工作，对 AI 暴露一组工具，用于在设计协作流程中实现自动化操作。

## 技术栈
- **语言**：TypeScript（编译为 JavaScript 模块）
- **运行时**：Node.js >= 18
- **核心协议**：Model Context Protocol (MCP)（`@modelcontextprotocol/sdk`）
- **通信**：WebSocket（`ws`）用于 MCP 服务器与 Figma 插件之间的本地桥接
- **工具库**：`uuid`、`zod`
- **构建工具**：tsup（主项目）、tsc（子包）
- **Figma 插件**：基于 Figma 插件 API（manifest.json, code.js, ui.html）

## 目录和入口
```
mcp-figma/
├── package.json                  # 主包，bin 入口指向 dist/talk_to_figma_mcp/server.js
├── tsup.config.ts (或类似)       # 构建配置
├── README.md
├── scripts/                      # 辅助脚本（发布插件、配置 AI 助手）
├── src/
│   ├── talk_to_figma_mcp/        # MCP 服务器源码
│   │   ├── package.json          # 子包独立声明，包含 ts-node 运行脚本
│   │   ├── server.ts             # 主入口 (作为 MCP 服务器，同时启动 WebSocket)
│   │   └── ...
│   ├── mcp_plugin/               # Figma 插件源码（manifest, code.js, ui.html 等）
│   └── socket.ts                 # WebSocket 服务器（被 MCP 服务器自动拉起）
└── dist/                         # 构建产物 (npm 包包含此目录)
    └── talk_to_figma_mcp/server.js  # 实际可执行入口
```

**入口说明**：
- 全局命令：执行 `npx mcp-figma` 或 `node dist/talk_to_figma_mcp/server.js` 启动 MCP 服务器。
- NPM 包 `@sethdouglasford/mcp-figma` 发布后可通过 `npx ai-figma-mcp@latest` 使用（README 所示）。

## 运行与构建

### 初始化
```bash
npm run setup          # 安装依赖并构建
```

### 构建
```bash
npm run build          # 使用 tsup 构建主项目
npm run build:watch    # 监听模式
```

子目录 `src/talk_to_figma_mcp/` 独立构建（`npm run build` 在该目录执行 `tsc`），主要用于开发阶段直接运行 TS。

### 启动服务
- 生产模式：
  ```bash
  npm start            # 运行 dist/talk_to_figma_mcp/server.js
  ```
- 开发模式（ts-node 直接运行 TS）：
  ```bash
  npm run dev          # tsup --watch (主项目)
  # 或进入子目录执行：
  cd src/talk_to_figma_mcp && npm run dev
  ```
- 单独启动 WebSocket 服务器（调试用，一般不需要手动执行）：
  ```bash
  npm run socket       # 运行 dist/socket.js
  ```

### 发布
- NPM 发布：
  ```bash
  npm run pub:release  # 构建后执行 npm publish
  ```
- Figma 插件发布：
  ```bash
  npm run publish:figma  # 执行 ./scripts/publish-figma-plugin.sh
  ```

### AI 助手配置
最终用户通过配置其 AI 助手的 MCP 参数来连接本服务，典型配置为：
```json
{
  "mcpServers": {
    "TalkToFigma": {
      "command": "npx",
      "args": ["ai-figma-mcp@latest"]
    }
  }
}
```
具体配置路径参考 README 中针对 Cursor、GitHub Copilot、Windsurf、Claude Desktop 的说明。

## 配置和密钥
- 项目未检出 `.env` 或类似环境变量文件。
- 无显式环境变量需求（如 API Token）。与 Figma 的实际交互依赖本地 Figma Desktop 或 Web 环境中已登录的用户会话及通过 WebSocket 建立的连接。
- 若未来需要持久化配置（如自定义 WebSocket 端口），应通过环境变量注入，但当前代码未声明相关 KEY。

**注意**：任何未来引入的 Figma Personal Access Token 或其他凭据，均不应写入代码库，应通过环境变量或安全的 Secret 管理方式提供。

## 外部依赖
### 运行时依赖
- `@modelcontextprotocol/sdk`：MCP 协议实现
- `ws`：WebSocket 客户端/服务器
- `uuid`：唯一标识生成
- `zod`：运行时类型校验

### 开发依赖
- `typescript`、`ts-node`：TypeScript 支持
- `tsup`：主构建工具
- `@types/node`、`@types/ws`、`@types/uuid`：类型定义
- `eslint`：代码质量

### 外部服务
- **Figma**：需本地运行 Figma 客户端并安装配套插件。插件可通过社区安装或从 `src/mcp_plugin/` 本地加载。
- **AI 助手**：要求具备 MCP 客户端功能（Cursor、GitHub Copilot 等）。

## 部署线索
- 本项目以 NPM 包形式分发，核心是 `@sethdouglasford/mcp-figma`（或 `ai-figma-mcp`，可能为简名）。部署方式为用户全局或项目级 `npx` 启动。
- 无传统服务端部署需求，所有通信在本地进行：
  1. AI 助手通过标准 I/O 或 SSE 与 MCP 服务器通信。
  2. MCP 服务器在 `localhost` 上启动一个 WebSocket 服务器（端口从代码逻辑推断，但未硬编码公开）。
  3. Figma 插件连接到同一 WebSocket，从而转发 AI 指令和 Figma 响应。
- 无数据库、无第三方 API 回调域名。
- 如需在公司内部镜像或离线使用，可将 NPM 包发布至私有 Registry，并确保 Figma 插件通过内部分发渠道安装。

## 复刻检查清单
1. **环境准备**：Node.js >= 18，npm。
2. **克隆仓库**：
   ```bash
   git clone <repo-url>
   cd mcp-figma
   ```
3. **安装与构建**：
   ```bash
   npm run setup
   ```
4. **验证构建产物**：确认 `dist/` 目录生成，且 `dist/talk_to_figma_mcp/server.js` 存在。
5. **启动 MCP 服务器（本地测试）**：
   ```bash
   npm start
   ```
   检查是否输出 WebSocket 服务启动信息（可能无显式日志，需确认端口监听）。
6. **安装 Figma 插件**：
   - 通过社区链接安装，或从 `src/mcp_plugin/` 本地开发加载。
7. **配置 AI 助手**：
   按对应 IDE 的 MCP 配置指引，将服务器命令填为 `npx ai-figma-mcp@latest`（或指向本地开发路径，如 `node /path/to/dist/talk_to_figma_mcp/server.js`）。
8. **功能验证**：
   在 AI 助手中输入类似 `"Join the Figma channel 'xxxx' and tell me about the current design"` 的指令，验证双向通信。
9. **若需发布内部版本**：
   修改 `package.json` 中的包名，执行 `npm run pub:release` 推送到内部 Registry。

## 待补充信息
- [ ] WebSocket 服务器默认端口号（代码中可能动态分配或使用固定值，需查 `socket.ts`）
- [ ] 本地 `.env` 备份位置说明（当前未提供，但文档模板提及 `private/env-backup/`，实际不存在）
- [ ] Figma 插件清单中是否包含硬编码的 WebSocket 地址或端口
- [ ] 生产环境中是否存在 MCP 服务器的远程部署模式（如通过 SSE 而非本机进程）
- [ ] lint 配置和测试用例详情（目前 `test` 脚本等同于构建）
- [ ] 更新日志和版本兼容性说明

需要上述信息时，应由熟悉源码的开发者补充，不得编造。

---

*文档由工程知识库维护助手基于项目扫描自动生成，最后更新：基于源码提交 efc2199 (2025-06-08)。*
