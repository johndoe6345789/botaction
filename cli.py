#!/usr/bin/env python3
"""
Sketchfab Model Tools CLI

A command-line interface for working with Sketchfab 3D models.
Supports fetching, decrypting, inspecting, and exporting models.
"""

import argparse
import sys
import json
from pathlib import Path
import http.cookiejar

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

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


def cmd_info(args):
    """Show information about available commands."""
    print("Sketchfab Model Tools CLI")
    print("=" * 40)
    print()
    print("Available commands:")
    print("  fetch    - Fetch model info and download files from Sketchfab")
    print("  decrypt  - Decrypt an encrypted .binz file")
    print("  inspect  - Inspect a .binz file structure")
    print("  export   - Export decrypted model to 3MF format")
    print("  scrape   - Scrape webpage content using requests and BeautifulSoup")
    print("  session  - Demonstrate session management with cookiejar")
    print("  download-js - Download all JavaScript files from a website")
    print("  demo     - Launch demonstration scripts")
    print("  gui      - Launch graphical user interface")
    print("  info     - Show this help information")
    print()
    print("Use 'sketchfab-cli <command> --help' for command-specific help.")


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

                # Process JSON files that might contain JS references
                elif 'application/json' in content_type and args.parse_json:
                    try:
                        json_data = response.json()

                        # Recursively search for URLs in JSON
                        def find_urls(obj, path=""):
                            urls = []
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    current_path = f"{path}.{key}" if path else key
                                    if isinstance(value, str) and (value.endswith('.js') or '.js' in value):
                                        # Check if it looks like a URL
                                        if value.startswith(('http://', 'https://', '//')):
                                            urls.append(value)
                                        elif value.startswith('/'):
                                            # Relative URL
                                            urls.append(urljoin(args.url, value))
                                    else:
                                        urls.extend(find_urls(value, current_path))
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    urls.extend(find_urls(item, f"{path}[{i}]"))
                            return urls

                        js_urls = find_urls(json_data)
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
                                   help='Parse JSON responses for additional JS file references')
    download_js_parser.add_argument('--verbose', action='store_true',
                                   help='Show verbose output')
    download_js_parser.set_defaults(func=cmd_download_js)

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