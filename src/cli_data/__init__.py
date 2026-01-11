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