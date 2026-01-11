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

# =============================================================================
# CONSTANTS - Derived from Sketchfab JavaScript analysis
# =============================================================================

# API Endpoints (from error_messages.js.md / api_client.js.md)
SKETCHFAB_API_BASE = "https://api.sketchfab.com/v3"
SKETCHFAB_BASE_URL = "https://sketchfab.com"

API_ENDPOINTS = {
    'models': '/models',
    'model_detail': '/models/{model_id}',
    'model_download': '/models/{model_id}/download',
    'model_embed': '/models/{model_id}/embed',
    'user': '/users/{username}',
    'user_models': '/users/{username}/models',
    'search': '/search',
    'categories': '/categories',
    'collections': '/collections',
    'me': '/me',
    'likes': '/me/likes',
    'purchases': '/me/purchases',
}

# Viewer Embed Options (from material_options.js.md)
EMBED_OPTIONS = {
    'autostart': {'type': bool, 'default': False, 'desc': 'Auto-load model on page load'},
    'autospin': {'type': float, 'default': 0, 'desc': 'Auto-rotate speed (0 to disable)'},
    'camera': {'type': bool, 'default': True, 'desc': 'Enable camera controls'},
    'preload': {'type': bool, 'default': True, 'desc': 'Preload textures'},
    'transparent': {'type': bool, 'default': False, 'desc': 'Transparent background'},
    'ui_controls': {'type': bool, 'default': True, 'desc': 'Show UI controls'},
    'ui_infos': {'type': bool, 'default': True, 'desc': 'Show info panel'},
    'ui_inspector': {'type': bool, 'default': True, 'desc': 'Show inspector'},
    'ui_watermark': {'type': bool, 'default': True, 'desc': 'Show watermark'},
    'ui_help': {'type': bool, 'default': True, 'desc': 'Show help button'},
    'ui_settings': {'type': bool, 'default': True, 'desc': 'Show settings button'},
    'ui_fullscreen': {'type': bool, 'default': True, 'desc': 'Show fullscreen button'},
    'ui_annotations': {'type': bool, 'default': True, 'desc': 'Show annotations'},
    'annotations_visible': {'type': bool, 'default': True, 'desc': 'Annotations visible on load'},
    'animation_autoplay': {'type': bool, 'default': False, 'desc': 'Auto-play animations'},
    'scrollwheel': {'type': bool, 'default': True, 'desc': 'Enable scroll wheel zoom'},
    'double_click': {'type': bool, 'default': True, 'desc': 'Enable double-click to focus'},
    'orbit_constraint_pan': {'type': bool, 'default': False, 'desc': 'Constrain panning'},
    'orbit_constraint_zoom_in': {'type': float, 'default': None, 'desc': 'Min zoom distance'},
    'orbit_constraint_zoom_out': {'type': float, 'default': None, 'desc': 'Max zoom distance'},
}

# Material Display Options (from material_options.js.md)
MATERIAL_OPTIONS = {
    'diffuse': 'Base color texture',
    'normal': 'Normal map',
    'emissive': 'Emissive/glow',
    'transparency': 'Alpha/transparency',
    'metalness': 'Metalness map (PBR)',
    'roughness': 'Roughness map (PBR)',
    'glossiness': 'Glossiness (spec workflow)',
    'specular': 'Specular map',
    'f0': 'Fresnel reflectance',
    'cavity': 'Cavity/AO detail',
    'ao': 'Ambient occlusion',
    'displacement': 'Displacement/height map',
    'wireframe': 'Show wireframe',
    'vertexColors': 'Show vertex colors',
}

# Viewer Quality Presets (from viewer_config.js.md)
QUALITY_PRESETS = {
    'low': {
        'name': 'Low',
        'pixelRatio': 1,
        'shadows': False,
        'ssao': False,
        'antialiasing': False,
        'textureQuality': 0.5
    },
    'medium': {
        'name': 'Medium',
        'pixelRatio': 1.5,
        'shadows': True,
        'ssao': False,
        'antialiasing': True,
        'textureQuality': 0.75
    },
    'high': {
        'name': 'High',
        'pixelRatio': 2,
        'shadows': True,
        'ssao': True,
        'antialiasing': True,
        'textureQuality': 1
    },
    'ultra': {
        'name': 'Ultra',
        'pixelRatio': 2,
        'shadows': True,
        'ssao': True,
        'antialiasing': True,
        'textureQuality': 1,
        'supersample': True
    }
}

# Environment Presets (from viewer_config.js.md)
ENVIRONMENT_PRESETS = {
    'studio': {'name': 'Studio', 'intensity': 1, 'shadows': True},
    'urban': {'name': 'Urban', 'intensity': 0.8, 'shadows': True},
    'dawn': {'name': 'Dawn', 'intensity': 0.6, 'shadows': True},
    'night': {'name': 'Night', 'intensity': 0.3, 'shadows': False},
    'custom': {'name': 'Custom', 'intensity': 1, 'shadows': True},
}

# AI Action Types (from ai_tools.js.md)
AI_ACTIONS = {
    'text_to_3d': 'Generate 3D model from text prompt',
    'image_to_3d': 'Generate 3D model from image',
    'mesh_rigging': 'Auto-rig a 3D mesh',
    'texture_generation': 'Generate textures with AI',
    'mesh_retopology': 'Retopologize mesh automatically',
}

# AI Providers (from ai_tools.js.md)
AI_PROVIDERS = {
    'CSM': {'actions': ['text_to_3d', 'image_to_3d']},
    'FLUX': {'actions': ['image_generation']},
    'Gemini': {'actions': ['text_to_3d']},
    'Meshy': {'actions': ['text_to_3d', 'mesh_rigging']},
    'Rodin': {'actions': ['image_to_3d']},
    'Stability': {'actions': ['image_to_3d']},
    'Tripo': {'actions': ['text_to_3d', 'image_to_3d']},
}

# Download Formats (from model_page.js.md)
DOWNLOAD_FORMATS = ['glb', 'gltf', 'fbx', 'obj', 'usdz', 'blend']

# Visibility Types (from api_client.js.md / visibility_popup.js.md)
VISIBILITY_TYPES = {
    'public': 'Visible to everyone - anyone can find and view',
    'unlisted': 'Accessible via direct link only',
    'private': 'Only visible to owner (requires Pro)',
    'password': 'Password protected (requires Pro)',
    'org': 'Organization members only',
}

# Subscription Tiers (from visibility_popup.js.md)
SUBSCRIPTION_TIERS = {
    'free': {
        'name': 'Free',
        'features': {
            'privateModels': False,
            'passwordProtected': False,
            'downloadableModels': 0,
            'customBranding': False,
            'maxFileSize': '100MB',
            'monthlyUploads': 10,
        }
    },
    'plus': {
        'name': 'Plus',
        'badgeColor': '#1caad9',
        'features': {
            'privateModels': True,
            'passwordProtected': True,
            'downloadableModels': 5,
            'customBranding': False,
            'maxFileSize': '500MB',
            'monthlyUploads': 50,
        }
    },
    'pro': {
        'name': 'Pro',
        'badgeColor': '#ffc107',
        'features': {
            'privateModels': True,
            'passwordProtected': True,
            'downloadableModels': 20,
            'customBranding': True,
            'maxFileSize': '1GB',
            'monthlyUploads': 200,
        }
    },
    'business': {
        'name': 'Business',
        'badgeColor': '#9c27b0',
        'features': {
            'privateModels': True,
            'passwordProtected': True,
            'downloadableModels': 'unlimited',
            'customBranding': True,
            'maxFileSize': '2GB',
            'monthlyUploads': 'unlimited',
        }
    },
}

# Thumbnail Sizes (from viewer_utils.js.md)
THUMBNAIL_SIZES = {
    'small': {'width': 200, 'height': 150},
    'medium': {'width': 320, 'height': 240},
    'large': {'width': 640, 'height': 480},
    'xlarge': {'width': 1280, 'height': 720},
}

# Model Badges (from viewer_utils.js.md)
MODEL_BADGES = {
    'staffpick': 'Featured by Sketchfab staff',
    'store': 'Available for purchase in store',
    'downloadable': 'Free to download',
    'animated': 'Contains animation',
    'sound': 'Has audio/sound',
    'restricted': 'Age-restricted content',
}

# Search Filters (from navigation.js.md)
SEARCH_FILTERS = {
    'type': ['models', 'collections', 'users'],
    'sort': ['relevance', 'likeCount', 'viewCount', 'createdAt', 'publishedAt'],
    'downloadable': [True, False],
    'animated': [True, False],
    'staffpicked': [True, False],
    'rigged': [True, False],
    'pbr': [True, False],
}

# Search Categories (from navigation.js.md)
SEARCH_CATEGORIES = [
    'animals-pets', 'architecture', 'art-abstract',
    'cars-vehicles', 'characters-creatures', 'cultural-heritage-history',
    'electronics-gadgets', 'fashion-style', 'food-drink',
    'furniture-home', 'music', 'nature-plants',
    'news-politics', 'people', 'places-travel',
    'science-technology', 'sports-fitness', 'weapons-military',
]

# User Roles (from viewer_loading.js.md)
ORG_MEMBER_ROLES = {
    'owner': {'permissions': ['all'], 'description': 'Full access to organization'},
    'admin': {'permissions': ['manage_members', 'manage_projects', 'manage_settings'], 'description': 'Can manage team and projects'},
    'member': {'permissions': ['view', 'edit_models', 'create_projects'], 'description': 'Can create and edit content'},
    'viewer': {'permissions': ['view'], 'description': 'Can only view content'},
}

