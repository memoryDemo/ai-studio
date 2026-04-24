"""通用工具模块，支撑模型服务配置、网络、日志、结构化数据、数据库查询和参数处理。"""

import re


def remove_sql_comments(sql: str) -> str:
    """删除对应数据。"""

    # 代码说明。
    sql = re.sub(r"--.*?(\n|$)", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql
