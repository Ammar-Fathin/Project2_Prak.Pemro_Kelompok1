import sys

from App.menu_app import MenuApp
from App import tampilan


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        MenuApp().jalankan()
    except (KeyboardInterrupt, EOFError):
        print()
        tampilan.info("Program dihentikan.")


if __name__ == "__main__":
    main()