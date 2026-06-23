"""
Template Manager - 统一模板管理接口

提供统一的模板调用接口，支持Python和R双语言实现，
便于交叉验证和方法对比。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, List, Any, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Language(Enum):
    PYTHON = "python"
    R = "r"


class TemplateType(Enum):
    BASELINE = "baseline"
    FOREST_PLOT = "forest_plot"
    COX = "cox"
    LOGISTIC = "logistic"
    ROC = "roc"
    GEE = "gee"
    BLAND_ALTMAN = "bland_altman"
    SAMPLE_SIZE = "sample_size"
    SURVIVAL = "survival"
    REGRESSION = "regression"
    CORRELATION = "correlation"
    ANOVA = "anova"


TEMPLATE_MAPPING: Dict[TemplateType, Dict[Language, str]] = {
    TemplateType.BASELINE: {
        Language.PYTHON: "baseline_table1_engine",
        Language.R: "table1_template",
    },
    TemplateType.FOREST_PLOT: {
        Language.PYTHON: "forest_plot_template",
        Language.R: "forest_plot_template",
    },
    TemplateType.COX: {
        Language.PYTHON: "cox_template",
        Language.R: "cox_enhanced",
    },
    TemplateType.LOGISTIC: {
        Language.PYTHON: "logistic_template",
        Language.R: "logistic_family_template",
    },
    TemplateType.ROC: {
        Language.PYTHON: "roc_template",
        Language.R: "roc_visualization_template",
    },
    TemplateType.GEE: {
        Language.PYTHON: "gee_template",
        Language.R: "gee_template",
    },
    TemplateType.BLAND_ALTMAN: {
        Language.PYTHON: "bland_altman_template",
        Language.R: "bland_altman_template",
    },
    TemplateType.SAMPLE_SIZE: {
        Language.PYTHON: "sample_size_template",
        Language.R: "sample_size_calculator",
    },
    TemplateType.SURVIVAL: {
        Language.PYTHON: "survival_lifelines",
        Language.R: "survival_ggsurvfit",
    },
    TemplateType.REGRESSION: {
        Language.PYTHON: "linear_regression_template",
        Language.R: "regression_template",
    },
    TemplateType.CORRELATION: {
        Language.PYTHON: "correlation_template",
        Language.R: "correlation_template",
    },
    TemplateType.ANOVA: {
        Language.PYTHON: "anova_template",
        Language.R: "repeated_measures_anova_template",
    },
}


class TemplateManager:
    """统一模板管理器"""

    def __init__(self, templates_dir: Optional[str] = None):
        """初始化模板管理器

        Args:
            templates_dir: 模板目录路径（默认使用shared/templates）
        """
        if templates_dir is None:
            templates_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "templates"
            )
        self.templates_dir = Path(templates_dir)
        self._loaded_templates: Dict[str, Any] = {}

    def _get_template_path(self, template_name: str, language: Language) -> Path:
        """获取模板文件路径"""
        ext = ".py" if language == Language.PYTHON else ".R"
        return self.templates_dir / f"{template_name}{ext}"

    def _load_python_template(self, template_name: str) -> Any:
        """加载Python模板模块"""
        if template_name in self._loaded_templates:
            return self._loaded_templates[template_name]

        template_path = self._get_template_path(template_name, Language.PYTHON)
        if not template_path.exists():
            raise FileNotFoundError(f"Python template not found: {template_path}")

        import importlib.util

        spec = importlib.util.spec_from_file_location(template_name, str(template_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self._loaded_templates[template_name] = module
        logger.info(f"Loaded Python template: {template_name}")
        return module

    def _load_r_template(self, template_name: str) -> str:
        """加载R模板内容"""
        template_path = self._get_template_path(template_name, Language.R)
        if not template_path.exists():
            raise FileNotFoundError(f"R template not found: {template_path}")

        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        logger.info(f"Loaded R template: {template_name}")
        return content

    def list_templates(self) -> List[Dict[str, Any]]:
        """列出所有可用模板"""
        templates = []
        for template_type, mappings in TEMPLATE_MAPPING.items():
            info = {
                "type": template_type.value,
                "description": self._get_template_description(template_type),
                "python_available": self._get_template_path(
                    mappings[Language.PYTHON], Language.PYTHON
                ).exists(),
                "r_available": self._get_template_path(
                    mappings[Language.R], Language.R
                ).exists(),
            }
            templates.append(info)
        return templates

    def _get_template_description(self, template_type: TemplateType) -> str:
        """获取模板描述"""
        descriptions = {
            TemplateType.BASELINE: "基线特征表生成",
            TemplateType.FOREST_PLOT: "森林图生成",
            TemplateType.COX: "Cox比例风险模型",
            TemplateType.LOGISTIC: "逻辑回归分析",
            TemplateType.ROC: "ROC曲线分析",
            TemplateType.GEE: "广义估计方程",
            TemplateType.BLAND_ALTMAN: "Bland-Altman一致性分析",
            TemplateType.SAMPLE_SIZE: "样本量计算",
            TemplateType.SURVIVAL: "生存分析",
            TemplateType.REGRESSION: "线性回归分析",
            TemplateType.CORRELATION: "相关性分析",
            TemplateType.ANOVA: "方差分析",
        }
        return descriptions.get(template_type, "未知模板")

    def get_template(self, template_type: TemplateType, language: Language) -> Any:
        """获取指定类型和语言的模板

        Args:
            template_type: 模板类型
            language: 语言（Python或R）

        Returns:
            Python模板返回模块对象，R模板返回代码字符串
        """
        if template_type not in TEMPLATE_MAPPING:
            raise ValueError(f"Unknown template type: {template_type}")

        template_name = TEMPLATE_MAPPING[template_type][language]

        if language == Language.PYTHON:
            return self._load_python_template(template_name)
        else:
            return self._load_r_template(template_name)

    def run_python_template(
        self, template_type: TemplateType, function_name: str, **kwargs
    ) -> Any:
        """运行Python模板中的函数

        Args:
            template_type: 模板类型
            function_name: 函数名称
            **kwargs: 函数参数

        Returns:
            函数返回值
        """
        module = self.get_template(template_type, Language.PYTHON)
        if not hasattr(module, function_name):
            raise AttributeError(
                f"Function {function_name} not found in template {template_type}"
            )
        func = getattr(module, function_name)
        return func(**kwargs)

    def generate_r_code(
        self, template_type: TemplateType, data_path: str = None, **parameters
    ) -> str:
        """生成R代码

        Args:
            template_type: 模板类型
            data_path: 数据文件路径
            **parameters: 分析参数

        Returns:
            生成的R代码字符串
        """
        template_content = self.get_template(template_type, Language.R)

        placeholders = {
            "{{DATA_PATH}}": data_path or "data.csv",
        }
        placeholders.update({f"{{{{{k.upper()}}}}}": str(v) for k, v in parameters.items()})

        for placeholder, value in placeholders.items():
            template_content = template_content.replace(placeholder, value)

        return template_content

    def cross_validate(
        self, template_type: TemplateType, data: Any, **kwargs
    ) -> Dict[str, Any]:
        """交叉验证：同时用Python和R执行同一分析

        Args:
            template_type: 模板类型
            data: 输入数据
            **kwargs: 分析参数

        Returns:
            包含Python和R执行结果的字典
        """
        results = {
            "template_type": template_type.value,
            "python_result": None,
            "r_result": None,
            "python_error": None,
            "r_error": None,
        }

        try:
            results["python_result"] = self._run_cross_validate_python(
                template_type, data, **kwargs
            )
        except Exception as e:
            results["python_error"] = str(e)
            logger.error(f"Python cross-validation error: {e}")

        try:
            results["r_result"] = self._run_cross_validate_r(
                template_type, data, **kwargs
            )
        except Exception as e:
            results["r_error"] = str(e)
            logger.error(f"R cross-validation error: {e}")

        return results

    def _run_cross_validate_python(
        self, template_type: TemplateType, data: Any, **kwargs
    ) -> Any:
        """执行Python交叉验证"""
        dispatch_map = {
            TemplateType.BASELINE: self._run_baseline_python,
            TemplateType.COX: self._run_cox_python,
            TemplateType.LOGISTIC: self._run_logistic_python,
            TemplateType.ROC: self._run_roc_python,
            TemplateType.GEE: self._run_gee_python,
            TemplateType.FOREST_PLOT: self._run_forest_plot_python,
        }

        if template_type in dispatch_map:
            return dispatch_map[template_type](data, **kwargs)
        else:
            raise NotImplementedError(
                f"Cross-validation not implemented for {template_type}"
            )

    def _run_cross_validate_r(
        self, template_type: TemplateType, data: Any, **kwargs
    ) -> Any:
        """执行R交叉验证（生成代码）"""
        import tempfile
        import pandas as pd

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            if isinstance(data, pd.DataFrame):
                data.to_csv(f.name, index=False)
                data_path = f.name
            else:
                data_path = str(data)

        r_code = self.generate_r_code(template_type, data_path=data_path, **kwargs)

        return {
            "code": r_code,
            "data_path": data_path,
            "parameters": kwargs,
        }

    def _run_baseline_python(self, data, **kwargs):
        """运行基线表Python模板"""
        module = self.get_template(TemplateType.BASELINE, Language.PYTHON)
        if hasattr(module, "generate_baseline_table"):
            return module.generate_baseline_table(data, **kwargs)
        elif hasattr(module, "create_table1"):
            return module.create_table1(data, **kwargs)
        return {"error": "No suitable function found"}

    def _run_cox_python(self, data, **kwargs):
        """运行Cox模型Python模板"""
        module = self.get_template(TemplateType.COX, Language.PYTHON)
        if hasattr(module, "run_cox_regression"):
            return module.run_cox_regression(data, **kwargs)
        return {"error": "No suitable function found"}

    def _run_logistic_python(self, data, **kwargs):
        """运行逻辑回归Python模板"""
        module = self.get_template(TemplateType.LOGISTIC, Language.PYTHON)
        if hasattr(module, "run_logistic_regression"):
            return module.run_logistic_regression(data, **kwargs)
        return {"error": "No suitable function found"}

    def _run_roc_python(self, data, **kwargs):
        """运行ROC分析Python模板"""
        module = self.get_template(TemplateType.ROC, Language.PYTHON)
        if hasattr(module, "run_roc_analysis"):
            return module.run_roc_analysis(data, **kwargs)
        return {"error": "No suitable function found"}

    def _run_gee_python(self, data, **kwargs):
        """运行GEE分析Python模板"""
        module = self.get_template(TemplateType.GEE, Language.PYTHON)
        if hasattr(module, "run_gee_analysis"):
            return module.run_gee_analysis(data, **kwargs)
        return {"error": "No suitable function found"}

    def _run_forest_plot_python(self, data, **kwargs):
        """运行森林图Python模板"""
        module = self.get_template(TemplateType.FOREST_PLOT, Language.PYTHON)
        if hasattr(module, "generate_forest_plot"):
            return module.generate_forest_plot(data, **kwargs)
        return {"error": "No suitable function found"}


def get_template_manager() -> TemplateManager:
    """获取全局模板管理器实例"""
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager


_template_manager: Optional[TemplateManager] = None
