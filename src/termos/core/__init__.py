import os
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
