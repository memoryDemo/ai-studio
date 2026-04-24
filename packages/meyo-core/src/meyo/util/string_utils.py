"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""

import re
import string
from typing import Dict


def is_all_chinese(text):
    # 代码说明。
    pattern = re.compile(r"^[一-龥]+$")
    match = re.match(pattern, text)
    return match is not None


def contains_chinese(text):
    """执行当前函数对应的业务逻辑。"""
    return re.search(r"[\u4e00-\u9fa5]", text) is not None


def is_number_chinese(text):
    # 代码说明。
    pattern = re.compile(r"^[\d一-龥]+$")
    match = re.match(pattern, text)
    return match is not None


def is_chinese_include_number(text):
    # 代码说明。
    pattern = re.compile(r"^[一-龥]+[\d一-龥]*$")
    match = re.match(pattern, text)
    return match is not None


def is_scientific_notation(string):
    # 科学计数法的正则表达式
    pattern = r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$"
    # 使用正则表达式匹配字符串
    match = re.match(pattern, str(string))
    # 判断是否匹配成功
    if match is not None:
        return True
    else:
        return False


def is_valid_ipv4(address):
    """校验条件并返回判断结果。"""
    pattern = re.compile(
        r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )
    return pattern.match(address) is not None


def extract_content(long_string, s1, s2, is_include: bool = False) -> Dict[int, str]:
    # 提取文本。
    match_map = {}
    start_index = long_string.find(s1)
    while start_index != -1:
        if is_include:
            end_index = long_string.find(s2, start_index + len(s1) + 1)
            extracted_content = long_string[start_index : end_index + len(s2)]
        else:
            end_index = long_string.find(s2, start_index + len(s1))
            extracted_content = long_string[start_index + len(s1) : end_index]
        if extracted_content:
            match_map[start_index] = extracted_content
        start_index = long_string.find(s1, start_index + 1)
    return match_map


def extract_content_open_ending(long_string, s1, s2, is_include: bool = False):
    # 提取文本。
    match_map = {}
    start_index = long_string.find(s1)
    while start_index != -1:
        if long_string.find(s2, start_index) <= 0:
            end_index = len(long_string)
        else:
            if is_include:
                end_index = long_string.find(s2, start_index + len(s1) + 1)
            else:
                end_index = long_string.find(s2, start_index + len(s1))
        if is_include:
            extracted_content = long_string[start_index : end_index + len(s2)]
        else:
            extracted_content = long_string[start_index + len(s1) : end_index]
        if extracted_content:
            match_map[start_index] = extracted_content
        start_index = long_string.find(s1, start_index + 1)
    return match_map


def str_to_bool(s):
    if s.lower() in ("true", "t", "1", "yes", "y"):
        return True
    elif s.lower().startswith("true"):
        return True
    elif s.lower() in ("false", "f", "0", "no", "n"):
        return False
    else:
        return False


def _to_str(x, charset="utf8", errors="strict"):
    if x is None or isinstance(x, str):
        return x

    if isinstance(x, bytes):
        return x.decode(charset, errors)

    return str(x)


def remove_trailing_punctuation(s):
    """删除对应数据。"""
    punctuation = set(string.punctuation)
    chinese_punctuation = {
        "。",
        "，",
        "！",
        "？",
        "；",
        "：",
        "“",
        "”",
        "‘",
        "’",
        "（",
        "）",
        "【",
        "】",
        "—",
        "…",
        "《",
        "》",
    }
    punctuation.update(chinese_punctuation)
    while s and s[-1] in punctuation:
        s = s[:-1]

    return s
