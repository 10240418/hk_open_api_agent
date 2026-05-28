# harmony-cursor-rules

## 项目定位

该项目包含两个主要功能模块：

1. **HarmonyOS 开发规则生成器（根项目）**  
   自动爬取华为官方 HarmonyOS 开发文档，通过 AI 提取最佳实践，生成 Cursor IDE 的 `.cursorrules` 开发规则文件（主要为 ArkTS 规范）。

2. **同人小说创作规则生成器（子项目 `book_rules_ai`）**  
   基于用户提供的网址、文件或文本内容，提取世界观、角色经历、情节等信息，自动生成可用于 Cursor 的同人小说创作提示词规则。

整体上，项目定位为“内容抓取 + AI 分析 + 结构化规则输出”的自动化工具链，适合在本地或容器中运行，产物可直接用于 Cursor 编辑器。


## 技术栈

- 语言：Python 3.11
- 基础镜像：`python:3.11-slim`
- 浏览器自动化：Playwright（Chromium）
- AI 后端：支持 SiliconFlow、Gemini 两家服务商，通过环境变量切换
- 容器化：Docker、Docker Compose
- 配置管理：`.env`、JSON 配置文件（如 `harmony_modules_config.json`）
- 其他依赖：详见项目根目录的 `Requirements.txt`（未在本次扫描中列出具体包名）


## 目录和入口

### 项目根目录（`harmony-cursor-rules/`）

```
.
├── main.py                         # 根项目入口（HarmonyOS 规则生成）
├── Dockerfile                      # 根项目镜像定义
├── docker-compose.yml              # 根项目容器编排
├── Requirements.txt                # Python 依赖清单（待补充）
├── env.example                     # 环境变量模板
├── harmony_modules_config.json     # 爬取模块配置
├── harmony_cursor_rules/           # 输出目录（挂载点）
│   └── final_cursor_rules/        # 最终规则输出
├── book_rules_ai/                  # 子项目目录
│   ├── main.py                     # 子项目入口
│   ├── Dockerfile                  # 子项目专用镜像（构建上下文为父目录）
│   ├── docker-compose.yml          # 子项目容器编排
│   ├── README.md                   # 子项目说明
│   ├── output/                     # 子项目输出挂载目录
│   │   └── fanfiction_rules/      # 生成的小说规则
│   ├── crawler/                    # 内容爬取模块
│   ├── analyzer/                   # 内容分析模块
│   ├── prompt_generator/           # 提示词生成模块
│   ├── templates/                  # 提示词模板
│   └── config.json                 # 子项目配置
└── README.md
```

### 关键入口文件

- **根项目**  
  - 本地启动：`python main.py`  
  - Docker 启动：`docker-compose up --build` 或 `./docker-run.sh`（未在扫描中提供内容，但 README 提及）

- **子项目 `book_rules_ai`**  
  - 本地启动：`cd book_rules_ai && python main.py --url/-file/-text`  
  - Docker 启动：在子项目目录下 `docker-compose up --build` 或使用 `./docker-run.sh`，也可以从父目录通过 `docker-compose -f book_rules_ai/docker-compose.yml ...`

两个模块可在同一宿主机独立运行，共享父目录的 `.env` 配置。


## 运行与构建

### 本地 Python 环境

1. 安装依赖：  
   ```bash
   pip install -r Requirements.txt
   ```
2. 准备配置：  
   ```bash
   cp env.example .env
   # 编辑 .env，填写 AI_PROVIDER 及对应的 API Key
   ```
3. 运行 HarmonyOS 规则生成：  
   ```bash
   python main.py
   ```
4. 运行同人小说规则生成（从 book_rules_ai 目录）：  
   ```bash
   cd book_rules_ai
   python main.py --url "https://example.com/novel"
   ```

### Docker 方式（推荐）

- **根项目**（HarmonyOS 规则）  
  ```bash
  # 在项目根目录执行
  docker-compose up --build
  # 后台运行
  docker-compose up -d
  # 查看日志
  docker-compose logs -f
  # 调试模式（可选）
  docker-compose run --rm harmony-crawler python main.py --debug
  ```

- **子项目**（同人小说规则）  
  ```bash
  # 进入 book_rules_ai 目录
  cd book_rules_ai
  docker-compose up --build
  # 或使用脚本
  ./docker-run.sh --url "https://example.com/novel"
  ```

