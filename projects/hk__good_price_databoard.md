# hk__good_price_databoard

## 项目定位
香港超市格价资料库 MVP。后端使用 Go + Postgres 导入消费者委员会每日价格 CSV，解析优惠文案，提供商品搜索、90 日历史趋势、商品详情、邮箱注册/登录、到价提醒与优惠提醒 API。前端使用 React + Vite + Tailwind 展示首页、格价浏览、优惠页、数据说明及商品详情页。

## 技术栈
- **后端**：Go 1.25+（模块路径 `good-price-databoard/backend`），直接依赖 `pgx/v5`、`golang.org/x/crypto`
- **前端**：React 19 + TypeScript + Vite 8，样式使用 Tailwind CSS 3，测试 vitest + jsdom
- **数据库**：PostgreSQL 16（Docker Compose 提供，开发端口 `5433`）
- **运行时/工具链**：Node.js 20+，Docker Desktop，ESLint，Go toolchain

## 目录和入口

```
hk/good_price_databoard/
├── docker-compose.yml          # 仅定义 postgres 服务
├── README.md
├── backend/                    # Go 后端代码
│   ├── go.mod
│   └── ...                     # 入口可通过 go run . 启动
├── frontend/                   # 前端 SPA
│   ├── package.json
│   ├── vite.config.ts
│   └── src/                    # React 入口
├── data/                       # CSV 及历史归档数据（本地开发用）
│   ├── pricewatch_zh-Hant.csv
│   ├── history/                # 历史 CSV/ZIP 归档目录
│   └── history_urls.txt        # 历史归档下载链接列表
└── .deploy/                    # 预置部署资源
    ├── db/pricewatch.dump      # 数据库导出（可能用于初始化）
    ├── frontend-dist/          # 前端构建产物
    └── good_price_backend      # 预编译后端二进制
```

关键入口：
- 后端启动：`backend/` 目录下执行 `go run .`
- 前端开发模式：`frontend/` 目录下 `npm run dev`
- 生产构建：`frontend/` 目录下 `npm run build`，产出默认在 `frontend/dist/`

## 运行与构建

### 数据库
```bash
docker compose up -d postgres
```
PostgreSQL 16 实例监听 `localhost:5433`，默认库名 `pricewatch`，用户 `pricewatch`，密码通过环境变量 `POSTGRES_PASSWORD` 设置（`docker-compose.yml` 中已脱敏，部署时需自行配置安全密码）。

### 后端
```bash
cd backend
go mod download
# 设置环境变量后启动
go run .
```
后端启动时会自动执行以下任务：
- 连接 `DATABASE_URL` 指定的 Postgres
- 若配置了 `PRICEWATCH_ARCHIVE_DIR`，导入目录中文件名含日期的 CSV/ZIP（如 `網上價格一覽通 (繁體中文) - 20260514.zip`）
- 保留最近 `PRICEWATCH_HISTORY_DAYS` 天的价格数据，过期记录自动清理
- 根据 `PRICEWATCH_CSV_URL` 每日定时（`PRICEWATCH_DAILY_IMPORT_HOUR:00`）下载最新繁体中文 CSV 并入库、刷新缓存、评估提醒规则

### 前端
```bash
cd frontend
npm install
# 本地开发（指向独立后端）
VITE_API_BASE=http://localhost:8080 npm run dev
```
开发服务器默认运行在 `http://localhost:5173`。

生产构建：
```bash
cd frontend
npm run build   # 内部执行 tsc -b && vite build
```
构建后静态资源出现在 `frontend/dist/`，可直接复制到 `.deploy/frontend-dist/` 或由 Web 服务器对外服务。**生产前端默认请求同源 `/api/...`**，因此需要将后端放置在同一域名下（反代或后端直接提供静态文件）。

### 验证
后端测试：
```bash
cd backend
go test ./...
```
前端测试与代码质量：
```bash
cd frontend
npm run test
npm run lint
npm run build
```

## 配置和密钥
所有敏感值均通过环境变量注入，不可写入代码仓库。以下为关键变量列表（值均已省略/脱敏，真实部署时应使用安全凭据）：

| 变量名 | 用途 | 备注 |
|--------|------|------|
| `DATABASE_URL` | Postgres 连接串 | 格式 `postgres://pricewatch:<PASSWORD>@host:5433/pricewatch?sslmode=disable` |
| `JWT_SECRET` | 签发/验证 JWT | 必须为随机高强度字符串 |
| `SMTP_PASSWORD` | 邮件发送认证 | 若 `MAIL_ENABLED=false` 可不设 |
| `SMTP_HOST` | SMTP 服务器地址 | 默认 `localhost` |
| `SMTP_PORT` | SMTP 端口 | 默认 `25` |
| `SMTP_USERNAME` | SMTP 用户名 | |
| `SMTP_HELLO_NAME` | SMTP HELO 名称 | |
| `MAIL_ENABLED` | 是否启用邮件发送 | `false` 时不会实际连接 SMTP |
| `PRICEWATCH_CSV` | 本地 CSV 路径（用于初始导入） | 开发时可指向 `../data/pricewatch_zh-Hant.csv` |
| `PRICEWATCH_CSV_URL` | 每日更新的在线 CSV | 默认消费者委员会繁体中文 CSV |
| `PRICEWATCH_ARCHIVE_DIR` | 历史归档本地目录 | 如 `../data/history` |
| `PRICEWATCH_HISTORY_DAYS` | 数据库中保留的历史天数 | 默认 90 |
| `PRICEWATCH_DAILY_IMPORT_HOUR` | 每日定时导入的小时 | 默认 9 |
| `PRICEWATCH_HISTORICAL_ARCHIVE_LIST` | 历史归档下载 URL 列表文件 | 每行一个 DATA.GOV.HK 归档 URL |
| `PRICEWATCH_HISTORICAL_ARCHIVE_URLS` | 历史归档 URL（直接指定） | 用逗号/分号/换行分隔，与上一条二选一 |
| `FRONTEND_BASE_URL` | 前端地址（可能用于邮件链接） | 默认 `http://localhost:5173` |

