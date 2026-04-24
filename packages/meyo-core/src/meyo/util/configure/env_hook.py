"""配置加载和配置格式化工具，负责解析开发配置并支持环境变量注入。"""


import os
from typing import Any, Dict, List, Optional


class EnvVarSetHook:
    """当前类的职责定义。"""

    def __init__(self, env_vars: Optional[List[Dict[str, str]]] = None):
        """初始化实例。"""
        env_kv = {}
        for env_var in env_vars or []:
            if not isinstance(env_var, dict):
                raise ValueError(
                    f"Expected env_vars to be a list of dictionaries, got {env_var}"
                )
            if not env_var:
                raise ValueError("Expected env_var to be a non-empty dictionary")
            env_key = env_var.get("key")
            env_value = env_var.get("value")
            env_kv[env_key] = env_value
        self.env_vars = env_kv
        self._original_env = {}

    def __call__(self, config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """执行调用逻辑。"""
        # 代码说明。
        self._original_env = {
            key: os.environ.get(key) for key in self.env_vars if key in os.environ
        }

        # 设置对应数据。
        for key, value in self.env_vars.items():
            os.environ[key] = str(value)

        return config
