"""模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。"""

import logging

from transformers import TextIteratorStreamer

from .llm_metrics import LLMPerformanceMonitor

logger = logging.getLogger(__name__)


class PerformanceMonitoringStreamer(TextIteratorStreamer):
    """当前类的职责定义。"""

    def __init__(
        self,
        tokenizer,
        skip_prompt=False,
        timeout=None,
        input_token_count=0,
        **decode_kwargs,
    ):
        super().__init__(
            tokenizer, skip_prompt=skip_prompt, timeout=timeout, **decode_kwargs
        )

        # 代码说明。
        self.perf_monitor = LLMPerformanceMonitor(input_token_count=input_token_count)

        # 添加对应数据。
        self.is_prompt_token = True  # 代码说明。

    def start_prefill(self):
        """初始化并启动相关能力。"""
        self.perf_monitor.start_prefill()

    def put(self, value):
        """执行当前函数对应的业务逻辑。"""
        # 代码说明。
        if self.skip_prompt and self.is_prompt_token:
            self.is_prompt_token = False  # 代码说明。
            logger.debug("Skipping prompt tokens for performance measurement")
            super().put(value)  # 代码说明。
            return

        # 代码说明。
        token_count = len(value.tolist())
        total_token_count = self.perf_monitor.metrics.prev_tokens_count + token_count

        # 代码说明。
        self.perf_monitor.on_tokens_received(total_token_count)

        # 代码说明。
        super().put(value)

    def end(self):
        """执行当前函数对应的业务逻辑。"""
        # 代码说明。
        self.perf_monitor.end_generation()

        # 代码说明。
        super().end()

    def get_performance_metrics(self):
        """获取对应数据。"""
        return self.perf_monitor.get_metrics_dict()
