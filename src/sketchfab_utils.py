"""
Sketchfab Utilities - Python port of interesting JS patterns from Sketchfab codebase.

Includes:
- sRGB/Linear color space conversions
- Deep cloning utilities
- Memoization decorator
- Array flattening utilities
- Popup/Modal management pattern
- Lazy loading utilities
"""

from __future__ import annotations
import math
import copy
from typing import Any, Callable, TypeVar, Dict, List, Optional, Union
from functools import wraps
from dataclasses import dataclass, field
from collections import OrderedDict
import weakref


# =============================================================================
# COLOR SPACE CONVERSIONS (from WebGL shaders)
# =============================================================================

def linear_to_srgb(value: float) -> float:
    """
    Convert a linear color value to sRGB.

    Uses the standard sRGB transfer function:
    - For values < 0.0031308: linear * 12.92
    - Otherwise: 1.055 * value^(1/2.4) - 0.055
    """
    if value < 0.0031308:
        return value * 12.92
    return 1.055 * math.pow(value, 1.0 / 2.4) - 0.055


def srgb_to_linear(value: float) -> float:
    """
    Convert an sRGB color value to linear.

    Uses the inverse sRGB transfer function:
    - For values < 0.04045: value / 12.92
    - Otherwise: ((value + 0.055) / 1.055)^2.4
    """
    if value < 0.04045:
        return value * (1.0 / 12.92)
    return math.pow((value + 0.055) * (1.0 / 1.055), 2.4)


def linear_to_srgb_rgb(r: float, g: float, b: float) -> tuple[float, float, float]:
    """Convert RGB values from linear to sRGB color space."""
    return (linear_to_srgb(r), linear_to_srgb(g), linear_to_srgb(b))


def srgb_to_linear_rgb(r: float, g: float, b: float) -> tuple[float, float, float]:
    """Convert RGB values from sRGB to linear color space."""
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b))


def linear_to_srgb_rgba(r: float, g: float, b: float, a: float) -> tuple[float, float, float, float]:
    """Convert RGBA values from linear to sRGB (alpha unchanged)."""
    return (linear_to_srgb(r), linear_to_srgb(g), linear_to_srgb(b), a)


# =============================================================================
# DEEP CLONE UTILITIES (from lodash-like implementation)
# =============================================================================

T = TypeVar('T')


def deep_clone(obj: T) -> T:
    """
    Create a deep clone of an object.

    Handles:
    - Primitives (returned as-is)
    - Lists and tuples
    - Dicts
    - Custom objects with __dict__
    - Sets and frozensets
    """
    return copy.deepcopy(obj)


