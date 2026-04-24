"""配置加载和配置格式化工具，负责解析开发配置并支持环境变量注入。
"""

import hashlib
import json
import logging
from dataclasses import is_dataclass
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Type

from meyo.util.configure.manager import (
    ConfigurationManager,
    RegisterParameters,
)
from meyo.util.module_utils import import_from_string
from meyo.util.parameter_utils import ParameterDescription

logger = logging.getLogger(__name__)


def is_direct_subclass(cls, parent_cls):
    """校验条件并返回判断结果。"""
    # 检查条件是否满足。
    if not issubclass(cls, parent_cls):
        return False

    # 检查条件是否满足。
    return parent_cls in cls.__bases__


def _is_skip_class(cls):
    return is_direct_subclass(cls, RegisterParameters)


class MDXDocGenerator:
    def __init__(self):
        self.processed_classes: Set[str] = set()
        self.link_cache: Dict[str, str] = {}  # 代码说明。
        self._doc_cache: Dict[str, str] = {}
        self.generated_files: Set[str] = set()

    def generate_safe_filename(self, doc_id: str) -> str:
        """生成模型输出。"""
        if doc_id in self.link_cache:
            return self.link_cache[doc_id]

        parts = doc_id.split(".")[-2:]  # 代码说明。
        main_part = "_".join(parts)
        hash_suffix = hashlib.md5(doc_id.encode()).hexdigest()[:6]
        filename = f"{main_part}_{hash_suffix}.mdx".lower()
        self.link_cache[doc_id] = filename
        return filename

    def get_abs_link(self, cls: Type, doc_id: str) -> str:
        filename = self.generate_safe_filename(doc_id)
        link_url = "/docs/config-reference/"
        cfg_type, _ = self._parse_class_metadata(cls)
        if cfg_type:
            link_url += f"{cfg_type}/"
        link_url += filename[:-4]
        return link_url

    def get_rel_link(self, cls: Type, doc_id: str, source_cls: Type = None) -> str:
        """获取对应数据。"""
        filename = self.generate_safe_filename(doc_id)
        target_type, _ = self._parse_class_metadata(cls)

        # 返回对应结果。
        # 代码说明。
        if not source_cls:
            if target_type:
                return f"{target_type}/{filename[:-4]}"
            return filename[:-4]

        # 获取对应数据。
        source_type, _ = self._parse_class_metadata(source_cls)

        # 代码说明。
        if source_type == target_type:
            return filename[:-4]

        # 代码说明。
        if source_type and target_type:
            return f"../{target_type}/{filename[:-4]}"
        elif source_type and not target_type:
            return f"../{filename[:-4]}"
        elif not source_type and target_type:
            return f"{target_type}/{filename[:-4]}"
        else:
            return filename[:-4]

    def get_desc_for_class(self, cls: Type, default_desc: str = "") -> str:
        """获取对应数据。"""
        doc_id = self.get_class_doc_id(cls)
        return self._doc_cache.get(doc_id, default_desc)

    def get_class_doc_id(self, cls: Type) -> str:
        """获取对应数据。"""
        return f"{cls.__module__}.{cls.__name__}"

    def convert_to_mdx_dict(self, value: Any) -> Dict:
        """转换为目标数据结构。"""
        if value is None:
            return {"type": "code", "content": "None"}

        if is_dataclass(type(value)):
            return {"type": "code", "content": value.__class__.__name__}

        if isinstance(value, str):
            if "${" in value or "/" in value:
                return {"type": "code", "content": value}
            if len(value) > 50:
                return {"type": "codeblock", "content": value}
            return {"type": "code", "content": value}

        if isinstance(value, (list, dict, tuple)):
            return {"type": "codeblock", "language": "python", "content": repr(value)}

        return {"type": "code", "content": str(value)}

    def process_nested_fields(
        self,
        nested_fields: Dict[str, List[ParameterDescription]],
        output_dir: Path,
        source_cls: Type,
    ) -> Tuple[List[Dict], List[str]]:
        """执行当前函数对应的业务逻辑。"""
        links = []
        generated_files = []

        for type_name, params in nested_fields.items():
            if not params:
                continue

            try:
                nested_cls = import_from_string(params[0].param_class)

                doc_id = self.get_class_doc_id(nested_cls)

                if doc_id not in self.processed_classes:
                    new_files = self.generate_class_doc(nested_cls, output_dir)
                    generated_files.extend(new_files)
                # 代码说明。
                link_url = self.get_rel_link(nested_cls, doc_id, source_cls=source_cls)
                links.append(
                    {
                        "type": "link",
                        "text": f"{type_name} configuration",
                        "url": f"{link_url}",
                    }
                )

            except ImportError:
                logger.warning(
                    f"Cann't import configuration class: {params[0].param_class}"
                )
                links.append({"type": "text", "content": type_name})

        return links, generated_files

    def _parse_class_doc(self, param_cls: Type) -> Tuple[str, str, str]:
        metadata_name = f"_resource_metadata_{param_cls.__name__}"
        if hasattr(param_cls, metadata_name):
            from meyo.core.awel.flow import ResourceMetadata

            flow_metadata: ResourceMetadata = getattr(param_cls, metadata_name)
            label = flow_metadata.label
            description = flow_metadata.description
            documentation_url = flow_metadata.documentation_url
        else:
            label = param_cls.__name__
            description = param_cls.__doc__.strip() if param_cls.__doc__ else ""
            documentation_url = ""
        return label, description, documentation_url

    def _parse_class_metadata(self, param_cls: Type) -> Tuple[str | None, str | None]:
        cfg_type = None
        cfg_desc = None
        if hasattr(param_cls, "__cfg_type__"):
            cfg_type = getattr(param_cls, "__cfg_type__")
        if hasattr(param_cls, "__cfg_desc__"):
            cfg_desc = getattr(param_cls, "__cfg_desc__")
        return cfg_type, cfg_desc

    def generate_class_doc(self, cls: Type, output_dir: Path) -> List[str]:
        """生成模型输出。"""
        # 历史调试代码，当前不启用。
        # 历史调试代码，当前不启用。
        if not is_dataclass(cls):
            return []
        doc_id = self.get_class_doc_id(cls)
        if doc_id in self.processed_classes:
            return []

        self.processed_classes.add(doc_id)
        generated_files = []

        descriptions = ConfigurationManager.parse_description(
            cls, cache_enable=True, verbose=True
        )
        cfg_type, cfg_desc = self._parse_class_metadata(cls)

        filename = self.generate_safe_filename(doc_id)
        if cfg_type:
            output_path = output_dir / cfg_type / filename
        else:
            output_path = output_dir / filename

        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
        generated_files.append(filename)

        cls_label, cls_desc, cls_doc_url = self._parse_class_doc(cls)
        self._doc_cache[doc_id] = cls_desc
        with open(output_path, "w", encoding="utf-8") as f:
            # 设置对应数据。
            f.write("---\n")
            f.write(f'title: "{cls_label} Configuration"\n')
            f.write(f'description: "{cls_desc}"\n')
            f.write("---\n\n")

            # 代码说明。
            _config_component = '"@site/src/components/mdx/ConfigDetail";\n\n'
            f.write("import { ConfigDetail } from " + _config_component)

            # 代码说明。
            config_data = {
                "name": cls.__name__,
                "description": cls_desc,
                "documentationUrl": cls_doc_url,
                "parameters": [],
            }

            for param in sorted(
                descriptions,
                key=lambda x: (
                    x.param_order
                    if x.param_order is not None
                    else (1000 if x.required else float("inf"))
                ),
            ):
                param_data = {
                    "name": param.param_name,
                    "type": param.param_type or "",
                    "required": param.required,
                    "description": param.description or "",
                }
                # 代码说明。
                if param.nested_fields:
                    nested_links, nested_files = self.process_nested_fields(
                        param.nested_fields, output_dir, source_cls=cls
                    )
                    generated_files.extend(nested_files)
                    if nested_links:
                        param_data["nestedTypes"] = nested_links

                # 默认配置说明。
                if param.default_value is not None:
                    if is_dataclass(type(param.default_value)):
                        param_data["defaultValue"] = (
                            param.default_value.__class__.__name__
                        )
                    else:
                        param_data["defaultValue"] = str(param.default_value)

                # 代码说明。
                if param.valid_values:
                    param_data["validValues"] = [str(v) for v in param.valid_values]

                config_data["parameters"].append(param_data)

            # 代码说明。
            f.write("<ConfigDetail config={")
            f.write(json.dumps(config_data, indent=2, ensure_ascii=False))
            f.write("} />\n\n")

            # 代码说明。
            if hasattr(cls, "__abstract__"):
                subs = [c for c in cls.__subclasses__() if is_dataclass(c)]
                if subs:
                    f.write("## Implementations\n\n")
                    for sub_cls in subs:
                        sub_files = self.generate_class_doc(sub_cls, output_dir)
                        generated_files.extend(sub_files)

                        sub_doc_id = self.get_class_doc_id(sub_cls)
                        sub_filename = self.generate_safe_filename(sub_doc_id)
                        f.write(
                            f"- [{sub_cls.__name__} configuretion](./{sub_filename})\n"
                        )

        self.generated_files.add(filename)
        return generated_files

    def _collect_relationships(
        self, cls: Type, processed: Set[str], relationships: List[Dict]
    ):
        """执行当前函数对应的业务逻辑。"""

        if not is_dataclass(cls):
            return
        class_id = self.get_class_doc_id(cls)
        if class_id in processed:
            return
        processed.add(class_id)

        descriptions = ConfigurationManager.parse_description(
            cls, cache_enable=True, verbose=True
        )
        for param in descriptions:
            if param.nested_fields:
                for nested_type, nested_params in param.nested_fields.items():
                    if nested_params:
                        try:
                            nested_cls = import_from_string(
                                nested_params[0].param_class
                            )
                            relationships.append(
                                {
                                    "from": cls.__name__,
                                    "to": nested_cls.__name__,
                                    "label": param.param_name,
                                }
                            )
                            self._collect_relationships(
                                nested_cls, processed, relationships
                            )
                        except ImportError:
                            logger.warning(
                                "Can't import configuration class: "
                                f"{nested_params[0].param_class}"
                            )

    def generate_overview(self, output_dir: Path, config_classes: List[Type]):
        """生成模型输出。"""

        overview_path = output_dir / "overview.mdx"

        # 代码说明。
        relationships = []
        processed = set()

        for cls in config_classes:
            self._collect_relationships(cls, processed, relationships)

        # 代码说明。
        type_groups = {}
        class_map = {
            cls.__name__: cls for cls in config_classes if hasattr(cls, "__name__")
        }

        # 获取对应数据。
        for cls in config_classes:
            if _is_skip_class(cls):
                logger.info("Skipping class: %s", cls)
                continue
            # 默认配置说明。
            cfg_type = getattr(cls, "__cfg_type__", "other")
            if not cfg_type:
                cfg_type = "other"

            if cfg_type not in type_groups:
                type_groups[cfg_type] = []
            type_groups[cfg_type].append(cls)

        # 代码说明。
        type_relationships = {}
        for rel in relationships:
            from_cls = class_map.get(rel["from"])
            to_cls = class_map.get(rel["to"])

            if from_cls and to_cls:
                from_type = getattr(from_cls, "__cfg_type__", "other") or "other"
                to_type = getattr(to_cls, "__cfg_type__", "other") or "other"

                # 添加对应数据。
                # 代码说明。
                if from_type == to_type:
                    if from_type not in type_relationships:
                        type_relationships[from_type] = []
                    type_relationships[from_type].append(rel)

        # 代码说明。
        with open(overview_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write('title: "Configuration Overview"\n')
            f.write("---\n\n")

            f.write("# Configuration Overview\n\n")
            f.write(
                "This document provides an overview of all configuration classes "
                "organized by type.\n\n"
            )

            # 创建相关资源。
            f.write("## Configuration Types\n\n")

            for cfg_type, classes in sorted(type_groups.items()):
                f.write(
                    f"- [{cfg_type}](#type-{cfg_type.lower().replace(' ', '-')}) ({len(classes)} classes)\n"  # noqa
                )

            f.write("\n## Type Details\n\n")

            # 创建相关资源。
            for cfg_type, classes in sorted(type_groups.items()):
                if cfg_type != "other":
                    index_path = output_dir / f"{cfg_type}/index.mdx"
                    with open(index_path, "w", encoding="utf-8") as f_index:
                        f_index.write("---\n")
                        f_index.write(f'title: "{cfg_type}"\n')
                        f_index.write(f'description: "{cfg_type} Configuration"\n')
                        f_index.write("---\n\n")
                        f_index.write(
                            f"# {cfg_type} Configuration\n\n"
                            f"This document provides an overview of all configuration classes in {cfg_type} type.\n\n"  # noqa
                        )

                        # 代码说明。
                        f_index.write(
                            "import { ConfigClassTable } from '@site/src/components/mdx/ConfigClassTable';\n\n"  # noqa
                        )  # noqa

                        # 代码说明。
                        f_index.write("## Configuration Classes\n\n")
                        f_index.write("<ConfigClassTable classes={[\n")

                        # 代码说明。
                        for cls in sorted(classes, key=lambda x: x.__name__):
                            cls_name = cls.__name__
                            cfg_desc = getattr(cls, "__cfg_desc__", "") or ""
                            cfg_desc = self.get_desc_for_class(cls, cfg_desc)

                            doc_id = self.get_class_doc_id(cls)
                            # 获取对应数据。
                            doc_link = self.generate_safe_filename(doc_id)
                            f_index.write("  {\n")
                            f_index.write(f'    "name": "{cls_name}",\n')
                            f_index.write(
                                f'    "description": {json.dumps(cfg_desc)},\n'
                            )  # noqa
                            if doc_link:
                                f_index.write(f'    "link": "./{doc_link[:-4]}"\n')
                            else:
                                f_index.write('    "link": ""\n')
                            f_index.write("  },\n")

                        f_index.write("]} />\n\n")

                # 创建相关资源。
                anchor = f"type-{cfg_type.lower().replace(' ', '-')}"
                f.write(f"### {cfg_type} {{#{anchor}}}\n\n")

                # 代码说明。
                f.write(f"This type contains {len(classes)} configuration classes.\n\n")

                # 代码说明。
                type_rels = type_relationships.get(cfg_type, [])

                # 代码说明。
                # 代码说明。
                if 1 <= len(type_rels) <= 30:
                    f.write("#### Relationships\n\n")
                    f.write("```mermaid\ngraph TD\n")

                    for rel in type_rels:
                        f.write(f"    {rel['from']} -->|{rel['label']}| {rel['to']}\n")

                    f.write("```\n\n")
                elif len(type_rels) > 30:
                    # 添加对应数据。
                    f.write(
                        f"This type has {len(type_rels)} relationships, which is too many to display in a single diagram.\n\n"  # noqa
                    )

                # 代码说明。
                f.write("#### Configuration Classes\n\n")
                f.write("| Class | Description |\n")
                f.write("|-------|-------------|\n")

                for cls in sorted(classes, key=lambda x: x.__name__):
                    cls_name = cls.__name__
                    cfg_desc = getattr(cls, "__cfg_desc__", "")
                    # 获取对应数据。
                    # 代码说明。
                    doc_id = self.get_class_doc_id(cls)
                    if doc_id in self.link_cache:
                        # 代码说明。
                        if cfg_type != "other":
                            link_url = (
                                f"{cfg_type}/{self.generate_safe_filename(doc_id)[:-4]}"
                            )
                        else:
                            link_url = f"{self.generate_safe_filename(doc_id)[:-4]}"
                        f.write(f"| [{cls_name}]({link_url}) | {cfg_desc} |\n")
                    else:
                        f.write(f"| {cls_name} | {cfg_desc} |\n")

                f.write("\n---\n\n")  # 代码说明。

            # 添加对应数据。
            f.write("## Cross-Type Relationships\n\n")
            f.write(
                "The following diagram shows relationships between different configuration types:\n\n"  # noqa
            )

            # 创建相关资源。
            type_to_type = {}
            for rel in relationships:
                from_cls = class_map.get(rel["from"])
                to_cls = class_map.get(rel["to"])

                if from_cls and to_cls:
                    from_type = getattr(from_cls, "__cfg_type__", "other") or "other"
                    to_type = getattr(to_cls, "__cfg_type__", "other") or "other"

                    if from_type != to_type:
                        key = f"{from_type}|{to_type}"
                        if key not in type_to_type:
                            type_to_type[key] = 0
                        type_to_type[key] += 1

            if type_to_type:
                f.write("```mermaid\ngraph TD\n")

                # 添加对应数据。
                for cfg_type in type_groups:
                    f.write(
                        f"    {cfg_type}[{cfg_type} - {len(type_groups[cfg_type])} classes]\n"  # noqa
                    )

                # 添加对应数据。
                for key, count in type_to_type.items():
                    from_type, to_type = key.split("|")
                    f.write(f"    {from_type} -->|{count} connections| {to_type}\n")

                f.write("```\n\n")
            else:
                f.write("No cross-type relationships found.\n\n")

            # 添加对应数据。
            f.write("## Looking for a specific configuration?\n\n")
            f.write("1. Use the search function in the documentation site\n")
            f.write("2. Browse the configuration types above\n")
            f.write(
                "3. Check the specific class documentation for detailed parameter information\n"  # noqa
            )


def generate_docs(config_classes: List[Type], output_path: str):
    """生成模型输出。"""
    generator = MDXDocGenerator()
    output_dir = Path(output_path)
    backup_dir = None
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.exists():
        backup_dir = Path("/tmp") / "meyo_tmp_backup"
        if backup_dir.exists():
            os.system(f"rm -rf {backup_dir}")
        # 代码说明。
        os.system(f"mv {output_dir} {backup_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    ConfigurationManager._description_cache = {}
    # 代码说明。
    try:
        all_generated_files = []
        for cls in config_classes[:1]:
            # 代码说明。
            generated_files = generator.generate_class_doc(cls, output_dir)
            all_generated_files.extend(generated_files)

        # 代码说明。
        generator.generate_overview(output_dir, config_classes)
    except Exception as e:
        logger.error(f"Error generating documentation: {e}")
        # 代码说明。
        if backup_dir:
            # 删除对应数据。
            os.system(f"rm -rf {output_dir}")
            os.system(f"mv {backup_dir} {output_dir}")
        raise e

    return all_generated_files


def _get_all_subclasses(cls):
    all_subclasses = []
    direct_subclasses = cls.__subclasses__()
    all_subclasses.extend(direct_subclasses)
    for subclass in direct_subclasses:
        all_subclasses.extend(_get_all_subclasses(subclass))

    return all_subclasses


if __name__ == "__main__":
    import os
    import sys

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    from meyo.configs.model_config import ROOT_PATH
    from meyo_app.config import ApplicationConfig
    from meyo_app.meyo_server import scan_configs

    output_path = os.path.join(ROOT_PATH, "docs", "docs", "config-reference")

    scan_configs()

    config_classes = [ApplicationConfig]
    for subclass in _get_all_subclasses(RegisterParameters):
        config_classes.append(subclass)
    logger.info(f"Generating docs for {len(config_classes)} classes")
    logger.info(f"Generated for classes: {config_classes}")

    generate_docs(config_classes, output_path=output_path)
