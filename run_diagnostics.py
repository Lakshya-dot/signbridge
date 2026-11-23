"""
SignBridge System Diagnostic Launcher
Checks camera, models, audio, and presentation visuals.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SignBridge.check_setup import run_diagnostics

if __name__ == "__main__":
    run_diagnostics()
