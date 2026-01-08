from sys import path
from pathlib import Path

# Adjust the path to include the src directory from the cloned repo
path.insert(0, str(Path(__file__).parent / "src"))

from quickbooks_desktop import QuickbooksDesktop

if __name__ == '__main__':
    qb = QuickbooksDesktop()
    qb.open_connection()
    qb.begin_session()
    print("Connected to QB!")
    qb.close_qb()
