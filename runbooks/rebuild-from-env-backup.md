# Rebuild From Env Backup

这个流程用于从本地知识库和备份配置复刻一个项目的关键能力，例如邮件发送、支付、数据库连接或设备接入。

## 安全边界

1. `private/env-backup/` 默认不提交 Git。
2. 任何 AI 回复、Markdown 文档、commit message 都不能包含 secret value。
3. 可以记录变量名、用途、凭据来源和验证方式。
4. 如果需要上传到服务器，使用 `scp` 或密码管理器导出，不要把 secret 写入可提交目录。

## 复刻步骤

1. 找到项目文档，例如 `projects/ajoliving_web.md`。
2. 查看 `配置文件和环境变量`，确认需要哪些 key。
3. 在 `private/env-backup/<project>/` 找到原始 `.env` 或样例。
4. 将原始 `.env` 复制到目标项目工作目录，按新域名、端口、数据库和回调地址调整。
5. 对照 `inventory/service-map.md` 的横向能力表检查同类项目。
6. 本地启动并验证关键路径。
7. 部署后写入 `deployments/YYYY-MM-DD-project.md`。

## 邮件发送能力检查

常见变量：

- `MAIL_ENABLED`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `SMTP_HELLO_NAME`
- `SMTP_TO`

验证建议：

1. 先确认端口和 TLS/STARTTLS 要求。
2. 使用项目内测试入口，例如 SVAVO 的 `cmd/mailtest`。
3. 确认发件人、收件人、主题和正文编码。
4. 生产环境只记录测试结果，不记录密码。

## 支付能力检查

常见变量：

- `EASYLINK_ENV`
- `EASYLINK_BASE_URL`
- `EASYLINK_MCH_NO`
- `EASYLINK_*_APP_ID`
- `EASYLINK_*_APP_SECRET`
- `EASYLINK_RETURN_BASE_URL`
- `EASYLINK_NOTIFY_URL`
- `PAYMENTS_MYSQL_DSN`

验证建议：

1. 区分 sandbox 和 production。
2. 回调 URL 必须是公网 HTTPS。
3. 支付订单库要先备份再迁移。
4. 新服务上线前先用小额或沙箱订单验证 query、close、cancel、notify。

## 数据库能力检查

常见变量：

- `DATABASE_URL`
- `DB_DSN`
- `POSTGRES_*`
- `MYSQL_*`
- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

验证建议：

1. 数据库端口默认只绑定 `127.0.0.1`。
2. 先确认迁移是否自动执行。
3. 有生产数据时先备份再部署。
4. 记录备份文件路径和恢复命令。
