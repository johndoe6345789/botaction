#!/usr/bin/env python3
"""
Sketchfab Model Tools CLI

A command-line interface for working with Sketchfab 3D models.
Supports fetching, decrypting, inspecting, exporting models, and various utilities.

Based on analysis of Sketchfab's JavaScript architecture including:
- Viewer configuration and embed options
- API endpoints and data structures
- AI tools integration (text-to-3D, image-to-3D)
- Material and rendering options
- URL utilities and query parsing
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from cli_data import get_commands
from src.cli_context import (
    CLI_DESCRIPTION,
    INTERRUPT_MESSAGE,
    UNEXPECTED_ERROR,
)


TYPE_MAP = {
    'int': int,
    'float': float,
    'str': str,
}


def main():
    parser = argparse.ArgumentParser(
        description=CLI_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    commands = get_commands()

    for command_name, command_data in commands.items():
        command_parser = subparsers.add_parser(command_name, help=command_data['help'])

        for arg in command_data.get('arguments', []):
            names = [arg['name']]
            short_opt = arg.get('short')
            if short_opt:
                names.insert(0, short_opt)

            kwargs = {
                k: v for k, v in arg.items()
                if k not in {'name', 'short', 'choices_from'}
            }

            type_hint = kwargs.get('type')
            if isinstance(type_hint, str):
                kwargs['type'] = TYPE_MAP.get(type_hint, type_hint)

            choices_key = arg.get('choices_from')
            if choices_key:
                choices_source = globals().get(choices_key)
                if isinstance(choices_source, dict):
                    kwargs['choices'] = list(choices_source.keys())
                elif isinstance(choices_source, (list, tuple)):
                    kwargs['choices'] = choices_source

            command_parser.add_argument(*names, **kwargs)

        if 'defaults' in command_data:
            command_parser.set_defaults(**command_data['defaults'])

        command_parser.set_defaults(func=globals()[command_data['func']])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print(f"\n{INTERRUPT_MESSAGE}")
        return 1
    except Exception as e:
        print(UNEXPECTED_ERROR.format(error=e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
