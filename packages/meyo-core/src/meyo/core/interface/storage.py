"""存储接口定义，为缓存、向量库、图存储和知识库提供统一抽象。"""


from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, cast

from meyo.core.interface.serialization import Serializable, Serializer
from meyo.util.annotations import PublicAPI
from meyo.util.i18n_utils import _
from meyo.util.pagination_utils import PaginationResult
from meyo.util.serialization.json_serialization import JsonSerializer

from meyo.model.resource import Parameter, ResourceCategory, register_resource


@PublicAPI(stability="beta")
class ResourceIdentifier(Serializable, ABC):
    """当前类的职责定义。"""

    @property
    @abstractmethod
    def str_identifier(self) -> str:
        """执行当前函数对应的业务逻辑。"""

    def __hash__(self) -> int:
        """执行当前函数对应的业务逻辑。"""
        return hash(self.str_identifier)

    def __eq__(self, other: Any) -> bool:
        """执行当前函数对应的业务逻辑。"""
        if not isinstance(other, ResourceIdentifier):
            return False
        return self.str_identifier == other.str_identifier


@PublicAPI(stability="beta")
class StorageItem(Serializable, ABC):
    """存储能力实现。"""

    @property
    @abstractmethod
    def identifier(self) -> ResourceIdentifier:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def merge(self, other: "StorageItem") -> None:
        """执行当前函数对应的业务逻辑。"""


ID = TypeVar("ID", bound=ResourceIdentifier)
T = TypeVar("T", bound=StorageItem)
TDataRepresentation = TypeVar("TDataRepresentation")


class StorageItemAdapter(Generic[T, TDataRepresentation]):
    """存储能力实现。"""

    @abstractmethod
    def to_storage_format(self, item: T) -> TDataRepresentation:
        """转换为目标数据结构。"""

    @abstractmethod
    def from_storage_format(self, data: TDataRepresentation) -> T:
        """根据输入参数创建对象。"""

    @abstractmethod
    def get_query_for_identifier(
        self,
        storage_format: Type[TDataRepresentation],
        resource_id: ResourceIdentifier,
        **kwargs,
    ) -> Any:
        """获取对应数据。"""


class DefaultStorageItemAdapter(StorageItemAdapter[T, T]):
    """存储能力实现。"""

    def to_storage_format(self, item: T) -> T:
        """转换为目标数据结构。"""
        return item

    def from_storage_format(self, data: T) -> T:
        """根据输入参数创建对象。"""
        return data

    def get_query_for_identifier(
        self, storage_format: Type[T], resource_id: ID, **kwargs
    ) -> bool:
        """获取对应数据。"""
        return True


@PublicAPI(stability="beta")
class StorageError(Exception):
    """异常类型定义。"""

    def __init__(self, message: str):
        """初始化实例。"""
        super().__init__(message)


@PublicAPI(stability="beta")
class QuerySpec:
    """当前类的职责定义。"""

    def __init__(
        self, conditions: Dict[str, Any], limit: Optional[int] = None, offset: int = 0
    ) -> None:
        """初始化实例。"""
        self.conditions = conditions
        self.limit = limit
        self.offset = offset


