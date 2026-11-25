#!/usr/bin/env python3
"""wildstream-guardian 零依赖自检（仅 Python 标准库，不安装第三方依赖）。

检查项：
  1. 必要文件存在（双语 README / LICENSE / .gitignore / requirements.txt / 入口模块）
  2. Python 语法编译（逐个模块 compile，捕获语法错误）
  3. JSON 文件可解析；PWA manifest 字段与图标存在
  4. HTML 本地相对引用与 /static/* 引用是否存在
  5. Service Worker 预缓存清单条目是否存在
  6. 多语言 JSON 键集合一致性
  7. 密钥外泄扫描（高危记 error，可疑硬编码记 warning）
  8. 残留版本冲突标记

退出码：存在 error 时为 1，否则为 0。
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO_NAME = "wildstream-guardian"
ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "README.md", "README.en.md", "LICENSE", ".gitignore",
    "requirements.txt", "main.py", "config.py", "templates/base.html",
]
SKIP_DIRS = {
    ".git", ".github", "node_modules", "__pycache__", ".venv", "venv",
    ".idea", ".vscode", "vendor",
}
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".yml", ".yaml", ".py", ".js", ".ts", ".html", ".css",
    ".toml", ".ini", ".cfg", ".sh", ".bat", ".ps1", ".xml", ".gitignore", "",
}
MAX_SCAN_BYTES = 2 * 1024 * 1024

MD_LINK_RE = re.compile(r"\]\(\s*([^()\s]+(?:\([^()]*\)[^()\s]*)*)\s*\)")
HTML_REF_RE = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""")
SW_ASSETS_RE = re.compile(
    r"(?:PRECACHE|CACHE_FILES|CACHE_ASSETS|STATIC_FILES|SHELL|ASSETS)\s*=\s*\[(.*?)\]",
    re.DOTALL,
)
SW_ENTRY_RE = re.compile(r"""["']([^"']+)["']""")
CONFLICT_RE = re.compile(r"^(<{7}|={7}|>{7})(\s|$)", re.MULTILINE)
H1_RE = re.compile(r"^#\s+\S", re.MULTILINE)

