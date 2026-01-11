# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

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
