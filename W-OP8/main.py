# W-OP8/main.py
import os
import sys
import pyfiglet

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from src.tui.interface import WOP8Interface

def main():
    """Main entry point for W-OP8 application"""
    # Clear screen
    os.system('clear' if os.name == 'posix' else 'cls')

    
    # Launch TUI
    try:
        interface = WOP8Interface()
        interface.run()
    except KeyboardInterrupt:
        print("\n\nExiting W-OP8...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()