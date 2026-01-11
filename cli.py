#!/usr/bin/env python3
"""
Sketchfab Model Tools CLI

A command-line interface for working with Sketchfab 3D models.
Supports fetching, decrypting, inspecting, exporting models, and various utilities.

Based on analysis of Sketchfab's JavaScript architecture including:
- Viewer configuration and embed options
- API endpoints and data structures
- AI tools integration (text-to-3D, image-to-3D)
- Material and rendering options
- URL utilities and query parsing
"""

import argparse
import sys
import json
from pathlib import Path
import http.cookiejar
from urllib.parse import urljoin, urlparse, urlencode, parse_qs
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import data loader
from cli_data import (
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
    get_url_templates, get_strftime_map, get_strings_config
)

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
    """Helper to lazy-load data from JSON."""
    cache = {}
    def wrapper():
        if cache_attr not in cache:
            cache[cache_attr] = getter_func()
        return cache[cache_attr]
    return wrapper

# Create lazy properties for all data
API_ENDPOINTS = None  # Loaded from api.json
EMBED_OPTIONS = None  # Loaded from embed.json
MATERIAL_OPTIONS = None  # Loaded from materials.json
QUALITY_PRESETS = None  # Loaded from viewer.json
ENVIRONMENT_PRESETS = None  # Loaded from viewer.json
AI_ACTIONS = None  # Loaded from ai.json
AI_PROVIDERS = None  # Loaded from ai.json
DOWNLOAD_FORMATS = None  # Loaded from models.json
VISIBILITY_TYPES = None  # Loaded from models.json
SUBSCRIPTION_TIERS = None  # Loaded from subscriptions.json
THUMBNAIL_SIZES = None  # Loaded from models.json
MODEL_BADGES = None  # Loaded from models.json
SEARCH_FILTERS = None  # Loaded from search.json
SEARCH_CATEGORIES = None  # Loaded from search.json
ORG_MEMBER_ROLES = None  # Loaded from subscriptions.json
THEMES = None  # Loaded from design.json
VALIDATION_PATTERNS = None  # Loaded from validation.json
TYPOGRAPHY_SCALE = None  # Loaded from layout.json
THEME_COLORS = None  # Loaded from design.json
GRADIENT_PRESETS = None  # Loaded from design.json
RATING_CONFIG = None  # Loaded from layout.json
NOTIFICATION_TYPES = None  # Loaded from design.json
SHADOW_PRESETS = None  # Loaded from design.json
BRAND_COLORS = None  # Loaded from design.json
BREAKPOINTS = None  # Loaded from layout.json
LAYOUT_DIMENSIONS = None  # Loaded from layout.json
SPACING_SCALE = None  # Loaded from layout.json
DATE_FORMATS = None  # Loaded from validation.json
MARKDOWN_TOOLBAR = None  # Loaded from markdown.json
REPORT_REASONS = None  # Loaded from social.json
SHARE_PLATFORMS = None  # Loaded from social.json
LICENSE_TYPES = None  # Loaded from licenses.json
WEBGL_ERRORS = None  # Loaded from webgl.json
CONSENT_CATEGORIES = None  # Loaded from privacy.json
SPRING_PRESETS = None  # Loaded from animation.json
POPUP_PLACEMENTS = None  # Loaded from animation.json
USER_PROFILE_FIELDS = None  # Loaded from validation.json
GRID_COLUMNS = None  # Loaded from layout.json
EMOJI_CATEGORIES = None  # Loaded from social.json
MODEL_PROPERTIES = None  # Loaded from models.json


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


# Initialize constants on module load
_init_constants()

# Shared string resources
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

from src.sketchfab_fetcher import SketchfabFetcher
from src.model_decryptor import SketchfabDecryptor, decrypt_model
from src.binz_reader import BinzReader


def cmd_fetch(args):
    """Fetch model information and download files."""
    msgs = get_messages()['fetch']
    print(msgs['fetching'].format(url=args.url))

    fetcher = SketchfabFetcher()
    result = fetcher.fetch_model(args.url)

    if result['error']:
        print(msgs['error'].format(error=result['error']))
        return 1

    # Print summary
    api_data = result.get('api_data', {})
    if api_data:
        print(f"\n{msgs['model'].format(name=api_data.get('name', 'Unknown'))}")
        print(msgs['author'].format(username=api_data.get('user', {}).get('username', 'Unknown')))
        print(msgs['views'].format(count=api_data.get('viewCount', 0)))
        print(msgs['likes'].format(count=api_data.get('likeCount', 0)))

    # Download files if requested
    if args.download:
        print(f"\n{msgs['downloading'].format(output_dir=args.output_dir)}")
        downloaded = fetcher.download_model_files(
            result['model_id'],
            output_dir=args.output_dir
        )
        print(msgs['downloaded'].format(count=len(downloaded)))
        for name, path in downloaded.items():
            print(f"  {name}: {path}")

    # Save metadata
    if args.save_meta:
        meta_file = Path(args.output_dir) / f"{result['model_id']}_metadata.json"
        with open(meta_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(msgs['metadata_saved'].format(meta_file=meta_file))

    return 0


def cmd_decrypt(args):
    """Decrypt an encrypted .binz file."""
    msgs = get_messages()['decrypt']
    binz_path = Path(args.binz_file)
    params_path = Path(args.params_file) if args.params_file else None

    if not binz_path.exists():
        print(msgs['error_binz_not_found'].format(path=binz_path))
        return 1

    if params_path and not params_path.exists():
        print(msgs['error_params_not_found'].format(path=params_path))
        return 1

    print(msgs['decrypting'].format(name=binz_path.name))

    try:
        if params_path:
            # Use the convenience function
            decrypted_data = decrypt_model(binz_path, params_path)
        else:
            # Manual decryption with key
            if not args.key:
                print(msgs['error_need_key'])
                return 1

            try:
                from Crypto.Cipher import AES
                from Crypto.Util.Padding import unpad
            except ImportError:
                print(msgs['error_pycryptodome'])
                return 1

            decryptor = SketchfabDecryptor()
            key, iv = decryptor.decode_encryption_params(args.key)

            # Read and decrypt
            with open(binz_path, 'rb') as f:
                encrypted_data = f.read()

            # Decrypt AES-256-CBC
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

            # Try to decompress if it looks compressed
            import zlib
            if len(decrypted_data) >= 2 and decrypted_data[0] == 0x78 and decrypted_data[1] in (0x01, 0x9C, 0xDA):
                try:
                    decrypted_data = zlib.decompress(decrypted_data)
                except:
                    pass  # Not compressed, use as-is

        # Save decrypted file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

        print(msgs['decrypted_bytes'].format(count=len(decrypted_data)))
        print(msgs['saved_to'].format(path=output_path))

        # Inspect if requested
        if args.inspect:
            reader = BinzReader()
            info = reader.inspect(decrypted_data)
            print(f"\n{msgs['inspection_header']}")
            for key, value in info.items():
                print(f"  {key}: {value}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_inspect(args):
    """Inspect a .binz file."""
    msgs = get_messages()['inspect']
    symbols = get_symbols()
    binz_path = Path(args.binz_file)

    if not binz_path.exists():
        print(f"Error: File not found: {binz_path}")
        return 1

    print(msgs['inspecting'].format(name=binz_path.name))
    print(msgs['size'].format(size=binz_path.stat().st_size))

    try:
        reader = BinzReader()
        data = reader.read_file(binz_path)
        print(msgs['decompressed_size'].format(size=len(data)))

        info = reader.inspect(data)
        print(f"\n{msgs['data_structure']}")
        for key, value in info.items():
            print(f"  {key}: {value}")

        # Try to load params and parse geometry
        params_path = binz_path.with_suffix('.binz').parent / f"{binz_path.stem}_params.json"
        if params_path.exists():
            print(f"\n{msgs['found_params'].format(name=params_path.name)}")
            with open(params_path, 'r') as f:
                params = json.load(f)

            print(msgs['parsing_geometry'])
            geometry = reader.parse_geometry_from_params(data, params)

            if geometry.vertices:
                print(f"{symbols['checkmark']} {msgs['found_vertices'].format(count=geometry.vertex_count)}")
            if geometry.normals:
                print(f"{symbols['checkmark']} {msgs['found_normals'].format(count=geometry.normal_count)}")
            if geometry.uvs:
                print(f"{symbols['checkmark']} {msgs['found_uvs'].format(count=geometry.uv_count)}")
            if geometry.indices:
                print(f"{symbols['checkmark']} {msgs['found_indices'].format(count=geometry.index_count)}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_export(args):
    """Export decrypted model to 3MF format."""
    msgs = get_messages()['export']
    symbols = get_symbols()
    try:
        from src.export_3mf import Model3MFExporter
    except ImportError:
        print(msgs['error_import'])
        return 1

    binz_path = Path(args.binz_file)
    output_path = Path(args.output)

    if not binz_path.exists():
        print(msgs['error_not_found'].format(path=binz_path))
        return 1

    print(msgs['exporting'].format(name=binz_path.name))

    try:
        exporter = Model3MFExporter()
        exporter.load_from_binary(binz_path)
        exporter.export_3mf(output_path)

        print(f"{symbols['checkmark']} {msgs['exported'].format(path=output_path)}")
        print(f"  {msgs['vertices'].format(count=len(exporter.vertices))}")
        print(f"  {msgs['triangles'].format(count=len(exporter.triangles))}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_demo(args):
    """Launch a demonstration script."""
    msgs = get_messages()['demo']
    demos = get_demos()

    if args.demo_name not in demos:
        print(msgs['error_unknown'].format(name=args.demo_name, available=', '.join(demos.keys())))
        return 1

    demo_path = Path(__file__).parent / demos[args.demo_name]
    if not demo_path.exists():
        print(msgs['error_not_found'].format(path=demo_path))
        return 1

    print(msgs['launching'].format(name=args.demo_name))
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(demo_path)])
        return result.returncode
    except Exception as e:
        print(msgs['error_launch'].format(error=e))
        return 1


def cmd_gui(args):
    """Launch the graphical user interface."""
    msgs = get_messages()['gui']
    gui_file = get_gui_file()
    gui_path = Path(__file__).parent / gui_file
    if not gui_path.exists():
        print(msgs['error_not_found'].format(path=gui_path))
        return 1

    print(msgs['launching'])
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(gui_path)])
        return result.returncode
    except Exception as e:
        print(msgs['error_launch'].format(error=e))
        return 1


