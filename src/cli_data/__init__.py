"""
CLI Data Loader

Loads configuration data from JSON files in the cli_data directory.
"""

import json
from pathlib import Path
from functools import lru_cache

# Path to the cli_data directory (same as this file's directory)
DATA_DIR = Path(__file__).parent


@lru_cache(maxsize=32)
def load_json(filename: str) -> dict:
    """Load a JSON file from the cli_data directory."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_api_config():
    """Load API configuration."""
    return load_json('api.json')


def get_embed_options():
    """Load embed options."""
    return load_json('embed.json')['options']


def get_material_options():
    """Load material options."""
    return load_json('materials.json')['options']


def get_viewer_config():
    """Load viewer configuration."""
    return load_json('viewer.json')


def get_quality_presets():
    """Load quality presets."""
    return load_json('viewer.json')['quality_presets']


def get_environment_presets():
    """Load environment presets."""
    return load_json('viewer.json')['environment_presets']


def get_ai_config():
    """Load AI tools configuration."""
    return load_json('ai.json')


def get_ai_actions():
    """Load AI actions."""
    return load_json('ai.json')['actions']


def get_ai_providers():
    """Load AI providers."""
    return load_json('ai.json')['providers']


def get_models_config():
    """Load models configuration."""
    return load_json('models.json')


def get_download_formats():
    """Load download formats."""
    return load_json('models.json')['download_formats']


def get_visibility_types():
    """Load visibility types."""
    return load_json('models.json')['visibility_types']


def get_model_badges():
    """Load model badges."""
    return load_json('models.json')['badges']


def get_thumbnail_sizes():
    """Load thumbnail sizes."""
    return load_json('models.json')['thumbnail_sizes']


def get_model_properties():
    """Load model properties."""
    return load_json('models.json')['properties']


def get_subscriptions_config():
    """Load subscriptions configuration."""
    return load_json('subscriptions.json')


def get_subscription_tiers():
    """Load subscription tiers."""
    return load_json('subscriptions.json')['tiers']


def get_org_roles():
    """Load organization roles."""
    return load_json('subscriptions.json')['org_roles']


def get_search_config():
    """Load search configuration."""
    return load_json('search.json')


def get_search_filters():
    """Load search filters."""
    return load_json('search.json')['filters']


def get_search_categories():
    """Load search categories."""
    return load_json('search.json')['categories']


def get_design_config():
    """Load design configuration."""
    return load_json('design.json')


def get_themes():
    """Load themes."""
    return load_json('design.json')['themes']


def get_gradients():
    """Load gradients."""
    return load_json('design.json')['gradients']


def get_shadows():
    """Load shadows."""
    return load_json('design.json')['shadows']


def get_brand_colors():
    """Load brand colors."""
    return load_json('design.json')['brands']


def get_notification_types():
    """Load notification types."""
    return load_json('design.json')['notification_types']


def get_layout_config():
    """Load layout configuration."""
    return load_json('layout.json')


def get_typography():
    """Load typography scale."""
    return load_json('layout.json')['typography']


def get_breakpoints():
    """Load breakpoints."""
    return load_json('layout.json')['breakpoints']


def get_layout_dimensions():
    """Load layout dimensions."""
    return load_json('layout.json')['layout']


def get_spacing_scale():
    """Load spacing scale."""
    return load_json('layout.json')['spacing']


def get_grid_columns():
    """Load grid columns."""
    return load_json('layout.json')['grid_columns']


def get_rating_config():
    """Load rating config."""
    return load_json('layout.json')['rating']


def get_validation_config():
    """Load validation configuration."""
    return load_json('validation.json')


def get_validation_patterns():
    """Load validation patterns."""
    return load_json('validation.json')['validation_patterns']


def get_date_formats():
    """Load date formats."""
    return load_json('validation.json')['date_formats']


def get_user_profile_fields():
    """Load user profile fields."""
    return load_json('validation.json')['user_profile_fields']


def get_markdown_config():
    """Load markdown configuration."""
    return load_json('markdown.json')


def get_markdown_toolbar():
    """Load markdown toolbar."""
    return load_json('markdown.json')['toolbar']


def get_social_config():
    """Load social configuration."""
    return load_json('social.json')


def get_report_reasons():
    """Load report reasons."""
    return load_json('social.json')['report_reasons']


def get_share_platforms():
    """Load share platforms."""
    return load_json('social.json')['share_platforms']


def get_emoji_categories():
    """Load emoji categories."""
    return load_json('social.json')['emoji_categories']


def get_licenses():
    """Load license types."""
    return load_json('licenses.json')['licenses']


def get_webgl_errors():
    """Load WebGL errors."""
    return load_json('webgl.json')['errors']


def get_consent_categories():
    """Load consent categories."""
    return load_json('privacy.json')['consent_categories']


def get_animation_config():
    """Load animation configuration."""
    return load_json('animation.json')


def get_spring_presets():
    """Load spring presets."""
    return load_json('animation.json')['spring_presets']


def get_popup_placements():
    """Load popup placements."""
    return load_json('animation.json')['popup_placements']


# Convenience function to load all data
def load_all_data():
    """Load all configuration data."""
    return {
        'api': get_api_config(),
        'embed': get_embed_options(),
        'materials': get_material_options(),
        'viewer': get_viewer_config(),
        'ai': get_ai_config(),
        'models': get_models_config(),
        'subscriptions': get_subscriptions_config(),
        'search': get_search_config(),
        'design': get_design_config(),
        'layout': get_layout_config(),
        'validation': get_validation_config(),
        'markdown': get_markdown_config(),
        'social': get_social_config(),
        'licenses': get_licenses(),
        'webgl': get_webgl_errors(),
        'privacy': get_consent_categories(),
        'animation': get_animation_config(),
    }

def get_arguments_config():
    """Load CLI arguments configuration."""
    return load_json('arguments.json')


def get_commands():
    """Load command definitions."""
    return load_json('arguments.json')['commands']


def get_strings_config():
    """Load strings configuration."""
    return load_json('strings.json')


def get_demos():
    """Load demo paths."""
    return load_json('strings.json')['demos']


def get_info_strings():
    """Load info command strings."""
    return load_json('strings.json')['info']


def get_messages():
    """Load message templates."""
    return load_json('strings.json')['messages']


def get_labels():
    """Load UI labels."""
    return load_json('strings.json')['labels']


def get_symbols():
    """Load symbols/icons."""
    return load_json('strings.json')['symbols']


def get_config_options():
    """Load config command options."""
    return load_json('strings.json')['config_options']


def get_api_options():
    """Load api command options."""
    return load_json('strings.json')['api_options']


def get_design_options():
    """Load design command options."""
    return load_json('strings.json')['design_options']


def get_layout_options():
    """Load layout command options."""
    return load_json('strings.json')['layout_options']


def get_defaults():
    """Load default values."""
    return load_json('strings.json')['defaults']


def get_file_units():
    """Load file size units."""
    return load_json('strings.json')['file_units']


def get_iframe_template():
    """Load iframe template."""
    return load_json('strings.json')['iframe_template']


def get_markdown_examples():
    """Load markdown examples."""
    return load_json('strings.json')['markdown_examples']


def get_dayjs_tokens():
    """Load Day.js token reference."""
    return load_json('strings.json')['dayjs_tokens']


def get_strftime_map():
    """Load strftime mapping for Day.js patterns."""
    return load_json('strings.json')['strftime_map']


def get_permission_types():
    """Load license permission types."""
    return load_json('strings.json')['permission_types']


def get_spring_formulas():
    """Load spring physics formulas."""
    return load_json('strings.json')['spring_formulas']


def get_spring_variables():
    """Load spring physics variables."""
    return load_json('strings.json')['spring_variables']


def get_code_snippets():
    """Load code snippets."""
    return load_json('strings.json')['code_snippets']


def get_http_config():
    """Load HTTP configuration (user agent, timeout)."""
    return load_json('strings.json')['http']


def get_url_templates():
    """Load URL templates."""
    return load_json('strings.json')['url_templates']


def get_model_id_patterns():
    """Load model ID extraction patterns."""
    return load_json('strings.json')['model_id_patterns']


def get_model_id_regex():
    """Load model ID validation regex."""
    return load_json('strings.json')['model_id_regex']


def get_geometry_labels():
    """Load geometry component labels."""
    return load_json('strings.json')['geometry_labels']


def get_yes_no():
    """Load yes/no labels."""
    return load_json('strings.json')['yes_no']


def get_number_suffixes():
    """Load number format suffixes (K, M)."""
    return load_json('strings.json')['number_suffixes']


def get_gui_file():
    """Load GUI filename."""
    return load_json('strings.json')['gui_file']


def get_separator_lengths():
    """Load separator line lengths."""
    return load_json('strings.json')['separator_lengths']


def get_constants():
    """Load URL constants (api base, base url)."""
    return load_json('strings.json')['constants']


def get_headers():
    """Load section headers."""
    return load_json('strings.json')['headers']


def get_subheaders():
    """Load section subheaders."""
    return load_json('strings.json')['subheaders']


def get_config_defaults():
    """Load configuration defaults."""
    return load_json('strings.json')['config_defaults']


def get_embed_defaults():
    """Load embed defaults (width, height)."""
    return load_json('strings.json')['embed_defaults']


def get_viewer_info_template():
    """Load viewer info label template."""
    return load_json('strings.json')['viewer_info_template']


def get_window_sizes():
    """Load default window sizes."""
    return load_json('strings.json')['window_sizes']


def get_search_defaults():
    """Load search defaults."""
    return load_json('strings.json')['search_defaults']


def get_truncate_lengths():
    """Load truncate lengths."""
    return load_json('strings.json')['truncate_lengths']


def get_css_comments():
    """Load CSS/SCSS comment templates."""
    return load_json('strings.json')['css_comments']


def get_format_strings():
    """Load format string templates."""
    return load_json('strings.json')['format_strings']


def get_error_messages():
    """Load error message templates."""
    return load_json('strings.json')['error_messages']


def get_valid_invalid():
    """Load valid/invalid message templates."""
    return load_json('strings.json')['valid_invalid']


def get_result_indicators():
    """Load result indicator strings."""
    return load_json('strings.json')['result_indicators']


def get_info_config():
    """Load info command config strings."""
    return load_json('strings.json')['info_config']


def get_stats_labels():
    """Load stats command labels."""
    return load_json('strings.json')['stats_labels']


def get_user_labels():
    """Load user command labels."""
    return load_json('strings.json')['user_labels']


def get_tier_labels():
    """Load tier command labels."""
    return load_json('strings.json')['tier_labels']


def get_design_summary():
    """Load design command summary strings."""
    return load_json('strings.json')['design_summary']


def get_layout_summary():
    """Load layout command summary strings."""
    return load_json('strings.json')['layout_summary']


def get_string_conversions():
    """Load string conversion labels."""
    return load_json('strings.json')['string_conversions']


def get_date_labels():
    """Load date command labels."""
    return load_json('strings.json')['date_labels']


def get_license_labels():
    """Load license command labels."""
    return load_json('strings.json')['license_labels']


def get_webgl_labels():
    """Load webgl command labels."""
    return load_json('strings.json')['webgl_labels']


def get_animation_labels():
    """Load animation command labels."""
    return load_json('strings.json')['animation_labels']


def get_privacy_labels():
    """Load privacy command labels."""
    return load_json('strings.json')['privacy_labels']


def get_model_fields_labels():
    """Load model fields command labels."""
    return load_json('strings.json')['model_fields_labels']


def get_grid_labels():
    """Load grid command labels."""
    return load_json('strings.json')['grid_labels']


def get_placements_labels():
    """Load placements command labels."""
    return load_json('strings.json')['placements_labels']


def get_main_labels():
    """Load main/common labels."""
    return load_json('strings.json')['main_labels']


def get_print_templates():
    """Load print formatting templates."""
    return load_json('strings.json')['print_templates']


def get_cli_description():
    """Load CLI description."""
    return load_json('strings.json')['cli_description']


def get_interrupt_message():
    """Load interrupt message."""
    return load_json('strings.json')['interrupt_message']


def get_unexpected_error():
    """Load unexpected error template."""
    return load_json('strings.json')['unexpected_error']


def get_messages_embed():
    """Load embed command messages."""
    return load_json('strings.json')['messages_embed']


def get_messages_config():
    """Load config command messages."""
    return load_json('strings.json')['messages_config']


def get_messages_api():
    """Load api command messages."""
    return load_json('strings.json')['messages_api']


def get_messages_stats():
    """Load stats command messages."""
    return load_json('strings.json')['messages_stats']


def get_messages_search():
    """Load search command messages."""
    return load_json('strings.json')['messages_search']


def get_messages_user():
    """Load user command messages."""
    return load_json('strings.json')['messages_user']


def get_messages_thumbnail():
    """Load thumbnail command messages."""
    return load_json('strings.json')['messages_thumbnail']


def get_messages_categories():
    """Load categories command messages."""
    return load_json('strings.json')['messages_categories']


def get_messages_licenses():
    """Load licenses command messages."""
    return load_json('strings.json')['messages_licenses']


def get_messages_dates():
    """Load dates command messages."""
    return load_json('strings.json')['messages_dates']


def get_embed_params():
    """Load embed parameter names."""
    return load_json('strings.json')['embed_params']


def get_config_keys():
    """Load config JSON keys."""
    return load_json('strings.json')['config_keys']


def get_api_keys():
    """Load API placeholder keys."""
    return load_json('strings.json')['api_keys']


def get_data_keys():
    """Load data/response JSON keys."""
    return load_json('strings.json')['data_keys']


def get_search_params():
    """Load search query parameters."""
    return load_json('strings.json')['search_params']


def get_content_types():
    """Load content type strings."""
    return load_json('strings.json')['content_types']


def get_file_extensions():
    """Load file extension strings."""
    return load_json('strings.json')['file_extensions']


def get_url_prefixes():
    """Load URL prefix strings."""
    return load_json('strings.json')['url_prefixes']


def get_css_selectors():
    """Load CSS selector strings."""
    return load_json('strings.json')['css_selectors']


def get_html_parser():
    """Load HTML parser name."""
    return load_json('strings.json')['html_parser']


def get_placeholders():
    """Load placeholder strings."""
    return load_json('strings.json')['placeholders']


def get_root_selector():
    """Load CSS root selector."""
    return load_json('strings.json')['root_selector']


def get_css_class_prefix():
    """Load CSS class prefixes."""
    return load_json('strings.json')['css_class_prefix']


def get_scss_syntax():
    """Load SCSS syntax strings."""
    return load_json('strings.json')['scss_syntax']


def get_thumbnail_defaults():
    """Load thumbnail default values."""
    return load_json('strings.json')['thumbnail_defaults']


def get_direction_names():
    """Load direction name list."""
    return load_json('strings.json')['direction_names']


def get_center_label():
    """Load center label string."""
    return load_json('strings.json')['center_label']


def get_theme_suffix():
    """Load theme suffix string."""
    return load_json('strings.json')['theme_suffix']


def get_views_label():
    """Load views label template."""
    return load_json('strings.json')['views_label']


def get_ellipsis():
    """Load ellipsis string."""
    return load_json('strings.json')['ellipsis']


def get_truncate_suffix():
    """Load truncate suffix string."""
    return load_json('strings.json')['truncate_suffix']