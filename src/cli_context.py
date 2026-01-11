"""
Shared CLI context: imports, constants, and helpers used by commands.
"""

import json
import re
import http.cookiejar
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlencode, parse_qs

from .cli_data import (
    get_api_config, get_embed_options, get_material_options,
    get_quality_presets, get_environment_presets,
    get_ai_actions, get_ai_providers, get_download_formats,
    get_visibility_types, get_model_badges, get_thumbnail_sizes,
    get_model_properties, get_subscription_tiers, get_org_roles,
    get_search_filters, get_search_categories, get_themes,
    get_gradients, get_shadows, get_brand_colors, get_notification_types,
    get_typography, get_breakpoints, get_layout_dimensions,
    get_spacing_scale, get_grid_columns, get_rating_config,
    get_validation_patterns, get_date_formats, get_user_profile_fields,
    get_markdown_toolbar, get_report_reasons, get_share_platforms,
    get_emoji_categories, get_licenses, get_webgl_errors,
    get_consent_categories, get_spring_presets, get_popup_placements,
    get_commands, get_demos, get_info_strings, get_labels, get_symbols,
    get_config_options, get_api_options, get_design_options, get_layout_options,
    # String getters
    get_constants, get_messages, get_error_messages, get_result_indicators,
    get_yes_no, get_file_units, get_http_config, get_code_snippets,
    get_markdown_examples, get_dayjs_tokens, get_permission_types,
    get_spring_formulas, get_spring_variables, get_defaults,
    get_separator_lengths, get_gui_file, get_iframe_template,
    get_url_templates, get_strftime_map, get_strings_config, get_window_sizes
)

from .sketchfab_fetcher import SketchfabFetcher
from .model_decryptor import SketchfabDecryptor, decrypt_model
from .binz_reader import BinzReader

# =============================================================================
# CONSTANTS - Loaded from JSON files in src/cli_data/
# =============================================================================

# Lazy-load API config
_api_config = None
def _get_api():
    global _api_config
    if _api_config is None:
        _api_config = get_api_config()
    return _api_config

# API Endpoints
@property
def SKETCHFAB_API_BASE():
    return _get_api()['base_url']

@property  
def SKETCHFAB_BASE_URL():
    return _get_api()['sketchfab_url']

# Load from JSON for backward compatibility
_constants = get_constants()
SKETCHFAB_API_BASE = _constants['sketchfab_api_base']
SKETCHFAB_BASE_URL = _constants['sketchfab_base_url']

# Lazy-loaded constants from JSON - use getter functions for dynamic access
# These are loaded on first access via the get_* functions from cli_data

def _lazy_load(getter_func, cache_attr):
    cache = {}
    def wrapper():
        if cache_attr not in cache:
            cache[cache_attr] = getter_func()
        return cache[cache_attr]
    return wrapper

# Create lazy references for configuration data
API_ENDPOINTS = None
EMBED_OPTIONS = None
MATERIAL_OPTIONS = None
QUALITY_PRESETS = None
ENVIRONMENT_PRESETS = None
AI_ACTIONS = None
AI_PROVIDERS = None
DOWNLOAD_FORMATS = None
VISIBILITY_TYPES = None
SUBSCRIPTION_TIERS = None
THUMBNAIL_SIZES = None
MODEL_BADGES = None
SEARCH_FILTERS = None
SEARCH_CATEGORIES = None
ORG_MEMBER_ROLES = None
THEMES = None
VALIDATION_PATTERNS = None
TYPOGRAPHY_SCALE = None
THEME_COLORS = None
GRADIENT_PRESETS = None
RATING_CONFIG = None
NOTIFICATION_TYPES = None
SHADOW_PRESETS = None
BRAND_COLORS = None
BREAKPOINTS = None
LAYOUT_DIMENSIONS = None
SPACING_SCALE = None
DATE_FORMATS = None
MARKDOWN_TOOLBAR = None
REPORT_REASONS = None
SHARE_PLATFORMS = None
LICENSE_TYPES = None
WEBGL_ERRORS = None
CONSENT_CATEGORIES = None
SPRING_PRESETS = None
POPUP_PLACEMENTS = None
USER_PROFILE_FIELDS = None
GRID_COLUMNS = None
EMOJI_CATEGORIES = None
MODEL_PROPERTIES = None

