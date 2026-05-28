# python_translate_tool

## 项目定位
这是一个面向游戏本地化的批量文本翻译工具，主要处理 **Lua 格式**的游戏数据文件。  
通过 CLI 命令行或 GUI 界面，将源语言（通常是中文）文本翻译为多个目标语言（英文、泰文、日文等）。  
翻译引擎支持：
- 云端 API（OpenAI、SiliconFlow）
- 本地模型（Ollama 或任意兼容 OpenAI 接口的本地服务）

工具本身定位为**开发辅助工具**，运行在开发者本机，不涉及服务端部署。

## 技术栈
- 语言：Python 3
- 主要标准库：`tkinter`（GUI）、`argparse`（CLI）、`json`、`csv`、`concurrent.futures`
- 第三方依赖（通过 `requirements.txt` 管理）：
  - `openai`（OpenAI 及兼容 API 调用）
  - `ollama`（Ollama 本地模型调用）
  - `pandas`（处理 CSV/Excel 翻译表格）
  - 其他可能依赖：`requests`、`PyYAML` 等（以 `requirements.txt` 为准）
- 无 Web 框架，不依赖数据库或消息队列。

## 目录和入口

项目根目录关键文件与入口脚本：

| 文件 | 用途 |
|------|------|
| `main.py` | GUI 主程序入口（`python main.py --optimized` 启动 GUI） |
| `translate_quest_optimized.py` | 一体化命令行翻译工具，可直接输入文件 -> 输出翻译后文件 |
| `extract_unique_texts.py` | 分步流程第一步：提取唯一文本生成 CSV/表格 |
| `ai_translate_texts.py` | 分步流程第二步：调用 AI 翻译表格数据 |
| `apply_translations.py` | 分步流程第三步：将翻译结果应用回原始文件 |
| `config.json` | 翻译服务配置（API key、模型等），**需用户自建，不可提交至仓库** |
| `requirements.txt` | Python 依赖声明 |
| `README.md` | 使用说明 |

无其他复杂的目录结构；推测存在 `gui/` 或类似模块化目录，但扫描仅提取到以上文件，如需复刻应先阅读 `README.md` 了解完整文件列表。

## 运行与构建

### 环境准备
```bash
pip install -r requirements.txt
```
确保 Python 版本 >= 3.7（推荐 3.9+）。

### 运行方式
1. **GUI 界面**
   ```bash
   python main.py --optimized
   ```

2. **命令行分步流水线（推荐大文件）**
   ```bash
   # 第一步：提取唯一文本
   python extract_unique_texts.py input_file.txt -o extracted_texts -c 1000

   # 第二步：AI 翻译（示例使用 OpenAI）
   python ai_translate_texts.py extracted_texts/input_file.txt_texts.csv \
       -o translated_texts.csv -t en,th,ja -a openai -k <YOUR_API_KEY>

   # 第三步：应用翻译
   python apply_translations.py input_file.txt translated_texts.csv \
       -o translated_input_file.txt -c 1000
   ```

3. **一体化命令（中小文件）**
   ```bash
   python translate_quest_optimized.py input_file.txt \
       -o translated_file.txt -l en th ja
   ```

各脚本均支持 `-h` 查看详细参数。

## 配置和密钥

项目通过 **`config.json`** 文件管理所有 API 密钥和模型参数，该文件不随仓库分发。  
结构示例（敏感值已隐藏）：

```json
{
  "translation_service": "openai",
  "openai": {
    "api_key": "<YOUR_OPENAI_API_KEY>",
    "model": "gpt-3.5-turbo"
  },
  "siliconflow": {
    "api_key": "<YOUR_SILICONFLOW_API_KEY>",
    "model": "Qwen/QwQ-32B"
  },
  "ollama": {
    "api_url": "http://localhost:11434/api/generate",
    "model_name": "llama3:8b"
  },
  "local_model": {
    "api_url": "http://localhost:8000/v1/chat/completions",
    "model_name": "llama3"
  }
}
```

