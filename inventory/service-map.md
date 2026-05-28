# Service Map

本文件是给 Hermes 和 Codex 的高层入口。需要具体配置时，再进入 `projects/*.md` 查看项目级知识库。

## 核心业务系统

| 系统 | 项目文档 | 类型 | 关键外部依赖 | 部署线索 |
| --- | --- | --- | --- | --- |
| AJO Living | `projects/ajoliving_web.md` | Go 后端 + Vue 前端 | PostgreSQL、Aliyun OSS、SMTP、POS/iSmart、EasyLink | `deploy-ajoliving.sh`、后端服务、前端静态 |
| Good Price Databoard | `projects/hk__good_price_databoard.md` | Go 后端 + React 前端 | PostgreSQL、Consumer Council pricewatch、SMTP | Postgres compose、同源 `/api` 反代 |
| SVAVO Smart Databoard | `projects/svavo_smart_databoard.md` | Go 后端 + React 前端 | PostgreSQL、SVAVO IoT API、SMTP | Docker、nginx、Supervisor、hybrid deploy |
| POS Web | `projects/pos__pos_web.md` | Vue 前端 | POS relay、EasyLink 支付服务 | 静态前端，dev proxy 到 `/api` 和 `/api/payments` |
| POS Payment Service | `projects/pos__pos_web_payment_http_service.md` | Go 支付后端 | MySQL、EasyLink/Gnete、POS business API | Go + Supervisor，默认 `127.0.0.1:20034` |
| iSmart POS Relay | `projects/pos__ismart_pos_relay.md` | Go relay | AWS API Gateway POS API | Docker 或 Go binary |
| iBoard Service | `projects/iboard_http_service.md` | Go API | MySQL、Redis、SMTP、OSS、iSmart sync | Docker Compose，端口 `10031` |
| iBoard Web Admin | `projects/ilock__iboard_web_admin.md` | Vue 前端 | iBoard API | Docker + nginx，生产路径 `/admin/` |
| iCCTV Service | `projects/icctv-http-service.md` | Go API | MySQL/SQLite、OrangePi auth、NVR/RTSP | Docker Compose，端口 `32001` |
| iCCTV Web Admin | `projects/icctv_web_admin.md` | Vue 前端 | iCCTV API | Docker + nginx，`/api` 反代 `32001` |
| iCCTV OrangePi Auth | `projects/icctv_orangepi_auth_service.md` | Python FastAPI edge service | MediaMTX、FRP、Docker socket、RTSP/NVR | OrangePi/Linux ARM Docker Compose |
| Intercom API | `projects/intercom__iNtercom_http_service.md` | Go API | MySQL、Redis、MQTT、Tencent RTC、FRP | Docker，健康检查 `/api/ping` |
| Intercom Web Admin | `projects/intercom__iNtercom_web_admin.md` | Vue 前端 | Intercom API | Vercel rewrite 或静态前端反代 |
| iLock Service | `projects/ilock__ilock_http_service.md` | Go API | MySQL、Redis、EMQX/MQTT、InfluxDB | binary 同目录需要 `config.yaml` |
| HK Dashboard | `projects/hk-dashboard.md` | 静态 PWA | HKO、EPD、HA、MTR、KMB、TD、Stooq 等公开 API | 纯静态部署 |
| YLS Databoard | `projects/yls_databoard.md` | Node 静态/API 代理 | `code.ylsagi.com`、Bearer token | Node 进程，默认 `127.0.0.1:3000` |

## 横向能力

| 能力 | 涉及项目 | 复刻时必须检查 |
| --- | --- | --- |
| 邮件发送 | AJO Living、Good Price、SVAVO、iBoard | `MAIL_ENABLED`、`SMTP_HOST`、`SMTP_PORT`、`SMTP_USERNAME`、`SMTP_PASSWORD`、`SMTP_FROM`、收件人配置 |
| 支付 | POS Payment Service、AJO Living | EasyLink/Gnete app id/secret、merchant number、return/notify URL、支付方式映射 |
| 对象存储 | AJO Living、iBoard | OSS bucket、endpoint、region、access key、media base URL、CORS/callback |
| 数据库 | 多数 Go 后端 | PostgreSQL/MySQL DSN、迁移策略、端口绑定、备份和恢复脚本 |
| 设备和 IoT | SVAVO、iCCTV、iLock、Intercom | 设备号、MQTT topic、FRP 映射、公网端口、NVR/RTSP 源 |
| FRP 内网穿透 | Intercom、iCCTV OrangePi、frp_local_public_service | `frpc.toml`、`frps.toml`、公网端口、Host 路由 |

## 使用建议

1. 新部署任务先读本文件，再读对应 `projects/*.md`。
2. 需要密钥时只查看 `private/env-backup/` 或密码管理器，不要让 AI 在回复中输出 secret value。
3. 需要复刻某能力时，优先按横向能力表找同类项目，例如邮件发送系统可参考 AJO Living、Good Price、SVAVO、iBoard。
4. 部署完成后更新 `inventory/projects.yaml`、项目文档和 `deployments/` 记录。