默认行为：
- 容器启动后执行 Python 主程序，将生成结果写入挂载的宿主机目录。
- 资源限制已在 Compose 文件中设置（CPU 2 核心、内存 4G 上限）。
- 重启策略为 `on-failure`（失败时自动重启，正常退出不重启）。


## 配置和密钥

所有运行时配置通过 `.env` 文件注入。项目提供 `env.example` 作为模板，部署或复刻时需复制并填入真实值。

### 环境变量清单

| 变量名 | 说明 | 备注 |
|--------|------|------|
| `AI_PROVIDER` | AI 服务商选择 | 可选值：`siliconflow`、`gemini` |
| `SILICONFLOW_API_KEY` | SiliconFlow 的 API 密钥 | 当 `AI_PROVIDER=siliconflow` 时必需 |
| `SILICONFLOW_BASE_URL` | SiliconFlow API 基础 URL | 通常为官方地址 |
| `SILICONFLOW_MODEL` | 使用的 SiliconFlow 模型名称 | 例如 `Qwen/Qwen2.5-72B-Instruct` |
| `SILICONFLOW_TEMPERATURE` | 模型生成温度参数 | 控制随机性 |
| （如使用 Gemini） | `GEMINI_API_KEY` 等 | 需参考模板或代码，扫描未列出完整变量，但 README 提及 |

**安全约束**  
- 任何文档、日志、版本控制中**禁止**写入真实 API Key 或密码。  
- 本文档仅保留变量名，实际部署时请从密钥管理系统中获取对应值（SiliconFlow 控制台、Gemini API 页面等）。  
- 子项目 `book_rules_ai` 复用父目录的 `.env`，无需单独配置 AI 凭证。

### 其他配置文件

- `harmony_modules_config.json`：控制爬取的华为文档模块（内容未在本次扫描中提供）。  
- `book_rules_ai/config.json`：子项目的运行参数（如默认模型、输入输出格式等）。


## 外部依赖

1. **华为 HarmonyOS 官方文档网站**  
   爬虫会访问 `developer.huawei.com` 相关页面获取开发规范与最佳实践。需要宿主机/容器具备外网访问能力。

