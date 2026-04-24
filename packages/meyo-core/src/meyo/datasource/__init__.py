"""包入口，集中导出当前目录下的模型服务相关能力。"""


from typing import Any

from .base import BaseConnector  # noqa: F401


def __getattr__(name: str) -> Any:
    if name == "RDBMSConnector":
        from .rdbms.base import RDBMSConnector  # noqa: F401

        return RDBMSConnector
    else:
        raise AttributeError(f"Could not find: {name} in datasource")


__ALL__ = ["BaseConnector", "RDBMSConnector"]
