"""模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。"""

import json
import re
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union

_DEFAULT_THINK_START_TOKEN = "<think>"
_DEFAULT_THINK_END_TOKEN = "</think>"


class StreamingEvent(NamedTuple):
    """当前类的职责定义。"""

    type: str
    """字段说明。"""
    content: str  # 代码说明。


class ParsedChatMessage:
    """接口数据结构定义。"""

    def __init__(self):
        self.role: str = "assistant"
        self.content: str = ""
        self.reasoning_content: str = ""
        self.tool_calls: List[Dict[str, Any]] = []
        # 代码说明。
        self.streaming_state: Dict[str, Any] = {
            "in_reasoning": False,
            "reasoning_pattern": None,
            "in_tool_call": False,
            "tool_call_pattern": None,
            # 代码说明。
        }


def string_strip(s: str) -> str:
    """执行当前函数对应的业务逻辑。"""
    return s.strip() if s else ""


def parse_json_tool_calls(
    tool_calls_text: str,
    default_name: Optional[str] = None,
    function_regex: Optional[re.Pattern] = None,
    close_regex: Optional[re.Pattern] = None,
) -> List[Dict[str, Any]]:
    """执行调用逻辑。"""
    tool_calls = []

    # 默认配置说明。
    if function_regex is None:
        function_regex = re.compile(
            r'function\s*(?:name)?\s*[:=]?\s*["\']?([^"\'\n]+)["\']?\s*\n```(?:json)?\s*\n'  # noqa
        )

    if close_regex is None:
        close_regex = re.compile(r"```\s*")

    current_pos = 0
    remaining_text = tool_calls_text

    while current_pos < len(tool_calls_text):
        # 代码说明。
        function_match = function_regex.search(remaining_text)
        if not function_match:
            break

        function_name = function_match.group(1).strip()
        start_json = function_match.end()

        # 代码说明。
        close_match = close_regex.search(remaining_text[start_json:])
        if not close_match:
            break

        json_content = remaining_text[start_json : start_json + close_match.start()]

        try:
            args = json.loads(json_content)
            tool_call = {"name": function_name or default_name or "", "arguments": args}
            tool_calls.append(tool_call)
        except json.JSONDecodeError:
            # 代码说明。
            tool_call = {
                "name": function_name or default_name or "",
                "arguments": json_content.strip(),
            }
            tool_calls.append(tool_call)

        # 执行检索。
        current_pos += start_json + close_match.end()
        remaining_text = tool_calls_text[current_pos:]

    return tool_calls