def cmd_viewer(args):
    """Launch the 3D model viewer."""
    msgs = get_messages()['viewer']
    window_sizes = get_window_sizes() if hasattr(sys.modules[__name__], 'get_window_sizes') else {'min_width': 800, 'min_height': 600}
    try:
        from PyQt6.QtWidgets import QApplication
        from src.model_viewer import ModelViewerPanel
        import sys
    except ImportError as e:
        print(msgs['error_packages'].format(error=e))
        print(msgs['install_hint'])
        return 1

    print(msgs['launching'])

    try:
        # Create Qt application
        app = QApplication(sys.argv)

        # Create viewer window
        from PyQt6.QtWidgets import QMainWindow
        window = QMainWindow()
        window.setWindowTitle(msgs['window_title'])
        window.setMinimumSize(800, 600)

        # Create viewer panel
        viewer = ModelViewerPanel()
        window.setCentralWidget(viewer)

        # Load model if specified
        if args.binz_file:
            binz_path = Path(args.binz_file)
            if binz_path.exists():
                print(msgs['loading_model'].format(path=binz_path))
                # Look for params file
                params_path = binz_path.with_name(binz_path.stem + "_params.json")
                if not params_path.exists():
                    params_path = None

                if viewer.viewer.load_model(str(binz_path), str(params_path) if params_path else None):
                    vertex_count = viewer.viewer.geometry.vertex_count if viewer.viewer.geometry else 0
                    triangle_count = viewer.viewer.geometry.triangle_count if viewer.viewer.geometry else 0
                    viewer.info_label.setText(
                        f"Loaded: {binz_path.name} | "
                        f"Vertices: {vertex_count:,} | "
                        f"Triangles: {triangle_count:,}"
                    )
                    print(msgs['model_loaded'].format(vertices=vertex_count, triangles=triangle_count))
                else:
                    print(msgs['load_failed'].format(path=binz_path))
            else:
                print(msgs['not_found'].format(path=binz_path))

        # Show window
        window.show()

        # Run application
        return app.exec()

    except Exception as e:
        print(msgs['error_launch'].format(error=e))
        return 1


def cmd_info(args):
    """Show information about available commands."""
    info = get_info_strings()
    sep = info['separator'] * info['separator_length']

    print(info['title'])
    print(sep)
    print()

    # Print each section
    for section_key, section in info['sections'].items():
        print(section['title'])
        for cmd in section['commands']:
            print(f"  {cmd['name']:14}- {cmd['description']}")
        print()

    print(INFO_CONFIG['config_constants_header'])
    print(f"  {INFO_CONFIG['api_base_url']} {SKETCHFAB_API_BASE}")
    print(
        INFO_CONFIG['embed_options_count'].format(
            count=len(EMBED_OPTIONS)
        )
    )
    print(
        INFO_CONFIG['quality_presets_list'].format(
            list=', '.join(QUALITY_PRESETS.keys())
        )
    )
    print(
        INFO_CONFIG['environment_presets_list'].format(
            list=', '.join(ENVIRONMENT_PRESETS.keys())
        )
    )
    print(
        INFO_CONFIG['ai_providers_list'].format(
            list=', '.join(AI_PROVIDERS.keys())
        )
    )
    print(
        INFO_CONFIG['download_formats_list'].format(
            list=', '.join(DOWNLOAD_FORMATS)
        )
    )
    print(
        INFO_CONFIG['brand_colors_count'].format(
            count=len(BRAND_COLORS)
        )
    )
    print(
        INFO_CONFIG['breakpoints_info'].format(
            count=len(BREAKPOINTS),
            list=', '.join(BREAKPOINTS.keys())
        )
    )
    print(
        INFO_CONFIG['license_types_count'].format(
            count=len(LICENSE_TYPES)
        )
    )
    print(
        INFO_CONFIG['spring_presets_count'].format(
            count=len(SPRING_PRESETS)
        )
    )
    print()
    print(info['footer'])