SECRET_RULES = [
    ("私钥块", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"), "error"),
    ("AWS Access Key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "error"),
    ("GitHub Token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "error"),
    ("Google API Key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "error"),
    ("Slack Token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"), "error"),
    ("OpenAI 风格密钥", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "error"),
]
ASSIGN_RE = re.compile(
    r"(?i)\b(api[_-]?key|apikey|secret|secret[_-]?key|token|access[_-]?token|password|passwd)\b"
    r"\s*[:=]\s*[\"'][^\"'\n]{8,}[\"']"
)
PLACEHOLDERS = (
    "your", "xxx", "placeholder", "example", "sample", "changeme", "change-me",
    "todo", "dummy", "fake", "test", "none", "null", "{{", "${",
)

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def iter_files() -> list[Path]:
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            out.append(Path(dirpath) / name)
    return out


def read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_SCAN_BYTES:
            return None
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check_required() -> None:
    for name in REQUIRED_FILES:
        if not (ROOT / name).is_file():
            err(f"缺少必要文件：{name}")
    zh = ROOT / "README.md"
    en = ROOT / "README.en.md"
    if zh.is_file() and "README.en.md" not in zh.read_text(encoding="utf-8", errors="replace"):
        err("README.md 未链接英文版 README.en.md")
    if en.is_file() and "README.md" not in en.read_text(encoding="utf-8", errors="replace"):
        err("README.en.md 未回链中文版 README.md")


def check_python_syntax() -> None:
    for path in iter_files():
        if path.suffix != ".py":
            continue
        text = read_text(path)
        if text is None:
            continue
        try:
            compile(text, str(path), "exec")
        except SyntaxError as exc:
            err(f"{rel(path)} 语法错误：第 {exc.lineno} 行 {exc.msg}")


def check_json() -> None:
    for path in iter_files():
        if path.suffix != ".json":
            continue
        text = read_text(path)
        if text is None:
            continue
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            err(f"{rel(path)} JSON 解析失败：第 {exc.lineno} 行 {exc.msg}")


def resolve_ref(base_dir: Path, target: str) -> Path | None:
    raw = target.strip()
    if not raw or raw.startswith("#"):
        return None
    if any(token in raw for token in ("{{", "}}", "${", "<%", "%}")):
        return None
    parsed = urlsplit(raw)
    if parsed.scheme or raw.startswith("//"):
        return None
    candidate = unquote(raw.split("#", 1)[0].split("?", 1)[0])
    if not candidate:
        return None
    if candidate.startswith("/"):
        # 以根路径书写的静态资源按仓库根目录校验；其余视为服务端路由，跳过
        if not candidate.startswith(("/static/", "/docs/", "/assets/", "/stacked/")):
            return None
        return ROOT / candidate.lstrip("/")
    return base_dir / candidate


def check_html_refs() -> None:
    for path in iter_files():
        if path.suffix.lower() not in (".html", ".htm"):
            continue
        text = read_text(path)
        if text is None:
            continue
        for match in HTML_REF_RE.finditer(text):
            resolved = resolve_ref(path.parent, match.group(1))
            if resolved is None:
                continue
            if not resolved.exists():
                err(f"{rel(path)} 引用不存在：{match.group(1)}")


def check_markdown() -> None:
    for path in iter_files():
        if path.suffix.lower() != ".md":
            continue
        text = read_text(path)
        if text is None:
            continue
        if path.name in ("README.md", "README.en.md") and not H1_RE.search(text):
            err(f"{rel(path)} 缺少一级标题")
        for match in MD_LINK_RE.finditer(text):
            resolved = resolve_ref(path.parent, match.group(1))
            if resolved is None:
                continue
            if not resolved.exists():
                err(f"{rel(path)} 链接指向的文件不存在：{match.group(1)}")


def check_manifest() -> None:
    manifest_path = ROOT / "docs" / "manifest.json"
    if not manifest_path.is_file():
        warn("未找到 docs/manifest.json，跳过 PWA manifest 检查")
        return
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    for field in ("name", "short_name", "start_url", "display", "icons"):
        if field not in data:
            err(f"docs/manifest.json 缺少字段：{field}")
    for icon in data.get("icons", []):
        src = icon.get("src")
        if not src:
            err("docs/manifest.json icons 条目缺少 src")
            continue
        if not (manifest_path.parent / unquote(src)).exists():
            err(f"docs/manifest.json 图标不存在：{src}")


def check_service_worker() -> None:
    sw_path = ROOT / "docs" / "sw.js"
    if not sw_path.is_file():
        warn("未找到 docs/sw.js，跳过 Service Worker 检查")
        return
    text = sw_path.read_text(encoding="utf-8", errors="replace")
    match = SW_ASSETS_RE.search(text)
    if not match:
        warn("docs/sw.js 未找到预缓存清单数组，跳过条目校验")
        return
    entries = SW_ENTRY_RE.findall(match.group(1))
    if not entries:
        warn("docs/sw.js 预缓存清单为空")
        return
    for entry in entries:
        raw = entry.strip()
        if raw in ("./", "/", "."):
            continue
        if any(token in raw for token in ("{{", "}}", "${", "<%")):
            continue
        parsed = urlsplit(raw)
        if parsed.scheme or raw.startswith("//"):
            continue
        candidate = unquote(raw.split("#", 1)[0].split("?", 1)[0]).lstrip("./")
        if not (sw_path.parent / candidate).exists():
            err(f"docs/sw.js 预缓存条目不存在：{entry}")


def flatten_keys(data: object, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(data, dict):
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            keys.add(path)
            keys |= flatten_keys(value, path)
    return keys


def check_i18n() -> None:
    i18n_dir = ROOT / "templates" / "i18n"
    if not i18n_dir.is_dir():
        return
    files = sorted(i18n_dir.glob("*.json"))
    if len(files) < 2:
        return
    baseline_name = files[0].name
    try:
        baseline = flatten_keys(json.loads(files[0].read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return
    for path in files[1:]:
        try:
            current = flatten_keys(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
        missing = sorted(baseline - current)
        extra = sorted(current - baseline)
        if missing:
            warn(f"templates/i18n/{path.name} 相比 {baseline_name} 缺少 {len(missing)} 个键：{', '.join(missing[:5])}")
        if extra:
            warn(f"templates/i18n/{path.name} 相比 {baseline_name} 多出 {len(extra)} 个键：{', '.join(extra[:5])}")


def check_secrets() -> None:
    for path in iter_files():
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = read_text(path)
        if text is None:
            continue
        rel_path = rel(path)
        if CONFLICT_RE.search(text):
            err(f"{rel_path} 含未解决的版本冲突标记")
        for label, pattern, level in SECRET_RULES:
            if pattern.search(text):
                (err if level == "error" else warn)(f"{rel_path} 疑似{label}外泄")
        for match in ASSIGN_RE.finditer(text):
            quoted = re.search(r"[\"']([^\"']+)[\"']", match.group(0))
            inner = quoted.group(1).strip().lower() if quoted else ""
            if not inner or any(token in inner for token in PLACEHOLDERS):
                continue
            warn(f"{rel_path} 疑似硬编码凭据赋值：{match.group(1)}")


def main() -> int:
    print(f"== {REPO_NAME} · 项目自检 ==")
    check_required()
    check_python_syntax()
    check_json()
    check_markdown()
    check_html_refs()
    check_manifest()
    check_service_worker()
    check_i18n()
    check_secrets()

    for item in errors:
        print(f"ERROR  {item}")
    for item in warnings:
        print(f"WARN   {item}")
    print(f"\n结果：{len(errors)} error(s), {len(warnings)} warning(s)")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fp:
            fp.write(f"## {REPO_NAME} 自检\n\n")
            fp.write(f"- error: {len(errors)}\n- warning: {len(warnings)}\n")
            for item in errors:
                fp.write(f"- ERROR: {item}\n")
            for item in warnings:
                fp.write(f"- WARN: {item}\n")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
