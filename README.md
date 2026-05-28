# HK Open API Agent Knowledge Base

这是公司内部项目知识库和部署智能体上下文仓库。它面向 Hermes、Codex 和人工运维共同使用。

## 目录

- `inventory/`：结构化资产台账，包括项目、服务器、域名和端口。
- `projects/`：每个 Git 项目的知识库 Markdown。
- `runbooks/`：部署、验证、回滚和知识更新流程。
- `templates/`：nginx、Supervisor、frp、Docker 等配置模板。
- `deployments/`：每次部署后的记录。
- `ai/`：Hermes/Codex 使用规则。
- `private/`：本地敏感备份，默认不提交。

## 当前索引

- 生成时间：`2026-05-28T19:46:00+08:00`
- Git 项目数量：`37`

## 推荐阅读入口

1. `inventory/service-map.md`：业务系统和横向能力总览。
2. `inventory/projects.yaml`：全部 Git 项目结构化台账。
3. `projects/*.md`：每个项目的独立知识库文件。
4. `runbooks/rebuild-from-env-backup.md`：从本地 env 备份复刻邮件、支付、数据库等能力。
5. `ai/deployment-agent-rules.md`：Hermes/Codex 部署执行规则。

## 使用规则

1. `inventory/*.yaml` 是事实来源，Markdown 是给人和 AI 阅读的说明。
2. 真实密钥和 `.env` 内容只允许存在于 `private/` 或密码管理器，不允许提交到 Git。
3. 每次部署成功后必须新增 `deployments/YYYY-MM-DD-project.md`，并更新项目台账。
4. AI 执行部署前必须先生成计划、列出将修改的服务器文件、等待确认。
