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

        # Fetch page HTML first to establish cookies for later requests
        try:
            html = self.fetch_page(url)
            result['page_data'] = self.extract_embed_data(html)
            result['file_urls'] = self.find_file_urls(html)
        except requests.RequestException as e:
            result['error'] = f"Page fetch failed: {e}"

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

        return result

    def download_model_files(self, model_id: str, output_dir: str = '.') -> Dict[str, str]:
        """
        Download model files (encrypted .binz and any available assets).

        Args:
            model_id: Sketchfab model ID
            output_dir: Directory to save files

        Returns:
            Dict mapping file type to local path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        downloaded = {}

        # Get embed config for file URLs
        config = self.fetch_embed_config(model_id)
        if not config or 'files' not in config:
            print("Could not get file configuration")
            return downloaded

        for file_info in config['files']:
            file_uid = file_info.get('uid', 'unknown')
            binz_url = file_info.get('osgjsUrl')

            if binz_url:
                print(f"Downloading: {binz_url}")
                try:
                    response = self.session.get(binz_url)
                    if response.status_code == 200:
                        filename = f"{model_id}_{file_uid}.binz"
                        filepath = output_path / filename
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        downloaded['binz'] = str(filepath)
                        print(f"  Saved: {filepath} ({len(response.content)} bytes)")

                        # Also save encryption params
                        params = file_info.get('p', [])
                        if params:
                            params_file = output_path / f"{model_id}_{file_uid}_params.json"
                            with open(params_file, 'w') as f:
                                json.dump(params, f, indent=2)
                            downloaded['params'] = str(params_file)
                            print(f"  Params: {params_file}")

                        # Attempt to download geometry files from the same directory
                        base_url = binz_url.rsplit('/', 1)[0]
                        for suffix in ("model_file.binz", "model_file_wireframe.binz"):
                            file_url = f"{base_url}/{suffix}"
                            try:
                                file_resp = self.session.get(file_url)
                                if file_resp.status_code == 200:
                                    out_name = f"{model_id}_{suffix}"
                                    out_path = output_path / out_name
                                    with open(out_path, 'wb') as f:
                                        f.write(file_resp.content)
                                    key = "model_file" if "wireframe" not in suffix else "wireframe"
                                    downloaded[key] = str(out_path)
                                    print(f"  Saved: {out_path} ({len(file_resp.content)} bytes)")
                            except Exception as e:
                                print(f"  Failed to download {file_url}: {e}")
                except Exception as e:
                    print(f"  Failed: {e}")

        # Try to get thumbnails
        api_data = self.fetch_model_api(model_id)
        if api_data:
            thumbnails = api_data.get('thumbnails', {}).get('images', [])
            if thumbnails:
                # Get largest thumbnail
                largest = max(thumbnails, key=lambda x: x.get('width', 0))
                thumb_url = largest.get('url')
                if thumb_url:
                    try:
                        response = self.session.get(thumb_url)
                        if response.status_code == 200:
                            ext = thumb_url.split('.')[-1].split('?')[0]
                            thumb_path = output_path / f"{model_id}_thumbnail.{ext}"
                            with open(thumb_path, 'wb') as f:
                                f.write(response.content)
                            downloaded['thumbnail'] = str(thumb_path)
                            print(f"  Thumbnail: {thumb_path}")
                    except:
                        pass

        return downloaded

    def download_diter_files(self, model_id: str, output_dir: str = "downloads") -> Dict[str, str]:
        """
        Download DITER WASM decoder and key files from Sketchfab embed page.
        
        Returns:
            Dictionary with paths to downloaded WASM and key files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        downloaded = {}
        
        # Fetch embed page to find JS bundle URLs
        embed_url = f"{self.BASE_URL}/models/{model_id}/embed"
        try:
            response = self.session.get(embed_url)
            if response.status_code != 200:
                return downloaded
            
            html = response.text
            
            # Look for JS bundle URLs
            js_pattern = r'src="(https://static\.sketchfab\.com/[^"]+\.js)"'
            js_matches = re.findall(js_pattern, html)
            
            print(f"  Found {len(js_matches)} JS bundles to search")
            
            # Download and search each JS bundle for WASM content
            for idx, js_url in enumerate(js_matches):
                try:
                    # Only show progress for large searches
                    if idx % 5 == 0 and idx > 0:
                        print(f"    Searching bundle {idx}/{len(js_matches)}...")
                    
                    js_response = self.session.get(js_url, timeout=10)
                    if js_response.status_code != 200:
                        continue
                    
                    content = js_response.text
                    
                    # Check if this bundle contains WASM base64 (starts with AGFzbQEAAAAB)
                    if 'AGFzbQEAAAAB' in content:
                        # Extract WASM base64 - try multiple patterns
                        wasm_patterns = [
                            # Pattern 1: Long continuous string
                            r'["\'](AGFzbQEAAAAB[A-Za-z0-9+/=]{5000,})["\']',
                            # Pattern 2: String that might be split across lines
                            r'["\']([A-Za-z0-9+/=]*AGFzbQEAAAAB[A-Za-z0-9+/=\n\r\s]{5000,}?)["\']',
                            # Pattern 3: Variable assignment
                            r'=\s*["\']([A-Za-z0-9+/=]*AGFzbQEAAAAB[A-Za-z0-9+/=]{5000,})["\']',
                        ]
                        
                        wasm_match = None
                        for pattern in wasm_patterns:
                            wasm_match = re.search(pattern, content, re.DOTALL)
                            if wasm_match:
                                break
                        
                        if wasm_match:
                            try:
                                import base64
                                wasm_b64 = wasm_match.group(1)
                                # Clean up base64 string - remove whitespace and newlines
                                wasm_b64 = re.sub(r'[\s\n\r]', '', wasm_b64)
                                # Also handle escaped characters
                                wasm_b64 = wasm_b64.replace('\\n', '').replace('\\r', '').replace('\\t', '')
                                
                                # Try to decode
                                wasm_bytes = base64.b64decode(wasm_b64)
                                
                                # Verify it's actually WASM (starts with magic number 0x00 0x61 0x73 0x6D = "\0asm")
                                if len(wasm_bytes) > 4 and wasm_bytes[:4] == b'\x00asm':
                                    wasm_path = output_path / 'diter_wasm_blob.wasm'
                                    with open(wasm_path, 'wb') as f:
                                        f.write(wasm_bytes)
                                    downloaded['wasm'] = str(wasm_path)
                                    print(f"  ✓ WASM: {wasm_path.name} ({len(wasm_bytes)} bytes)")
                                    
                                    # Save the JS bundle too for reference
                                    js_filename = js_url.split('/')[-1]
                                    js_path = output_path / f'diter_{js_filename}'
                                    with open(js_path, 'w', encoding='utf-8') as f:
                                        f.write(content)
                                    downloaded['wasm_js'] = str(js_path)
                                    
                                    # Once we find WASM, we can stop searching
                                    break
                            except Exception as e:
                                # Try to get more details about what went wrong
                                pass
                    
                    # Also look for key/cipher patterns
                    if not downloaded.get('key'):
                        # Look for hex keys (40+ hex characters)
                        hex_pattern = r'["\']([0-9a-fA-F]{40,})["\']'
                        hex_matches = re.findall(hex_pattern, content)
                        
                        if hex_matches and 'module.exports' in content or 'diter' in content.lower():
                            # Found potential key material
                            key_path = output_path / 'diter_standalone_deob.js'
                            with open(key_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            downloaded['key'] = str(key_path)
                            print(f"  ✓ Key: {key_path.name}")
                
                except Exception as e:
                    continue
            
            # If we didn't find the files, suggest fallback
            if not downloaded.get('wasm'):
                print(f"  ⚠ Could not find WASM decoder in JS bundles")
        
        except Exception as e:
            print(f"  Warning: Failed to scrape DITER files: {e}")
        
        return downloaded

    def get_encryption_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Extract encryption parameters for a model.

        Returns key material and encryption status.
        """
        config = self.fetch_embed_config(model_id)
        if not config or 'files' not in config:
            return None

        result = {
            'model_id': model_id,
            'files': []
        }

        for file_info in config['files']:
            file_data = {
                'uid': file_info.get('uid'),
                'url': file_info.get('osgjsUrl'),
                'model_size': file_info.get('modelSize'),
                'osgjs_size': file_info.get('osgjsSize'),
                'encrypted': False,
                'key_material': None,
            }

            params = file_info.get('p', [])
            for p in params:
                if p.get('d'):  # d=true means encrypted
                    file_data['encrypted'] = True
                    file_data['version'] = p.get('v')

                    # Decode the key material
                    b64_data = p.get('b', '').replace('\n', '')
                    if b64_data:
                        try:
                            decoded = base64.b64decode(b64_data)
                            file_data['key_material'] = {
                                'raw_length': len(decoded),
                                'potential_key': decoded[:32].hex(),
                                'potential_iv': decoded[32:48].hex(),
                            }
                        except:
                            pass

            result['files'].append(file_data)

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

    # Show encryption info
    print("\n" + "=" * 60)
    print("Encryption Info")
    print("=" * 60)

    enc_info = fetcher.get_encryption_info(result['model_id'])
    if enc_info:
        for f in enc_info['files']:
            print(f"\nFile UID: {f['uid']}")
            print(f"  Encrypted: {f['encrypted']}")
            print(f"  Model size: {f['model_size']} bytes")
            print(f"  OSGJS size: {f['osgjs_size']} bytes")
            if f['key_material']:
                km = f['key_material']
                print(f"  Key material length: {km['raw_length']} bytes")
                print(f"  Potential key (32 bytes): {km['potential_key'][:32]}...")
                print(f"  Potential IV (16 bytes): {km['potential_iv']}")

    # Download files
    print("\n" + "=" * 60)
    print("Downloading Files")
    print("=" * 60)

    downloaded = fetcher.download_model_files(result['model_id'], output_dir='downloads')
    print(f"\nDownloaded: {downloaded}")

    return result


if __name__ == "__main__":
    main()