def cmd_scrape(args):
    """Scrape webpage content using requests and BeautifulSoup."""
    msgs = get_messages()['scrape']
    http_config = get_http_config()
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        print(msgs['error_packages'].format(error=e))
        print(msgs['install_hint'])
        return 1

    print(msgs['scraping'].format(url=args.url))

    try:
        # Make request
        headers = {
            'User-Agent': http_config['user_agent']
        }
        response = requests.get(args.url, headers=headers, timeout=http_config['timeout'])
        response.raise_for_status()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        if args.title:
            title = soup.title.string if soup.title else "No title found"
            print(msgs['title'].format(title=title))

        if args.links:
            links = soup.find_all('a', href=True)
            print(msgs['found_links'].format(count=len(links)))
            for i, link in enumerate(links[:args.max_links]):
                print(f"  {i+1}. {link.get('href')} - {link.get_text().strip()[:50]}")

        if args.text:
            # Extract text content
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            print(msgs['text_content'].format(count=len(lines)))
            for line in lines[:args.max_lines]:
                print(f"  {line}")

        if args.save_html:
            output_path = Path(args.save_html)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(msgs['html_saved'].format(path=output_path))

        return 0

    except requests.RequestException as e:
        print(msgs['request_error'].format(error=e))
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_session(args):
    """Demonstrate session management with cookiejar."""
    msgs = get_messages()['session']
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        print(f"Error: Missing required packages: {e}")
        print("Install with: pip install requests beautifulsoup4")
        return 1

    print(msgs['demonstrating'])

    try:
        # Create a cookiejar and session
        jar = http.cookiejar.CookieJar()
        session = requests.Session()
        session.cookies = jar

        # First request to establish session
        print(msgs['initial_request'].format(url=args.url))
        response1 = session.get(args.url, timeout=10)
        response1.raise_for_status()

        print(msgs['response_status'].format(status=response1.status_code))
        print(msgs['cookies_received'].format(count=len(jar)))

        # List cookies
        for cookie in jar:
            print(f"  {cookie.name}: {cookie.value}")

        # Optional second request to demonstrate persistence
        if args.follow_link:
            soup = BeautifulSoup(response1.content, 'html.parser')
            first_link = soup.find('a', href=True)
            if first_link:
                next_url = first_link['href']
                if not next_url.startswith('http'):
                    from urllib.parse import urljoin
                    next_url = urljoin(args.url, next_url)

                print(f"\n{msgs['following_link'].format(url=next_url)}")
                response2 = session.get(next_url, timeout=10)
                response2.raise_for_status()
                print(msgs['followup_status'].format(status=response2.status_code))
                print(msgs['cookies_after'].format(count=len(jar)))
            else:
                print(msgs['no_links'])

        # Save cookies if requested
        if args.save_cookies:
            cookie_file = Path(args.save_cookies)
            jar.save(cookie_file, ignore_discard=True, ignore_expires=True)
            print(msgs['cookies_saved'].format(path=cookie_file))

        return 0

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_download_js(args):
    """Download all JavaScript files from a website."""
    msgs = get_messages()['download_js']
    http_config = get_http_config()
    try:
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin, urlparse
        import json
    except ImportError as e:
        print(f"Error: Missing required packages: {e}")
        print("Install with: pip install requests beautifulsoup4")
        return 1

    print(msgs['downloading'].format(url=args.url))

    try:
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Set for tracking downloaded files and processed URLs
        downloaded_files = set()
        processed_urls = set()

        # Queue of URLs to process
        url_queue = [args.url]

        headers = {
            'User-Agent': http_config['user_agent']
        }

        while url_queue and (not args.max_pages or len(processed_urls) < args.max_pages):
            current_url = url_queue.pop(0)

            if current_url in processed_urls:
                continue

            processed_urls.add(current_url)
            print(msgs['processing'].format(url=current_url))

            try:
                response = requests.get(current_url, headers=headers, timeout=10)
                response.raise_for_status()

                content_type = response.headers.get('content-type', '').lower()

                # Process HTML pages
                if 'text/html' in content_type:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Find all script tags
                    script_tags = soup.find_all('script', src=True)
                    for script in script_tags:
                        js_url = urljoin(current_url, script['src'])

                        # Skip if already downloaded or external domain (unless allowed)
                        if js_url in downloaded_files:
                            continue

                        parsed_js = urlparse(js_url)
                        parsed_base = urlparse(args.url)

                        if not args.external_domains and parsed_js.netloc != parsed_base.netloc:
                            if args.verbose:
                                print(f"  Skipping external JS: {js_url}")
                            continue

                        # Download JS file
                        try:
                            js_response = requests.get(js_url, headers=headers, timeout=10)
                            js_response.raise_for_status()

                            # Create filename from URL
                            js_filename = parsed_js.path.split('/')[-1]
                            if not js_filename or not js_filename.endswith('.js'):
                                js_filename = f"script_{len(downloaded_files)}.js"

                            output_path = output_dir / js_filename

                            # Handle duplicate filenames
                            counter = 1
                            while output_path.exists():
                                name_parts = js_filename.rsplit('.', 1)
                                if len(name_parts) == 2:
                                    output_path = output_dir / f"{name_parts[0]}_{counter}.{name_parts[1]}"
                                else:
                                    output_path = output_dir / f"{js_filename}_{counter}"
                                counter += 1

                            with open(output_path, 'wb') as f:
                                f.write(js_response.content)

                            downloaded_files.add(js_url)
                            print(f"  Downloaded: {js_filename} ({len(js_response.content)} bytes)")

                        except requests.RequestException as e:
                            print(f"  Failed to download {js_url}: {e}")

                    # Find links to other pages if recursive
                    if args.recursive:
                        for link in soup.find_all('a', href=True):
                            link_url = urljoin(current_url, link['href'])
                            parsed_link = urlparse(link_url)
                            parsed_base = urlparse(args.url)

                            # Only follow links on the same domain
                            if parsed_link.netloc == parsed_base.netloc and link_url not in processed_urls:
                                # Check if it's an HTML page (not just a file)
                                path = parsed_link.path.lower()
                                if not path or path.endswith('/') or '.' not in path.split('/')[-1]:
                                    url_queue.append(link_url)

                # Process JSON files that might contain JS references and API endpoints
                elif 'application/json' in content_type and args.parse_json:
                    try:
                        json_data = response.json()

                        # Recursively search for URLs in JSON
                        def find_urls(obj, path=""):
                            urls = []
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    current_path = f"{path}.{key}" if path else key
                                    if isinstance(value, str):
                                        # Check if it looks like a URL (JS files or API endpoints)
                                        if value.startswith(('http://', 'https://', '//')):
                                            urls.append(value)
                                        elif value.startswith('/') and ('.js' in value or '/api/' in value or value.endswith('.json')):
                                            # Relative URL that looks like JS or API
                                            urls.append(urljoin(args.url, value))
                                    else:
                                        urls.extend(find_urls(value, current_path))
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    urls.extend(find_urls(item, f"{path}[{i}]"))
                            return urls

                        found_urls = find_urls(json_data)

                        # Separate JS files from potential API endpoints
                        js_urls = []
                        api_urls = []

                        for found_url in found_urls:
                            if '.js' in found_url:
                                js_urls.append(found_url)
                            elif found_url.endswith('.json') or '/api/' in found_url or found_url.count('/') > 3:
                                # Likely an API endpoint or JSON file
                                api_urls.append(found_url)

                        # Download JS files
                        for js_url in js_urls:
                            if js_url in downloaded_files:
                                continue

                            try:
                                js_response = requests.get(js_url, headers=headers, timeout=10)
                                js_response.raise_for_status()

                                parsed_js = urlparse(js_url)
                                js_filename = parsed_js.path.split('/')[-1] or f"json_script_{len(downloaded_files)}.js"

                                output_path = output_dir / js_filename
                                counter = 1
                                while output_path.exists():
                                    name_parts = js_filename.rsplit('.', 1)
                                    if len(name_parts) == 2:
                                        output_path = output_dir / f"{name_parts[0]}_{counter}.{name_parts[1]}"
                                    else:
                                        output_path = output_dir / f"{js_filename}_{counter}"
                                    counter += 1

                                with open(output_path, 'wb') as f:
                                    f.write(js_response.content)

                                downloaded_files.add(js_url)
                                print(f"  Downloaded from JSON: {js_filename} ({len(js_response.content)} bytes)")

                            except requests.RequestException as e:
                                if args.verbose:
                                    print(f"  Failed to download JSON JS {js_url}: {e}")

                        # Add API endpoints to processing queue for recursive discovery
                        for api_url in api_urls:
                            if api_url not in processed_urls:
                                parsed_api = urlparse(api_url)
                                parsed_base = urlparse(args.url)

                                # Only follow APIs on the same domain (unless external domains allowed)
                                if args.external_domains or parsed_api.netloc == parsed_base.netloc:
                                    url_queue.append(api_url)
                                    if args.verbose:
                                        print(f"  Found API endpoint in JSON: {api_url}")

                    except json.JSONDecodeError:
                        if args.verbose:
                            print(f"  Could not parse JSON from {current_url}")

            except requests.RequestException as e:
                print(f"Failed to process {current_url}: {e}")

        print(f"\nCompleted! Downloaded {len(downloaded_files)} JavaScript files to {output_dir}")
        print(f"Processed {len(processed_urls)} pages")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


# =============================================================================
# NEW COMMANDS - Based on Sketchfab JavaScript Analysis
# =============================================================================