@PublicAPI(stability="beta")
class StorageInterface(Generic[T, TDataRepresentation], ABC):
    """存储能力实现。"""

    def __init__(
        self,
        serializer: Optional[Serializer] = None,
        adapter: Optional[StorageItemAdapter[T, TDataRepresentation]] = None,
    ):
        """初始化实例。"""
        self._serializer = serializer or JsonSerializer()
        self._storage_item_adapter = adapter or DefaultStorageItemAdapter()

    @property
    def serializer(self) -> Serializer:
        """执行当前函数对应的业务逻辑。"""
        return self._serializer

    @property
    def adapter(self) -> StorageItemAdapter[T, TDataRepresentation]:
        """执行当前函数对应的业务逻辑。"""
        return self._storage_item_adapter

    @abstractmethod
    def save(self, data: T) -> None:
        """保存数据或资源。"""

    @abstractmethod
    def update(self, data: T) -> None:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def save_or_update(self, data: T) -> None:
        """保存数据或资源。"""

    def save_list(self, data: List[T]) -> None:
        """保存数据或资源。"""
        for d in data:
            self.save(d)

    def save_or_update_list(self, data: List[T]) -> None:
        """保存数据或资源。"""
        for d in data:
            self.save_or_update(d)

    @abstractmethod
    def load(self, resource_id: ID, cls: Type[T]) -> Optional[T]:
        """加载数据或资源。"""

    def load_list(self, resource_id: List[ID], cls: Type[T]) -> List[T]:
        """加载数据或资源。"""
        result = []
        for r in resource_id:
            item = self.load(r, cls)
            if item is not None:
                result.append(item)
        return result

    @abstractmethod
    def delete(self, resource_id: ID) -> None:
        """删除对应数据。"""

    def delete_list(self, resource_id: List[ID]) -> None:
        """删除对应数据。"""
        for r in resource_id:
            self.delete(r)

    @abstractmethod
    def query(self, spec: QuerySpec, cls: Type[T]) -> List[T]:
        """执行查询并返回结果。"""

    @abstractmethod
    def count(self, spec: QuerySpec, cls: Type[T]) -> int:
        """执行当前函数对应的业务逻辑。"""

    def paginate_query(
        self, page: int, page_size: int, cls: Type[T], spec: Optional[QuerySpec] = None
    ) -> PaginationResult[T]:
        """执行查询并返回结果。"""
        if spec is None:
            spec = QuerySpec(conditions={})
        spec.limit = page_size
        spec.offset = (page - 1) * page_size
        items = self.query(spec, cls)
        total = self.count(spec, cls)
        return PaginationResult(
            items=items,
            total_count=total,
            total_pages=(total + page_size - 1) // page_size,
            page=page,
            page_size=page_size,
        )


@register_resource(
    label=_("Memory Storage"),
    name="in_memory_storage",
    category=ResourceCategory.STORAGE,
    description=_("Save your data in memory."),
    parameters=[
        Parameter.build_from(
            _("Serializer"),
            "serializer",
            Serializer,
            optional=True,
            default=None,
            description=_(
                "The serializer for serializing the data. If not set, the "
                "default JSON serializer will be used."
            ),
        )
    ],
)
@PublicAPI(stability="alpha")
class InMemoryStorage(StorageInterface[T, T]):
    """存储能力实现。"""

    def __init__(
        self,
        serializer: Optional[Serializer] = None,
    ):
        """初始化实例。"""
        super().__init__(serializer)
        # 代码说明。
        self._data: Dict[str, bytes] = {}

    def save(self, data: T) -> None:
        """保存数据或资源。"""
        if not data:
            raise StorageError("Data cannot be None")
        if not data._serializer:
            data.set_serializer(self.serializer)

        if data.identifier.str_identifier in self._data:
            raise StorageError(
                f"Data with identifier {data.identifier.str_identifier} already exists"
            )
        self._data[data.identifier.str_identifier] = data.serialize()

    def update(self, data: T) -> None:
        """执行当前函数对应的业务逻辑。"""
        if not data:
            raise StorageError("Data cannot be None")
        if not data._serializer:
            data.set_serializer(self.serializer)
        self._data[data.identifier.str_identifier] = data.serialize()

    def save_or_update(self, data: T) -> None:
        """保存数据或资源。"""
        self.update(data)

    def load(self, resource_id: ID, cls: Type[T]) -> Optional[T]:
        """加载数据或资源。"""
        serialized_data = self._data.get(resource_id.str_identifier)
        if serialized_data is None:
            return None
        return cast(T, self.serializer.deserialize(serialized_data, cls))

    def delete(self, resource_id: ID) -> None:
        """删除对应数据。"""
        if resource_id.str_identifier in self._data:
            del self._data[resource_id.str_identifier]

    def query(self, spec: QuerySpec, cls: Type[T]) -> List[T]:
        """执行查询并返回结果。"""
        result = []
        for serialized_data in self._data.values():
            data = cast(T, self._serializer.deserialize(serialized_data, cls))
            if all(
                getattr(data, key) == value for key, value in spec.conditions.items()
            ):
                result.append(data)

        # 设置对应数据。
        if spec.limit is not None:
            result = result[spec.offset : spec.offset + spec.limit]
        else:
            result = result[spec.offset :]
        return result

    def count(self, spec: QuerySpec, cls: Type[T]) -> int:
        """执行当前函数对应的业务逻辑。"""
        count = 0
        for serialized_data in self._data.values():
            data = self._serializer.deserialize(serialized_data, cls)
            if all(
                getattr(data, key) == value for key, value in spec.conditions.items()
            ):
                count += 1
        return count