**密钥策略：**
- **所有密钥均在 `config.json` 中明文存放**，未使用环境变量或密钥管理器。
- 该文件必须加入 `.gitignore`，任何情况下不得提交到版本库。
- 分发或备份时，使用 `.gitignore` 保护，或手动将 `config.json` 存放于 `private/env-backup/` 等本地私密路径。
- 如需在 CI 或团队环境中共享，建议改用环境变量注入（如 `OPENAI_API_KEY`），但当前项目未实现该能力，需自行改造。

## 外部依赖

- **翻译 API 服务**（按需启用一种或多种）：
  - **OpenAI**：需有效 API key，网络能访问 `api.openai.com`。
  - **SiliconFlow**：需注册并获取 key，网络能访问其端点（国内友好）。
  - **本地 Ollama**：需提前在**本机**启动 Ollama 服务并拉取模型（如 `llama3:8b`），默认端口 `11434`，无需外网。
  - **通用本地 API**：可指向任何兼容 OpenAI Chat Completions 接口的服务（如 vLLM、LocalAI），需提供 URL 和模型名。

- **网络要求**：使用云端翻译时需要外网连接；纯本地模型可离线运行。
- **无数据库、无缓存服务依赖**。

## 部署线索

本项目为**单机命令行工具 / 桌面 GUI 工具**，不存在传统“服务端部署”。  
“部署”即在工作站上完成以下动作：
1. 按运行章节安装依赖。
2. 手动创建 `config.json` 并填入至少一种翻译服务的有效凭据。
3. 如需使用 Ollama，确保本地 Ollama 已启动。

- **无需分配域名、固定端口、服务发现**。
- **无需反向代理、负载均衡**。
- GUI 仅绑定本地回环（`tkinter` 默认行为），不存在远程暴露风险。
- 若有批量处理的服务器需求，可直接在服务器上安装相同 Python 环境，通过 SSH 执行命令行模式，**不要暴露 `config.json` 到公网**。

## 复刻检查清单

在任意新环境下复现项目功能时，按以下步骤检查：

- [ ] 克隆仓库：`git clone https://github.com/10240418/python_translate_tool.git`
- [ ] 检查 `requirements.txt` 是否完整，安装依赖：`pip install -r requirements.txt`
- [ ] 确认 Python 版本 ≥ 3.7。
- [ ] 创建 `config.json`，填写至少一种翻译服务的 key 或本地模型地址。
- [ ] （若使用 Ollama）启动本地 Ollama 服务并确保模型已拉取。
- [ ] 运行基础测试：
  - `python translate_quest_optimized.py -h` 显示帮助。
  - 准备一个简单 Lua 测试文件，执行翻译并检查输出。
- [ ] 确认 `config.json` 已被 `.gitignore` 忽略（避免意外提交）。
- [ ] 若需要 GUI，检查 Tkinter 库是否可用（多数 Python 发行版自带，若缺失需安装 `python3-tk`）。
- [ ] 如有性能需求，根据文件大小调整 `--chunk-size` 和 `--workers`。

## 待补充信息

以下内容在当前扫描/文档中缺失，复刻或维护时需要人工补充：

1. **`requirements.txt` 具体依赖清单**：必须从仓库获取实际文件，以锁定版本。
2. **GUI 实现细节**：`main.py` 中引用的具体模块文件（如 `gui.py`）未被扫描列出，需检查仓库完整结构。
3. **输入文件格式规范**：README 提到 Lua 格式，但未给出明确语法示例和需要提取的字段规则（如 `'中文|FT:繁体|EN:英文|TH:泰文'` 的解析细节是否硬编码？）。
4. **错误处理与日志**：命令行输出是否足够？是否有日志文件？如何处理 API 调用失败重试？
5. **离线/本地模型质量调优**：README 提及“优化版翻译器”和本地模型短翻译问题，但具体解决方案（提示词调整）未文档化，需查阅源码或询问作者。
6. **配置模板分发**：建议在仓库中提供 `config.example.json`（不含真实密钥），降低复刻门槛。
7. **单元测试 / 集成测试**：未发现任何测试文件，质量依赖人工验证。
