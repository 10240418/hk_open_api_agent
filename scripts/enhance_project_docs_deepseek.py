#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


KB_ROOT = Path(__file__).resolve().parents[1]
CODE_ROOT = Path("/Users/yangliu/Documents/Code")
PROJECTS_DIR = KB_ROOT / "projects"
OUTPUT_DIR = KB_ROOT / "generated" / "deepseek-project-docs"
ENV_PATH = KB_ROOT / ".env"

BASE_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-v4-pro"

SECRET_VALUE_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|passwd|pwd|access[_-]?key|private[_-]?key)\s*[:=]\s*['\"]?[^'\"\s`]+"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
]


def load_env_file(path):
    if not path.exists():
        return {}
    values = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip().replace("export ", "")
        value = value.strip().strip("'\"")
        values[key] = value
    return values


def get_api_key():
    env_values = load_env_file(ENV_PATH)
    for key in ("DEEPSEEK_API_KEY", "deepseek_api_key", "DEEPSEEK_KEY"):
        if os.environ.get(key):
            return os.environ[key]
        if env_values.get(key):
            return env_values[key]
    return ""


def read_text(path, limit=12000):
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text[:limit]


def project_source_path(slug):
    projects_yaml = read_text(KB_ROOT / "inventory" / "projects.yaml", limit=200000)
    pattern = re.compile(
        rf"- name: .+?\n\s+slug: {re.escape(slug)}\n\s+path: ([^\n]+)",
        re.MULTILINE,
    )
    match = pattern.search(projects_yaml)
    if not match:
        return None
    return Path(match.group(1).strip().strip('"'))


def collect_source_signals(source_root):
    if not source_root or not source_root.exists():
        return ""
    wanted = [
        "README.md",
        "package.json",
        "go.mod",
        "docker-compose.yml",
        "docker-compose.yaml",
        "Dockerfile",
        "vite.config.ts",
        "vite.config.js",
        "config.example.yaml",
        "deploy-ajoliving.sh",
    ]
    chunks = []
    for name in wanted:
        for path in source_root.rglob(name):
            if any(part in {".git", "node_modules", "dist", "build", "private"} for part in path.parts):
                continue
            try:
                rel = path.relative_to(source_root)
            except ValueError:
                rel = path
            content = read_text(path, limit=5000)
            if content:
                chunks.append(f"### {rel}\n\n```text\n{content}\n```")
            if len(chunks) >= 8:
                break
        if len(chunks) >= 8:
            break
    return "\n\n".join(chunks)[:30000]


def redact_suspicious_values(text):
    redacted = text
    for pattern in SECRET_VALUE_PATTERNS:
        redacted = pattern.sub(lambda m: m.group(0).split("=", 1)[0] + "=<redacted>" if "=" in m.group(0) else "<redacted-secret>", redacted)
    return redacted


def build_prompt(slug, current_doc, source_signals):
    return f"""
你是公司内部工程知识库文档维护助手。请把下面的项目扫描结果改写成高质量中文 Markdown。

要求：
1. 不要输出任何 secret value、密码、token、API key 的值。
2. 可以保留环境变量 key 名称。
3. 不要编造不存在的部署域名、端口或凭据。
4. 结构要利于 Hermes/Codex 后续自动部署和复刻能力。
5. 语气直接、工程化，中文为主，必要的技术名词保留英文。
6. 输出必须是完整 Markdown 文档，不要包裹在代码块中。
7. 必须包含这些章节：项目定位、技术栈、目录和入口、运行与构建、配置和密钥、外部依赖、部署线索、复刻检查清单、待补充信息。

项目 slug：{slug}

当前自动生成文档：

{current_doc}

补充源码信号：

{source_signals}
""".strip()


def call_deepseek(api_key, prompt, model, timeout):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是严谨的中文工程知识库文档维护助手。"},
            {"role": "user", "content": prompt},
        ],
        "thinking": {"type": "enabled"},
        "reasoning_effort": "high",
        "stream": False,
    }
    req = Request(
        BASE_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"DeepSeek HTTP {exc.code}: {detail[:1000]}") from exc
    except URLError as exc:
        raise RuntimeError(f"DeepSeek request failed: {exc}") from exc

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected DeepSeek response: {json.dumps(data, ensure_ascii=False)[:1000]}") from exc


def target_docs(args):
    if args.all:
        return sorted(PROJECTS_DIR.glob("*.md"))
    docs = []
    for project in args.project:
        name = project[:-3] if project.endswith(".md") else project
        path = PROJECTS_DIR / f"{name}.md"
        if not path.exists():
            raise SystemExit(f"Project doc not found: {path}")
        docs.append(path)
    return docs


def main():
    parser = argparse.ArgumentParser(description="Enhance project docs with DeepSeek.")
    parser.add_argument("--project", action="append", default=[], help="Project slug, e.g. hk__good_price_databoard")
    parser.add_argument("--all", action="store_true", help="Enhance all project docs")
    parser.add_argument("--write", action="store_true", help="Overwrite projects/*.md. Without this, write to generated/")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    if not args.all and not args.project:
        raise SystemExit("Pass --project <slug> or --all")

    api_key = get_api_key()
    if not api_key:
        raise SystemExit("Missing DEEPSEEK_API_KEY or deepseek_api_key in .env/environment")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    docs = target_docs(args)

    for doc_path in docs:
        slug = doc_path.stem
        current_doc = read_text(doc_path, limit=30000)
        source_root = project_source_path(slug)
        source_signals = collect_source_signals(source_root)
        prompt = build_prompt(
            slug,
            redact_suspicious_values(current_doc),
            redact_suspicious_values(source_signals),
        )
        enhanced = call_deepseek(api_key, prompt, args.model, args.timeout)
        enhanced = redact_suspicious_values(enhanced).strip() + "\n"

        out_path = doc_path if args.write else OUTPUT_DIR / doc_path.name
        out_path.write_text(enhanced, encoding="utf-8")
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
