"""
SignBridge Interactive Web AI Studio Launcher
Starts the Flask server, launches camera thread, and opens the interactive dashboard in your web browser!
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SignBridge.web_dashboard import launch_web_studio

if __name__ == "__main__":
    launch_web_studio(port=5000)