def _init_constants():
    global API_ENDPOINTS, EMBED_OPTIONS, MATERIAL_OPTIONS, QUALITY_PRESETS
    global ENVIRONMENT_PRESETS, AI_ACTIONS, AI_PROVIDERS, DOWNLOAD_FORMATS
    global VISIBILITY_TYPES, SUBSCRIPTION_TIERS, THUMBNAIL_SIZES, MODEL_BADGES
    global SEARCH_FILTERS, SEARCH_CATEGORIES, ORG_MEMBER_ROLES, THEMES
    global VALIDATION_PATTERNS, TYPOGRAPHY_SCALE, THEME_COLORS, GRADIENT_PRESETS
    global RATING_CONFIG, NOTIFICATION_TYPES, SHADOW_PRESETS, BRAND_COLORS
    global BREAKPOINTS, LAYOUT_DIMENSIONS, SPACING_SCALE, DATE_FORMATS
    global MARKDOWN_TOOLBAR, REPORT_REASONS, SHARE_PLATFORMS, LICENSE_TYPES
    global WEBGL_ERRORS, CONSENT_CATEGORIES, SPRING_PRESETS, POPUP_PLACEMENTS
    global USER_PROFILE_FIELDS, GRID_COLUMNS, EMOJI_CATEGORIES, MODEL_PROPERTIES

    api_config = get_api_config()
    API_ENDPOINTS = api_config.get('endpoints', {})
    EMBED_OPTIONS = get_embed_options()
    MATERIAL_OPTIONS = get_material_options()
    QUALITY_PRESETS = get_quality_presets()
    ENVIRONMENT_PRESETS = get_environment_presets()
    AI_ACTIONS = get_ai_actions()
    AI_PROVIDERS = get_ai_providers()
    DOWNLOAD_FORMATS = get_download_formats()
    VISIBILITY_TYPES = get_visibility_types()
    SUBSCRIPTION_TIERS = get_subscription_tiers()
    THUMBNAIL_SIZES = get_thumbnail_sizes()
    MODEL_BADGES = get_model_badges()
    SEARCH_FILTERS = get_search_filters()
    SEARCH_CATEGORIES = get_search_categories()
    ORG_MEMBER_ROLES = get_org_roles()
    THEMES = get_themes()
    VALIDATION_PATTERNS = get_validation_patterns()
    TYPOGRAPHY_SCALE = get_typography()
    THEME_COLORS = get_themes()
    GRADIENT_PRESETS = get_gradients()
    RATING_CONFIG = get_rating_config()
    NOTIFICATION_TYPES = get_notification_types()
    SHADOW_PRESETS = get_shadows()
    BRAND_COLORS = get_brand_colors()
    BREAKPOINTS = get_breakpoints()
    LAYOUT_DIMENSIONS = get_layout_dimensions()
    SPACING_SCALE = get_spacing_scale()
    DATE_FORMATS = get_date_formats()
    MARKDOWN_TOOLBAR = get_markdown_toolbar()
    REPORT_REASONS = get_report_reasons()
    SHARE_PLATFORMS = get_share_platforms()
    LICENSE_TYPES = get_licenses()
    WEBGL_ERRORS = get_webgl_errors()
    CONSENT_CATEGORIES = get_consent_categories()
    SPRING_PRESETS = get_spring_presets()
    POPUP_PLACEMENTS = get_popup_placements()
    USER_PROFILE_FIELDS = get_user_profile_fields()
    GRID_COLUMNS = get_grid_columns()
    EMOJI_CATEGORIES = get_emoji_categories()
    MODEL_PROPERTIES = get_model_properties()


# Initialize constants when module is imported
_init_constants()

# Shared strings
_STRINGS = get_strings_config()
LABELS = get_labels()
HEADERS = _STRINGS['headers']
SUBHEADERS = _STRINGS['subheaders']
MAIN_LABELS = _STRINGS['main_labels']
INFO_CONFIG = _STRINGS['info_config']
LAYOUT_SUMMARY = _STRINGS['layout_summary']
STRING_CONVERSIONS = _STRINGS['string_conversions']
DATE_LABELS = _STRINGS['date_labels']
LICENSE_LABELS = _STRINGS['license_labels']
WEBGL_LABELS = _STRINGS['webgl_labels']
ANIMATION_LABELS = _STRINGS['animation_labels']
PRIVACY_LABELS = _STRINGS['privacy_labels']
MODEL_FIELDS_LABELS = _STRINGS['model_fields_labels']
GRID_LABELS = _STRINGS['grid_labels']
PLACEMENTS_LABELS = _STRINGS['placements_labels']
CODE_SNIPPETS = _STRINGS['code_snippets']
DEFAULTS = get_defaults()
ERROR_MESSAGES = get_error_messages()
DAYJS_TOKENS = get_dayjs_tokens()
STRFTIME_MAP = get_strftime_map()
PERMISSION_TYPES = get_permission_types()
SPRING_FORMULAS = get_spring_formulas()
SPRING_VARIABLES = get_spring_variables()
MARKDOWN_EXAMPLES = get_markdown_examples()
DATES_MESSAGES = _STRINGS.get('messages_dates', {})
CLI_DESCRIPTION = _STRINGS['cli_description']
INTERRUPT_MESSAGE = _STRINGS['interrupt_message']
UNEXPECTED_ERROR = _STRINGS['unexpected_error']


def extract_model_id(url_or_id):
    """Extract model ID from a Sketchfab URL or return raw ID."""
    if re.match(r'^[a-f0-9]{32}$', url_or_id, re.IGNORECASE):
        return url_or_id

    patterns = [
        r'sketchfab\\.com/(?:3d-)?models/[^/]+-([a-f0-9]{32})',
        r'sketchfab\\.com/(?:3d-)?models/([a-f0-9]{32})',
        r'sketchfab\\.com/models/([a-f0-9]{32})',
        r'/([a-f0-9]{32})(?:/embed)?(?:\\?|$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def format_number(num):
    """Format large numbers with K or M suffix."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)