2. **AI API 服务**  
   - SiliconFlow：[https://siliconflow.cn](https://siliconflow.cn)（国内可直接访问）  
   - Google Gemini：需科学上网或代理，API 地址及 Key 从 Google AI Studio 获取。  
   程序通过环境变量切换 Provider，通过对应 SDK 或 HTTP 客户端调用。

3. **Playwright 浏览器**  
   用于动态页面渲染或内容提取，容器内安装 Chromium 及系统依赖（`libgtk-3-0`、`libnss3` 等），Dockerfile 已包含安装步骤。

4. **Python 依赖包**  
   所有 Python 依赖列于根目录 `Requirements.txt`（具体包名和版本未在扫描中提供，有待补充）。推测可能包括：`playwright`、AI SDK（如 `openai` 风格客户端）、HTTP 爬虫库（`requests`、`beautifulsoup4` 等）、配置管理库等。


## 部署线索

- **容器编排**  
  - 根项目 Compose 文件：`docker-compose.yml`，服务名 `harmony-crawler`，镜像名 `harmony-cursor-rules:latest`。  
  - 子项目 Compose 文件：`book_rules_ai/docker-compose.yml`，服务名 `book-rules-generator`，镜像名 `book-rules-ai:latest`。  
  - 子项目构建上下文为父目录（`context: ..`），因此构建命令需在 `book_rules_ai/` 目录下执行，或使用 `-f` 指定文件。

- **挂载卷**  
  - 根项目输出目录：`./harmony_cursor_rules:/app/harmony_cursor_rules`，配置文件：`./harmony_modules_config.json:/app/harmony_modules_config.json:ro`。  
  - 子项目输出目录：`./output:/app/book_rules_ai/output`。

- **网络**  
  两个服务均使用 `network_mode: bridge`，独立运行，不依赖外部预定义网络。

- **健康检查**  
  Dockerfile 中定义了健康检查命令，通过检测 `main.py` 文件是否存在简单判断（生产部署可视需要优化）。

- **资源限制**  
  Compose 文件中设置了 CPU 和内存的上下限，可根据服务器规格调整。

- **日志与调试**  
  未默认挂载日志目录，可按需在 Compose 文件中取消注释 `./logs:/app/logs`。

- **无外部域名或持久端口**  
  该工具为一次性任务型容器，执行完成后退出，不暴露 HTTP 端口，不需要反向代理或 Ingress 配置。


## 复刻检查清单

若需在全新环境中复刻并运行本项目，请按以下步骤操作：

1. **基础环境准备**  
   - 安装 Docker 及 Docker Compose（版本需支持 3.8 语法）。  
   - 或配置 Python 3.11 虚拟环境及 Playwright 浏览器（如选本地运行）。

2. **获取源码**  
   ```bash
   git clone https://github.com/10240418/harmony-cursor-rules.git
   cd harmony-cursor-rules
   ```

3. **配置 AI 凭证**  
   - 复制模板：`cp env.example .env`  
   - 编辑 `.env`，设定 `AI_PROVIDER`（如 `siliconflow`），并填写对应的 `SILICONFLOW_API_KEY`（从 SiliconFlow 控制台获取）或其他关键变量。  
   - 确保 `.env` 已加入 `.gitignore`，避免提交。

4. **（可选）调整模块配置**  
   - 如需修改华为文档爬取范围，编辑 `harmony_modules_config.json`（具体字段待补充）。  
   - 子项目配置在 `book_rules_ai/config.json` 中按需调整。

5. **运行 HarmonyOS 规则生成**  
   ```bash
   docker-compose up --build
   ```
   等待容器执行完成，检查输出目录 `harmony_cursor_rules/final_cursor_rules/`。

6. **运行同人小说规则生成**  
   ```bash
   cd book_rules_ai
   docker-compose up --build
   # 或使用命令行参数：
   docker-compose run --rm book-rules-generator python main.py --url "http://..."
   ```
   生成文件在 `book_rules_ai/output/fanfiction_rules/`。

7. **验证生成结果**  
   - 确认 `.md` 规则文件内容合理。  
   - 将其复制到对应 Cursor 项目的 `.cursorrules` 文件中测试。

8. **清理与停止**  
   ```bash
   docker-compose down   # 在相应目录执行
   ```

9. **（生产部署）持久化与监控**  
   - 如需定时执行，考虑配合 cron 或 CI 工具调用 `docker-compose run --rm ...`。  
   - 若要保存日志，取消 Compose 文件中日志卷的注释，并挂载到固定路径。


## 待补充信息

以下内容在本次项目扫描中未能完全收集，建议在后续维护中补全：

1. **`Requirements.txt` 完整内容**  
   - 扫描未提供 Python 依赖的具体包名和版本，需从源码仓库中提取并同步至本文档，利于环境复现和依赖审计。

2. **`harmony_modules_config.json` 结构**  
   - 该配置文件决定了 HarmonyOS 规则生成器爬取的具体模块。其字段定义、可选范围未在文档中体现，对定制化部署有影响。

3. **`book_rules_ai/config.json` 详细字段**  
   - 默认的输入输出格式、分析器开启关闭、提示词模板选择等细节需要补充。

4. **Gemini 相关环境变量**  
   - 除 `GEMINI_API_KEY` 外，是否需要 `GEMINI_BASE_URL`、`GEMINI_MODEL` 等变量，以及它们的默认值，需从代码逻辑中确认。

5. **代理/网络限制**  
   - 如果运行环境需要通过代理访问华为开发者网站或 AI API，是否有相应的环境变量或代码设置支持（如 `HTTP_PROXY`、`HTTPS_PROXY`）。

6. **错误处理和日志策略**  
   - 当前健康检查较简陋，生产环境中建议定义更可靠的探针。日志级别、输出位置以及失败通知机制（如接入 Webhook）待说明。

7. **持续集成/部署流水线**  
   - 若存在自动化构建、镜像推送、周期性执行等流程，未在本次资料中体现，可补充。

8. **输入输出目录的权限与清理策略**  
   - Docker 挂载目录的宿主机用户权限、输出文件的保留或自动清理策略（如保留最近 N 次生成结果）尚未定义。

9. **性能与并发**  
   - 是否支持多线程爬取或模型调用，资源限制是否需要根据文档数量调整，缺少基准数据。

10. **上游仓库同步策略**  
    - 项目同时关联 `origin` 和 `upstream`，如需从上游 `skindhu/harmony-cursor-rules` 拉取更新并合并，应有操作指引。

补充上述信息后，本知识库文档将足够支撑 Hermes/Codex 自动部署及后续运维工作。
