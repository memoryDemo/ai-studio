#!/usr/bin/env python3
"""Normalize translated zh-CN docs/blog markdown formatting."""

from __future__ import annotations

import re
from pathlib import Path


DOCS_ROOT = Path(__file__).resolve().parents[1]
ZH_DOCS_ROOT = DOCS_ROOT / "i18n" / "zh-CN" / "docusaurus-plugin-content-docs" / "current"
SOURCE_DOCS_ROOT = DOCS_ROOT / "docs"
TARGETS = [
    ZH_DOCS_ROOT,
    DOCS_ROOT / "i18n" / "zh-CN" / "docusaurus-plugin-content-blog",
    DOCS_ROOT / "i18n" / "zh-CN" / "docusaurus-plugin-content-docs" / "current.json",
    DOCS_ROOT / "i18n" / "zh-CN" / "docusaurus-theme-classic" / "navbar.json",
    DOCS_ROOT / "i18n" / "zh-CN" / "docusaurus-theme-classic" / "footer.json",
    DOCS_ROOT / "i18n" / "zh-CN" / "docusaurus-plugin-content-blog" / "options.json",
]


def move_imports_to_top(text: str) -> str:
    front_matter = ""
    body = text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            front_matter = text[: end + 5]
            body = text[end + 5 :]

    lines = body.splitlines()
    import_lines = [line for line in lines if re.match(r"^(import|export)\s.+;$", line.strip())]
    if not import_lines:
        return text

    remaining = [line for line in lines if line not in import_lines]
    while remaining and not remaining[0].strip():
        remaining.pop(0)

    new_body = "\n".join(import_lines) + "\n\n" + "\n".join(remaining)
    if body.endswith("\n"):
        new_body += "\n"
    return front_matter + new_body


def normalize_front_matter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text

    front_matter = text[4:end]
    body = text[end + 5 :]
    lines = front_matter.splitlines()
    out = []
    i = 0

    while i < len(lines):
        line = lines[i]
        match = re.match(r"^(\s*)(title|description):\s*(.*)$", line)
        if not match:
            out.append(line)
            i += 1
            continue

        indent, key, remainder = match.groups()
        remainder = remainder.strip()
        if remainder[:1] in {'"', "'"}:
            remainder = remainder[1:]
        if remainder[-1:] in {'"', "'"}:
            remainder = remainder[:-1]

        value_lines = [remainder] if remainder else []
        i += 1
        while i < len(lines):
            current = lines[i]
            if re.match(r"^\s*(title|description):\s*", current):
                break
            if current.strip() == "":
                i += 1
                continue
            if current.startswith((" ", "\t")):
                value = current.strip()
                if value[-1:] in {'"', "'"}:
                    value = value[:-1]
                value_lines.append(value)
                i += 1
                continue
            break

        value = "\n".join(value_lines)
        value = value.replace("\r\n", "\n").replace("\r", "\n")
        value = re.sub(r"\s*\n\s*", " ", value)
        value = re.sub(r"\s+", " ", value).strip()
        value = value.replace("\\", "\\\\").replace('"', '\\"')
        out.append(f'{indent}{key}: "{value}"')

    return "---\n" + "\n".join(out) + "\n---\n" + body


def repair_config_reference_literals(path: Path, text: str) -> str:
    if not path.is_relative_to(ZH_DOCS_ROOT):
        return text
    relative_path = path.relative_to(ZH_DOCS_ROOT)
    if not str(relative_path).startswith("config-reference/"):
        return text
    source_path = SOURCE_DOCS_ROOT / relative_path
    if not source_path.exists():
        return text

    text = text.replace("“", '"').replace("”", '"')
    localized_lines = text.splitlines()
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    repaired = list(localized_lines)
    max_len = min(len(source_lines), len(localized_lines))
    scalar_pattern = re.compile(r'^\s*"[^"]+"\s*,?\s*$')
    object_pattern = re.compile(r"^\s*\{.*\}\s*,?\s*$")
    for i in range(max_len):
        source_line = source_lines[i]
        local_line = localized_lines[i]
        if scalar_pattern.match(source_line):
            repaired[i] = source_line
            continue
        if object_pattern.match(source_line) and any(token in local_line for token in ['“', '”', '：', '，']):
            repaired[i] = source_line
    return "\n".join(repaired) + ("\n" if text.endswith("\n") else "")


def normalize_content(path: Path, text: str) -> str:
    text = normalize_front_matter(text)
    text = move_imports_to_top(text)
    text = repair_config_reference_literals(path, text)
    text = text.replace("＃", "#")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"([^\n])(```|~~~)", r"\1\n\2", text)
    text = re.sub(r"(```|~~~)([^\n])", r"\1\n\2", text)
    text = re.sub(r"([^\n])(<Tabs\b)", r"\1\n\n\2", text)
    text = re.sub(r"([^\n])(<TabItem\b)", r"\1\n\n\2", text)
    text = re.sub(r"([^\n])(<p\b)", r"\1\n\2", text)
    text = re.sub(r"([^\n])(<img\b)", r"\1\n\2", text)
    text = re.sub(r"([^\n])(</TabItem>)", r"\1\n\2", text)
    text = re.sub(r"([^\n])(</p>)", r"\1\n\2", text)
    text = re.sub(r"(?m)^```\n(bash|python|env|toml|json|yaml|yml|sql)$", r"```\1", text)
    text = re.sub(r"LLM 代的", "LLM 生成的", text)
    text = re.sub(r"LLM 代", "LLM 生成", text)
    text = re.sub(r"(?<=\n)(#{2,6})([^ #])", r"\1 \2", text)
    text = re.sub(
        r"(?m)^(#{1,6}\s+[^\n]{1,30}?)(首先|然后|请|我们|您|LLM|Then|First|You|本文档|在此示例中|通过|创建|本指南|开始使用|给定)",
        r"\1\n\n\2",
        text,
    )
    text = re.sub(r"(\[[^\]]+\]\([^)]+\))(?=[\u4e00-\u9fffA-Za-z])", r"\1 ", text)
    text = re.sub(r"UMBER-STUDIO(?=[\u4e00-\u9fff])", "UMBER-STUDIO ", text)
    text = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", text)
    text = re.sub(r"智能体\s+应用程序", "智能体应用程序", text)
    text = re.sub(r"多智能体\s+系统", "多智能体系统", text)
    text = re.sub(r"UMBER-STUDIO\s+智能体", "UMBER-STUDIO 智能体", text)
    text = text.replace("代理工作流程", "智能体工作流")
    text = text.replace("系列型号", "系列模型")
    text = text.replace("变形金刚", "transformers")
    text = text.replace("源代码部署", "源码部署")
    text = text.replace("请cd到", "请切换到 ")
    text = text.replace("awel_教程", "AWEL 教程")
    text = text.replace("应用程序API", "应用 API")
    text = text.replace("应用程序编程接口", "API")
    text = text.replace("食谱", "Cookbook")
    return text


def normalize_path(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        for child in path.rglob("*"):
            if child.suffix not in {".md", ".mdx", ".json"}:
                continue
            text = child.read_text(encoding="utf-8")
            normalized = normalize_content(child, text)
            child.write_text(normalized, encoding="utf-8")
        return

    if path.suffix in {".md", ".mdx", ".json"}:
        text = path.read_text(encoding="utf-8")
        normalized = normalize_content(path, text)
        path.write_text(normalized, encoding="utf-8")


def main() -> int:
    for target in TARGETS:
        normalize_path(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
