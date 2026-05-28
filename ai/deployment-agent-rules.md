# Deployment Agent Rules

## 核心原则

1. 先读后改：修改服务器配置前必须先读取原文件。
2. 先计划后执行：部署前必须输出部署计划、端口、域名、回滚方案。
3. 敏感信息不外泄：不在 Markdown、聊天消息、Git commit 中输出 secret value。
4. 数据库端口默认只绑定 `127.0.0.1`。
5. 修改 nginx、Supervisor、Docker、frp 后必须执行对应验证命令。
6. 部署完成后必须更新 `inventory/` 和 `deployments/`。
