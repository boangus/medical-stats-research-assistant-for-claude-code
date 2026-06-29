"""Metadata Catalog exceptions.

异常层级:
    MetadataCatalogError (base)
    ├── VariableNotFoundError         # 变量未注册
    ├── VariableAlreadyExistsError    # 重复注册
    └── InvalidLineageError          # 血缘关系不合法（循环）
"""


class MetadataCatalogError(Exception):
    """元数据目录基础异常。"""


class VariableNotFoundError(MetadataCatalogError):
    """变量未在目录中注册。"""

    def __init__(self, variable: str) -> None:
        self.variable = variable
        super().__init__(f"变量 '{variable}' 未在元数据目录中注册。")


class VariableAlreadyExistsError(MetadataCatalogError):
    """变量重复注册（未通过 overwrite=True）。"""

    def __init__(self, variable: str) -> None:
        self.variable = variable
        super().__init__(
            f"变量 '{variable}' 已注册。如需覆盖，请使用 register(..., overwrite=True)。"
        )


class InvalidLineageError(MetadataCatalogError):
    """血缘关系不合法（如检测到循环依赖）。"""

    def __init__(self, cycle_path: list) -> None:
        self.cycle_path = cycle_path
        super().__init__(
            f"检测到循环依赖: {' -> '.join(cycle_path)}"
        )
