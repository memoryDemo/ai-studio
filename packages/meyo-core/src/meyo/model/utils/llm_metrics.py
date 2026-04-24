"""模型服务工具函数，支撑词元、流式输出、媒体处理和请求解析等通用逻辑。"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LLMPerformanceMetrics:
    """模型能力抽象或实现。"""

    # 代码说明。
    input_token_count: int = 0
    total_tokens_generated: int = 0
    prev_tokens_count: int = 0

    # 代码说明。
    start_time_ns: int = field(default_factory=time.time_ns)
    prefill_start_time_ns: Optional[int] = None
    prefill_end_time_ns: Optional[int] = None
    prefill_time_ns: Optional[int] = None
    decode_start_time_ns: Optional[int] = None
    total_time_ns: Optional[int] = None

    # 代码说明。
    token_timestamps_ns: List[int] = field(default_factory=list)
    decode_times_ns: List[int] = field(default_factory=list)

    # 代码说明。
    prefill_tokens_per_second: Optional[float] = None
    decode_tokens_per_second: Optional[float] = None
    end_to_end_tokens_per_second: Optional[float] = None

    # 添加对应数据。
    avg_decode_time: Optional[float] = None

    def to_dict(self) -> Dict[str, any]:
        """转换为目标数据结构。"""
        metrics = {
            "input_token_count": self.input_token_count,
            "total_tokens_generated": self.total_tokens_generated,
        }

        # 添加对应数据。
        if self.prefill_time_ns is not None:
            metrics["prefill_time"] = self.prefill_time_ns / 1e9
            metrics["prefill_tokens_per_second"] = self.prefill_tokens_per_second or 0

        if self.total_time_ns is not None:
            metrics["total_time"] = self.total_time_ns / 1e9

        if self.decode_times_ns:
            metrics["avg_decode_time"] = self.avg_decode_time
            metrics["decode_tokens_per_second"] = self.decode_tokens_per_second or 0

        # 添加对应数据。
        metrics["end_to_end_tokens_per_second"] = self.end_to_end_tokens_per_second or 0

        return metrics


class LLMPerformanceMonitor:
    """模型能力抽象或实现。"""

    def __init__(self, input_token_count: int = 0):
        # 代码说明。
        self.metrics = LLMPerformanceMetrics(input_token_count=input_token_count)

        # 代码说明。
        self.prefill_started: bool = False
        self.first_token_received: bool = False

    def start_prefill(self) -> int:
        """初始化并启动相关能力。"""
        timestamp = time.time_ns()
        self.metrics.prefill_start_time_ns = timestamp
        self.prefill_started = True
        return timestamp

    def on_tokens_received(self, current_token_count: int) -> Dict[str, any]:
        """执行当前函数对应的业务逻辑。"""
        current_time_ns = time.time_ns()

        # 代码说明。
        new_tokens = current_token_count - self.metrics.prev_tokens_count

        # 代码说明。
        if self.prefill_started and not self.first_token_received and new_tokens > 0:
            # 代码说明。
            self.metrics.prefill_end_time_ns = current_time_ns
            self.metrics.prefill_time_ns = (
                self.metrics.prefill_end_time_ns - self.metrics.prefill_start_time_ns
            )

            # 转换数据格式。
            prefill_time_sec = self.metrics.prefill_time_ns / 1e9

            # 代码说明。
            if self.metrics.input_token_count > 0 and prefill_time_sec > 0:
                self.metrics.prefill_tokens_per_second = (
                    self.metrics.input_token_count / prefill_time_sec
                )
                logger.info(
                    f"Prefill speed: {self.metrics.prefill_tokens_per_second:.2f} "
                    f"tokens/s for {self.metrics.input_token_count} tokens"
                )

            # 代码说明。
            self.metrics.decode_start_time_ns = current_time_ns
            self.first_token_received = True

        # 代码说明。
        if self.first_token_received and new_tokens > 0:
            # 添加对应数据。
            if len(self.metrics.token_timestamps_ns) > 0:
                last_timestamp_ns = self.metrics.token_timestamps_ns[-1]
                token_decode_time_ns = current_time_ns - last_timestamp_ns

                # 代码说明。
                time_per_token = token_decode_time_ns / new_tokens
                for _ in range(new_tokens):
                    self.metrics.decode_times_ns.append(time_per_token)

        # 代码说明。
        self.metrics.token_timestamps_ns.append(current_time_ns)
        self.metrics.total_tokens_generated += new_tokens
        self.metrics.prev_tokens_count = current_token_count

        # 代码说明。
        self._update_metrics(current_time_ns)

        return self.get_metrics_dict()

    def _update_metrics(self, current_time_ns: Optional[int] = None) -> None:
        """执行当前函数对应的业务逻辑。"""
        if current_time_ns is None:
            current_time_ns = time.time_ns()

        # 代码说明。
        self.metrics.total_time_ns = current_time_ns - self.metrics.start_time_ns

        # 代码说明。
        if self.metrics.decode_times_ns:
            # 转换数据格式。
            decode_times_sec = [t / 1e9 for t in self.metrics.decode_times_ns]
            self.metrics.avg_decode_time = sum(decode_times_sec) / len(decode_times_sec)
            self.metrics.decode_tokens_per_second = 1.0 / self.metrics.avg_decode_time

        # 代码说明。
        total_time_sec = self.metrics.total_time_ns / 1e9
        if total_time_sec > 0:
            total_tokens = (
                self.metrics.input_token_count + self.metrics.total_tokens_generated
            )
            self.metrics.end_to_end_tokens_per_second = total_tokens / total_time_sec

    def end_generation(self) -> Dict[str, any]:
        """执行当前函数对应的业务逻辑。"""
        current_time_ns = time.time_ns()
        self._update_metrics(current_time_ns)

        # 代码说明。
        total_time_sec = self.metrics.total_time_ns / 1e9
        logger.info(f"Generation complete. Total time: {total_time_sec:.6f}s")

        if self.metrics.prefill_tokens_per_second:
            logger.info(
                f"Final prefill speed: {self.metrics.prefill_tokens_per_second:.2f} "
                "tokens/s"
            )

        if self.metrics.decode_tokens_per_second:
            logger.info(
                f"Final decode speed: {self.metrics.decode_tokens_per_second:.2f} "
                "tokens/s"
            )

        if self.metrics.end_to_end_tokens_per_second:
            logger.info(
                "End-to-end throughput: "
                f"{self.metrics.end_to_end_tokens_per_second:.2f} tokens/s"
            )

        return self.get_metrics_dict()

    def get_metrics_dict(self) -> Dict[str, any]:
        """获取对应数据。"""
        return self.metrics.to_dict()
