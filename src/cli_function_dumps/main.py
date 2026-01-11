# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def main():
    parser = argparse.ArgumentParser(
        description=_STRINGS['cli_description'],
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    commands = get_commands()

    for command_name, command_data in commands.items():
        parser = subparsers.add_parser(command_name, help=command_data['help'])

        for arg in command_data.get('arguments', []):
            kwargs = {k: v for k, v in arg.items() if k != 'name'}
            parser.add_argument(arg['name'], **kwargs)

        if 'defaults' in command_data:
            parser.set_defaults(**command_data['defaults'])

        parser.set_defaults(func=globals()[command_data['func']])

    # Parse args
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Run the command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print(f"\n{_STRINGS['interrupt_message']}")
        return 1
    except Exception as e:
        print(_STRINGS['unexpected_error'].format(error=e))
        return 1
