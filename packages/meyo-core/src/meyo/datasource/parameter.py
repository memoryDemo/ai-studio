"""数据源参数定义，负责描述外部连接器初始化所需的配置项。
"""

import os
from abc import abstractmethod
from dataclasses import asdict, dataclass, fields
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

from meyo.util.configure import RegisterParameters
from meyo.util.parameter_utils import BaseParameters

if TYPE_CHECKING:
    from meyo.datasource.base import BaseConnector


@dataclass
class BaseDatasourceParameters(BaseParameters, RegisterParameters):
    """配置参数定义。"""

    __cfg_type__ = "datasource"

    def engine_args(self) -> Optional[Dict[str, Any]]:
        """执行当前函数对应的业务逻辑。"""
        return None

    def create_connector(self) -> "BaseConnector":
        """创建对象实例。"""
        raise NotImplementedError("Current connector does not support create_connector")

    @classmethod
    def from_persisted_state(
        cls: Type["BaseDatasourceParameters"], state: Dict[str, Any]
    ) -> "BaseDatasourceParameters":
        """根据输入参数创建对象。"""
        new_state = cls._parse_persisted_state(state)
        valid_state = {}
        for fd in fields(cls):
            if fd.name in new_state:
                valid_state[fd.name] = new_state[fd.name]
        return cls(**valid_state)

    @classmethod
    def _parse_persisted_state(cls, state: Dict[str, Any]) -> Dict[str, Any]:
        """执行当前函数对应的业务逻辑。"""
        mapping = cls._persisted_state_mapping()
        unmapping = {v: k for k, v in mapping.items()}
        new_state = {}
        for k, v in state.items():
            if k in unmapping:
                new_state[unmapping[k]] = v
            elif k == "ext_config" and isinstance(v, dict) and v:
                new_state.update(v)
        return new_state

    def persisted_state(self) -> Dict[str, Any]:
        """执行当前函数对应的业务逻辑。"""
        db_type = getattr(self, "__type__", "unknown")
        state = asdict(self)
        new_state = {"db_type": db_type}
        mapping = self._persisted_state_mapping()
        ext_config = {}
        for k, v in state.items():
            if k in mapping:
                new_state[mapping[k]] = v
            else:
                ext_config[k] = v
        if ext_config:
            new_state["ext_config"] = ext_config
        db_name = new_state.get("db_name")
        db_path = new_state.get("db_path")
        if not db_name and db_path:
            # 代码说明。
            # 代码说明。
            # 代码说明。
            db_name = os.path.basename(db_path).split(".")[0]

            new_state["db_name"] = f"{db_type}_{db_name}"
        return new_state

    @classmethod
    def _persisted_state_mapping(cls) -> Dict[str, str]:
        """执行当前函数对应的业务逻辑。"""
        return {
            "host": "db_host",
            "port": "db_port",
            "user": "db_user",
            "password": "db_pwd",
            "database": "db_name",
            "path": "db_path",
        }

    @abstractmethod
    def db_url(self, ssl: bool = False, charset: Optional[str] = None) -> str:
        """执行当前函数对应的业务逻辑。"""
