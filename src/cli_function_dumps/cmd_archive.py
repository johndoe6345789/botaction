# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_archive(args):
    """Download model archive via internal API endpoints."""
    try:
        import requests
        from urllib.parse import urlparse
    except ImportError as e:
        print(f"Error: Missing required packages: {e}")
        print("Install with: pip install requests")
        return 1

    model_id = extract_model_id(args.model_id_or_url)
    if not model_id:
        print(f"Error: Could not extract model ID from: {args.model_id_or_url}")
        return 1

    http_config = get_http_config()
    session = requests.Session()
    session.headers.update({
        'User-Agent': http_config['user_agent'],
        'Accept': 'application/json',
    })

    if args.cookie_jar:
        jar_path = Path(args.cookie_jar)
        if not jar_path.exists():
            print(f"Error: Cookie jar not found: {jar_path}")
            return 1

        raw_jar = http.cookiejar.MozillaCookieJar(str(jar_path))
        raw_jar.load(ignore_discard=True, ignore_expires=True)
        jar = requests.cookies.RequestsCookieJar()
        for cookie in raw_jar:
            jar.set_cookie(cookie)
        session.cookies = jar

    model_url = f"{SKETCHFAB_BASE_URL}/models/{model_id}"
    try:
        session.get(model_url, timeout=10)
    except requests.RequestException as e:
        print(f"Warning: Failed to load model page: {e}")

    archive_type = (args.archive_type or "gltf").lower()
    archive_endpoint = f"{SKETCHFAB_BASE_URL}/i/archives/latest?archive_type={archive_type}&model={model_id}"
    download_endpoint = f"{SKETCHFAB_BASE_URL}/i/models/{model_id}/download"

    def extract_urls(obj):
        urls = []
        if isinstance(obj, dict):
            for value in obj.values():
                urls.extend(extract_urls(value))
        elif isinstance(obj, list):
            for value in obj:
                urls.extend(extract_urls(value))
        elif isinstance(obj, str) and obj.startswith(("http://", "https://")):
            urls.append(obj)
        return urls

    def pick_url(urls):
        if not urls:
            return None
        for url in urls:
            if archive_type in url:
                return url
        if archive_type == "glb":
            for url in urls:
                if url.lower().endswith(".glb"):
                    return url
        if archive_type in ("gltf", "source"):
            for url in urls:
                if url.lower().endswith(".zip"):
                    return url
        if archive_type == "usdz":
            for url in urls:
                if url.lower().endswith(".usdz"):
                    return url
        return urls[0]

    def resolve_url(resp):
        try:
            data = resp.json()
        except ValueError:
            return None, None

        if args.json:
            print(json.dumps(data, indent=2))

        archive_entry = data.get(archive_type)
        if isinstance(archive_entry, dict) and archive_entry.get("url"):
            return archive_entry.get("url"), data

        if isinstance(data, dict) and data.get("url"):
            return data.get("url"), data

        urls = extract_urls(data)
        return pick_url(urls), data

    url = None
    data = None

    try:
        resp = session.get(archive_endpoint, headers={'Referer': model_url}, timeout=10)
        if resp.status_code == 200:
            url, data = resolve_url(resp)
        else:
            print(f"Archive endpoint returned {resp.status_code}")
    except requests.RequestException as e:
        print(f"Archive endpoint error: {e}")

    if not url:
        try:
            resp = session.get(download_endpoint, headers={'Referer': model_url}, timeout=10)
            if resp.status_code == 200:
                url, data = resolve_url(resp)
            else:
                print(f"Download endpoint returned {resp.status_code}")
        except requests.RequestException as e:
            print(f"Download endpoint error: {e}")

    if not url:
        print("Error: No archive URL found. This endpoint usually requires an authenticated session.")
        return 1

    if args.url_only:
        print(url)
        return 0

    output_path = Path(args.output) if args.output else None
    if output_path is None:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = Path(urlparse(url).path).name
        if not filename:
            ext = ""
            if archive_type == "glb":
                ext = ".glb"
            elif archive_type in ("gltf", "source"):
                ext = ".zip"
            elif archive_type == "usdz":
                ext = ".usdz"
            filename = f"{model_id}_{archive_type}{ext}"
        output_path = output_dir / filename

    try:
        with session.get(url, stream=True, timeout=30) as download:
            download.raise_for_status()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                for chunk in download.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"Downloaded archive to: {output_path}")
        return 0
    except requests.RequestException as e:
        print(f"Download failed: {e}")
        return 1