# Themes (from visibility_popup.js.md)
THEMES = {
    'light': {
        'background': '#ffffff',
        'surface': '#f5f5f5',
        'text': '#1a1a1a',
        'primary': '#1caad9',
    },
    'dark': {
        'background': '#1a1a1a',
        'surface': '#2d2d2d',
        'text': '#ffffff',
        'primary': '#1caad9',
    },
}

# Validation Patterns (from viewer_inspector.js.md)
VALIDATION_PATTERNS = {
    'username': r'^[a-zA-Z0-9_]{3,20}$',
    'email': r'^[^\s@]+@[^\s@]+\.[^\s@]+$',
    'model_id': r'^[a-f0-9]{32}$',
    'url': r'^https?://[^\s]+$',
}

# Typography Scale (from viewer_postprocessing.js.md)
TYPOGRAPHY_SCALE = {
    'h1': {'fontSize': '2.5rem', 'fontWeight': 700, 'lineHeight': 1.2},
    'h2': {'fontSize': '2rem', 'fontWeight': 700, 'lineHeight': 1.25},
    'h3': {'fontSize': '1.5rem', 'fontWeight': 600, 'lineHeight': 1.3},
    'h4': {'fontSize': '1.25rem', 'fontWeight': 600, 'lineHeight': 1.4},
    'body': {'fontSize': '1rem', 'fontWeight': 400, 'lineHeight': 1.5},
    'small': {'fontSize': '0.875rem', 'fontWeight': 400, 'lineHeight': 1.5},
    'caption': {'fontSize': '0.75rem', 'fontWeight': 400, 'lineHeight': 1.4},
}

# Full Theme Colors (from viewer_postprocessing.js.md)
THEME_COLORS = {
    'light': {
        'background': '#ffffff',
        'backgroundSecondary': '#f5f5f5',
        'surface': '#ffffff',
        'surfaceHover': '#f8f8f8',
        'text': '#1a1a1a',
        'textSecondary': '#666666',
        'textMuted': '#999999',
        'primary': '#1caad9',
        'primaryHover': '#0e8ab8',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'info': '#3b82f6',
        'border': '#e0e0e0',
    },
    'dark': {
        'background': '#1a1a1a',
        'backgroundSecondary': '#2d2d2d',
        'surface': '#2d2d2d',
        'surfaceHover': '#3d3d3d',
        'text': '#ffffff',
        'textSecondary': '#b0b0b0',
        'textMuted': '#808080',
        'primary': '#1caad9',
        'primaryHover': '#3dbde8',
        'success': '#34d399',
        'warning': '#fbbf24',
        'error': '#f87171',
        'info': '#60a5fa',
        'border': '#404040',
    },
}

# Gradient Presets (from viewer_components.js.md)
GRADIENT_PRESETS = {
    'primary': {'start': '#1caad9', 'end': '#0e7490'},
    'success': {'start': '#10b981', 'end': '#059669'},
    'warning': {'start': '#f59e0b', 'end': '#d97706'},
    'danger': {'start': '#ef4444', 'end': '#dc2626'},
    'purple': {'start': '#8b5cf6', 'end': '#7c3aed'},
    'rainbow': {'start': '#ec4899', 'middle': '#8b5cf6', 'end': '#3b82f6'},
}

# Rating System (from viewer_components.js.md)
RATING_CONFIG = {
    'max': 5,
    'allowHalf': True,
    'sizes': ['small', 'medium', 'large'],
}

# Notification Types (from viewer_annotations.js.md)
NOTIFICATION_TYPES = {
    'info': {'backgroundColor': '#e3f2fd', 'borderColor': '#1976d2', 'textColor': '#1565c0'},
    'warning': {'backgroundColor': '#fff3e0', 'borderColor': '#f57c00', 'textColor': '#e65100'},
    'success': {'backgroundColor': '#e8f5e9', 'borderColor': '#4caf50', 'textColor': '#2e7d32'},
    'error': {'backgroundColor': '#ffebee', 'borderColor': '#f44336', 'textColor': '#c62828'},
}

# Shadow Presets (from viewer_postprocessing.js.md)
SHADOW_PRESETS = {
    'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
    'md': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'lg': '0 10px 15px rgba(0, 0, 0, 0.1)',
    'xl': '0 20px 25px rgba(0, 0, 0, 0.15)',
}

from src.sketchfab_fetcher import SketchfabFetcher
from src.model_decryptor import SketchfabDecryptor, decrypt_model
from src.binz_reader import BinzReader


