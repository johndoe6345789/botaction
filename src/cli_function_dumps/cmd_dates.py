# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

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
