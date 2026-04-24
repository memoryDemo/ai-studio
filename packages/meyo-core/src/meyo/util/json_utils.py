"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""


import json
import logging
import re
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, time

logger = logging.getLogger(__name__)

LLM_DEFAULT_RESPONSE_FORMAT = "llm_response_format_1"


def serialize(obj):
    if isinstance(obj, date):
        return obj.isoformat()


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, time):
            return obj.isoformat()
        return super().default(obj)


def extract_char_position(error_message: str) -> int:
    """执行当前函数对应的业务逻辑。"""

    char_pattern = re.compile(r"\(char (\d+)\)")
    if match := char_pattern.search(error_message):
        return int(match[1])
    else:
        raise ValueError("Character position not found in the error message.")


def find_json_objects(text: str):
    json_objects = []
    inside_string = False
    escape_character = False
    stack = []
    start_index = -1
    modified_text = list(text)  # 转换数据格式。

    for i, char in enumerate(text):
        # 代码说明。
        if char == "\\" and not escape_character:
            escape_character = True
            continue

        # 代码说明。
        if char == '"' and not escape_character:
            inside_string = not inside_string

        # 代码说明。
        if inside_string:
            if char == "\n":
                modified_text[i] = "\\n"
            elif char == "\t":
                modified_text[i] = "\\t"

        # 代码说明。
        if char in "{[" and not inside_string:
            stack.append(char)
            if len(stack) == 1:
                start_index = i
        # 代码说明。
        if char in "}]" and not inside_string and stack:
            if (char == "}" and stack[-1] == "{") or (char == "]" and stack[-1] == "["):
                stack.pop()
                if not stack:
                    end_index = i + 1
                    try:
                        json_str = "".join(modified_text[start_index:end_index])
                        json_obj = json.loads(json_str)
                        json_objects.append(json_obj)
                    except json.JSONDecodeError:
                        pass
        # 设置对应数据。
        escape_character = False if escape_character else escape_character

    return json_objects


def parse_or_raise_error(text: str, is_array: bool = False):
    if not text:
        return None
    parsed_objs = find_json_objects(text)
    if not parsed_objs:
        # 加载对应资源。
        return json.loads(text)
    return parsed_objs if is_array else parsed_objs[0]


@staticmethod
def _format_json_str(jstr):
    """执行当前函数对应的业务逻辑。"""
    result = []
    inside_quotes = False
    last_char = " "
    for char in jstr:
        if last_char != "\\" and char == '"':
            inside_quotes = not inside_quotes
        last_char = char
        if not inside_quotes and char == "\n":
            continue
        if inside_quotes and char == "\n":
            char = "\\n"
        if inside_quotes and char == "\t":
            char = "\\t"
        result.append(char)
    return "".join(result)


def compare_json_properties(json1, json2):
    """执行当前函数对应的业务逻辑。"""
    obj1 = json.loads(json1)
    obj2 = json.loads(json2)

    # 检查两个对象的键集合是否相同
    if set(obj1.keys()) == set(obj2.keys()):
        return True

    return False


def compare_json_properties_ex(json1, json2):
    """执行当前函数对应的业务逻辑。"""
    # 检查两个对象的键集合是否相同
    if set(json1.keys()) == set(json2.keys()):
        return True

    return False