def cmd_fetch(args):
    """Fetch model information and download files."""
    print(f"Fetching model from: {args.url}")

    fetcher = SketchfabFetcher()
    result = fetcher.fetch_model(args.url)

    if result['error']:
        print(f"Error: {result['error']}")
        return 1

    # Print summary
    api_data = result.get('api_data', {})
    if api_data:
        print(f"\nModel: {api_data.get('name', 'Unknown')}")
        print(f"Author: {api_data.get('user', {}).get('username', 'Unknown')}")
        print(f"Views: {api_data.get('viewCount', 0):,}")
        print(f"Likes: {api_data.get('likeCount', 0):,}")

    # Download files if requested
    if args.download:
        print(f"\nDownloading files to: {args.output_dir}")
        downloaded = fetcher.download_model_files(
            result['model_id'],
            output_dir=args.output_dir
        )
        print(f"Downloaded: {len(downloaded)} files")
        for name, path in downloaded.items():
            print(f"  {name}: {path}")

    # Save metadata
    if args.save_meta:
        meta_file = Path(args.output_dir) / f"{result['model_id']}_metadata.json"
        with open(meta_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Metadata saved to: {meta_file}")

    return 0


def cmd_decrypt(args):
    """Decrypt an encrypted .binz file."""
    binz_path = Path(args.binz_file)
    params_path = Path(args.params_file) if args.params_file else None

    if not binz_path.exists():
        print(f"Error: .binz file not found: {binz_path}")
        return 1

    if params_path and not params_path.exists():
        print(f"Error: params file not found: {params_path}")
        return 1

    print(f"Decrypting: {binz_path.name}")

    try:
        if params_path:
            # Use the convenience function
            decrypted_data = decrypt_model(binz_path, params_path)
        else:
            # Manual decryption with key
            if not args.key:
                print("Error: Must provide --key or --params-file")
                return 1

            try:
                from Crypto.Cipher import AES
                from Crypto.Util.Padding import unpad
            except ImportError:
                print("Error: PyCryptodome required for manual key decryption")
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

        print(f"Decrypted {len(decrypted_data):,} bytes")
        print(f"Saved to: {output_path}")

        # Inspect if requested
        if args.inspect:
            reader = BinzReader()
            info = reader.inspect(decrypted_data)
            print("\nDecrypted data inspection:")
            for key, value in info.items():
                print(f"  {key}: {value}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_inspect(args):
    """Inspect a .binz file."""
    binz_path = Path(args.binz_file)

    if not binz_path.exists():
        print(f"Error: File not found: {binz_path}")
        return 1

    print(f"Inspecting: {binz_path.name}")
    print(f"Size: {binz_path.stat().st_size:,} bytes")

    try:
        reader = BinzReader()
        data = reader.read_file(binz_path)
        print(f"Decompressed size: {len(data):,} bytes")

        info = reader.inspect(data)
        print("\nData structure:")
        for key, value in info.items():
            print(f"  {key}: {value}")

        # Try to load params and parse geometry
        params_path = binz_path.with_suffix('.binz').parent / f"{binz_path.stem}_params.json"
        if params_path.exists():
            print(f"\nFound params file: {params_path.name}")
            with open(params_path, 'r') as f:
                params = json.load(f)

            print("Attempting to parse geometry...")
            geometry = reader.parse_geometry_from_params(data, params)

            if geometry.vertices:
                print(f"✓ Found vertices: {geometry.vertex_count:,}")
            if geometry.normals:
                print(f"✓ Found normals: {geometry.normal_count:,}")
            if geometry.uvs:
                print(f"✓ Found UVs: {geometry.uv_count:,}")
            if geometry.indices:
                print(f"✓ Found indices: {geometry.index_count:,}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_export(args):
    """Export decrypted model to 3MF format."""
    try:
        from src.export_3mf import Model3MFExporter
    except ImportError:
        print("Error: Could not import 3MF exporter")
        return 1

    binz_path = Path(args.binz_file)
    output_path = Path(args.output)

    if not binz_path.exists():
        print(f"Error: .binz file not found: {binz_path}")
        return 1

    print(f"Exporting {binz_path.name} to 3MF...")

    try:
        exporter = Model3MFExporter()
        exporter.load_from_binary(binz_path)
        exporter.export_3mf(output_path)

        print(f"✓ Exported to: {output_path}")
        print(f"  Vertices: {len(exporter.vertices):,}")
        print(f"  Triangles: {len(exporter.triangles):,}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_demo(args):
    """Launch a demonstration script."""
    demos = {
        'decryption': 'demos/demo_decryption.py',
        'viewer': 'demos/demo_viewer.py',
        'inspect': 'demos/inspect_model.py'
    }
    
    if args.demo_name not in demos:
        print(f"Error: Unknown demo '{args.demo_name}'. Available: {', '.join(demos.keys())}")
        return 1
    
    demo_path = Path(__file__).parent / demos[args.demo_name]
    if not demo_path.exists():
        print(f"Error: Demo file not found: {demo_path}")
        return 1
    
    print(f"Launching demo: {args.demo_name}")
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(demo_path)])
        return result.returncode
    except Exception as e:
        print(f"Error launching demo: {e}")
        return 1


def cmd_gui(args):
    """Launch the graphical user interface."""
    gui_path = Path(__file__).parent / 'sketchfab_gui.py'
    if not gui_path.exists():
        print(f"Error: GUI file not found: {gui_path}")
        return 1
    
    print("Launching GUI...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(gui_path)])
        return result.returncode
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return 1


def cmd_viewer(args):
    """Launch the 3D model viewer."""
    try:
        from PyQt6.QtWidgets import QApplication
        from src.model_viewer import ModelViewerPanel
        import sys
    except ImportError as e:
        print(f"Error: Missing required packages for viewer: {e}")
        print("Install with: pip install PyQt6 PyOpenGL")
        return 1

    print("Launching 3D Model Viewer...")

    try:
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Create viewer window
        from PyQt6.QtWidgets import QMainWindow
        window = QMainWindow()
        window.setWindowTitle("Sketchfab Model Viewer")
        window.setMinimumSize(800, 600)
        
        # Create viewer panel
        viewer = ModelViewerPanel()
        window.setCentralWidget(viewer)
        
        # Load model if specified
        if args.binz_file:
            binz_path = Path(args.binz_file)
            if binz_path.exists():
                print(f"Loading model: {binz_path}")
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
                    print(f"Model loaded successfully: {vertex_count:,} vertices, {triangle_count:,} triangles")
                else:
                    print(f"Failed to load model: {binz_path}")
            else:
                print(f"Model file not found: {binz_path}")
        
        # Show window
        window.show()
        
        # Run application
        return app.exec()
        
    except Exception as e:
        print(f"Error launching viewer: {e}")
        return 1


def cmd_info(args):
    """Show information about available commands."""
    print("Sketchfab Model Tools CLI")
    print("=" * 65)
    print()
    print("Core Commands:")
    print("  fetch       - Fetch model info and download files from Sketchfab")
    print("  decrypt     - Decrypt an encrypted .binz file")
    print("  inspect     - Inspect a .binz file structure")
    print("  export      - Export decrypted model to 3MF format")
    print("  viewer      - Launch 3D model viewer")
    print()
    print("Search & Discovery Commands (from Sketchfab JS analysis):")
    print("  search      - Search for models on Sketchfab")
    print("  user        - Look up a Sketchfab user")
    print("  stats       - Fetch and display model statistics from API")
    print("  categories  - Display model categories")
    print()
    print("URL & Embed Commands:")
    print("  embed       - Generate embed URL or iframe code for a model")
    print("  parse-url   - Parse and analyze Sketchfab URLs")
    print("  thumbnail   - Generate thumbnail URLs for a model")
    print()
    print("Configuration & Design Commands:")
    print("  config      - Display or generate viewer configuration")
    print("  api         - Display API endpoint information and utilities")
    print("  ai-info     - Show information about Sketchfab AI tools")
    print("  tiers       - Display subscription tier information")
    print("  design      - Show design system (colors, typography, gradients)")
    print("  validate    - Validate input values (username, email, model_id, url)")
    print()
    print("Web Scraping Commands:")
    print("  scrape      - Scrape webpage content using requests/BeautifulSoup")
    print("  session     - Demonstrate session management with cookiejar")
    print("  download-js - Download all JavaScript files from a website")
    print()
    print("Other Commands:")
    print("  demo        - Launch demonstration scripts")
    print("  gui         - Launch graphical user interface")
    print("  info        - Show this help information")
    print()
    print("Configuration Constants (from JS analysis):")
    print(f"  API Base URL: {SKETCHFAB_API_BASE}")
    print(f"  Embed Options: {len(EMBED_OPTIONS)} parameters available")
    print(f"  Quality Presets: {', '.join(QUALITY_PRESETS.keys())}")
    print(f"  Environment Presets: {', '.join(ENVIRONMENT_PRESETS.keys())}")
    print(f"  AI Providers: {', '.join(AI_PROVIDERS.keys())}")
    print(f"  Download Formats: {', '.join(DOWNLOAD_FORMATS)}")
    print()
    print("Use 'python cli.py <command> --help' for command-specific help.")


def cmd_scrape(args):
    """Scrape webpage content using requests and BeautifulSoup."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        print(f"Error: Missing required packages: {e}")
        print("Install with: pip install requests beautifulsoup4")
        return 1

    print(f"Scraping: {args.url}")

    try:
        # Make request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(args.url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        if args.title:
            title = soup.title.string if soup.title else "No title found"
            print(f"Title: {title}")

        if args.links:
            links = soup.find_all('a', href=True)
            print(f"Found {len(links)} links:")
            for i, link in enumerate(links[:args.max_links]):
                print(f"  {i+1}. {link.get('href')} - {link.get_text().strip()[:50]}")

        if args.text:
            # Extract text content
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            print(f"Text content ({len(lines)} lines):")
            for line in lines[:args.max_lines]:
                print(f"  {line}")

        if args.save_html:
            output_path = Path(args.save_html)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"HTML saved to: {output_path}")

        return 0

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_session(args):
    """Demonstrate session management with cookiejar."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        print(f"Error: Missing required packages: {e}")
        print("Install with: pip install requests beautifulsoup4")
        return 1

    print("Demonstrating session management with cookiejar...")

    try:
        # Create a cookiejar and session
        jar = http.cookiejar.CookieJar()
        session = requests.Session()
        session.cookies = jar

        # First request to establish session
        print(f"Making initial request to: {args.url}")
        response1 = session.get(args.url, timeout=10)
        response1.raise_for_status()

        print(f"Initial response status: {response1.status_code}")
        print(f"Cookies received: {len(jar)}")

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

                print(f"\nFollowing link to: {next_url}")
                response2 = session.get(next_url, timeout=10)
                response2.raise_for_status()
                print(f"Follow-up response status: {response2.status_code}")
                print(f"Cookies after follow-up: {len(jar)}")
            else:
                print("No links found to follow")

        # Save cookies if requested
        if args.save_cookies:
            cookie_file = Path(args.save_cookies)
            jar.save(cookie_file, ignore_discard=True, ignore_expires=True)
            print(f"Cookies saved to: {cookie_file}")

        return 0

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_download_js(args):
    """Download all JavaScript files from a website."""
    try:
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin, urlparse
        import json
    except ImportError as e:
        print(f"Error: Missing required packages: {e}")
        print("Install with: pip install requests beautifulsoup4")
        return 1

    print(f"Downloading JavaScript files from: {args.url}")

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        while url_queue and (not args.max_pages or len(processed_urls) < args.max_pages):
            current_url = url_queue.pop(0)

            if current_url in processed_urls:
                continue

            processed_urls.add(current_url)
            print(f"Processing: {current_url}")

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
        print(f"Error: Could not extract model ID from: {args.model_id_or_url}")
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


def main():
    parser = argparse.ArgumentParser(
        description="Sketchfab Model Tools CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch model from Sketchfab')
    fetch_parser.add_argument('url', help='Sketchfab model URL')
    fetch_parser.add_argument('--download', action='store_true',
                             help='Download model files')
    fetch_parser.add_argument('--output-dir', default='downloads',
                             help='Output directory for downloads (default: downloads)')
    fetch_parser.add_argument('--save-meta', action='store_true',
                             help='Save metadata to JSON file')
    fetch_parser.set_defaults(func=cmd_fetch)

    # Decrypt command
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt .binz file')
    decrypt_parser.add_argument('binz_file', help='Path to .binz file')
    decrypt_parser.add_argument('--params-file',
                               help='Path to params JSON file (alternative to --key)')
    decrypt_parser.add_argument('--key', help='Base64-encoded encryption key')
    decrypt_parser.add_argument('--output', required=True,
                               help='Output path for decrypted file')
    decrypt_parser.add_argument('--inspect', action='store_true',
                               help='Inspect decrypted data after decryption')
    decrypt_parser.set_defaults(func=cmd_decrypt)

    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect .binz file')
    inspect_parser.add_argument('binz_file', help='Path to .binz file')
    inspect_parser.set_defaults(func=cmd_inspect)

    # Export command
    export_parser = subparsers.add_parser('export', help='Export to 3MF format')
    export_parser.add_argument('binz_file', help='Path to decrypted .binz file')
    export_parser.add_argument('--output', required=True,
                              help='Output .3mf file path')
    export_parser.set_defaults(func=cmd_export)

    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Launch demonstration scripts')
    demo_parser.add_argument('demo_name', choices=['decryption', 'viewer', 'inspect'],
                            help='Name of the demo to launch')
    demo_parser.set_defaults(func=cmd_demo)

    # GUI command
    gui_parser = subparsers.add_parser('gui', help='Launch graphical user interface')
    gui_parser.set_defaults(func=cmd_gui)

    # Viewer command
    viewer_parser = subparsers.add_parser('viewer', help='Launch 3D model viewer')
    viewer_parser.add_argument('binz_file', nargs='?', help='Path to .binz file to load (optional)')
    viewer_parser.set_defaults(func=cmd_viewer)

    # Info command
    info_parser = subparsers.add_parser('info', help='Show information')
    info_parser.set_defaults(func=cmd_info)

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape webpage with requests and BeautifulSoup')
    scrape_parser.add_argument('url', help='URL to scrape')
    scrape_parser.add_argument('--title', action='store_true',
                              help='Extract and display page title')
    scrape_parser.add_argument('--links', action='store_true',
                              help='Extract and display links')
    scrape_parser.add_argument('--text', action='store_true',
                              help='Extract and display text content')
    scrape_parser.add_argument('--max-links', type=int, default=10,
                              help='Maximum number of links to display (default: 10)')
    scrape_parser.add_argument('--max-lines', type=int, default=20,
                              help='Maximum number of text lines to display (default: 20)')
    scrape_parser.add_argument('--save-html', 
                              help='Save parsed HTML to file')
    scrape_parser.set_defaults(func=cmd_scrape)

    # Session command
    session_parser = subparsers.add_parser('session', help='Demonstrate session management with cookiejar')
    session_parser.add_argument('url', help='URL to start session with')
    session_parser.add_argument('--follow-link', action='store_true',
                               help='Follow the first link found on the page')
    session_parser.add_argument('--save-cookies',
                               help='Save cookies to file (Mozilla format)')
    session_parser.set_defaults(func=cmd_session)

    # Download JS command
    download_js_parser = subparsers.add_parser('download-js', help='Download all JavaScript files from a website')
    download_js_parser.add_argument('url', help='Website URL to download JS files from')
    download_js_parser.add_argument('--output-dir', default='js_downloads',
                                   help='Output directory for downloaded files (default: js_downloads)')
    download_js_parser.add_argument('--recursive', action='store_true',
                                   help='Recursively follow links on the same domain')
    download_js_parser.add_argument('--max-pages', type=int,
                                   help='Maximum number of pages to process (default: unlimited)')
    download_js_parser.add_argument('--external-domains', action='store_true',
                                   help='Download JS files from external domains')
    download_js_parser.add_argument('--parse-json', action='store_true',
                                   help='Parse JSON responses for JS files and recursively follow API endpoints')
    download_js_parser.add_argument('--verbose', action='store_true',
                                   help='Show verbose output')
    download_js_parser.set_defaults(func=cmd_download_js)

    # =========================================================================
    # NEW COMMANDS - Based on JavaScript analysis
    # =========================================================================
    
    # Embed command - Generate embed URLs and iframe code
    embed_parser = subparsers.add_parser('embed', 
        help='Generate embed URL or iframe code for a Sketchfab model')
    embed_parser.add_argument('model_id_or_url', 
        help='Model ID or Sketchfab URL')
    embed_parser.add_argument('--iframe', action='store_true',
        help='Generate iframe HTML code')
    embed_parser.add_argument('--width', type=int, default=640,
        help='iFrame width (default: 640)')
    embed_parser.add_argument('--height', type=int, default=480,
        help='iFrame height (default: 480)')
    embed_parser.add_argument('--autostart', action='store_true',
        help='Auto-load model on page load')
    embed_parser.add_argument('--autospin', type=float,
        help='Auto-rotate speed (0 to disable)')
    embed_parser.add_argument('--no-ui', action='store_true',
        help='Hide all UI controls')
    embed_parser.add_argument('--no-watermark', dest='watermark', action='store_false',
        help='Hide watermark (requires plan)')
    embed_parser.add_argument('--transparent', action='store_true',
        help='Transparent background')
    embed_parser.add_argument('--no-scrollwheel', action='store_true',
        help='Disable scroll wheel zoom')
    embed_parser.add_argument('--animation-autoplay', action='store_true',
        help='Auto-play animations')
    embed_parser.add_argument('--annotation', type=int,
        help='Open specific annotation by index')
    embed_parser.add_argument('--preload', action='store_true',
        help='Preload textures')
    embed_parser.add_argument('--copy', action='store_true',
        help='Copy URL to clipboard')
    embed_parser.set_defaults(func=cmd_embed, watermark=True)

    # Config command - Viewer configuration utilities
    config_parser = subparsers.add_parser('config',
        help='Display or generate viewer configuration')
    config_parser.add_argument('--list-presets', action='store_true',
        help='Show quality and environment presets')
    config_parser.add_argument('--list-embed-options', action='store_true',
        help='Show all embed URL parameters')
    config_parser.add_argument('--list-materials', action='store_true',
        help='Show material display options')
    config_parser.add_argument('--generate', action='store_true',
        help='Generate viewer configuration JSON')
    config_parser.add_argument('--quality', choices=['low', 'medium', 'high', 'ultra'],
        help='Quality preset for generated config')
    config_parser.add_argument('--environment', choices=['studio', 'urban', 'dawn', 'night', 'custom'],
        help='Environment preset')
    config_parser.add_argument('--fov', type=int,
        help='Camera field of view')
    config_parser.add_argument('--exposure', type=float,
        help='Lighting exposure')
    config_parser.add_argument('--auto-rotate', action='store_true',
        help='Enable auto-rotation')
    config_parser.add_argument('--no-shadows', action='store_true',
        help='Disable shadows')
    config_parser.add_argument('--no-postprocessing', action='store_true',
        help='Disable post-processing')
    config_parser.add_argument('--ssao', action='store_true',
        help='Enable SSAO')
    config_parser.add_argument('--bloom', action='store_true',
        help='Enable bloom effect')
    config_parser.add_argument('--output', '-o',
        help='Save generated config to file')
    config_parser.set_defaults(func=cmd_config)

    # API command - API endpoint utilities
    api_parser = subparsers.add_parser('api',
        help='Display API endpoint information and utilities')
    api_parser.add_argument('--list-endpoints', action='store_true',
        help='Show all API endpoints')
    api_parser.add_argument('--build-url',
        help='Build a specific API URL (endpoint name)')
    api_parser.add_argument('--model-id',
        help='Model ID for URL building')
    api_parser.add_argument('--username',
        help='Username for URL building')
    api_parser.add_argument('--params', nargs='*',
        help='Query parameters (key=value format)')
    api_parser.add_argument('--token',
        help='API token for authentication')
    api_parser.add_argument('--curl', action='store_true',
        help='Output as curl command')
    api_parser.add_argument('--formats', action='store_true',
        help='Show download formats')
    api_parser.add_argument('--visibility', action='store_true',
        help='Show visibility types')
    api_parser.set_defaults(func=cmd_api)

    # AI Info command - AI tools information
    ai_parser = subparsers.add_parser('ai-info',
        help='Display information about Sketchfab AI tools and providers')
    ai_parser.set_defaults(func=cmd_ai_info)

    # Parse URL command - URL analysis
    parse_url_parser = subparsers.add_parser('parse-url',
        help='Parse and analyze Sketchfab URLs')
    parse_url_parser.add_argument('url',
        help='URL to parse')
    parse_url_parser.set_defaults(func=cmd_parse_url)

    # Stats command - Fetch model statistics
    stats_parser = subparsers.add_parser('stats',
        help='Fetch and display model statistics')
    stats_parser.add_argument('model_id_or_url',
        help='Model ID or Sketchfab URL')
    stats_parser.add_argument('--token',
        help='API token for authenticated requests')
    stats_parser.add_argument('--json', action='store_true',
        help='Output raw JSON response')
    stats_parser.set_defaults(func=cmd_stats)

    # Search command - Search for models
    search_parser = subparsers.add_parser('search',
        help='Search for models on Sketchfab')
    search_parser.add_argument('query',
        help='Search query')
    search_parser.add_argument('--type', choices=['models', 'collections', 'users'],
        default='models', help='Type of results (default: models)')
    search_parser.add_argument('--sort', 
        choices=['relevance', 'likeCount', 'viewCount', 'createdAt', 'publishedAt'],
        help='Sort results by')
    search_parser.add_argument('--downloadable', action='store_true',
        help='Only show downloadable models')
    search_parser.add_argument('--animated', action='store_true',
        help='Only show animated models')
    search_parser.add_argument('--staffpicked', action='store_true',
        help='Only show staff picks')
    search_parser.add_argument('--category',
        help='Filter by category slug')
    search_parser.add_argument('--count', type=int, default=10,
        help='Number of results (default: 10, max: 24)')
    search_parser.add_argument('--json', action='store_true',
        help='Output raw JSON response')
    search_parser.set_defaults(func=cmd_search)

    # User command - Look up user
    user_parser = subparsers.add_parser('user',
        help='Look up a Sketchfab user')
    user_parser.add_argument('username',
        help='Username to look up (with or without @)')
    user_parser.add_argument('--models', action='store_true',
        help='Show user\'s recent models')
    user_parser.add_argument('--json', action='store_true',
        help='Output raw JSON response')
    user_parser.set_defaults(func=cmd_user)

    # Thumbnail command - Generate thumbnail URLs
    thumbnail_parser = subparsers.add_parser('thumbnail',
        help='Generate thumbnail URLs for a model')
    thumbnail_parser.add_argument('model_id_or_url',
        help='Model ID or Sketchfab URL')
    thumbnail_parser.add_argument('--fetch', action='store_true',
        help='Fetch actual thumbnails from API')
    thumbnail_parser.set_defaults(func=cmd_thumbnail)

    # Tiers command - Subscription tier info
    tiers_parser = subparsers.add_parser('tiers',
        help='Display subscription tier information')
    tiers_parser.set_defaults(func=cmd_tiers)

    # Validate command - Validate input values
    validate_parser = subparsers.add_parser('validate',
        help='Validate input values against Sketchfab patterns')
    validate_parser.add_argument('type',
        choices=['username', 'email', 'model_id', 'url'],
        help='Type of value to validate')
    validate_parser.add_argument('value',
        help='Value to validate')
    validate_parser.set_defaults(func=cmd_validate)

    # Categories command - List categories
    categories_parser = subparsers.add_parser('categories',
        help='Display Sketchfab model categories')
    categories_parser.set_defaults(func=cmd_categories)

    # Design command - Design system information
    design_parser = subparsers.add_parser('design',
        help='Display Sketchfab design system information')
    design_parser.add_argument('--colors', action='store_true',
        help='Show color palettes')
    design_parser.add_argument('--typography', action='store_true',
        help='Show typography scale')
    design_parser.add_argument('--gradients', action='store_true',
        help='Show gradient presets')
    design_parser.add_argument('--shadows', action='store_true',
        help='Show shadow presets')
    design_parser.add_argument('--notifications', action='store_true',
        help='Show notification type colors')
    design_parser.add_argument('--generate-css', action='store_true',
        help='Generate CSS variables')
    design_parser.add_argument('--theme', choices=['light', 'dark'],
        help='Theme for CSS generation')
    design_parser.set_defaults(func=cmd_design)

    # Parse args
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Run the command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())