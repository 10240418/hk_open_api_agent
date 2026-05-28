# Go + Supervisor 部署流程

1. 本地交叉编译：`GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o service`。
2. 上传二进制和配置文件到 `/home/admin/<project>/`。
3. 创建 `run.sh`，由 Supervisor 直接管理进程。
4. 创建 `/etc/supervisor/conf.d/<project>.conf`。
5. 执行 `supervisorctl reread && supervisorctl update`。
6. 检查进程、日志、端口和健康接口。
7. 更新知识库部署记录。
