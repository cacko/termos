import sys
from termos.cli import main as cli
from termos import start

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(cli())
    else:
        start()