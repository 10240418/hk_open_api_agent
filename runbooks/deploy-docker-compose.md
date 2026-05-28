# Docker Compose 部署流程

1. 检查 `docker-compose.yml` 是否设置唯一 `name`。
2. 数据库端口必须优先绑定 `127.0.0.1`。
3. 上传 compose、env 和必要配置。
4. 执行 `docker compose up -d`。
5. 检查 `docker compose ps`、日志、端口和健康接口。
6. 更新知识库部署记录。
