# hk_open_api_agent

## 项目定位

hk_open_api_agent 是公司内部“HK Open API Agent”的知识库与部署上下文仓库。它为 Hermes、Codex 等 AI 智能体以及人工运维提供结构化的资产台账、部署运行手册、配置模板和部署记录。仓库本身不承载应用代码，而是集中管理多个 Git 项目的部署知识和运维规则。当前索引包含 37 个 Git 项目的信息。

## 技术栈

- 语言/工具：Python（扫描标识），实际主体为 Markdown 文档和配置模板
- 框架：不适用（非应用服务）
- 运维组件：Docker Compose、Supervisor、nginx

## 目录和入口

```
.
├── README.md
├── inventory/                  # 资产台账 (projects.yaml、service-map.md 等)
├── projects/                   # 每个项目的独立知识库 Markdown
├── runbooks/                   # 部署、验证、回滚流程手册
│   ├── deploy-docker-compose.md
│   ├── deploy-go-supervisor.md
│   └── deploy-static-nginx.md
├── templates/                  # 配置模板
│   ├── nginx-site.conf.tpl
│   └── supervisor.conf.tpl
├── deployments/                # 历次部署记录 (含 .gitkeep)
├── ai/                         # 面向 AI 智能体的执行规则
│   └── deployment-agent-rules.md
└── private/                    # 本地敏感备份，默认不提交
```

推荐阅读入口：
- 人工运维：README 及 `runbooks/` 下的流程手册
- AI 部署：`ai/deployment-agent-rules.md`，结合 `inventory/` 和 `projects/` 生成部署计划

## 运行与构建

本仓库为知识库，无传统构建、编译或服务启动过程。不存在 package.json、Makefile 等构建配置，也未发现自动化运行脚本。

日常使用方式：
- 人工参照 `runbooks/` 中的手册执行服务部署、回滚和维护
- AI 根据 `ai/` 中的规则读取台账和项目文档，生成计划并实施部署

## 配置和密钥

- 仓库内未检出任何 `.env` 或 `.env.*` 文件，符合安全策略
- 真实密钥、Token、API Key、数据库密码等敏感内容只允许存放在 `private/` 目录或外部密码管理器中，且已通过 `.gitignore` 排除 Git 提交
- 配置模板（如 `templates/nginx-site.conf.tpl`、`templates/supervisor.conf.tpl`）使用变量占位，部署时从环境变量或外部备份注入实际值，变量名称由各项目的文档定义，此处不具名
- 环境变量恢复可参考 README 中提到的 `runbooks/rebuild-from-env-backup.md`（若文件存在）及 `private/env-backup/` 本地备份

## 外部依赖

本知识库自身无运行时外部依赖。其所管理的各项目实际部署时依赖 Docker、Docker Compose、Supervisor、nginx 等基础组件，以及各项目专有的数据库、支付网关、邮件服务等。具体依赖关系记录在对应的 `projects/<slug>.md` 中，不在本文档重复。

## 部署线索

本仓库不直接部署，而是部署动作的指挥中枢。完整流程线索如下：

1. 读取 `inventory/service-map.md` 和 `inventory/projects.yaml` 了解整体拓扑及目标项目信息
2. 查看 `projects/<slug>.md` 获取该项目具体的部署方式与依赖
3. 选用对应 runbook：如 `runbooks/deploy-docker-compose.md`、`deploy-go-supervisor.md`、`deploy-static-nginx.md`
4. 根据 `templates/` 中的模板生成配置文件，并结合来自 `private/` 或密码管理器的敏感变量完成渲染
5. 执行部署，完成后在 `deployments/` 下创建 `YYYY-MM-DD-project.md`，并更新 `inventory/projects.yaml` 的项目状态

扫描结果中的部署线索 `Docker Compose, Supervisor, nginx` 与此流程一致。

## 复刻检查清单

在新的运维环境基于本仓库重建部署能力，请按以下清单操作：

- [ ] 克隆仓库 `git clone https://github.com/10240418/hk_open_api_agent.git`（注意当前 main 分支存在未提交改动，建议先确认或切换至稳定标签）
- [ ] 从安全备份源（如 `private/env-backup/` 或密码管理器）恢复所需的环境变量文件，确保模板渲染可读取所有必要值
- [ ] 确认基础运维工具已安装：Docker、Docker Compose、Supervisor、nginx
- [ ] 核对 `inventory/projects.yaml` 和 `inventory/service-map.md` 中的服务器 IP、域名、端口等信息，确保与目标环境一致（本文档不含具体数值，需运维自行提供）
- [ ] 若使用 AI 智能体执行部署，阅读 `ai/deployment-agent-rules.md`，并授予其读取仓库、写入 `deployments/` 的权限
- [ ] 任何部署操作前，先行生成计划并列出所有将变更的服务器文件，等待确认
- [ ] 部署完成后，在 `deployments/` 下新增记录，并更新台账

## 待补充信息

- 未发现具体的环境变量键名清单，各项目所需变量（如数据库地址、第三方 API Key 等）应补充至对应的 `projects/*.md`
- `private/env-backup/` 的实际组织结构和版本未记录，需本地确认
- `runbooks/rebuild-from-env-backup.md` 是否已存在及内容待核实
- Git 提交记录显示“最近提交: none”，仓库可能处于初始阶段或存在未提交内容，建议在复刻前打上稳定标签
- 索引的 37 个项目具体清单需读取 `inventory/projects.yaml`，本文档未列出
- 扫描判定语言为 Python，但仓库中未见可执行的 Python 源代码，请确认是否有辅助脚本被遗漏或该标识为误报
