"""图存储基础抽象，为知识图谱和图数据库扩展提供统一接口。"""


import itertools
import json
import logging
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class GraphElemType(Enum):
    """枚举类型定义。"""

    DOCUMENT = "document"
    CHUNK = "chunk"
    ENTITY = "entity"  # 默认配置说明。
    RELATION = "relation"  # 默认配置说明。
    INCLUDE = "include"
    NEXT = "next"

    DOCUMENT_INCLUDE_CHUNK = "document_include_chunk"
    CHUNK_INCLUDE_CHUNK = "chunk_include_chunk"
    CHUNK_INCLUDE_ENTITY = "chunk_include_entity"
    CHUNK_NEXT_CHUNK = "chunk_next_chunk"

    def is_vertex(self) -> bool:
        """校验条件并返回判断结果。"""
        return self in [
            GraphElemType.DOCUMENT,
            GraphElemType.CHUNK,
            GraphElemType.ENTITY,
        ]

    def is_edge(self) -> bool:
        """校验条件并返回判断结果。"""
        return self in [
            GraphElemType.RELATION,
            GraphElemType.INCLUDE,
            GraphElemType.NEXT,
            GraphElemType.DOCUMENT_INCLUDE_CHUNK,
            GraphElemType.CHUNK_INCLUDE_CHUNK,
            GraphElemType.CHUNK_INCLUDE_ENTITY,
            GraphElemType.CHUNK_NEXT_CHUNK,
        ]


class Direction(Enum):
    """枚举类型定义。"""

    OUT = 0
    IN = 1
    BOTH = 2


