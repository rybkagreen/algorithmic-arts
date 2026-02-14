#!/usr/bin/env python3
"""
ALGORITHMIC ARTS DEV HUB — Interactive Developer Menu (2026)
Unified CLI for managing services, environments, tests, and infrastructure.
"""

import sys
from pathlib import Path

# Add dev/ to sys.path for plugin imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from dev import menu
except ImportError as e:
    print(f"❌ Error loading dev menu plugins: {e}")
    print("Please run: mkdir -p platform/scripts/dev && touch platform/scripts/dev/__init__.py")
    sys.exit(1)

def main():
    try:
        menu.show_main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()