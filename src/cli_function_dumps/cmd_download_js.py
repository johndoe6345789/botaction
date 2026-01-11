# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

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
