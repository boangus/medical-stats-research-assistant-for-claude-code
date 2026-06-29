"""ETL 工作流异常。"""

from __future__ import annotations

from typing import Optional


class ETLStageError(Exception):
    """ETL 阶段错误（extract/transform/load 中的任意阶段失败）。"""

    def __init__(self, message: str, stage: Optional[str] = None) -> None:
        self.stage = stage
        super().__init__(message)