数据库初始化密码通过 `docker-compose.yml` 的 `POSTGRES_PASSWORD` 设置，启动容器前请替换为强密码。

## 外部依赖
- **PostgreSQL 16**：核心数据存储，可通过 `docker compose up -d postgres` 启动
- **消费者委员会开放数据**：每日更新的价格 CSV
  - 默认 URL：`https://online-price-watch.consumer.org.hk/opw/opendata/pricewatch_zh-Hant.csv`
  - 数据来源：DATA.GOV.HK「Online Price Watch」，更新频率每日
- **DATA.GOV.HK 历史归档**：用于回填历史价格数据，后端会自动筛选繁体中文 CSV，仅处理 `pricewatch_zh-Hant.csv` 或文件名含「網上價格一覽通 (繁體中文)」的 ZIP/CSV
- **SMTP 邮件服务**：可选，用于发送价格提醒、注册确认等邮件；需提供 SMTP 服务器信息

## 部署线索
1. **数据库服务**：`docker compose up -d postgres` 仅启动 PostgreSQL。生产环境需自行托管数据库并确保网络可达。
2. **后端部署**：
   - 编译 Go 二进制（`GOOS=linux GOARCH=amd64 go build -o .deploy/good_price_backend ./backend`）或直接使用预编译版本。
   - 设置所有必需环境变量，启动二进制。
   - 后端应暴露 HTTP 端口（推测默认 `8080`，需在源码确认），并挂载数据卷用于归档 CSV。
3. **前端部署**：
   - 构建静态文件（`npm run build`），产出目录 `frontend/dist/`。
   - 推荐使用 Nginx 提供静态文件并对 `/api/*` 做反向代理到后端，或让后端直接 serve 前端静态资源（需要后端实现）。
   - 确保前端编译时未设置 `VITE_API_BASE`（生产使用同源 API）。
4. **数据初始化**：
   - 准备种子数据：手动下载 `pricewatch_zh-Hant.csv` 放入 `data/`，或设置 `PRICEWATCH_CSV_URL` 让服务自动拉取。
   - 历史数据回填：在 `data/history_urls.txt` 中提供历史归档链接，或将历史 CSV/ZIP 放入 `PRICEWATCH_ARCHIVE_DIR`。
5. **HTTPS & 域名**：无相关信息，生产环境请配置 TLS 终止于反向代理。
6. **进程守护**：建议使用 systemd、supervisor 或容器编排管理后端进程。

## 复刻检查清单
- [ ] 克隆仓库：`git clone https://github.com/The-Healthist/good_price_databoard.git`
- [ ] 进入项目目录，依据 `docker-compose.yml` 启动 postgres，并确保 `POSTGRES_PASSWORD` 已设置为安全值
- [ ] 创建本地 `.env` 文件（或导出环境变量），配置 `DATABASE_URL`、`JWT_SECRET` 及数据源相关变量
- [ ] （可选）准备历史数据：将历史归档 ZIP/CSV 放入 `data/history/` 或填写 `history_urls.txt`
- [ ] 后端依赖下载与测试：`cd backend && go mod download && go test ./...`
- [ ] 启动后端：`go run .` 并观察日志确认数据导入与定时任务正常
- [ ] 前端依赖安装与测试：`cd frontend && npm install && npm run test && npm run lint`
- [ ] 启动前端开发模式验证：`VITE_API_BASE=http://localhost:8080 npm run dev`，打开浏览器测试核心功能
- [ ] 前端生产构建：`npm run build`，将 `dist/` 部署到 Web 服务器，配置 `/api` 反代指向后端
- [ ] 验证邮件功能（若启用）：设置 `MAIL_ENABLED=true` 并完成 SMTP 配置，测试注册/提醒邮件
- [ ] 部署后更新 `inventory/projects.yaml` 与部署记录

## 待补充信息
- 后端 HTTP 服务监听的默认端口（代码中可能默认为 8080，需核实）
- 项目是否使用数据库迁移工具（如 golang-migrate），还是启动时自动建表（后者需要在文档中注明）
- 邮箱服务的具体 SMTP 服务商/中继配置要求（如必要 TLS/STARTTLS）
- 生产环境推荐的 Nginx/Apache 配置示例（尤其是 API 反代规则与静态资源缓存策略）
- JWT Token 的有效期、刷新机制说明
- 后端是否实现了静态文件服务以直接托管前端产出，或者始终依赖外部 Web 服务器
- 监控、日志收集与备份策略（数据库 dump 计划等）
- 多语言/国际化的支持现状（目前仅处理繁体中文 CSV）
- 水平扩展能力与数据一致性保障（如使用单一的定时导入器需避免多实例重复任务）