def clone_with_transform(obj: Any, transform: Callable[[Any, str, Any], Any]) -> Any:
    """
    Deep clone with a transform function applied to each value.

    Args:
        obj: Object to clone
        transform: Function(value, key, parent) -> transformed_value
    """
    def _clone(value: Any, key: str = '', parent: Any = None) -> Any:
        transformed = transform(value, key, parent)

        if transformed is not value:
            return transformed

        if isinstance(value, dict):
            return {k: _clone(v, k, value) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            cloned = [_clone(item, str(i), value) for i, item in enumerate(value)]
            return type(value)(cloned)
        elif isinstance(value, set):
            return {_clone(item, '', value) for item in value}

        return value

    return _clone(obj)


# =============================================================================
# MEMOIZATION (from lodash memoize implementation)
# =============================================================================

def memoize(
    func: Callable = None,
    *,
    resolver: Callable[..., str] = None,
    max_size: int = 500
) -> Callable:
    """
    Memoize a function with optional custom cache key resolver.

    Args:
        func: Function to memoize
        resolver: Optional function to generate cache key from arguments
        max_size: Maximum cache size (clears when exceeded, like the JS version)

    Example:
        @memoize
        def expensive_calc(x, y):
            return x ** y

        @memoize(resolver=lambda x, y: f"{x},{y}")
        def another_calc(x, y):
            return x + y
    """
    def decorator(fn: Callable) -> Callable:
        cache: Dict[str, Any] = {}

        @wraps(fn)
        def memoized(*args, **kwargs):
            if resolver:
                key = resolver(*args, **kwargs)
            else:
                key = str(args) + str(sorted(kwargs.items()))

            if key in cache:
                return cache[key]

            result = fn(*args, **kwargs)

            # Clear cache if it exceeds max size (matches JS behavior)
            if len(cache) >= max_size:
                cache.clear()

            cache[key] = result
            return result

        memoized.cache = cache
        return memoized

    if func is not None:
        return decorator(func)
    return decorator


# =============================================================================
# ARRAY UTILITIES (from lodash-like flatten implementation)
# =============================================================================

def flatten(array: List, depth: int = 1) -> List:
    """
    Flatten a nested array to a specified depth.

    Args:
        array: The array to flatten
        depth: Maximum recursion depth (default: 1)

    Example:
        flatten([[1, 2], [3, [4, 5]]]) -> [1, 2, 3, [4, 5]]
        flatten([[1, 2], [3, [4, 5]]], 2) -> [1, 2, 3, 4, 5]
    """
    result = []

    def _flatten(arr: List, current_depth: int):
        for item in arr:
            if isinstance(item, list) and current_depth > 0:
                _flatten(item, current_depth - 1)
            else:
                result.append(item)

    _flatten(array, depth)
    return result


def flatten_deep(array: List) -> List:
    """Recursively flatten an array to a single level."""
    return flatten(array, float('inf'))


def compact(array: List) -> List:
    """Remove falsy values from an array."""
    return [item for item in array if item]


def uniq(array: List) -> List:
    """Remove duplicate values from an array while preserving order."""
    seen = set()
    result = []
    for item in array:
        # Handle unhashable types
        try:
            if item not in seen:
                seen.add(item)
                result.append(item)
        except TypeError:
            if item not in result:
                result.append(item)
    return result


# =============================================================================
# POPUP/MODAL MANAGEMENT (from Sketchfab popup system)
# =============================================================================

@dataclass
class PopupOptions:
    """Configuration options for popup behavior."""
    clean_on_close: bool = True
    should_exit_on_click_outside: bool = True
    should_exit_on_escape: bool = True
    should_reject_on_cancel: bool = False


class PopupManager:
    """
    Manages a stack of popups/modals.

    Provides:
    - Stack-based popup management
    - Top popup identification for keyboard handling
    - Automatic cleanup
    """

    _instance: Optional['PopupManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._stack: List[str] = []
        return cls._instance

    def add(self, identifier: str) -> None:
        """Add a popup to the stack."""
        if identifier not in self._stack:
            self._stack.append(identifier)

    def remove(self, identifier: str) -> None:
        """Remove a popup from the stack."""
        if identifier in self._stack:
            self._stack.remove(identifier)

    def get_top_popup(self) -> Optional[str]:
        """Get the identifier of the topmost popup."""
        return self._stack[-1] if self._stack else None

    def is_empty(self) -> bool:
        """Check if there are no popups open."""
        return len(self._stack) == 0

    def clear(self) -> None:
        """Remove all popups from the stack."""
        self._stack.clear()


@dataclass
class Popup:
    """
    A popup/modal instance.

    Based on Sketchfab's popup component pattern.
    """
    identifier: str
    options: PopupOptions = field(default_factory=PopupOptions)
    _is_open: bool = False
    _resolve: Optional[Callable] = None
    _reject: Optional[Callable] = None

    def open(self) -> 'Popup':
        """Open the popup and add it to the manager stack."""
        if not self._is_open:
            self._is_open = True
            PopupManager().add(self.identifier)
        return self

    def close(self) -> 'Popup':
        """Close the popup and remove it from the manager stack."""
        if self._is_open:
            self._is_open = False
            PopupManager().remove(self.identifier)
            if self.options.clean_on_close:
                self._cleanup()
        return self

    def cancel(self) -> 'Popup':
        """Cancel the popup (triggers reject if configured)."""
        self.close()
        if self._reject and self.options.should_reject_on_cancel:
            self._reject(Exception("Popup cancelled"))
        return self

    def continue_action(self, result: Any = None) -> 'Popup':
        """Continue/confirm the popup action."""
        self.close()
        if self._resolve:
            self._resolve(result)
        return self

    def _cleanup(self) -> None:
        """Clean up resources."""
        self._resolve = None
        self._reject = None

    @property
    def is_open(self) -> bool:
        return self._is_open

    def should_handle_escape(self) -> bool:
        """Check if this popup should handle escape key."""
        return (
            self.options.should_exit_on_escape and
            PopupManager().get_top_popup() == self.identifier
        )


# =============================================================================
# LAZY LOADING UTILITIES (from Sketchfab lazy image loader)
# =============================================================================

@dataclass
class LazyLoadConfig:
    """Configuration for lazy loading behavior."""
    root_margin: str = "0px"
    threshold: float = 0.0
    use_intersection_observer: bool = True


class LazyLoader:
    """
    Lazy loading utility for deferring resource loading.

    Python adaptation of Sketchfab's lazy image loading pattern.
    Can be used with any async loading scenario.
    """

    def __init__(self, config: LazyLoadConfig = None):
        self.config = config or LazyLoadConfig()
        self._pending: Dict[str, Callable] = {}
        self._loaded: set = set()

    def register(self, uri: str, on_load: Callable[[str], None]) -> None:
        """Register a resource for lazy loading."""
        if uri in self._loaded:
            on_load(uri)
        else:
            self._pending[uri] = on_load

    def trigger_load(self, uri: str) -> bool:
        """
        Trigger loading of a registered resource.

        Returns True if the resource was pending and triggered.
        """
        if uri in self._pending:
            callback = self._pending.pop(uri)
            self._loaded.add(uri)
            callback(uri)
            return True
        return False

    def trigger_all(self) -> int:
        """Trigger loading of all pending resources. Returns count loaded."""
        count = len(self._pending)
        for uri in list(self._pending.keys()):
            self.trigger_load(uri)
        return count

    def is_loaded(self, uri: str) -> bool:
        """Check if a resource has been loaded."""
        return uri in self._loaded

    def is_pending(self, uri: str) -> bool:
        """Check if a resource is pending load."""
        return uri in self._pending


# =============================================================================
# WEBGL FEATURE DETECTION (Python adaptation)
# =============================================================================

@dataclass
class WebGLCapabilities:
    """
    WebGL capability detection results.

    Python adaptation of Sketchfab's WebGL support detection.
    Useful for generating capability reports or configuring renderers.
    """
    supported: bool = False
    max_fragment_uniform_vectors: int = 0
    max_varying_vectors: int = 0
    webgl2_available: bool = False
    renderer_info: str = ""
    is_swiftshader: bool = False

    # Minimum requirements (from JS code)
    MIN_FRAGMENT_UNIFORM_VECTORS: int = 64
    MIN_VARYING_VECTORS: int = 8

    def meets_requirements(self) -> bool:
        """Check if capabilities meet minimum requirements."""
        return (
            self.max_fragment_uniform_vectors >= self.MIN_FRAGMENT_UNIFORM_VECTORS and
            self.max_varying_vectors >= self.MIN_VARYING_VECTORS and
            not self.is_swiftshader
        )

    def to_dict(self) -> Dict[str, Any]:
        """Export capabilities as a dictionary."""
        return {
            "supported": self.supported,
            "max_fragment_uniform_vectors": self.max_fragment_uniform_vectors,
            "max_varying_vectors": self.max_varying_vectors,
            "webgl2_available": self.webgl2_available,
            "renderer_info": self.renderer_info,
            "is_swiftshader": self.is_swiftshader,
            "meets_requirements": self.meets_requirements()
        }


def check_webgl_requirements(capabilities: Dict[str, Any]) -> WebGLCapabilities:
    """
    Validate WebGL capabilities against Sketchfab's requirements.

    Args:
        capabilities: Dict with WebGL parameters from a browser/renderer

    Returns:
        WebGLCapabilities with validation results
    """
    caps = WebGLCapabilities(
        supported=capabilities.get("supported", False),
        max_fragment_uniform_vectors=capabilities.get("max_fragment_uniform_vectors", 0),
        max_varying_vectors=capabilities.get("max_varying_vectors", 0),
        webgl2_available=capabilities.get("webgl2", False),
        renderer_info=capabilities.get("renderer", ""),
        is_swiftshader="SwiftShader" in capabilities.get("renderer", "")
    )
    return caps


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def omit(obj: Dict, keys: List[str]) -> Dict:
    """
    Create a new dict excluding specified keys.

    Port of lodash _.omit
    """
    return {k: v for k, v in obj.items() if k not in keys}


def pick(obj: Dict, keys: List[str]) -> Dict:
    """
    Create a new dict with only specified keys.

    Port of lodash _.pick
    """
    return {k: v for k, v in obj.items() if k in keys}


def get(obj: Any, path: str, default: Any = None) -> Any:
    """
    Get a value from a nested object using dot notation.

    Port of lodash _.get

    Example:
        get({"a": {"b": {"c": 1}}}, "a.b.c") -> 1
        get({"a": [1, 2, 3]}, "a.1") -> 2
    """
    keys = path.replace("[", ".").replace("]", "").split(".")
    result = obj

    for key in keys:
        if result is None:
            return default

        try:
            if isinstance(result, dict):
                result = result.get(key, default)
            elif isinstance(result, (list, tuple)):
                result = result[int(key)]
            else:
                result = getattr(result, key, default)
        except (KeyError, IndexError, AttributeError, ValueError):
            return default

    return result


def set_value(obj: Dict, path: str, value: Any) -> Dict:
    """
    Set a value in a nested object using dot notation.

    Modifies the object in place and returns it.

    Example:
        set_value({}, "a.b.c", 1) -> {"a": {"b": {"c": 1}}}
    """
    keys = path.replace("[", ".").replace("]", "").split(".")
    current = obj

    for i, key in enumerate(keys[:-1]):
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value
    return obj


def is_equal(a: Any, b: Any) -> bool:
    """
    Deep equality check.

    Port of lodash _.isEqual
    """
    if type(a) != type(b):
        return False

    if isinstance(a, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(is_equal(a[k], b[k]) for k in a)

    if isinstance(a, (list, tuple)):
        if len(a) != len(b):
            return False
        return all(is_equal(x, y) for x, y in zip(a, b))

    if isinstance(a, set):
        return a == b

    return a == b


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Color conversions
    "linear_to_srgb",
    "srgb_to_linear",
    "linear_to_srgb_rgb",
    "srgb_to_linear_rgb",
    "linear_to_srgb_rgba",

    # Clone utilities
    "deep_clone",
    "clone_with_transform",

    # Memoization
    "memoize",

    # Array utilities
    "flatten",
    "flatten_deep",
    "compact",
    "uniq",

    # Popup management
    "PopupOptions",
    "PopupManager",
    "Popup",

    # Lazy loading
    "LazyLoadConfig",
    "LazyLoader",

    # WebGL
    "WebGLCapabilities",
    "check_webgl_requirements",

    # Utilities
    "omit",
    "pick",
    "get",
    "set_value",
    "is_equal",
]
