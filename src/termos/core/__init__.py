from pathlib import Path
from typing import Optional
import os
from osascript import osascript
from termos.config import DATA_DIR
from termos import __name__

pid_file = DATA_DIR / f"{__name__}.pid"

def check_pid():
    try:
        assert pid_file.exists()
        pid = pid_file.read_text()
        assert pid
        os.kill(int(pid), 0)
        return True
    except (AssertionError, ValueError, OSError):
        return False


def show_alert(msg: str, title: Optional[str] = None):
    if not title:
        title = __name__
    icon_path = Path(__file__).parent / "icon.png"
    script = f'display dialog "{msg}" '
    f'with icon posix file "{icon_path.as_posix()}" '
    'buttons {"OK"} default button 1 '
    osascript.osascript(script)