class Elem(ABC):
    """当前类的职责定义。"""

    def __init__(self, name: Optional[str] = None):
        """初始化实例。"""
        self._name = name
        self._props: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self._name or ""

    @property
    def props(self) -> Dict[str, Any]:
        """执行当前函数对应的业务逻辑。"""
        return self._props

    def set_prop(self, key: str, value: Any):
        """设置对应数据。"""
        self._props[key] = value  # 代码说明。

    def get_prop(self, key: str):
        """获取对应数据。"""
        return self._props.get(key)

    def del_prop(self, key: str):
        """执行当前函数对应的业务逻辑。"""
        self._props.pop(key, None)

    def has_props(self, **props):
        """校验条件并返回判断结果。"""
        return all(self._props.get(k) == v for k, v in props.items())

    @abstractmethod
    def format(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        if len(self._props) == 1:
            return str(next(iter(self._props.values())))

        formatted_props = [
            f"{k}:{json.dumps(v, ensure_ascii=False)}" for k, v in self._props.items()
        ]
        return f"{{{';'.join(formatted_props)}}}"


class Vertex(Elem):
    """当前类的职责定义。"""

    def __init__(self, vid: str, name: Optional[str] = None, **props):
        """初始化实例。"""
        super().__init__(name)
        self._vid = vid
        for k, v in props.items():
            self.set_prop(k, v)

    @property
    def vid(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self._vid

    @property
    def name(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return super().name or self._vid

    def format(self, concise: bool = False):
        """执行当前函数对应的业务逻辑。"""
        name = self._name or self._vid
        if concise:
            return f"({name})"

        if self._props:
            return f"({name}:{super().format()})"
        else:
            return f"({name})"

    def __str__(self):
        """执行当前函数对应的业务逻辑。"""
        return f"({self._vid})"


class IdVertex(Vertex):
    """当前类的职责定义。"""

    def __init__(self, vid: str):
        """初始化实例。"""
        super().__init__(vid)


class Edge(Elem):
    """当前类的职责定义。"""

    def __init__(self, sid: str, tid: str, name: str, **props):
        """初始化实例。"""
        assert name, "Edge name is required"

        super().__init__(name)
        self._sid = sid
        self._tid = tid
        for k, v in props.items():
            self.set_prop(k, v)

    def __eq__(self, other):
        """执行当前函数对应的业务逻辑。"""
        return (self.sid, self.tid, self.name) == (other.sid, other.tid, other.name)

    def __hash__(self):
        """执行当前函数对应的业务逻辑。"""
        return hash((self.sid, self.tid, self.name))

    @property
    def sid(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self._sid

    @property
    def tid(self) -> str:
        """执行当前函数对应的业务逻辑。"""
        return self._tid

    def nid(self, vid):
        """执行当前函数对应的业务逻辑。"""
        if vid == self._sid:
            return self._tid
        elif vid == self._tid:
            return self._sid
        else:
            raise ValueError(f"Get nid of {vid} on {self} failed")

    def format(self):
        """执行当前函数对应的业务逻辑。"""
        if self._props:
            return f"-[{self._name}:{super().format()}]->"
        else:
            return f"-[{self._name}]->"

    def triplet(self) -> Tuple[str, str, str]:
        """执行当前函数对应的业务逻辑。"""
        return self.sid, self.name, self.tid

    def __str__(self):
        """执行当前函数对应的业务逻辑。"""
        return f"({self._sid})-[{self._name}]->({self._tid})"


class Graph(ABC):
    """当前类的职责定义。"""

    @abstractmethod
    def upsert_vertex(self, vertex: Vertex):
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def append_edge(self, edge: Edge):
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def has_vertex(self, vid: str) -> bool:
        """校验条件并返回判断结果。"""

    @abstractmethod
    def get_vertex(self, vid: str) -> Vertex:
        """获取对应数据。"""

    @abstractmethod
    def get_neighbor_edges(
        self,
        vid: str,
        direction: Direction = Direction.OUT,
        limit: Optional[int] = None,
    ) -> Iterator[Edge]:
        """获取对应数据。"""

    @abstractmethod
    def vertices(
        self, filter_fn: Optional[Callable[[Vertex], bool]] = None
    ) -> Iterator[Vertex]:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def edges(
        self, filter_fn: Optional[Callable[[Edge], bool]] = None
    ) -> Iterator[Edge]:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def del_vertices(self, *vids: str):
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def del_edges(self, sid: str, tid: str, name: str, **props):
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def del_neighbor_edges(self, vid: str, direction: Direction = Direction.OUT):
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def search(
        self,
        vids: List[str],
        direct: Direction = Direction.OUT,
        depth: Optional[int] = None,
        fan: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> "Graph":
        """执行查询并返回结果。"""

    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def format(self) -> str:
        """执行当前函数对应的业务逻辑。"""

    @abstractmethod
    def truncate(self):
        """执行调用逻辑。"""


class MemoryGraph(Graph):
    """当前类的职责定义。"""

    def __init__(self):
        """初始化实例。"""
        # 整理元数据。
        self._vertex_prop_keys = set()
        self._edge_prop_keys = set()
        self._edge_count = 0

        # 代码说明。
        self._vs: Any = defaultdict()
        self._oes: Any = defaultdict(lambda: defaultdict(set))
        self._ies: Any = defaultdict(lambda: defaultdict(set))

    @property
    def vertex_count(self):
        """执行当前函数对应的业务逻辑。"""
        return len(self._vs)

    @property
    def edge_count(self):
        """执行当前函数对应的业务逻辑。"""
        return self._edge_count

    def upsert_vertex(self, vertex: Vertex):
        """执行当前函数对应的业务逻辑。"""
        if vertex.vid in self._vs:
            if isinstance(self._vs[vertex.vid], IdVertex):
                self._vs[vertex.vid] = vertex
            else:
                self._vs[vertex.vid].props.update(vertex.props)
        else:
            self._vs[vertex.vid] = vertex

        # 整理元数据。
        self._vertex_prop_keys.update(vertex.props.keys())

    def append_edge(self, edge: Edge) -> bool:
        """执行当前函数对应的业务逻辑。"""
        sid = edge.sid
        tid = edge.tid

        if edge in self._oes[sid][tid]:
            return False

        # 代码说明。
        self._vs.setdefault(sid, IdVertex(sid))
        self._vs.setdefault(tid, IdVertex(tid))

        # 代码说明。
        self._oes[sid][tid].add(edge)
        self._ies[tid][sid].add(edge)

        # 整理元数据。
        self._edge_prop_keys.update(edge.props.keys())
        self._edge_count += 1
        return True

    def upsert_graph(self, graph: "MemoryGraph"):
        """执行当前函数对应的业务逻辑。"""
        for vertex in graph.vertices():
            self.upsert_vertex(vertex)

        for edge in graph.edges():
            self.append_edge(edge)

    def has_vertex(self, vid: str) -> bool:
        """校验条件并返回判断结果。"""
        return vid in self._vs

    def get_vertex(self, vid: str) -> Vertex:
        """获取对应数据。"""
        return self._vs[vid]

    def get_neighbor_edges(
        self,
        vid: str,
        direction: Direction = Direction.OUT,
        limit: Optional[int] = None,
    ) -> Iterator[Edge]:
        """获取对应数据。"""
        if direction == Direction.OUT:
            es = (e for es in self._oes[vid].values() for e in es)

        elif direction == Direction.IN:
            es = iter(e for es in self._ies[vid].values() for e in es)

        elif direction == Direction.BOTH:
            oes = (e for es in self._oes[vid].values() for e in es)
            ies = (e for es in self._ies[vid].values() for e in es)

            # 代码说明。
            tuples = itertools.zip_longest(oes, ies)
            es = (e for t in tuples for e in t if e is not None)

            # 代码说明。
            seen = set()

            # 添加对应数据。
            def unique_elements(elements):
                for element in elements:
                    if element not in seen:
                        seen.add(element)
                        yield element

            es = unique_elements(es)
        else:
            raise ValueError(f"Invalid direction: {direction}")

        return itertools.islice(es, limit) if limit else es

    def vertices(
        self, filter_fn: Optional[Callable[[Vertex], bool]] = None
    ) -> Iterator[Vertex]:
        """执行当前函数对应的业务逻辑。"""
        # 获取对应数据。
        all_vertices = self._vs.values()

        return all_vertices if filter_fn is None else filter(filter_fn, all_vertices)

    def edges(
        self, filter_fn: Optional[Callable[[Edge], bool]] = None
    ) -> Iterator[Edge]:
        """执行当前函数对应的业务逻辑。"""
        # 获取对应数据。
        all_edges = (e for nbs in self._oes.values() for es in nbs.values() for e in es)

        if filter_fn is None:
            return all_edges
        else:
            return filter(filter_fn, all_edges)

    def del_vertices(self, *vids: str):
        """执行当前函数对应的业务逻辑。"""
        for vid in vids:
            self.del_neighbor_edges(vid, Direction.BOTH)
            self._vs.pop(vid, None)

    def del_edges(self, sid: str, tid: str, name: str, **props):
        """执行当前函数对应的业务逻辑。"""
        old_edge_cnt = len(self._oes[sid][tid])

        def remove_matches(es: Set[Edge]):
            return set(
                filter(
                    lambda e: (
                        not (
                            (name == e.name if name else True) and e.has_props(**props)
                        )
                    ),
                    es,
                )
            )

        self._oes[sid][tid] = remove_matches(self._oes[sid][tid])
        self._ies[tid][sid] = remove_matches(self._ies[tid][sid])

        self._edge_count -= old_edge_cnt - len(self._oes[sid][tid])

    def del_neighbor_edges(self, vid: str, direction: Direction = Direction.OUT):
        """执行当前函数对应的业务逻辑。"""

        def del_index(idx, i_idx):
            for nid in idx[vid].keys():
                self._edge_count -= len(i_idx[nid][vid])
                i_idx[nid].pop(vid, None)
            idx.pop(vid, None)

        if direction in [Direction.OUT, Direction.BOTH]:
            del_index(self._oes, self._ies)

        if direction in [Direction.IN, Direction.BOTH]:
            del_index(self._ies, self._oes)

    def search(
        self,
        vids: List[str],
        direct: Direction = Direction.OUT,
        depth: Optional[int] = None,
        fan: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> "MemoryGraph":
        """执行查询并返回结果。"""
        subgraph = MemoryGraph()

        for vid in vids:
            self.__search(vid, direct, depth, fan, limit, 0, set(), subgraph)

        return subgraph

    def __search(
        self,
        vid: str,
        direct: Direction,
        depth: Optional[int],
        fan: Optional[int],
        limit: Optional[int],
        _depth: int,
        _visited: Set,
        _subgraph: "MemoryGraph",
    ):
        if vid in _visited or depth and _depth >= depth:
            return

        # 代码说明。
        if not self.has_vertex(vid):
            return
        _subgraph.upsert_vertex(self.get_vertex(vid))
        _visited.add(vid)

        # 代码说明。
        nids = set()
        for edge in self.get_neighbor_edges(vid, direct, fan):
            if limit and _subgraph.edge_count >= limit:
                return

            # 代码说明。
            if _subgraph.append_edge(edge):
                nid = edge.nid(vid)
                if nid not in _visited:
                    nids.add(nid)

        # 代码说明。
        for nid in nids:
            self.__search(
                nid, direct, depth, fan, limit, _depth + 1, _visited, _subgraph
            )

    def schema(self) -> Dict[str, Any]:
        """执行当前函数对应的业务逻辑。"""
        return {
            "schema": [
                {
                    "type": "VERTEX",
                    "properties": [{"name": k} for k in self._vertex_prop_keys],
                },
                {
                    "type": "EDGE",
                    "properties": [{"name": k} for k in self._edge_prop_keys],
                },
            ]
        }

    def format(self, entities_only: Optional[bool] = False) -> str:
        """执行当前函数对应的业务逻辑。"""
        vs_str = "\n".join(v.format() for v in self.vertices())
        es_str = "\n".join(
            f"{self.get_vertex(e.sid).format(concise=True)}"
            f"{e.format()}"
            f"{self.get_vertex(e.tid).format(concise=True)}"
            for e in self.edges()
        )
        if entities_only:
            return f"Entities:\n{vs_str}" if vs_str else ""
        else:
            return (
                f"Entities:\n{vs_str}\n\nRelationships:\n{es_str}"
                if (vs_str or es_str)
                else ""
            )

    def truncate(self):
        """执行调用逻辑。"""
        # 整理元数据。
        self._vertex_prop_keys.clear()
        self._edge_prop_keys.clear()
        self._edge_count = 0

        # 代码说明。
        self._vs.clear()
        self._oes.clear()
        self._ies.clear()

    def graphviz(self, name="g"):
        """执行当前函数对应的业务逻辑。"""
        try:
            import networkx as nx
        except ImportError:
            raise ImportError(
                "networkx is required for graph visualization, please install it by "
                "running `pip install networkx`"
            )

        g = nx.MultiDiGraph()
        for vertex in self.vertices():
            g.add_node(vertex.vid)

        for edge in self.edges():
            triplet = edge.triplet()
            g.add_edge(triplet[0], triplet[2], label=triplet[1])

        digraph = nx.nx_agraph.to_agraph(g).to_string()
        digraph = digraph.replace('digraph ""', f"digraph {name}")
        digraph = re.sub(r"key=\d+,?\s*", "", digraph)
        return digraph
