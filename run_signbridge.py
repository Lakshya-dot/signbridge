"""
SignBridge - Indian Sign Language Recognition & Translation Launcher
Run this script to start the interactive live webcam dashboard with audio speech output!
"""

import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SignBridge.live_dashboard import launch_dashboard

if __name__ == "__main__":
    launch_dashboard()