def process_streaming_chunk(
    chunk: str,
    msg: ParsedChatMessage,
    reasoning_patterns: List[Dict[str, str]],
    tool_call_patterns: List[Dict[str, str]],
    extract_tool_calls: bool = True,
) -> List[StreamingEvent]:
    """生成模型输出。"""
    state = msg.streaming_state
    events = []
    remaining_chunk = chunk

    while remaining_chunk:
        # 代码说明。
        if state["in_reasoning"]:
            end_marker = state["reasoning_pattern"]["end"]
            if end_marker in remaining_chunk:
                end_idx = remaining_chunk.find(end_marker)
                # 代码说明。
                # 历史调试代码，当前不启用。
                reasoning_part = remaining_chunk[:end_idx]
                events.append(
                    StreamingEvent(type="reasoning_content", content=reasoning_part)
                )
                # 代码说明。
                msg.reasoning_content += reasoning_part

                # 代码说明。
                events.append(StreamingEvent(type="reasoning_end", content=""))

                # 设置对应数据。
                state["in_reasoning"] = False
                state["reasoning_pattern"] = None

                # 代码说明。
                remaining_chunk = remaining_chunk[end_idx + len(end_marker) :]
            else:
                # 代码说明。
                events.append(
                    StreamingEvent(type="reasoning_content", content=remaining_chunk)
                )
                # 代码说明。
                msg.reasoning_content += remaining_chunk
                remaining_chunk = ""
            continue

        # 代码说明。
        if state["in_tool_call"] and extract_tool_calls:
            end_marker = state["tool_call_pattern"]["end"]
            if end_marker in remaining_chunk:
                end_idx = remaining_chunk.find(end_marker)
                # 代码说明。
                if end_idx > 0:
                    tool_call_part = remaining_chunk[:end_idx]
                    events.append(
                        StreamingEvent(type="tool_call_content", content=tool_call_part)
                    )

                # 代码说明。
                tool_call_text = (
                    state.get("tool_call_text", "") + remaining_chunk[:end_idx]
                )

                # 代码说明。
                function_regex_patterns = [
                    re.compile(
                        r"<｜tool▁call▁begin｜>function<｜tool▁sep｜>([^\n]+)\n```json\n"
                    ),
                    re.compile(r"function\s*:\s*([^\n]+)\n```json\n"),
                    re.compile(r'function\s*name\s*=\s*"([^"]+)"\n```json\n'),
                ]

                close_regex_patterns = [
                    re.compile(r"```\s*<｜tool▁call▁end｜>"),
                    re.compile(r"```\s*"),
                ]

                # 代码说明。
                for func_regex in function_regex_patterns:
                    for close_regex in close_regex_patterns:
                        tool_calls = parse_json_tool_calls(
                            tool_call_text, None, func_regex, close_regex
                        )
                        if tool_calls:
                            msg.tool_calls.extend(tool_calls)
                            break
                    if msg.tool_calls:
                        break

                # 代码说明。
                events.append(StreamingEvent(type="tool_call_end", content=""))

                # 设置对应数据。
                state["in_tool_call"] = False
                state["tool_call_pattern"] = None
                state.pop("tool_call_text", None)

                # 代码说明。
                remaining_chunk = remaining_chunk[end_idx + len(end_marker) :]
            else:
                # 代码说明。
                events.append(
                    StreamingEvent(type="tool_call_content", content=remaining_chunk)
                )
                # 代码说明。
                state["tool_call_text"] = (
                    state.get("tool_call_text", "") + remaining_chunk
                )
                remaining_chunk = ""
            continue

        # 检查条件是否满足。
        # 代码说明。
        found_end_marker = False
        for pattern in reasoning_patterns:
            start_marker = pattern["start"]
            end_marker = pattern["end"]
            if end_marker in remaining_chunk and not state["in_reasoning"]:
                end_idx = remaining_chunk.find(end_marker)
                start_idx = 0
                if start_marker in remaining_chunk:
                    start_idx = remaining_chunk.find(start_marker) + len(start_marker)

                # 代码说明。
                # 代码说明。
                # 历史调试代码，当前不启用。
                reasoning_part = remaining_chunk[start_idx:end_idx]
                # 代码说明。
                reasoning_part = msg.content + reasoning_part
                msg.content = ""

                # 代码说明。
                events.append(StreamingEvent(type="reasoning_start", content=""))

                # 代码说明。
                events.append(
                    StreamingEvent(type="reasoning_content", content=reasoning_part)
                )

                # 添加对应数据。
                msg.reasoning_content += reasoning_part

                # 代码说明。
                events.append(StreamingEvent(type="reasoning_end", content=""))
                # 代码说明。
                remaining_chunk = remaining_chunk[end_idx + len(end_marker) :]
                found_end_marker = True
                state["reasoning_pattern"] = None
                break

        # 代码说明。
        if found_end_marker:
            continue

        # 检查条件是否满足。
        reasoning_start_found = False
        for pattern in reasoning_patterns:
            start_marker = pattern["start"]
            if start_marker in remaining_chunk:
                start_idx = remaining_chunk.find(start_marker)

                # 代码说明。
                # 历史调试代码，当前不启用。
                content_part = remaining_chunk[:start_idx]
                events.append(StreamingEvent(type="content", content=content_part))
                msg.content += content_part

                # 代码说明。
                events.append(StreamingEvent(type="reasoning_start", content=""))

                # 设置对应数据。
                state["in_reasoning"] = True
                state["reasoning_pattern"] = pattern

                # 代码说明。
                remaining_chunk = remaining_chunk[start_idx + len(start_marker) :]
                reasoning_start_found = True
                break

        if reasoning_start_found:
            continue

        # 检查条件是否满足。
        tool_call_start_found = False
        if extract_tool_calls:
            for pattern in tool_call_patterns:
                start_marker = pattern["start"]
                if start_marker in remaining_chunk:
                    start_idx = remaining_chunk.find(start_marker)

                    # 代码说明。
                    # 历史调试代码，当前不启用。
                    content_part = remaining_chunk[:start_idx]
                    events.append(StreamingEvent(type="content", content=content_part))
                    msg.content += content_part

                    # 代码说明。
                    events.append(StreamingEvent(type="tool_call_start", content=""))

                    # 设置对应数据。
                    state["in_tool_call"] = True
                    state["tool_call_pattern"] = pattern
                    state["tool_call_text"] = ""

                    # 代码说明。
                    remaining_chunk = remaining_chunk[start_idx + len(start_marker) :]
                    tool_call_start_found = True
                    break

        if tool_call_start_found:
            continue

        # 代码说明。
        events.append(StreamingEvent(type="content", content=remaining_chunk))
        msg.content += remaining_chunk
        remaining_chunk = ""

    return events


