"""
Sketchfab Model Fetcher

Fetches model data from Sketchfab including metadata and file URLs.

Key findings about Sketchfab's model format:
- Models are stored as .binz files (encrypted binary geometry)
- The 'p' parameter in file config contains base64-encoded encryption params
- 'd: true' in the config indicates the file is encrypted
- Encryption uses AES (exact mode TBD - likely in their osgjs viewer code)
- The osgjs viewer decrypts at runtime in the browser

File structure:
- osgjsUrl: URL to the encrypted .binz file
- osgjsSize: Size of the scene description
- modelSize: Size of the geometry data
- wireframeSize: Size of wireframe data
- p[].b: Base64-encoded key material (first 32 bytes = key, next 16 = IV)
- p[].d: Boolean indicating encryption status
- p[].v: Version number
"""

import requests
import json
import re
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


class SketchfabFetcher:
    """Fetches model data from Sketchfab."""

    BASE_URL = "https://sketchfab.com"
    API_URL = "https://api.sketchfab.com/v3"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

    def extract_model_id(self, url: str) -> Optional[str]:
        """Extract model ID from Sketchfab URL."""
        # Pattern: https://sketchfab.com/3d-models/model-name-{id}
        match = re.search(r'([a-f0-9]{32})$', url)
        if match:
            return match.group(1)

        # Try alternate patterns
        match = re.search(r'/models/([a-f0-9]{32})', url)
        if match:
            return match.group(1)

        return None

    def fetch_page(self, url: str) -> str:
        """Fetch the HTML page content."""
        response = self.session.get(url)
        response.raise_for_status()
        return response.text

    def fetch_model_api(self, model_id: str) -> Dict[str, Any]:
        """Fetch model data from Sketchfab API."""
        api_url = f"{self.API_URL}/models/{model_id}"
        response = self.session.get(api_url)
        response.raise_for_status()
        return response.json()

    def extract_embed_data(self, html: str) -> Optional[Dict[str, Any]]:
        """Extract embedded JSON data from page HTML."""
        # Look for prefetched data in script tags
        patterns = [
            r'window\.prefetchedData\s*=\s*(\{.*?\});',
            r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',
            r'"model"\s*:\s*(\{.*?\})\s*[,}]',
        ]

        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue

        return None

    def find_file_urls(self, html: str) -> Dict[str, str]:
        """Find file URLs in the page."""
        urls = {}

        # Look for osgjs file
        osgjs_match = re.search(r'(https?://[^"\']+\.osgjs[^"\']*)', html)
        if osgjs_match:
            urls['osgjs'] = osgjs_match.group(1)

        # Look for bin/binz files
        bin_matches = re.findall(r'(https?://[^"\']+\.bin[z]?[^"\']*)', html)
        for i, url in enumerate(bin_matches):
            urls[f'bin_{i}'] = url

        # Look for texture files
        texture_matches = re.findall(r'(https?://[^"\']+\.(jpg|png|jpeg|webp)[^"\']*)', html, re.I)
        for i, (url, ext) in enumerate(texture_matches):
            urls[f'texture_{i}'] = url

        return urls

    def fetch_embed_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Fetch the embed configuration which contains file URLs."""
        # Try the internal API endpoint
        config_url = f"{self.BASE_URL}/i/models/{model_id}"
        try:
            response = self.session.get(config_url)
            if response.status_code == 200:
                return response.json()
        except:
            pass

        # Try embed page
        embed_url = f"{self.BASE_URL}/models/{model_id}/embed"
        try:
            response = self.session.get(embed_url)
            if response.status_code == 200:
                # Look for configuration in embed page
                html = response.text

                # Find osgjs/files configuration
                config_match = re.search(r'var\s+config\s*=\s*(\{.*?\});', html, re.DOTALL)
                if config_match:
                    return json.loads(config_match.group(1))

                # Look for prefetched data
                prefetch_match = re.search(r'prefetchedData\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
                if prefetch_match:
                    return json.loads(prefetch_match.group(1))
        except:
            pass

        return None

    def fetch_file_config(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Fetch the file configuration for the 3D model."""
        # This endpoint returns the osgjs file locations
        file_url = f"{self.BASE_URL}/i/models/{model_id}/file"
        try:
            response = self.session.get(file_url)
            if response.status_code == 200:
                return response.json()
        except:
            pass

        return None

    def fetch_model(self, url: str) -> Dict[str, Any]:
        """
        Fetch all available data for a model.

        Args:
            url: Sketchfab model URL

        Returns:
            Dict with model data, API response, and discovered URLs
        """
        result = {
            'url': url,
            'model_id': None,
            'api_data': None,
            'page_data': None,
            'embed_config': None,
            'file_config': None,
            'file_urls': {},
            'error': None,
        }

        # Extract model ID
        model_id = self.extract_model_id(url)
        if not model_id:
            result['error'] = 'Could not extract model ID from URL'
            return result

        result['model_id'] = model_id
        print(f"Model ID: {model_id}")

        # Fetch API data
        try:
            api_data = self.fetch_model_api(model_id)
            result['api_data'] = api_data
            print(f"Model name: {api_data.get('name', 'Unknown')}")
            print(f"Author: {api_data.get('user', {}).get('username', 'Unknown')}")
        except requests.RequestException as e:
            print(f"API fetch failed: {e}")

        # Fetch embed config
        try:
            embed_config = self.fetch_embed_config(model_id)
            result['embed_config'] = embed_config
            if embed_config:
                print(f"Got embed config with {len(embed_config)} keys")
        except Exception as e:
            print(f"Embed config fetch failed: {e}")

        # Fetch file config
        try:
            file_config = self.fetch_file_config(model_id)
            result['file_config'] = file_config
            if file_config:
                print(f"Got file config")
        except Exception as e:
            print(f"File config fetch failed: {e}")

        # Fetch page HTML
        try:
            html = self.fetch_page(url)
            result['page_data'] = self.extract_embed_data(html)
            result['file_urls'] = self.find_file_urls(html)
        except requests.RequestException as e:
            result['error'] = f"Page fetch failed: {e}"

        return result