def cmd_embed(args):
    """Generate embed URL or iframe code for a Sketchfab model."""
    model_id = extract_model_id(args.model_id_or_url)
    
    if not model_id:
        print(
            ERROR_MESSAGES['model_id_extract_failed'].format(
                input=args.model_id_or_url
            )
        )
        return 1
    
    # Build embed parameters
    params = {}
    
    if args.autostart:
        params['autostart'] = 1
    if args.autospin is not None:
        params['autospin'] = args.autospin
    if args.no_ui:
        params['ui_controls'] = 0
        params['ui_infos'] = 0
        params['ui_inspector'] = 0
    if not args.watermark:
        params['ui_watermark'] = 0
    if args.transparent:
        params['transparent'] = 1
    if args.no_scrollwheel:
        params['scrollwheel'] = 0
    if args.animation_autoplay:
        params['animation_autoplay'] = 1
    if args.annotation is not None:
        params['annotation'] = args.annotation
    if args.preload:
        params['preload'] = 1
    
    # Build URL
    embed_url = f"{SKETCHFAB_BASE_URL}/models/{model_id}/embed"
    if params:
        embed_url += '?' + urlencode(params)
    
    print(f"Model ID: {model_id}")
    print(f"\nEmbed URL:")
    print(f"  {embed_url}")
    
    if args.iframe:
        width = args.width or 640
        height = args.height or 480
        iframe = f'''<iframe title="Sketchfab Model" width="{width}" height="{height}" src="{embed_url}" frameborder="0" allow="autoplay; fullscreen; xr-spatial-tracking" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>'''
        print(f"\niFrame Code:")
        print(f"  {iframe}")
    
    if args.copy:
        try:
            import pyperclip
            pyperclip.copy(embed_url if not args.iframe else iframe)
            print("\n✓ Copied to clipboard!")
        except ImportError:
            print("\n(Install pyperclip to enable clipboard copy: pip install pyperclip)")
    
    return 0


def cmd_config(args):
    """Display or generate viewer configuration."""
    
    if args.list_presets:
        print("Quality Presets:")
        print("=" * 50)
        for name, preset in QUALITY_PRESETS.items():
            print(f"\n{name.upper()}:")
            for key, value in preset.items():
                print(f"  {key}: {value}")
        
        print("\n\nEnvironment Presets:")
        print("=" * 50)
        for name, preset in ENVIRONMENT_PRESETS.items():
            print(f"\n{name.upper()}:")
            for key, value in preset.items():
                print(f"  {key}: {value}")
        return 0
    
    if args.list_embed_options:
        print("Embed URL Options:")
        print("=" * 50)
        for name, info in EMBED_OPTIONS.items():
            type_str = info['type'].__name__
            default = info['default']
            desc = info['desc']
            print(f"\n{name}:")
            print(f"  Type: {type_str}")
            print(f"  Default: {default}")
            print(f"  Description: {desc}")
        return 0
    
    if args.list_materials:
        print("Material Display Options:")
        print("=" * 50)
        for name, desc in MATERIAL_OPTIONS.items():
            print(f"  {name}: {desc}")
        return 0
    
    if args.generate:
        config = {
            'renderer': {
                'antialias': True,
                'alpha': False,
                'powerPreference': 'high-performance',
            },
            'camera': {
                'fov': args.fov or 45,
                'near': 0.1,
                'far': 10000,
            },
            'controls': {
                'enabled': True,
                'autoRotate': args.auto_rotate or False,
                'enablePan': True,
                'enableZoom': True,
            },
            'lighting': {
                'environment': args.environment or 'studio',
                'exposure': args.exposure or 1,
                'shadowsEnabled': not args.no_shadows,
            },
            'postProcessing': {
                'enabled': not args.no_postprocessing,
                'ssaoEnabled': args.ssao or False,
                'bloomEnabled': args.bloom or False,
            },
        }
        
        if args.quality and args.quality in QUALITY_PRESETS:
            config['quality'] = QUALITY_PRESETS[args.quality]
        
        print(json.dumps(config, indent=2))
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"\nConfig saved to: {args.output}")
        
        return 0
    
    # Default: show help
    print("Use one of the following options:")
    print("  --list-presets       Show quality and environment presets")
    print("  --list-embed-options Show embed URL parameters")
    print("  --list-materials     Show material display options")
    print("  --generate           Generate viewer configuration JSON")
    return 0


def cmd_api(args):
    """Display API endpoint information and utilities."""
    
    if args.list_endpoints:
        print("Sketchfab API Endpoints:")
        print("=" * 60)
        print(f"Base URL: {SKETCHFAB_API_BASE}")
        print()
        for name, endpoint in API_ENDPOINTS.items():
            full_url = SKETCHFAB_API_BASE + endpoint
            print(f"  {name}:")
            print(f"    {full_url}")
        return 0
    
    if args.build_url:
        endpoint_name = args.build_url
        if endpoint_name not in API_ENDPOINTS:
            print(f"Error: Unknown endpoint '{endpoint_name}'")
            print(f"Available: {', '.join(API_ENDPOINTS.keys())}")
            return 1
        
        endpoint = API_ENDPOINTS[endpoint_name]
        
        # Replace placeholders
        if args.model_id:
            endpoint = endpoint.replace('{model_id}', args.model_id)
        if args.username:
            endpoint = endpoint.replace('{username}', args.username)
        
        # Add query parameters
        params = {}
        if args.params:
            for param in args.params:
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
        
        url = SKETCHFAB_API_BASE + endpoint
        if params:
            url += '?' + urlencode(params)
        
        print(f"API URL: {url}")
        
        if args.curl:
            curl_cmd = f'curl -X GET "{url}"'
            if args.token:
                curl_cmd += f' -H "Authorization: Token {args.token}"'
            print(f"\ncURL command:\n  {curl_cmd}")
        
        return 0
    
    if args.formats:
        print("Available Download Formats:")
        print("=" * 40)
        for fmt in DOWNLOAD_FORMATS:
            print(f"  - {fmt}")
        return 0
    
    if args.visibility:
        print("Visibility Types:")
        print("=" * 40)
        for vis_type, desc in VISIBILITY_TYPES.items():
            print(f"  {vis_type}: {desc}")
        return 0
    
    # Default
    print("API Information Commands:")
    print("  --list-endpoints   Show all API endpoints")
    print("  --build-url NAME   Build a specific API URL")
    print("  --formats          Show download formats")
    print("  --visibility       Show visibility types")
    return 0


def cmd_ai_info(args):
    """Display information about Sketchfab AI tools and providers."""
    
    print("Sketchfab AI Tools")
    print("=" * 60)
    print("\nSupported AI Actions:")
    print("-" * 40)
    for action, desc in AI_ACTIONS.items():
        print(f"  {action}:")
        print(f"    {desc}")
    
    print("\n\nAI Providers:")
    print("-" * 40)
    for provider, info in AI_PROVIDERS.items():
        print(f"  {provider}:")
        print(f"    Supported actions: {', '.join(info['actions'])}")
    
    print("\n\nText-to-3D Providers:")
    print("-" * 40)
    text_to_3d = [p for p, i in AI_PROVIDERS.items() if 'text_to_3d' in i['actions']]
    print(f"  {', '.join(text_to_3d)}")
    
    print("\nImage-to-3D Providers:")
    print("-" * 40)
    img_to_3d = [p for p, i in AI_PROVIDERS.items() if 'image_to_3d' in i['actions']]
    print(f"  {', '.join(img_to_3d)}")
    
    return 0


