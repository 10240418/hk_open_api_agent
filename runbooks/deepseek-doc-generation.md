# DeepSeek Project Doc Generation

这个流程用于把 `projects/*.md` 的自动扫描结果交给 DeepSeek v4 pro 增强成更好的中文知识库文档。

## 配置 API Key

在仓库根目录创建 `.env`：

```bash
DEEPSEEK_API_KEY=your_api_key
```

也兼容：

```bash
deepseek_api_key=your_api_key
```

`.env` 已加入 `.gitignore`，不要提交。

## 试运行单个项目

默认不会覆盖原项目文档，而是输出到 `generated/deepseek-project-docs/`：

```bash
python3 scripts/enhance_project_docs_deepseek.py --project hk__good_price_databoard
```

检查生成结果：

```bash
sed -n '1,220p' generated/deepseek-project-docs/hk__good_price_databoard.md
```

## 覆盖写回项目文档

确认质量和安全性后再写回：

```bash
python3 scripts/enhance_project_docs_deepseek.py --project hk__good_price_databoard --write
```

## 批量处理全部项目

先输出到 `generated/` 检查：

```bash
python3 scripts/enhance_project_docs_deepseek.py --all
```

确认后再覆盖：

```bash
python3 scripts/enhance_project_docs_deepseek.py --all --write
```

## 安全规则

1. 脚本只读取 env key 名和源码信号，不应发送真实 `.env` 内容。
2. 脚本会对常见 secret 形态做二次脱敏，但这不是密钥管理替代品。
3. 提交前必须运行：

```bash
find . -path './private' -prune -o -type f \( -name '.env' -o -name '.env.*' -o -name '*.env' \) -print
rg -n "BEGIN (RSA|OPENSSH|PRIVATE) KEY|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9_]{20,}" . --glob '!private/**'
```

4. 如果 DeepSeek 输出了疑似密钥值，删除输出文件，不要提交。
