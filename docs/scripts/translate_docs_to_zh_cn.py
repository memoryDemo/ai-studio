#!/usr/bin/env python3
"""Translate Docusaurus docs/blog sources into zh-CN localized content."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

try:
    import requests
    from deep_translator import GoogleTranslator
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: deep-translator. Install it with "
        "`python -m pip install --user deep-translator`."
    ) from exc


DOCS_ROOT = Path(__file__).resolve().parents[1]
SITE_DOCS_ROOT = DOCS_ROOT / "docs"
BLOG_ROOT = DOCS_ROOT / "blog"
I18N_ROOT = DOCS_ROOT / "i18n" / "zh-CN"
DOCS_TARGET_ROOT = I18N_ROOT / "docusaurus-plugin-content-docs" / "current"
BLOG_TARGET_ROOT = I18N_ROOT / "docusaurus-plugin-content-blog"
CACHE_PATH = Path.home() / ".cache" / "dbgpt" / "docs_zh_cn_translation_cache.json"
REQUEST_TIMEOUT_SECONDS = 20


_ORIGINAL_REQUESTS_GET = requests.get


def _requests_get_with_timeout(*args, **kwargs):
    kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
    return _ORIGINAL_REQUESTS_GET(*args, **kwargs)


requests.get = _requests_get_with_timeout


GLOSSARY_TARGETS = {
    "UMBER-STUDIO": "UMBER-STUDIO",
    "AWEL": "AWEL",
    "RAG": "RAG",
    "LLM": "LLM",
    "OpenAI": "OpenAI",
    "DeepSeek": "DeepSeek",
    "Hugging Face": "Hugging Face",
    "Ollama": "Ollama",
    "Meta Llama 3.1": "Meta Llama 3.1",
    "Chat Dashboard": "Chat Dashboard",
    "Chat Data": "Chat Data",
    "Chat Excel": "Chat Excel",
    "Chat Knowledge": "Chat Knowledge",
    "Chat DB": "Chat DB",
    "Chat Normal": "Chat Normal",
    "Builder Console": "Builder Console",
    "Agentic Workflow Expression Language": "Agentic Workflow Expression Language",
    "top k": "top k",
    "top p": "top p",
}

SOURCE_PLACEHOLDER_PATTERNS = [
    (re.compile(r"\b[Mm]ulti-[Aa]gents?\b"), "多智能体"),
    (re.compile(r"\b[Mm]ulti [Aa]gents?\b"), "多智能体"),
    (re.compile(r"\b[Aa]gents\b"), "智能体"),
    (re.compile(r"\b[Aa]gent\b"), "智能体"),
    (re.compile(r"\bLLM generation\b", re.IGNORECASE), "LLM 生成"),
]

POST_REPLACEMENTS = [
    (re.compile(r"UMBER-STUDIO\s*Agent"), "UMBER-STUDIO 智能体"),
    (re.compile(r"多Agent"), "多智能体"),
    (re.compile(r"多智能体系统"), "多智能体系统"),
    (re.compile(r"LLM一代"), "LLM 生成"),
    (re.compile(r"LLM 一代"), "LLM 生成"),
    (re.compile(r"前 k"), "top k"),
    (re.compile(r"前 p"), "top p"),
    (re.compile(r"聊天仪表板"), "Chat Dashboard"),
    (re.compile(r"聊天数据"), "Chat Data"),
    (re.compile(r"聊天 Excel"), "Chat Excel"),
    (re.compile(r"聊天知识"), "Chat Knowledge"),
]

JSON_MESSAGE_FILES = [
    I18N_ROOT / "docusaurus-plugin-content-docs" / "current.json",
    I18N_ROOT / "docusaurus-plugin-content-blog" / "options.json",
    I18N_ROOT / "docusaurus-theme-classic" / "navbar.json",
    I18N_ROOT / "docusaurus-theme-classic" / "footer.json",
]


def load_cache() -> Dict[str, str]:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(cache: Dict[str, str]) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def ensure_i18n_skeleton() -> None:
    if I18N_ROOT.exists():
        return
    subprocess.run(
        ["npm", "run", "write-translations", "--", "--locale", "zh-CN"],
        cwd=DOCS_ROOT,
        check=True,
    )


def is_english_like(text: str) -> bool:
    stripped = strip_non_text(text)
    letters = sum(ch.isalpha() and ord(ch) < 128 for ch in stripped)
    cjk = sum("\u4e00" <= ch <= "\u9fff" for ch in stripped)
    if letters < 4:
        return False
    return letters > cjk * 1.6


def strip_non_text(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", "", text)
    text = re.sub(r"!\[[^\]]*]\([^)]+\)", "", text)
    text = re.sub(r"\[[^\]]*]\([^)]+\)", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"https?://\S+", "", text)
    return text


def protect_inline(text: str) -> Tuple[str, Dict[str, str]]:
    placeholders: Dict[str, str] = {}
    index = 0

    def reserve(value: str) -> str:
        nonlocal index
        key = f"__PH_{index}__"
        index += 1
        placeholders[key] = value
        return key

    text = re.sub(r"!\[[^\]]*]\([^)]+\)", lambda m: reserve(m.group(0)), text)
    text = re.sub(r"\[[^\]]*]\([^)]+\)", lambda m: reserve(m.group(0)), text)
    text = re.sub(r"`[^`\n]+`", lambda m: reserve(m.group(0)), text)
    text = re.sub(r"https?://\S+", lambda m: reserve(m.group(0)), text)

    for source, target in GLOSSARY_TARGETS.items():
        pattern = re.compile(re.escape(source))
        text = pattern.sub(lambda _: reserve(target), text)

    for pattern, replacement in SOURCE_PLACEHOLDER_PATTERNS:
        text = pattern.sub(lambda _: reserve(replacement), text)
    return text, placeholders


def restore_inline(text: str, placeholders: Dict[str, str]) -> str:
    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def translate_with_retry(
    translator: GoogleTranslator,
    text: str,
    cache: Dict[str, str],
    force: bool = False,
) -> str:
    if not text.strip():
        return text
    if not force and not is_english_like(text):
        return text
    cached = cache.get(text)
    if cached is not None:
        return cached

    protected, placeholders = protect_inline(text)
    for attempt in range(3):
        try:
            translated = translator.translate(protected)
            translated = restore_inline(translated, placeholders)
            translated = post_process(translated)
            cache[text] = translated
            return translated
        except Exception:
            if attempt == 2:
                return text
            time.sleep(1.5 * (attempt + 1))
    return text


def post_process(text: str) -> str:
    for pattern, replacement in POST_REPLACEMENTS:
        text = pattern.sub(replacement, text)
    text = text.replace("（ ", " (").replace(" ）", ") ")
    text = text.replace("` ", "`").replace(" `", "`")
    return text


def normalize_front_matter_value(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\s*\n\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def escape_yaml_double_quoted(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def split_front_matter(text: str) -> Tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return "", text
    return parts[0] + "\n---\n", parts[1]


def translate_front_matter(
    front_matter: str, translator: GoogleTranslator, cache: Dict[str, str]
) -> str:
    if not front_matter:
        return front_matter
    lines = front_matter.splitlines()
    if len(lines) < 2:
        return front_matter

    out: List[str] = ["---"]
    i = 1
    last = len(lines) - 1
    while i < last:
        line = lines[i]
        key_match = re.match(r"^(\s*)(title|description):\s*(.*)$", line)
        if not key_match:
            out.append(line)
            i += 1
            continue

        indent, key, remainder = key_match.groups()
        remainder = remainder.strip()
        quote = remainder[:1] if remainder[:1] in {'"', "'"} else ""
        value_lines: List[str] = []

        if quote:
            current = remainder[1:]
            if current.endswith(quote) and not current.endswith(f"\\{quote}"):
                value_lines.append(current[:-1])
                i += 1
            else:
                value_lines.append(current)
                i += 1
                while i < last:
                    next_line = lines[i]
                    if next_line.endswith(quote) and not next_line.endswith(f"\\{quote}"):
                        value_lines.append(next_line[:-1])
                        i += 1
                        break
                    value_lines.append(next_line)
                    i += 1
        else:
            value_lines.append(remainder)
            i += 1

        value = "\n".join(value_lines)
        translated = translate_with_retry(translator, value, cache, force=True)
        translated = normalize_front_matter_value(translated)
        escaped = escape_yaml_double_quoted(translated)
        out.append(f'{indent}{key}: "{escaped}"')

    out.append("---")
    return "\n".join(out) + "\n"


def is_special_mdx_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith(("import ", "export ", "<", "</", ":::")):
        return True
    if re.match(r"^[A-Za-z_]+\s*=", stripped):
        return True
    if stripped.startswith(("{label:", "{value:", "values={[", "defaultValue=")):
        return True
    if re.match(r'^\s*"[^"]+":\s*', line):
        return True
    if re.match(r'^\s*"[^"]*"\s*,?\s*$', line):
        return True
    if re.match(r"^\s*[\[\]{}(),]+\s*$", line):
        return True
    if stripped in {"{", "}", "},", "];", "])}", "]} />", "]}", "/>"}:
        return True
    return False


def translate_json_string_value(
    line: str, key: str, translator: GoogleTranslator, cache: Dict[str, str]
) -> str:
    line_ending = "\n" if line.endswith("\n") else ""
    stripped_line = line[:-1] if line_ending else line
    pattern = re.compile(rf'^(\s*"{re.escape(key)}":\s*")(.+?)(".*)$')
    match = pattern.match(stripped_line)
    if not match:
        return line
    prefix, value, suffix = match.groups()
    translated = translate_with_retry(translator, value, cache, force=True)
    return f"{prefix}{translated}{suffix}{line_ending}"


def translate_markdown_line(
    line: str, translator: GoogleTranslator, cache: Dict[str, str]
) -> str:
    line_ending = "\n" if line.endswith("\n") else ""
    raw = line[:-1] if line_ending else line
    stripped = raw.strip()

    if not stripped:
        return line
    if stripped.startswith(("```", "~~~", "<", "</", "import ", "export ", ":::")):
        return line
    if re.match(r"^\s*!\[[^\]]*]\([^)]+\)\s*$", raw):
        return line
    if re.match(r"^\s*[\[\]{}(),]+\s*$", raw):
        return line

    table_match = re.match(r"^(\s*)\|(.*)\|(\s*)$", raw)
    if table_match and not re.fullmatch(r"\s*:?-{3,}:?(?:\s*\|\s*:?-{3,}:?)*\s*", table_match.group(2)):
        indent, inner, trailing = table_match.groups()
        cells = inner.split("|")
        translated_cells = [
            translate_with_retry(translator, cell.strip(), cache, force=False)
            if cell.strip()
            else cell.strip()
            for cell in cells
        ]
        return f"{indent}| {' | '.join(translated_cells)} |{trailing}{line_ending}"

    markers = [
        r"^(\s{0,3}#{1,6}\s+)(.+)$",
        r"^(\s*(?:[-*+]\s+|\d+\.\s+))(.+)$",
        r"^(\s*>\s+)(.+)$",
    ]
    for pattern in markers:
        match = re.match(pattern, raw)
        if match:
            prefix, content = match.groups()
            translated = translate_with_retry(translator, content, cache, force=False)
            return f"{prefix}{translated}{line_ending}"

    indent_match = re.match(r"^(\s*)(.*)$", raw)
    indent, content = indent_match.groups()
    translated = translate_with_retry(translator, content, cache, force=False)
    return f"{indent}{translated}{line_ending}"


def translate_markdown_body(
    body: str, translator: GoogleTranslator, cache: Dict[str, str]
) -> str:
    out: List[str] = []
    in_code_fence = False

    for line in body.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_code_fence = not in_code_fence
            out.append(line)
            continue
        if in_code_fence:
            out.append(line)
            continue
        if is_special_mdx_line(line):
            out.append(line)
            continue
        out.append(translate_markdown_line(line, translator, cache))
    return "".join(out)


def translate_mdx_body(
    body: str, translator: GoogleTranslator, cache: Dict[str, str]
) -> str:
    out: List[str] = []
    in_code_fence = False

    for line in body.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_code_fence = not in_code_fence
            out.append(line)
            continue
        if in_code_fence:
            out.append(line)
            continue
        json_key_match = re.match(r'^\s*"([^"]+)":\s*', line)
        if json_key_match:
            key = json_key_match.group(1)
            if key in {"description", "text", "message", "title"}:
                out.append(translate_json_string_value(line, key, translator, cache))
            else:
                out.append(line)
            continue
        if is_special_mdx_line(line):
            out.append(line)
            continue
        out.append(translate_markdown_line(line, translator, cache))
    return "".join(out)


def translate_doc_file(
    source: Path, target: Path, translator: GoogleTranslator, cache: Dict[str, str]
) -> None:
    text = source.read_text(encoding="utf-8")
    front_matter, body = split_front_matter(text)
    translated_front_matter = translate_front_matter(front_matter, translator, cache)
    if source.suffix == ".mdx":
        translated_body = translate_mdx_body(body, translator, cache)
    else:
        translated_body = translate_markdown_body(body, translator, cache)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(translated_front_matter + translated_body, encoding="utf-8")


def translate_docs_tree(
    source_root: Path, target_root: Path, translator: GoogleTranslator, cache: Dict[str, str]
) -> None:
    files = sorted(
        path for path in source_root.rglob("*") if path.suffix in {".md", ".mdx"}
    )
    for source in files:
        target = target_root / source.relative_to(source_root)
        translate_doc_file(source, target, translator, cache)


def translate_json_messages(
    translator: GoogleTranslator, cache: Dict[str, str], path: Path
) -> None:
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    for value in payload.values():
        if isinstance(value, dict) and isinstance(value.get("message"), str):
            value["message"] = translate_with_retry(
                translator, value["message"], cache, force=True
            )
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def sync_static_assets() -> None:
    source = DOCS_ROOT / "static"
    target = I18N_ROOT / "docusaurus-plugin-content-docs" / "static"
    if source.exists():
        shutil.copytree(source, target, dirs_exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-blog", action="store_true")
    parser.add_argument("--reset-cache", action="store_true")
    parser.add_argument("--docs-only", action="store_true")
    parser.add_argument("--blog-only", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_i18n_skeleton()
    translator = GoogleTranslator(source="auto", target="zh-CN")
    cache = {} if args.reset_cache else load_cache()

    run_docs = not args.blog_only and not args.json_only
    run_blog = not args.docs_only and not args.json_only and not args.skip_blog
    run_json = not args.docs_only and not args.blog_only

    if run_docs:
        translate_docs_tree(SITE_DOCS_ROOT, DOCS_TARGET_ROOT, translator, cache)
    if run_blog:
        translate_docs_tree(BLOG_ROOT, BLOG_TARGET_ROOT, translator, cache)
    if run_json:
        for path in JSON_MESSAGE_FILES:
            translate_json_messages(translator, cache, path)
    sync_static_assets()

    save_cache(cache)
    return 0


if __name__ == "__main__":
    sys.exit(main())