def cmd_parse_url(args):
    """Parse and analyze Sketchfab URLs."""
    url = args.url
    
    print(f"Parsing: {url}")
    print("=" * 60)
    
    # Parse URL components
    parsed = urlparse(url)
    print(f"\nURL Components:")
    print(f"  Scheme: {parsed.scheme}")
    print(f"  Host: {parsed.netloc}")
    print(f"  Path: {parsed.path}")
    
    if parsed.query:
        print(f"  Query: {parsed.query}")
        query_params = parse_qs(parsed.query)
        print(f"  Query Parameters:")
        for key, values in query_params.items():
            print(f"    {key}: {', '.join(values)}")
    
    if parsed.fragment:
        print(f"  Fragment: {parsed.fragment}")
    
    # Try to extract model ID
    model_id = extract_model_id(url)
    if model_id:
        print(f"\n  Extracted Model ID: {model_id}")
        print(f"  Direct URL: {SKETCHFAB_BASE_URL}/models/{model_id}")
        print(f"  Embed URL: {SKETCHFAB_BASE_URL}/models/{model_id}/embed")
        print(f"  API URL: {SKETCHFAB_API_BASE}/models/{model_id}")
    
    # Check for embed parameters
    if '/embed' in parsed.path and parsed.query:
        print(f"\nEmbed Options Detected:")
        for key, values in query_params.items():
            if key in EMBED_OPTIONS:
                info = EMBED_OPTIONS[key]
                print(f"  {key} = {values[0]} ({info['desc']})")
            else:
                print(f"  {key} = {values[0]} (custom)")
    
    return 0


def cmd_stats(args):
    """Fetch and display model statistics."""
    try:
        import requests
    except ImportError:
        print("Error: requests library required. Install with: pip install requests")
        return 1
    
    model_id = extract_model_id(args.model_id_or_url)
    if not model_id:
        print(f"Error: Could not extract model ID from: {args.model_id_or_url}")
        return 1
    
    print(f"Fetching stats for model: {model_id}")
    
    api_url = f"{SKETCHFAB_API_BASE}/models/{model_id}"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    if args.token:
        headers['Authorization'] = f'Token {args.token}'
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print("\nModel Information:")
        print("=" * 50)
        print(f"  Name: {data.get('name', 'Unknown')}")
        print(f"  UID: {data.get('uid', model_id)}")
        
        user = data.get('user', {})
        print(f"  Author: {user.get('displayName', user.get('username', 'Unknown'))}")
        
        print(f"\nStats:")
        print(f"  Views: {data.get('viewCount', 0):,}")
        print(f"  Likes: {data.get('likeCount', 0):,}")
        print(f"  Comments: {data.get('commentCount', 0):,}")
        
        if data.get('isDownloadable'):
            print(f"  Downloads: {data.get('downloadCount', 0):,}")
        
        print(f"\nProperties:")
        print(f"  Downloadable: {'Yes' if data.get('isDownloadable') else 'No'}")
        print(f"  Animated: {'Yes' if data.get('isAnimated') else 'No'}")
        print(f"  Staff Pick: {'Yes' if data.get('staffpickedAt') else 'No'}")
        
        license_info = data.get('license', {})
        if license_info:
            print(f"  License: {license_info.get('label', 'Unknown')}")
        
        categories = data.get('categories', [])
        if categories:
            cat_names = [c.get('name', 'Unknown') for c in categories]
            print(f"  Categories: {', '.join(cat_names)}")
        
        tags = data.get('tags', [])
        if tags:
            tag_names = [t.get('name', t) if isinstance(t, dict) else t for t in tags[:10]]
            print(f"  Tags: {', '.join(tag_names)}")
        
        if args.json:
            print(f"\nRaw JSON:")
            print(json.dumps(data, indent=2))
        
        return 0
        
    except requests.RequestException as e:
        print(f"Error fetching model: {e}")
        return 1


def extract_model_id(url_or_id):
    """Extract model ID from URL or return if already an ID."""
    # If it's already just an ID (alphanumeric, 32 chars)
    if re.match(r'^[a-f0-9]{32}$', url_or_id, re.IGNORECASE):
        return url_or_id
    
    # Try to extract from URL patterns
    patterns = [
        r'sketchfab\.com/(?:3d-)?models/[^/]+-([a-f0-9]{32})',  # /models/name-id
        r'sketchfab\.com/(?:3d-)?models/([a-f0-9]{32})',         # /models/id
        r'sketchfab\.com/models/([a-f0-9]{32})',                  # Direct model ID
        r'/([a-f0-9]{32})(?:/embed)?(?:\?|$)',                    # ID in path
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def format_number(num):
    """Format large numbers with K, M suffixes."""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)


def cmd_search(args):
    """Search for models on Sketchfab."""
    try:
        import requests
    except ImportError:
        print("Error: requests library required. Install with: pip install requests")
        return 1
    
    print(f"Searching for: {args.query}")
    
    # Build search URL
    params = {
        'q': args.query,
        'type': args.type or 'models',
    }
    
    if args.sort:
        params['sort_by'] = f"-{args.sort}" if args.sort != 'relevance' else args.sort
    if args.downloadable:
        params['downloadable'] = 'true'
    if args.animated:
        params['animated'] = 'true'
    if args.staffpicked:
        params['staffpicked'] = 'true'
    if args.category:
        params['categories'] = args.category
    if args.count:
        params['count'] = min(args.count, 24)  # Max 24 per request
    
    api_url = f"{SKETCHFAB_API_BASE}/search"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        total = data.get('totalCount', len(results))
        
        print(f"\nFound {total:,} results:")
        print("=" * 60)
        
        for i, item in enumerate(results, 1):
            name = item.get('name', 'Unknown')
            uid = item.get('uid', 'N/A')
            user = item.get('user', {}).get('displayName', item.get('user', {}).get('username', 'Unknown'))
            views = item.get('viewCount', 0)
            likes = item.get('likeCount', 0)
            
            print(f"\n{i}. {name}")
            print(f"   ID: {uid}")
            print(f"   Author: {user}")
            print(f"   Views: {format_number(views)} | Likes: {format_number(likes)}")
            
            if item.get('isDownloadable'):
                print(f"   ✓ Downloadable")
            if item.get('isAnimated'):
                print(f"   ✓ Animated")
            if item.get('staffpickedAt'):
                print(f"   ★ Staff Pick")
        
        if args.json:
            print(f"\n\nRaw JSON:")
            print(json.dumps(data, indent=2))
        
        return 0
        
    except requests.RequestException as e:
        print(f"Error searching: {e}")
        return 1


def cmd_user(args):
    """Look up a Sketchfab user."""
    try:
        import requests
    except ImportError:
        print("Error: requests library required. Install with: pip install requests")
        return 1
    
    username = args.username.lstrip('@')
    print(f"Looking up user: {username}")
    
    api_url = f"{SKETCHFAB_API_BASE}/users/{username}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        user = response.json()
        
        print("\nUser Information:")
        print("=" * 50)
        print(f"  Username: {user.get('username', 'N/A')}")
        print(f"  Display Name: {user.get('displayName', 'N/A')}")
        print(f"  UID: {user.get('uid', 'N/A')}")
        
        if user.get('bio'):
            bio = user['bio'][:100] + '...' if len(user.get('bio', '')) > 100 else user.get('bio', '')
            print(f"  Bio: {bio}")
        
        if user.get('location'):
            print(f"  Location: {user.get('location')}")
        if user.get('website'):
            print(f"  Website: {user.get('website')}")
        
        print(f"\nStats:")
        print(f"  Models: {user.get('modelCount', 0):,}")
        print(f"  Followers: {user.get('followerCount', 0):,}")
        print(f"  Following: {user.get('followingCount', 0):,}")
        print(f"  Likes: {user.get('likeCount', 0):,}")
        
        print(f"\nStatus:")
        if user.get('isVerified'):
            print(f"  ✓ Verified")
        if user.get('isPro'):
            print(f"  ★ Pro Account")
        if user.get('isStaff'):
            print(f"  ⚡ Staff")
        
        print(f"\nProfile URL: {SKETCHFAB_BASE_URL}/@{username}")
        print(f"Models URL: {SKETCHFAB_BASE_URL}/@{username}/models")
        
        if args.models:
            # Fetch user's models
            models_url = f"{SKETCHFAB_API_BASE}/users/{username}/models"
            models_response = requests.get(models_url, headers=headers, timeout=10)
            models_response.raise_for_status()
            models_data = models_response.json()
            
            models = models_data.get('results', [])
            print(f"\nRecent Models ({len(models)} shown):")
            print("-" * 40)
            for model in models[:10]:
                name = model.get('name', 'Unknown')
                uid = model.get('uid', '')
                views = format_number(model.get('viewCount', 0))
                print(f"  - {name} ({views} views)")
                print(f"    ID: {uid}")
        
        if args.json:
            print(f"\nRaw JSON:")
            print(json.dumps(user, indent=2))
        
        return 0
        
    except requests.RequestException as e:
        print(f"Error fetching user: {e}")
        return 1


