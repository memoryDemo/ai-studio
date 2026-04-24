"""向量存储基础抽象，为向量检索、过滤和相似度查询提供统一接口。"""


from enum import Enum
from typing import List, Union

from meyo._private.pydantic import BaseModel, Field


class FilterOperator(str, Enum):
    """枚举类型定义。"""

    EQ = "=="
    GT = ">"
    LT = "<"
    NE = "!="
    GTE = ">="
    LTE = "<="
    IN = "in"
    NIN = "nin"
    EXISTS = "exists"


class FilterCondition(str, Enum):
    """枚举类型定义。"""

    AND = "and"
    OR = "or"


class MetadataFilter(BaseModel):
    """当前类的职责定义。"""

    key: str = Field(
        ...,
        description="The key of metadata to filter.",
    )
    operator: FilterOperator = Field(
        default=FilterOperator.EQ,
        description="The operator of metadata filter.",
    )
    value: Union[str, int, float, List[str], List[int], List[float]] = Field(
        ...,
        description="The value of metadata to filter.",
    )


class MetadataFilters(BaseModel):
    """当前类的职责定义。"""

    condition: FilterCondition = Field(
        default=FilterCondition.AND,
        description="The condition of metadata filters.",
    )
    filters: List[MetadataFilter] = Field(
        ...,
        description="The metadata filters.",
    )
