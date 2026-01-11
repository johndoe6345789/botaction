# Auto-generated extract of cli.py
# See cli.py for shared context and imports
from src.cli_context import *

def cmd_gui(args):
    """Launch the graphical user interface."""
    msgs = get_messages()['gui']
    gui_file = get_gui_file()
    gui_path = Path(__file__).parent / gui_file
    if not gui_path.exists():
        print(msgs['error_not_found'].format(path=gui_path))
        return 1

    print(msgs['launching'])
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(gui_path)])
        return result.returncode
    except Exception as e:
        print(msgs['error_launch'].format(error=e))
        return 1
