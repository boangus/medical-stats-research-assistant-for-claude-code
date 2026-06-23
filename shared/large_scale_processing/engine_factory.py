"""
Engine factory for unified processing engine creation.

Provides factory methods to create processing engine instances:
- By explicit engine type
- By automatic selection based on data size

Features:
- Graceful degradation: falls back to next best available engine
- Lazy loading: engines are loaded on first use
- Import safety: missing dependencies don't break the factory
"""

import logging
from typing import Any, Dict, Optional, Type

from .base_engine import BaseEngine
from .engine_selector import EngineSelector, ProcessingEngine

logger = logging.getLogger(__name__)

# Fallback order when preferred engine is unavailable
_ENGINE_FALLBACK = {
    "dask": ["duckdb", "polars"],
    "duckdb": ["polars"],
    "polars": ["duckdb"],
    "pandas": [],  # pandas is always available as compatibility layer
}

# Known engine types (the vocabulary of engines MSRA supports)
# Used to distinguish "truly unknown" from "known but not installed"
_KNOWN_ENGINE_TYPES = {"polars", "duckdb", "dask", "pandas"}


class EngineFactory:
    """
    Factory for creating processing engine instances.

    Supports creation by:
    - Explicit engine type (polars, duckdb, dask)
    - Automatic selection based on data size

    Graceful degradation:
        If the preferred engine is not installed, the factory
        automatically falls back to the next best available engine
        and logs a warning.
    """

    # Registry of engine classes
    # Format: engine_type_string -> engine_class
    _engine_registry: Dict[str, Type[BaseEngine]] = {}

    @classmethod
    def _load_engines(cls) -> Dict[str, Type[BaseEngine]]:
        """
        Lazily load available engine classes.

        Returns:
            Dict mapping engine type strings to engine classes
        """
        if cls._engine_registry:
            return cls._engine_registry

        registry = {}

        # Try to load PolarsEngine
        try:
            from .polars_engine import PolarsEngine
            registry["polars"] = PolarsEngine
        except ImportError:
            pass

        # Try to load DuckDBEngine
        try:
            from .duckdb_engine import DuckDBEngine
            registry["duckdb"] = DuckDBEngine
        except ImportError:
            pass

        # Try to load DaskEngine
        try:
            from .dask_engine import DaskEngine, _DASK_AVAILABLE
            if _DASK_AVAILABLE:
                registry["dask"] = DaskEngine
        except ImportError:
            pass

        cls._engine_registry = registry
        return registry

    @classmethod
    def create_engine(
        cls,
        engine_type: str,
        config: Optional[Dict[str, Any]] = None,
        allow_fallback: bool = True,
    ) -> BaseEngine:
        """
        Create engine by explicit type.

        Args:
            engine_type: Engine type string ("polars", "duckdb", "dask")
            config: Optional engine configuration dict
            allow_fallback: If True, fall back to next best engine
                when the requested one is unavailable (default: True)

        Returns:
            Engine instance

        Raises:
            ValueError: If engine_type is unknown or not available
                and fallback is disabled or exhausted
        """
        registry = cls._load_engines()

        engine_lower = engine_type.lower()
        if engine_lower not in registry:
            available = list(registry.keys())

            # Distinguish truly unknown types from known-but-uninstalled
            if engine_lower not in _KNOWN_ENGINE_TYPES:
                # Truly unknown engine type — never try fallback
                raise ValueError(
                    f"Unknown engine type: {engine_type}. "
                    f"Available engines: {available if available else 'none'}"
                )

            # Known engine type but not installed — try fallback
            if allow_fallback:
                for fallback in _ENGINE_FALLBACK.get(engine_lower, []):
                    if fallback in registry:
                        logger.warning(
                            "Engine '%s' is not available, "
                            "falling back to '%s'. "
                            "To use '%s', install it: pip install %s",
                            engine_lower,
                            fallback,
                            engine_lower,
                            engine_lower,
                        )
                        engine_lower = fallback
                        break
                else:
                    raise ValueError(
                        f"Engine '{engine_type}' is not available and no "
                        f"fallback engines could be found. "
                        f"Available engines: {available if available else 'none'}. "
                        f"To use '{engine_type}', install it: "
                        f"pip install {engine_type}"
                    )
            else:
                raise ValueError(
                    f"Engine '{engine_type}' is not available. "
                    f"Available engines: {available if available else 'none'}"
                )

        engine_class = registry[engine_lower]
        # Try to pass config if engine accepts it, otherwise instantiate without
        try:
            return engine_class(config)
        except TypeError:
            # Engine doesn't accept config, instantiate without
            return engine_class()

    @classmethod
    def create_for_size(
        cls,
        size_bytes: int,
        config: Optional[Dict[str, Any]] = None
    ) -> BaseEngine:
        """
        Create optimal engine based on data size.

        Size thresholds:
        - <1GB: pandas (compatibility, no engine class needed)
        - 1-10GB: Polars
        - 10-100GB: DuckDB
        - >100GB: Dask

        If the recommended engine is not installed, the factory
        automatically falls back to the next best available engine.

        Args:
            size_bytes: Estimated data size in bytes
            config: Optional engine configuration dict

        Returns:
            Optimal engine instance for the data size
        """
        engine_type = EngineSelector._select_by_size(size_bytes)
        return cls.create_engine(engine_type.value, config, allow_fallback=True)

    @classmethod
    def get_available_engines(cls) -> list:
        """
        Get list of available engine types.

        Returns:
            List of available engine type strings
        """
        registry = cls._load_engines()
        return list(registry.keys())