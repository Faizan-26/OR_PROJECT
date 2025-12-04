"""
PP Chemicals - Operations Research Problem Solver

A desktop application for solving:
- Linear Programming (Simplex with Sensitivity Analysis)
- Assignment Problems (Hungarian Algorithm)
- Transportation Problems (VAM + MODI)

Author: PP Chemicals OR Team
Version: 1.0.0
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import App


def main():
    """Main entry point for the application"""
    print("=" * 50)
    print("PP CHEMICALS - OR Problem Solver")
    print("=" * 50)
    print("\nStarting application...")
    
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install customtkinter numpy scipy pandas openpyxl")
        sys.exit(1)


if __name__ == "__main__":
    main()
