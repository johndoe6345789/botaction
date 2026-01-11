# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

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
