# hk-dashboard 工程文档

## 项目定位
香港城市仪表板（HK City Dashboard）是一个纯前端 PWA（Progressive Web App），通过聚合香港政府开放数据 API，提供天气、交通、巴士到站、潮汐、停车、环境、医疗等 15 类实时城市信息。无需后端服务，所有数据直接从前端调用公开 API 获取，部分 API 经由本地 Python 开发代理解决 CORS 问题，适合作为香港生活信息一站式入口。

## 技术栈
- **前端**：纯静态 HTML/CSS/JavaScript（推测原生实现，未发现前端框架）
- **PWA**：`manifest.json`、`service-worker.js`（支持离线缓存与主屏幕安装）
- **本地开发服务器**：Python（`dev_server.py`，提供静态文件服务及 API 代理）
- **运行时**：浏览器环境（生产） + Python 解释器（开发）
- **测试/构建工具**：未自动化，无 `package.json`

## 目录和入口
（完整目录树待补充，以下为已知文件/目录）

- `README.md` — 项目说明与快速开始
- `doc/deployment.md` — 部署文档
- `dev_server.py` — 本地开发代理服务器入口
- `index.html`（预期）— 主页面入口
- 可能包含 `manifest.json`、`service-worker.js` 及各类视图/组件目录
- 无 `node_modules`、`package.json`、`requirements.txt`（开发服务器可能使用标准库）

**当前分支**：`master`  
**最近提交**：`67c70b7` feat: Enhance transport page with new features and APIs (2026-05-15)  
**工作区状态**：干净

## 运行与构建

### 本地开发
```bash
git clone https://github.com/10240418/hk-dashboard.git
cd hk-dashboard
python3 dev_server.py 8080
```
开发服务器在 `localhost:8080` 提供静态文件并代理部分可能被浏览器限制的 API 请求（如 Stooq 恒生指数数据）。无需额外安装依赖（Python 标准库即可运行）。

### 构建部署
项目为纯前端静态资源，无需构建。生产环境直接将所有文件部署到任意静态文件托管服务即可，但需处理以下问题：
- **CORS 代理**：部分 API（如 Stooq）可能不返回 CORS 头，生产环境需由反向代理（如 Nginx）或 Serverless 函数实现相同的代理功能，具体配置见 `doc/deployment.md`。
- **PWA 离线**：确保 `service-worker.js` 正确定义缓存策略，Service Worker 作用域需涵盖所有页面。

## 配置和密钥
- 未发现 `.env`、`.env.*` 文件，未检测到显式的环境变量配置。
- 项目所依赖的外部 API 均为香港政府公开数据，无需注册 API key。
- 可能存在的隐式配置：
  - 恒生指数数据经 Stooq 代理，代理目标地址可能硬编码在 `dev_server.py` 中。
  - 若无特殊配置，可直接使用现有公开接口，无需额外凭据。
- 若后续引入需要认证的 API，应在 `doc/deployment.md` 中记录环境变量名称（如 `HK_WEATHER_API_KEY` 等），但**不得**在此文档中写入任何 token/password 的值。

## 外部依赖
所有数据源均为外部 HTTP API，均在前端直接调用或通过开发代理中转：

| 数据类别 | 来源 | API 域名 |
|---------|------|----------|
| 天气/潮汐/地震/九天预报/各區气温降雨 | 香港天文台 | `data.weather.gov.hk` |
| 空气质素 AQHI | 环保署 | `datagovhk.blob.core.windows.net` |
| 急症室等候 | 医院管理局 | `ha.org.hk` |
| MTR/轻铁班次、城巴ETA、屿巴路线、停车場空位 | data.gov.hk (统一平台) | `rt.data.gov.hk`、`api.data.gov.hk` |
| 九巴 ETA | 九巴公开数据 | `data.etabus.gov.hk` |
| 小巴 ETA | 运输署 | `data.etagmb.gov.hk` |
| 公众假期 | 1823 | `1823.gov.hk` |
| 恒生指数 | Stooq (经本地代理) | `stooq.com` (可能通过开发服务器代理) |
| 汇率 | Frankfurter | `api.frankfurter.dev` |
| 道路 CCTV | 运输署 | `tdcctv.data.one.gov.hk` |
| 泳灘水質 | 环保署 (静态) | 无实时 API，可能内嵌静态 JSON |

> 以上接口无需鉴权，服务稳定性依赖于各政府部门 API 可用性。

## 部署线索
- **上游仓库**：`origin` 指向 `https://github.com/10240418/hk-dashboard.git`，`upstream` 指向 `https://github.com/Jermen592/hk-dashboard.git`
- README 中提供的 Live Demo 链接为 GitHub 仓库页面（非站点），实际生产部署域名**未知**。
- 推测可部署于 GitHub Pages、Netlify、Vercel 等静态托管，但需解决 CORS 代理（例如通过 Serverless Functions 重现场 `dev_server.py` 的代理逻辑）。
- `doc/deployment.md` 应记录具体部署方式、反向代理配置、自定义域名等信息（待提取）。
- 生产环境 HTTPS 必须启用，以支持 PWA Service Worker 注册及安全策略。

## 复刻检查清单
1. **克隆仓库**  
   `git clone https://github.com/10240418/hk-dashboard.git`
2. **确认 Python 环境**  
   需要 Python 3.x，无额外包依赖。
3. **启动开发服务器**  
   `python3 dev_server.py 8080`，验证浏览器能访问首页并正常加载数据。
4. **检查外部 API 连通性**  
   逐一访问依赖的政府 API 域名，确保网络可达（注意某些政府 API 可能要求香港 IP）。
5. **审查代理逻辑**  
   查看 `dev_server.py` 了解代理的路由规则，准备生产环境代理方案。
6. **部署到静态平台**  
   将除 `.git` 外的所有文件上传至目标静态服务；配置反向代理或 Edge Function 以转发特定路径到第三方 API。
7. **验证 PWA 功能**  
   使用 Lighthouse 检查 PWA 得分，手动测试安装与离线缓存。
8. **更新项目清单**  
   部署成功后，更新仓库根目录下的部署记录文件（如 `inventory/projects.yaml` 和 `deployments/` 目录），记录生产 URL、代理配置及维护说明。

## 待补充信息
- 完整的项目目录树（特别是前端页面、JS 模块、PWA 资源的结构）。
- 前端是否使用任何 JavaScript 框架或构建工具（如 Vite/Webpack），目前仅推测为原生实现。
- `dev_server.py` 的代理范围与具体转发规则（是否包含多条 API 代理、是否有缓存逻辑等）。
- `doc/deployment.md` 的详细内容（应包含生产环境推荐配置、HTTPS 证书、自定义域名、CORS 代理方案）。
- 真实生产访问域名（README 中的 Live Demo 链接为占位/异常，需修正）。
- 是否需要针对某些 API 设置 API key（例如未来若 data.gov.hk 要求注册，应在此补充环境变量名称）。
- 移动端适配与测试结果，是否有 iOS PWA 全屏状态栏颜色、启动图等定制化配置。