def cmd_thumbnail(args):
    """Generate thumbnail URLs for a model."""
    model_id = extract_model_id(args.model_id_or_url)
    
    if not model_id:
        print(f"Error: Could not extract model ID from: {args.model_id_or_url}")
        return 1
    
    print(f"Thumbnail URLs for model: {model_id}")
    print("=" * 60)
    
    # Generate Sketchfab CDN thumbnail URLs
    base_url = f"https://media.sketchfab.com/models/{model_id}/thumbnails"
    
    print("\nStandard Thumbnails:")
    for size_name, dims in THUMBNAIL_SIZES.items():
        url = f"{base_url}/{dims['width']}x{dims['height']}.jpeg"
        print(f"  {size_name.capitalize()} ({dims['width']}x{dims['height']}):")
        print(f"    {url}")
    
    print("\nAlternative Formats:")
    print(f"  Default: {base_url}/default.jpeg")
    print(f"  Square: {base_url}/200x200.jpeg")
    
    if args.fetch:
        try:
            import requests
            api_url = f"{SKETCHFAB_API_BASE}/models/{model_id}"
            response = requests.get(api_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            thumbnails = data.get('thumbnails', {}).get('images', [])
            if thumbnails:
                print(f"\nActual Thumbnails from API ({len(thumbnails)} available):")
                for thumb in thumbnails:
                    width = thumb.get('width', 'N/A')
                    height = thumb.get('height', 'N/A')
                    url = thumb.get('url', 'N/A')
                    print(f"  {width}x{height}: {url}")
        except Exception as e:
            print(f"\nCould not fetch actual thumbnails: {e}")
    
    return 0


def cmd_tiers(args):
    """Display subscription tier information."""
    print("Sketchfab Subscription Tiers")
    print("=" * 60)
    
    for tier_id, tier_info in SUBSCRIPTION_TIERS.items():
        print(f"\n{tier_info['name'].upper()}")
        if tier_info.get('badgeColor'):
            print(f"  Badge Color: {tier_info['badgeColor']}")
        print(f"  Features:")
        for feature, value in tier_info['features'].items():
            display_value = '✓' if value is True else ('✗' if value is False else value)
            print(f"    {feature}: {display_value}")
    
    print("\n\nVisibility Options by Tier:")
    print("-" * 40)
    for vis_type, desc in VISIBILITY_TYPES.items():
        print(f"  {vis_type}: {desc}")
    
    return 0


def cmd_validate(args):
    """Validate input values against Sketchfab patterns."""
    value = args.value
    val_type = args.type
    
    if val_type not in VALIDATION_PATTERNS:
        print(f"Unknown validation type: {val_type}")
        print(f"Available types: {', '.join(VALIDATION_PATTERNS.keys())}")
        return 1
    
    pattern = VALIDATION_PATTERNS[val_type]
    
    if re.match(pattern, value):
        print(f"✓ Valid {val_type}: {value}")
        return 0
    else:
        print(f"✗ Invalid {val_type}: {value}")
        print(f"  Expected pattern: {pattern}")
        return 1


def cmd_categories(args):
    """Display Sketchfab model categories."""
    print("Sketchfab Model Categories")
    print("=" * 40)
    
    for i, category in enumerate(SEARCH_CATEGORIES, 1):
        # Convert slug to display name
        display_name = category.replace('-', ' & ' if '-' in category else ' ').title()
        print(f"  {i:2}. {display_name}")
        print(f"      Slug: {category}")
    
    print(f"\nTotal: {len(SEARCH_CATEGORIES)} categories")
    print("\nUse these slugs with: python cli.py search --category <slug> <query>")
    
    return 0


def cmd_design(args):
    """Display Sketchfab design system information."""
    
    if args.colors:
        print("Sketchfab Color Palette")
        print("=" * 60)
        
        for theme_name, colors in THEME_COLORS.items():
            print(f"\n{theme_name.upper()} THEME:")
            print("-" * 40)
            for color_name, color_value in colors.items():
                print(f"  {color_name:20} {color_value}")
        return 0
    
    if args.typography:
        print("Sketchfab Typography Scale")
        print("=" * 60)
        
        for level, props in TYPOGRAPHY_SCALE.items():
            print(f"\n{level.upper()}:")
            for prop, value in props.items():
                print(f"  {prop}: {value}")
        return 0
    
    if args.gradients:
        print("Sketchfab Gradient Presets")
        print("=" * 60)
        
        for name, colors in GRADIENT_PRESETS.items():
            print(f"\n{name.upper()}:")
            for key, value in colors.items():
                print(f"  {key}: {value}")
        return 0
    
    if args.shadows:
        print("Sketchfab Shadow Presets")
        print("=" * 60)
        
        for name, value in SHADOW_PRESETS.items():
            print(f"\n{name.upper()}:")
            print(f"  {value}")
        return 0
    
    if args.notifications:
        print("Sketchfab Notification Types")
        print("=" * 60)
        
        for notif_type, colors in NOTIFICATION_TYPES.items():
            print(f"\n{notif_type.upper()}:")
            for key, value in colors.items():
                print(f"  {key}: {value}")
        return 0
    
    if args.generate_css:
        theme = args.theme or 'light'
        if theme not in THEME_COLORS:
            print(f"Unknown theme: {theme}. Available: {', '.join(THEME_COLORS.keys())}")
            return 1
        
        print(f"/* Sketchfab {theme.title()} Theme CSS Variables */")
        print(":root {")
        for color_name, color_value in THEME_COLORS[theme].items():
            css_name = ''.join(['-' + c.lower() if c.isupper() else c for c in color_name]).lstrip('-')
            print(f"  --color-{css_name}: {color_value};")
        print("}")
        print()
        print("/* Typography */")
        for level, props in TYPOGRAPHY_SCALE.items():
            print(f".text-{level} {{")
            print(f"  font-size: {props['fontSize']};")
            print(f"  font-weight: {props['fontWeight']};")
            print(f"  line-height: {props['lineHeight']};")
            print("}")
        return 0
    
    # Default: show summary
    print("Sketchfab Design System")
    print("=" * 60)
    print("\nAvailable design information:")
    print("  --colors         Show color palettes (light/dark themes)")
    print("  --typography     Show typography scale")
    print("  --gradients      Show gradient presets")
    print("  --shadows        Show shadow presets")
    print("  --notifications  Show notification type colors")
    print("  --generate-css   Generate CSS variables")
    print("                   Use with --theme light|dark")
    print()
    print("Quick Stats:")
    print(f"  Themes: {', '.join(THEME_COLORS.keys())}")
    print(f"  Colors per theme: {len(THEME_COLORS['light'])}")
    print(f"  Typography levels: {len(TYPOGRAPHY_SCALE)}")
    print(f"  Gradient presets: {len(GRADIENT_PRESETS)}")
    print(f"  Shadow presets: {len(SHADOW_PRESETS)}")
    print(f"  Notification types: {len(NOTIFICATION_TYPES)}")
    
    return 0


def cmd_string(args):
    """String manipulation utilities inspired by Sketchfab's JS utilities."""
    text = args.text
    
    if args.slugify:
        # Convert to URL-friendly slug
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        print(f"{STRING_CONVERSIONS['slug']} {slug}")
        return 0
    
    if args.camel:
        # Convert to camelCase
        words = re.split(r'[-_\s]+', text)
        result = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        print(f"{STRING_CONVERSIONS['camelcase']} {result}")
        return 0
    
    if args.kebab:
        # Convert to kebab-case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
        result = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
        result = re.sub(r'[-_\s]+', '-', result)
        print(f"{STRING_CONVERSIONS['kebabcase']} {result}")
        return 0
    
    if args.snake:
        # Convert to snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        result = re.sub(r'[-_\s]+', '_', result)
        print(f"{STRING_CONVERSIONS['snakecase']} {result}")
        return 0
    
    if args.title:
        # Convert to Title Case
        result = text.replace('-', ' ').replace('_', ' ').title()
        print(f"{STRING_CONVERSIONS['titlecase']} {result}")
        return 0
    
    if args.truncate:
        max_len = args.truncate
        if len(text) <= max_len:
            print(text)
        else:
            print(f"{text[:max_len-3]}...")
        return 0
    
    # Default: show all conversions
    print(f"{STRING_CONVERSIONS['original']} {text}")
    print("-" * 40)
    
    # Slug
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    print(f"{STRING_CONVERSIONS['slug']:14} {slug}")
    
    # camelCase
    words = re.split(r'[-_\s]+', text)
    camel = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    print(f"{STRING_CONVERSIONS['camelcase']:14} {camel}")
    
    # kebab-case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
    kebab = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
    kebab = re.sub(r'[-_\s]+', '-', kebab)
    print(f"{STRING_CONVERSIONS['kebabcase']:14} {kebab}")
    
    # snake_case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    snake = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    snake = re.sub(r'[-_\s]+', '_', snake)
    print(f"{STRING_CONVERSIONS['snakecase']:14} {snake}")
    
    # Title Case
    title = text.replace('-', ' ').replace('_', ' ').title()
    print(f"{STRING_CONVERSIONS['titlecase']:14} {title}")
    
    return 0


def cmd_filesize(args):
    """Format file sizes in human-readable format."""
    size_bytes = args.bytes
    
    if size_bytes < 0:
        print(ERROR_MESSAGES['size_must_be_positive'])
        return 1
    
    # Human-readable format
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            print(f"{size_bytes:.2f} {unit}")
            break
        size_bytes /= 1024.0
    else:
        print(f"{size_bytes:.2f} PB")
    
    return 0


def cmd_layout(args):
    """Display responsive layout information."""
    
    if args.breakpoints:
        print(HEADERS['responsive_breakpoints'])
        print("=" * 60)
        
        for name, info in BREAKPOINTS.items():
            max_val = info['max'] if info['max'] else MAIN_LABELS['infinity']
            print(f"\n{name.upper()} - {info['desc']}")
            print(f"  Min: {info['min']}px")
            print(
                f"  Max: {max_val}px"
                if info['max']
                else f"  Max: {MAIN_LABELS['no_limit']}"
            )
            
            # Generate media query
            if info['min'] == 0 and info['max']:
                print(f"  Media Query: @media (max-width: {info['max']}px)")
            elif info['max']:
                print(f"  Media Query: @media (min-width: {info['min']}px) and (max-width: {info['max']}px)")
            else:
                print(f"  Media Query: @media (min-width: {info['min']}px)")
        return 0
    
    if args.dimensions:
        print(HEADERS['layout_dimensions'])
        print("=" * 60)
        
        for component, dims in LAYOUT_DIMENSIONS.items():
            print(f"\n{component.upper()}:")
            for key, value in dims.items():
                print(f"  {key}: {value}px")
        return 0
    
    if args.spacing:
        print(HEADERS['spacing_scale'])
        print("=" * 60)
        
        for level, value in SPACING_SCALE.items():
            print(f"  {level:3}: {value}")
        
        print(f"\n\n{HEADERS['css_custom_props']}")
        for level, value in SPACING_SCALE.items():
            print(f"  --spacing-{level}: {value};")
        return 0
    
    if args.generate_scss:
        print("// Sketchfab SCSS Variables")
        print()
        print("// Breakpoints")
        print("$breakpoints: (")
        for name, info in BREAKPOINTS.items():
            print(f"  '{name}': {info['min']}px,")
        print(");")
        print()
        print("// Spacing")
        print("$spacing: (")
        for level, value in SPACING_SCALE.items():
            print(f"  {level}: {value},")
        print(");")
        print()
        print("// Layout")
        for component, dims in LAYOUT_DIMENSIONS.items():
            for key, value in dims.items():
                var_name = f"${component}-{key}".replace('_', '-').lower()
                # Convert camelCase to kebab-case
                var_name = re.sub(r'([a-z])([A-Z])', r'\1-\2', var_name).lower()
                print(f"{var_name}: {value}px;")
        return 0
    
    # Default: show summary
    print(HEADERS['layout_responsive'])
    print("=" * 60)
    print(f"\n{LAYOUT_SUMMARY['options_header']}")
    print("  --breakpoints    Show responsive breakpoints")
    print("  --dimensions     Show layout dimensions")
    print("  --spacing        Show spacing scale")
    print("  --generate-scss  Generate SCSS variables")
    print()
    print(LAYOUT_SUMMARY['quick_stats'])
    print(
        f"  {LAYOUT_SUMMARY['breakpoints']} {len(BREAKPOINTS)} "
        f"({', '.join(BREAKPOINTS.keys())})"
    )
    print(f"  {LAYOUT_SUMMARY['spacing_levels']} {len(SPACING_SCALE)}")
    print(f"  {LAYOUT_SUMMARY['layout_components']} {len(LAYOUT_DIMENSIONS)}")
    
    return 0


def cmd_share(args):
    """Generate social sharing URLs for a model."""
    model_id = extract_model_id(args.model_id_or_url)
    
    if not model_id:
        print(f"Error: Could not extract model ID from: {args.model_id_or_url}")
        return 1
    
    model_url = f"{SKETCHFAB_BASE_URL}/3d-models/{model_id}"
    text = args.text or DEFAULTS['share_text']

    print(f"{HEADERS['social_sharing']} {model_id}")
    print("=" * 60)
    print(f"\n{LABELS['model_url']} {model_url}")
    print()
    
    for platform in SHARE_PLATFORMS:
        share_url = platform['url_template'].format(
            url=model_url,
            text=text.replace(' ', '%20')
        )
        print(f"{platform['name']:12} {share_url}")
    
    if args.platform:
        platform = next((p for p in SHARE_PLATFORMS if p['id'] == args.platform), None)
        if platform:
            share_url = platform['url_template'].format(
                url=model_url,
                text=text.replace(' ', '%20')
            )
            print(f"\n{LABELS['direct_link_for'].format(platform=platform['name'])}")
            print(share_url)
    
    return 0


def cmd_markdown(args):
    """Display markdown syntax reference from Sketchfab's editor."""
    
    print(HEADERS['markdown_reference'])
    print("=" * 60)
    print(SUBHEADERS['based_on_editor'])
    print()
    
    for category, buttons in MARKDOWN_TOOLBAR.items():
        display_name = category.replace('_', ' ').title()
        print(f"\n{display_name}:")
        print("-" * 40)
        
        for btn in buttons:
            shortcut = f" ({btn['shortcut']})" if btn.get('shortcut') else ""
            syntax = btn['syntax'].replace('\n', '\\n')
            print(f"  {btn['label']:20}{shortcut}")
            print(f"    Syntax: {syntax}")
    
    print(f"\n\n{HEADERS['examples']}")
    print("-" * 40)
    for example in MARKDOWN_EXAMPLES:
        print(f"  {example['syntax']:20} → {example['result']}")
    
    return 0


def cmd_brands(args):
    """Display brand/social media colors."""
    
    print(HEADERS['brand_colors'])
    print("=" * 60)
    
    for brand, color in BRAND_COLORS.items():
        # Create a simple visual indicator
        print(f"  {brand:15} {color}  {'█' * 3}")
    
    print(f"\n\n{HEADERS['usage_in_css']}")
    print("-" * 40)
    for brand, color in BRAND_COLORS.items():
        print(f"  --color-{brand}: {color};")
    
    return 0


def cmd_dates(args):
    """Display date format patterns used by Sketchfab."""
    
    print(HEADERS['date_format_patterns'])
    print("=" * 60)
    print(SUBHEADERS['based_on_dayjs'])
    print()
    
    from datetime import datetime
    now = datetime.now()
    dates_msgs = get_messages()['dates']

    print(DATE_LABELS['format_patterns'])
    print("-" * 40)

    for name, pattern in DATE_FORMATS.items():
        if pattern == 'fromNow':
            example = dates_msgs['from_now_example']
        else:
            try:
                strftime_pattern = pattern
                for dayjs_token, strftime_eq in STRFTIME_MAP.items():
                    strftime_pattern = strftime_pattern.replace(dayjs_token, strftime_eq)
                example = now.strftime(strftime_pattern)
            except Exception:
                example = pattern

        print(f"  {name:12} {pattern:30} {example}")

    print(f"\n\n{DATE_LABELS['dayjs_tokens']}")
    print("-" * 40)
    for token in DAYJS_TOKENS:
        print(f"  {token['token']:4} = {token['description']} ({token['example']})")

    return 0


def cmd_licenses(args):
    """Display Creative Commons license information."""
    
    if args.license:
        # Show specific license
        if args.license not in LICENSE_TYPES:
            print(ERROR_MESSAGES['unknown_license'].format(license=args.license))
            print(
                ERROR_MESSAGES['available_licenses'].format(
                    list=', '.join(LICENSE_TYPES.keys())
                )
            )
            return 1
        
        lic = LICENSE_TYPES[args.license]
        print(f"{LICENSE_LABELS['name']} {lic['name']}")
        print("=" * 60)
        if lic['url']:
            print(f"{LICENSE_LABELS['url']} {lic['url']}")
        allows = ', '.join(lic['allows']) if lic['allows'] else MAIN_LABELS['none']
        requires = ', '.join(lic['requires']) if lic['requires'] else MAIN_LABELS['none']
        print(f"\n{LICENSE_LABELS['allows']} {allows}")
        print(f"{LICENSE_LABELS['requires']} {requires}")
        return 0
    
    print(HEADERS['cc_licenses'])
    print("=" * 60)
    print(SUBHEADERS['used_for_licensing'])
    print()
    
    for code, lic in LICENSE_TYPES.items():
        print(f"\n{code}")
        print(f"  {LICENSE_LABELS['name']} {lic['name']}")
        allows = ', '.join(lic['allows']) if lic['allows'] else 'None'
        requires = ', '.join(lic['requires']) if lic['requires'] else 'None'
        print(f"  {LICENSE_LABELS['allows']} {allows}")
        print(f"  {LICENSE_LABELS['requires']} {requires}")
    
    print(f"\n\n{LICENSE_LABELS['permission_types_header']}")
    print("-" * 40)
    for perm in PERMISSION_TYPES:
        print(f"  {perm['name']:15} - {perm['description']}")
    
    return 0


def cmd_webgl(args):
    """Display WebGL error types and troubleshooting."""
    
    print(HEADERS['webgl_errors'])
    print("=" * 60)
    print()
    
    for error_type, info in WEBGL_ERRORS.items():
        print(f"\n{error_type.upper()}")
        print("-" * 40)
        print(f"{WEBGL_LABELS['title']} {info['title']}")
        print(f"{WEBGL_LABELS['message']} {info['message']}")
        print(WEBGL_LABELS['suggestions'])
        for suggestion in info['suggestions']:
            print(f"  • {suggestion}")
    
    print(f"\n\n{WEBGL_LABELS['detection_header']}")
    print("-" * 40)
    print(CODE_SNIPPETS['webgl_detection'])
    
    return 0


def cmd_animation(args):
    """Display spring animation presets."""
    
    print(HEADERS['spring_animation'])
    print("=" * 60)
    print(SUBHEADERS['physics_based'])
    print()
    
    for name, preset in SPRING_PRESETS.items():
        print(f"\n{name.upper()}")
        print(f"  {ANIMATION_LABELS['stiffness']} {preset['stiffness']}")
        print(f"  {ANIMATION_LABELS['damping']} {preset['damping']}")
        print(f"  {ANIMATION_LABELS['description']} {preset['desc']}")
    
    print(f"\n\n{ANIMATION_LABELS['formula_header']}")
    print("-" * 40)
    for formula in SPRING_FORMULAS:
        print(f"  {formula['formula']}  ({formula['description']})")
    print()
    for variable in SPRING_VARIABLES:
        print(f"  {variable['var']} = {variable['description']}")
    
    if args.generate_js:
        print(f"\n\n{ANIMATION_LABELS['js_impl_header']}")
        print("-" * 40)
        print(CODE_SNIPPETS['spring_js'])
    
    return 0


def cmd_privacy(args):
    """Display cookie consent categories."""
    
    print(HEADERS['cookie_consent'])
    print("=" * 60)
    print(SUBHEADERS['onetrust_gdpr'])
    print()
    
    for code, cat in CONSENT_CATEGORIES.items():
        required = "✓ Required" if cat['required'] else "○ Optional"
        print(f"\n{code} - {cat['name']} [{required}]")
        print(f"  {cat['description']}")
    
    print(f"\n\n{PRIVACY_LABELS['usage_header']}")
    print("-" * 40)
    print(CODE_SNIPPETS['consent_usage'])
    
    return 0


def cmd_model_fields(args):
    """Display model property field definitions."""
    
    print(HEADERS['model_props'])
    print("=" * 60)
    print(SUBHEADERS['field_definitions'])
    print()
    
    for field_name, field_def in MODEL_PROPERTIES.items():
        print(f"\n{field_name}")
        print(f"  Type: {field_def['type']}")
        for key, value in field_def.items():
            if key != 'type':
                print(f"  {key}: {value}")
    
    print(f"\n\n{MODEL_FIELDS_LABELS['groups_header']}")
    print("-" * 40)
    for group, fields in USER_PROFILE_FIELDS.items():
        print(f"\n{group.upper()}:")
        for field in fields:
            print(f"  • {field}")
    
    return 0


def cmd_grid(args):
    """Display responsive grid configuration."""
    
    print(HEADERS['responsive_grid'])
    print("=" * 60)
    print()
    
    for size, config in GRID_COLUMNS.items():
        print(
            f"{size.upper():10} "
            f"{GRID_LABELS['columns_at'].format(cols=config['columns'], breakpoint=config['breakpoint'])}"
        )
    
    print(f"\n\n{GRID_LABELS['css_impl_header']}")
    print("-" * 40)
    print(CODE_SNIPPETS['css_grid'])
    
    return 0


def cmd_placements(args):
    """Display UI popup/tooltip placement options."""
    
    print(HEADERS['popup_placements'])
    print("=" * 60)
    print(SUBHEADERS['floating_ui'])
    print()
    
    # Group by direction
    directions = {'top': [], 'right': [], 'bottom': [], 'left': []}
    for placement in POPUP_PLACEMENTS:
        direction = placement.split('-')[0]
        directions[direction].append(placement)
    
    for direction, placements in directions.items():
        print(f"\n{direction.upper()}:")
        for p in placements:
            suffix = p.replace(direction, '').lstrip('-') or 'center'
            print(
                f"  {p:15} "
                f"{PLACEMENTS_LABELS['aligned'].format(suffix=suffix)}"
            )
    
    print(f"\n\n{PLACEMENTS_LABELS['usage_header']}")
    print("-" * 40)
    print(CODE_SNIPPETS['floating_ui'])
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description=_STRINGS['cli_description'],
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    commands = get_commands()

    for command_name, command_data in commands.items():
        parser = subparsers.add_parser(command_name, help=command_data['help'])

        for arg in command_data.get('arguments', []):
            kwargs = {k: v for k, v in arg.items() if k != 'name'}
            parser.add_argument(arg['name'], **kwargs)

        if 'defaults' in command_data:
            parser.set_defaults(**command_data['defaults'])

        parser.set_defaults(func=globals()[command_data['func']])

    # Parse args
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Run the command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print(f"\n{_STRINGS['interrupt_message']}")
        return 1
    except Exception as e:
        print(_STRINGS['unexpected_error'].format(error=e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
