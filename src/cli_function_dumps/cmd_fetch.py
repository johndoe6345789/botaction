# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

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
