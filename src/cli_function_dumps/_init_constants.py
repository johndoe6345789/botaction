# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def _init_constants():
    """Initialize all constants from JSON files."""
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
    THEME_COLORS = get_themes()  # Same as THEMES
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