def parse_chat_message(
    input_text: str,
    extract_reasoning: bool = True,
    extract_tool_calls: bool = False,
    is_streaming: bool = False,
    reasoning_patterns: Optional[List[Dict[str, str]]] = None,
    tool_call_patterns: Optional[List[Dict[str, str]]] = None,
    streaming_state: Optional[ParsedChatMessage] = None,
) -> Union[ParsedChatMessage, Tuple[ParsedChatMessage, List[StreamingEvent]]]:
    """解析输入并返回标准结果。"""
    # 默认配置说明。
    if reasoning_patterns is None:
        reasoning_patterns = [
            {"start": _DEFAULT_THINK_START_TOKEN, "end": _DEFAULT_THINK_END_TOKEN},
            {"start": "<reasoning>", "end": "</reasoning>"},
            {"start": "<思考>", "end": "</思考>"},
        ]

    # 默认配置说明。
    if tool_call_patterns is None:
        tool_call_patterns = [
            {"start": "<｜tool▁calls▁begin｜>", "end": "<｜tool▁calls▁end｜>"},
            {"start": "<｜tool_calls_begin｜>", "end": "<｜tool_calls_end｜>"},
            {"start": "<｜tool calls begin｜>", "end": "<｜tool calls end｜>"},
            {"start": "<｜tool\\_calls\\_begin｜>", "end": "<｜tool\\_calls\\_end｜>"},
            {"start": "<tool_calls>", "end": "</tool_calls>"},
            {"start": "<tools>", "end": "</tools>"},
        ]

    # 代码说明。
    if is_streaming:
        # 创建相关资源。
        msg = streaming_state or ParsedChatMessage()

        # 获取对应数据。
        events = process_streaming_chunk(
            input_text, msg, reasoning_patterns, tool_call_patterns, extract_tool_calls
        )

        return msg, events

    # 非流式场景配置。
    msg = ParsedChatMessage()

    # 代码说明。
    reasoning_content = ""
    content = input_text

    # 检查条件是否满足。
    for pattern in reasoning_patterns:
        start_marker = pattern["start"]
        end_marker = pattern["end"]

        if start_marker in content and end_marker in content:
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker, start_idx + len(start_marker))

            if start_idx >= 0 and end_idx >= 0:
                reasoning_text = content[start_idx + len(start_marker) : end_idx]
                reasoning_content = string_strip(reasoning_text)

                # 代码说明。
                if extract_reasoning:
                    content = content[:start_idx] + content[end_idx + len(end_marker) :]
                break

    # 检查条件是否满足。
    # 代码说明。
    # 代码说明。
    if not reasoning_content:
        for pattern in reasoning_patterns:
            start_marker = pattern["start"]
            end_marker = pattern["end"]

            if end_marker in content:
                # 检查条件是否满足。
                # 历史调试代码，当前不启用。
                end_idx = content.find(end_marker)
                start_marker = pattern["start"]
                start_idx = content.find(start_marker)

                # 代码说明。
                if start_idx == -1 or end_idx < start_idx:
                    # 代码说明。
                    # 代码说明。
                    reasoning_content = string_strip(content[:end_idx])

                    # 代码说明。
                    if extract_reasoning:
                        content = content[end_idx + len(end_marker) :]
                    break
            elif start_marker in content:
                # 代码说明。
                # 代码说明。
                start_idx = content.find(start_marker)
                reasoning_content = string_strip(
                    content[start_idx + len(start_marker) :]
                )

                # 代码说明。
                if extract_reasoning:
                    content = ""
                break

    # 代码说明。
    tool_calls_text = ""

    if extract_tool_calls:
        for pattern in tool_call_patterns:
            start_marker = pattern["start"]
            end_marker = pattern["end"]

            if start_marker in content and end_marker in content:
                start_idx = content.find(start_marker)
                end_idx = content.find(end_marker, start_idx + len(start_marker))

                if start_idx >= 0 and end_idx >= 0:
                    tool_calls_text = content[start_idx + len(start_marker) : end_idx]

                    # 代码说明。
                    content = content[:start_idx] + content[end_idx + len(end_marker) :]
                    break

        # 代码说明。
        function_regex_patterns = [
            re.compile(
                r"<｜tool▁call▁begin｜>function<｜tool▁sep｜>([^\n]+)\n```json\n"
            ),
            re.compile(r"function\s*:\s*([^\n]+)\n```json\n"),
            re.compile(r'function\s*name\s*=\s*"([^"]+)"\n```json\n'),
        ]

        close_regex_patterns = [
            re.compile(r"```\s*<｜tool▁call▁end｜>"),
            re.compile(r"```\s*"),
        ]

        if tool_calls_text:
            for func_regex in function_regex_patterns:
                for close_regex in close_regex_patterns:
                    tool_calls = parse_json_tool_calls(
                        tool_calls_text, None, func_regex, close_regex
                    )
                    if tool_calls:
                        msg.tool_calls = tool_calls
                        break
                if msg.tool_calls:
                    break

    # 设置对应数据。
    msg.content = string_strip(content)
    if extract_reasoning:
        msg.reasoning_content = reasoning_content

    return msg
