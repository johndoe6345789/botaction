# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_demo(args):
    """Launch a demonstration script."""
    msgs = get_messages()['demo']
    demos = get_demos()

    if args.demo_name not in demos:
        print(msgs['error_unknown'].format(name=args.demo_name, available=', '.join(demos.keys())))
        return 1

    demo_path = Path(__file__).parent / demos[args.demo_name]
    if not demo_path.exists():
        print(msgs['error_not_found'].format(path=demo_path))
        return 1

    print(msgs['launching'].format(name=args.demo_name))
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(demo_path)])
        return result.returncode
    except Exception as e:
        print(msgs['error_launch'].format(error=e))
        return 1
