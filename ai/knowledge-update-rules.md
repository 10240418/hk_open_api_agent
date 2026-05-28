# Knowledge Update Rules

每次项目新增、部署、迁移或修改配置后，必须更新：

- `inventory/projects.yaml`
- 对应 `projects/*.md`
- 必要时更新 `inventory/domains.yaml`、`inventory/ports.yaml`、`inventory/servers.yaml`
- 新增一条 `deployments/YYYY-MM-DD-project.md`

禁止把 `.env` 的值写入可提交文件。只允许记录变量名、用途和凭据存放位置。