def main():
    url = "https://sketchfab.com/3d-models/annihilator-2000-dea4f17e94974e1fa720cbadc531ed63"

    print("=" * 60)
    print("Sketchfab Model Fetcher")
    print("=" * 60)
    print(f"\nFetching: {url}\n")

    fetcher = SketchfabFetcher()
    result = fetcher.fetch_model(url)

    print("\n" + "=" * 60)
    print("Results")
    print("=" * 60)

    if result['error']:
        print(f"\nError: {result['error']}")

    if result['api_data']:
        api = result['api_data']
        print(f"\n--- Model Info ---")
        print(f"Name: {api.get('name')}")
        print(f"Description: {api.get('description', '')[:200]}...")
        print(f"Author: {api.get('user', {}).get('username')}")
        print(f"Views: {api.get('viewCount', 0)}")
        print(f"Likes: {api.get('likeCount', 0)}")
        print(f"Is downloadable: {api.get('isDownloadable', False)}")
        print(f"License: {api.get('license', {}).get('label', 'Unknown')}")

        # Thumbnails
        thumbnails = api.get('thumbnails', {}).get('images', [])
        if thumbnails:
            print(f"\n--- Thumbnails ---")
            for thumb in thumbnails[:3]:
                print(f"  {thumb.get('width')}x{thumb.get('height')}: {thumb.get('url')}")

    if result['file_urls']:
        print(f"\n--- Discovered File URLs ---")
        for name, url in result['file_urls'].items():
            print(f"  {name}: {url[:80]}...")

    # Save full result to JSON
    output_file = 'model_data.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nFull data saved to: {output_file}")

    return result


if __name__ == "__main__":
    main()
