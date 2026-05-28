#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


CODE_ROOT = Path("/Users/yangliu/Documents/Code")
KB_ROOT = Path("/Users/yangliu/Documents/Code/hk/hk_open_api_agent")
GENERATED_AT = datetime.now().astimezone().isoformat(timespec="seconds")

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "coverage",
    ".dart_tool",
    "Pods",
    ".gradle",
    "DerivedData",
    "private",
}

SECRET_HINTS = (
    "KEY",
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "PASS",
    "PWD",
    "PRIVATE",
    "ACCESS",
    "AUTH",
    "DSN",
    "URL",
)


def run(cmd, cwd=None):
    try:
        return subprocess.check_output(
            cmd,
            cwd=cwd,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return ""


def rel(path):
    return os.path.relpath(path, CODE_ROOT)


def slugify(value):
    value = str(value).replace(str(CODE_ROOT), "").strip("/")
    value = value.replace("/", "__")
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", value)
    return value.strip("-") or "root"


def find_git_projects():
    projects = []
    for git_dir in CODE_ROOT.rglob(".git"):
        if not git_dir.is_dir():
            continue
        project_root = git_dir.parent
        if any(part in IGNORED_DIRS for part in project_root.relative_to(CODE_ROOT).parts):
            continue
        projects.append(project_root)
    return sorted(set(projects), key=lambda p: str(p).lower())


def iter_files(root, max_depth=4):
    root = Path(root)
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        depth = len(current_path.relative_to(root).parts)
        if depth > max_depth:
            dirs[:] = []
            continue
        for name in files:
            yield current_path / name


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def extract_env_keys(path):
    keys = []
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key = stripped.split("=", 1)[0].strip().replace("export ", "")
            if re.match(r"^[A-Za-z_][A-Za-z0-9_\\.\\-]*$", key):
                keys.append(key)
    except Exception:
        pass
    return sorted(set(keys))


def classify_project(root):
    files = {str(p.relative_to(root)): p for p in iter_files(root, max_depth=4)}
    languages = []
    frameworks = []
    runtime = []
    deploy = []

    package_paths = [p for name, p in files.items() if name.endswith("package.json")]
    go_mods = [p for name, p in files.items() if name.endswith("go.mod")]
    pubspecs = [p for name, p in files.items() if name.endswith("pubspec.yaml")]

    if go_mods:
        languages.append("Go")
        runtime.append("go")
    if package_paths:
        languages.extend(["JavaScript/TypeScript"])
        runtime.append("node")
    if pubspecs:
        languages.append("Dart")
        frameworks.append("Flutter")
    if any(name.endswith((".py", "requirements.txt", "pyproject.toml")) for name in files):
        languages.append("Python")
        runtime.append("python")
    if any(name.endswith("Dockerfile") for name in files):
        deploy.append("Dockerfile")
    if any("docker-compose" in name for name in files):
        deploy.append("Docker Compose")
    if any("nginx" in name.lower() for name in files):
        deploy.append("nginx")
    if any("supervisor" in name.lower() for name in files):
        deploy.append("Supervisor")

    scripts = {}
    dependencies = {}
    package_summaries = []
    for package_path in package_paths[:8]:
        data = read_json(package_path)
        if not data:
            continue
        rel_path = str(package_path.relative_to(root))
        package_summaries.append(rel_path)
        scripts.update({f"{rel_path}:{k}": v for k, v in data.get("scripts", {}).items()})
        deps = {}
        for section in ("dependencies", "devDependencies"):
            for name in data.get(section, {}).keys():
                deps[name] = section
        dependencies.update(deps)
        dep_names = set(deps.keys())
        if {"react", "react-dom"} & dep_names:
            frameworks.append("React")
        if "vite" in dep_names:
            frameworks.append("Vite")
        if "next" in dep_names:
            frameworks.append("Next.js")
        if "vue" in dep_names:
            frameworks.append("Vue")
        if "express" in dep_names:
            frameworks.append("Express")

    if go_mods:
        for go_mod in go_mods[:5]:
            text = go_mod.read_text(encoding="utf-8", errors="ignore")
            if "gin-gonic/gin" in text:
                frameworks.append("Gin")
            if "gofiber/fiber" in text:
                frameworks.append("Fiber")
            if "gorm.io/gorm" in text:
                frameworks.append("GORM")
            if "go-sql-driver/mysql" in text:
                dependencies["mysql"] = "go module"
            if "lib/pq" in text or "pgx" in text:
                dependencies["postgres"] = "go module"

    env_files = [
        p
        for name, p in files.items()
        if p.name == ".env" or p.name.startswith(".env.") or p.name.endswith(".env")
    ]
    env_summary = []
    for path in env_files:
        keys = extract_env_keys(path)
        env_summary.append(
            {
                "path": str(path.relative_to(root)),
                "keys": keys,
                "sensitive_key_count": sum(
                    1 for key in keys if any(hint in key.upper() for hint in SECRET_HINTS)
                ),
            }
        )

    important_files = []
    for name in sorted(files):
        lower = name.lower()
        if name in {"README.md", "README", "Makefile", "go.mod", "package.json", "pubspec.yaml"}:
            important_files.append(name)
        elif lower.endswith(("dockerfile", "docker-compose.yml", "docker-compose.yaml")):
            important_files.append(name)
        elif "nginx" in lower or "supervisor" in lower or "deploy" in lower:
            if not lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                important_files.append(name)

    git_remote = run(["git", "-C", str(root), "remote", "-v"])
    branch = run(["git", "-C", str(root), "branch", "--show-current"])
    last_commit = run(["git", "-C", str(root), "log", "-1", "--format=%h %ci %s"])
    dirty = bool(run(["git", "-C", str(root), "status", "--short"]))

    return {
        "name": root.name,
        "path": str(root),
        "relative_path": rel(root),
        "slug": slugify(root),
        "branch": branch or "unknown",
        "last_commit": last_commit or "none",
        "dirty": dirty,
        "remotes": git_remote.splitlines(),
        "languages": sorted(set(languages)),
        "frameworks": sorted(set(frameworks)),
        "runtime": sorted(set(runtime)),
        "deploy": sorted(set(deploy)),
        "scripts": scripts,
        "dependencies_sample": sorted(dependencies.keys())[:80],
        "package_files": package_summaries,
        "go_modules": [str(p.relative_to(root)) for p in go_mods],
        "pubspec_files": [str(p.relative_to(root)) for p in pubspecs],
        "env_files": env_summary,
        "important_files": sorted(set(important_files))[:120],
    }


def yaml_scalar(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    text = str(value)
    if not text:
        return '""'
    if re.match(r"^[A-Za-z0-9_./:@-]+$", text):
        return text
    return json.dumps(text, ensure_ascii=False)


def write_projects_yaml(projects):
    lines = [
        "# Generated by scripts/generate_knowledge_base.py",
        f"# generated_at: {GENERATED_AT}",
        "projects:",
    ]
    for item in projects:
        lines.extend(
            [
                f"  - name: {yaml_scalar(item['name'])}",
                f"    slug: {yaml_scalar(item['slug'])}",
                f"    path: {yaml_scalar(item['path'])}",
                f"    relative_path: {yaml_scalar(item['relative_path'])}",
                f"    branch: {yaml_scalar(item['branch'])}",
                f"    dirty: {yaml_scalar(item['dirty'])}",
                "    languages:",
            ]
        )
        lines.extend([f"      - {yaml_scalar(v)}" for v in item["languages"]] or ["      []"])
        lines.append("    frameworks:")
        lines.extend([f"      - {yaml_scalar(v)}" for v in item["frameworks"]] or ["      []"])
        lines.append("    deploy:")
        lines.extend([f"      - {yaml_scalar(v)}" for v in item["deploy"]] or ["      []"])
        lines.append(f"    doc: projects/{item['slug']}.md")
    (KB_ROOT / "inventory" / "projects.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_env_inventory(projects):
    lines = [
        "# Env Files Inventory",
        "",
        f"- Generated at: `{GENERATED_AT}`",
        "- This file records env file paths and key names only.",
        "- Secret values are backed up under ignored `private/env-backup/`.",
        "",
    ]
    for item in projects:
        if not item["env_files"]:
            continue
        lines.extend([f"## {item['relative_path']}", ""])
        for env in item["env_files"]:
            lines.append(f"### `{env['path']}`")
            lines.append("")
            lines.append(f"- Key count: `{len(env['keys'])}`")
            lines.append(f"- Sensitive-looking key count: `{env['sensitive_key_count']}`")
            if env["keys"]:
                lines.append("- Keys:")
                lines.extend([f"  - `{key}`" for key in env["keys"]])
            lines.append("")
    (KB_ROOT / "inventory" / "env-files.md").write_text("\n".join(lines), encoding="utf-8")


def write_project_md(item):
    lines = [
        f"# {item['name']}",
        "",
        "## 基本信息",
        "",
        f"- 本地路径：`{item['path']}`",
        f"- 相对路径：`{item['relative_path']}`",
        f"- 当前分支：`{item['branch']}`",
        f"- 最近提交：`{item['last_commit']}`",
        f"- 工作区有未提交改动：`{str(item['dirty']).lower()}`",
        "",
        "## 技术栈",
        "",
        f"- 语言：{', '.join(item['languages']) if item['languages'] else '待补充'}",
        f"- 框架：{', '.join(item['frameworks']) if item['frameworks'] else '待补充'}",
        f"- 运行时：{', '.join(item['runtime']) if item['runtime'] else '待补充'}",
        f"- 部署线索：{', '.join(item['deploy']) if item['deploy'] else '待补充'}",
        "",
        "## Git 远端",
        "",
    ]
    if item["remotes"]:
        lines.extend([f"- `{remote}`" for remote in item["remotes"]])
    else:
        lines.append("- 未配置或未读取到远端")

    lines.extend(["", "## 关键文件", ""])
    if item["important_files"]:
        lines.extend([f"- `{path}`" for path in item["important_files"]])
    else:
        lines.append("- 待补充")

    lines.extend(["", "## 构建和运行脚本", ""])
    if item["scripts"]:
        for key, command in sorted(item["scripts"].items()):
            lines.append(f"- `{key}`: `{command}`")
    else:
        lines.append("- 未在 package.json 中发现 scripts，或项目不是 Node 前端/服务")

    lines.extend(["", "## 配置文件和环境变量", ""])
    if item["env_files"]:
        for env in item["env_files"]:
            lines.append(f"### `{env['path']}`")
            lines.append("")
            lines.append(f"- 变量数量：{len(env['keys'])}")
            lines.append(f"- 疑似敏感变量数量：{env['sensitive_key_count']}")
            if env["keys"]:
                lines.append("- 变量名：")
                lines.extend([f"  - `{key}`" for key in env["keys"]])
            lines.append("")
    else:
        lines.append("- 未发现 `.env`、`.env.*` 或 `*.env` 文件")

    lines.extend(["", "## 依赖线索", ""])
    if item["dependencies_sample"]:
        lines.extend([f"- `{dep}`" for dep in item["dependencies_sample"]])
    else:
        lines.append("- 待补充")

    lines.extend(
        [
            "",
            "## 复刻和运维备注",
            "",
            "- 真实 `.env` 内容不写入本文档。需要复刻时先查看 `private/env-backup/` 的本地备份。",
            "- 如果项目涉及邮件、支付、数据库、第三方 API，请优先补充服务商、回调域名、端口和生产环境凭据来源。",
            "- 部署成功后必须更新 `inventory/projects.yaml` 和 `deployments/` 下的部署记录。",
            "",
        ]
    )
    (KB_ROOT / "projects" / f"{item['slug']}.md").write_text("\n".join(lines), encoding="utf-8")


def copy_env_backups(projects):
    backup_root = KB_ROOT / "private" / "env-backup"
    manifest_lines = [
        "# Env Backup Manifest",
        "",
        f"- Generated at: `{GENERATED_AT}`",
        "- This directory is intentionally ignored by Git.",
        "- Do not paste secret values into committed Markdown files.",
        "",
    ]
    for item in projects:
        project_root = Path(item["path"])
        for env in item["env_files"]:
            source = project_root / env["path"]
            dest = backup_root / item["slug"] / env["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            os.chmod(dest, 0o600)
            manifest_lines.append(f"- `{item['relative_path']}/{env['path']}` -> `{dest.relative_to(KB_ROOT)}`")
    backup_root.mkdir(parents=True, exist_ok=True)
    (backup_root / "MANIFEST.md").write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    os.chmod(backup_root, 0o700)


def write_static_docs(projects):
    readme = [
        "# HK Open API Agent Knowledge Base",
        "",
        "这是公司内部项目知识库和部署智能体上下文仓库。它面向 Hermes、Codex 和人工运维共同使用。",
        "",
        "## 目录",
        "",
        "- `inventory/`：结构化资产台账，包括项目、服务器、域名和端口。",
        "- `projects/`：每个 Git 项目的知识库 Markdown。",
        "- `runbooks/`：部署、验证、回滚和知识更新流程。",
        "- `templates/`：nginx、Supervisor、frp、Docker 等配置模板。",
        "- `deployments/`：每次部署后的记录。",
        "- `ai/`：Hermes/Codex 使用规则。",
        "- `private/`：本地敏感备份，默认不提交。",
        "",
        "## 当前索引",
        "",
        f"- 生成时间：`{GENERATED_AT}`",
        f"- Git 项目数量：`{len(projects)}`",
        "",
        "## 推荐阅读入口",
        "",
        "1. `inventory/service-map.md`：业务系统和横向能力总览。",
        "2. `inventory/projects.yaml`：全部 Git 项目结构化台账。",
        "3. `projects/*.md`：每个项目的独立知识库文件。",
        "4. `runbooks/rebuild-from-env-backup.md`：从本地 env 备份复刻邮件、支付、数据库等能力。",
        "5. `ai/deployment-agent-rules.md`：Hermes/Codex 部署执行规则。",
        "",
        "## 使用规则",
        "",
        "1. `inventory/*.yaml` 是事实来源，Markdown 是给人和 AI 阅读的说明。",
        "2. 真实密钥和 `.env` 内容只允许存在于 `private/` 或密码管理器，不允许提交到 Git。",
        "3. 每次部署成功后必须新增 `deployments/YYYY-MM-DD-project.md`，并更新项目台账。",
        "4. AI 执行部署前必须先生成计划、列出将修改的服务器文件、等待确认。",
        "",
    ]
    (KB_ROOT / "README.md").write_text("\n".join(readme), encoding="utf-8")

    (KB_ROOT / ".gitignore").write_text(
        "\n".join(
            [
                "private/",
                ".DS_Store",
                "*.log",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (KB_ROOT / "ai" / "deployment-agent-rules.md").write_text(
        "\n".join(
            [
                "# Deployment Agent Rules",
                "",
                "## 核心原则",
                "",
                "1. 先读后改：修改服务器配置前必须先读取原文件。",
                "2. 先计划后执行：部署前必须输出部署计划、端口、域名、回滚方案。",
                "3. 敏感信息不外泄：不在 Markdown、聊天消息、Git commit 中输出 secret value。",
                "4. 数据库端口默认只绑定 `127.0.0.1`。",
                "5. 修改 nginx、Supervisor、Docker、frp 后必须执行对应验证命令。",
                "6. 部署完成后必须更新 `inventory/` 和 `deployments/`。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (KB_ROOT / "ai" / "knowledge-update-rules.md").write_text(
        "\n".join(
            [
                "# Knowledge Update Rules",
                "",
                "每次项目新增、部署、迁移或修改配置后，必须更新：",
                "",
                "- `inventory/projects.yaml`",
                "- 对应 `projects/*.md`",
                "- 必要时更新 `inventory/domains.yaml`、`inventory/ports.yaml`、`inventory/servers.yaml`",
                "- 新增一条 `deployments/YYYY-MM-DD-project.md`",
                "",
                "禁止把 `.env` 的值写入可提交文件。只允许记录变量名、用途和凭据存放位置。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (KB_ROOT / "runbooks" / "deploy-go-supervisor.md").write_text(
        "\n".join(
            [
                "# Go + Supervisor 部署流程",
                "",
                "1. 本地交叉编译：`GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o service`。",
                "2. 上传二进制和配置文件到 `/home/admin/<project>/`。",
                "3. 创建 `run.sh`，由 Supervisor 直接管理进程。",
                "4. 创建 `/etc/supervisor/conf.d/<project>.conf`。",
                "5. 执行 `supervisorctl reread && supervisorctl update`。",
                "6. 检查进程、日志、端口和健康接口。",
                "7. 更新知识库部署记录。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (KB_ROOT / "runbooks" / "deploy-static-nginx.md").write_text(
        "\n".join(
            [
                "# 静态前端 + nginx 部署流程",
                "",
                "1. 本地执行项目构建命令。",
                "2. 上传 `dist/*` 或构建产物到服务器项目目录，避免多套一层目录。",
                "3. 创建或更新 nginx site 配置。",
                "4. 执行 `nginx -t`，通过后 reload。",
                "5. 检查域名、静态资源、前端路由和 API 反代。",
                "6. 更新知识库部署记录。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (KB_ROOT / "runbooks" / "deploy-docker-compose.md").write_text(
        "\n".join(
            [
                "# Docker Compose 部署流程",
                "",
                "1. 检查 `docker-compose.yml` 是否设置唯一 `name`。",
                "2. 数据库端口必须优先绑定 `127.0.0.1`。",
                "3. 上传 compose、env 和必要配置。",
                "4. 执行 `docker compose up -d`。",
                "5. 检查 `docker compose ps`、日志、端口和健康接口。",
                "6. 更新知识库部署记录。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (KB_ROOT / "templates" / "supervisor.conf.tpl").write_text(
        "[program:{{ project_name }}]\n"
        "command=/home/admin/{{ project_name }}/run.sh\n"
        "directory=/home/admin/{{ project_name }}\n"
        "user=admin\n"
        "autostart=true\n"
        "autorestart=true\n"
        "startsecs=3\n"
        "stdout_logfile=/home/admin/{{ project_name }}/tmp/supervisor-stdout.log\n"
        "stderr_logfile=/home/admin/{{ project_name }}/tmp/supervisor-stderr.log\n",
        encoding="utf-8",
    )

    (KB_ROOT / "templates" / "nginx-site.conf.tpl").write_text(
        "server {\n"
        "    listen {{ port }};\n"
        "    server_name _;\n"
        "    root /home/admin/{{ project_name }}/dist;\n"
        "    location / { try_files $uri $uri/ /index.html; }\n"
        "}\n",
        encoding="utf-8",
    )

    for name in ("servers.yaml", "domains.yaml", "ports.yaml"):
        path = KB_ROOT / "inventory" / name
        if not path.exists():
            path.write_text("# TODO: fill from production server audit.\n", encoding="utf-8")

    (KB_ROOT / "deployments" / ".gitkeep").write_text("", encoding="utf-8")


def main():
    for dirname in ("inventory", "projects", "runbooks", "templates", "deployments", "ai", "private"):
        (KB_ROOT / dirname).mkdir(parents=True, exist_ok=True)

    projects = [classify_project(path) for path in find_git_projects()]
    write_projects_yaml(projects)
    write_env_inventory(projects)
    for item in projects:
        write_project_md(item)
    copy_env_backups(projects)
    write_static_docs(projects)

    summary = {
        "generated_at": GENERATED_AT,
        "project_count": len(projects),
        "env_file_count": sum(len(item["env_files"]) for item in projects),
        "projects": [{"name": item["name"], "path": item["relative_path"], "doc": f"projects/{item['slug']}.md"} for item in projects],
    }
    (KB_ROOT / "inventory" / "generation-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
