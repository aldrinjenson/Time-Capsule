# utils/system_info.py
"""
System information module for the Time Capsule application.

This module provides the SystemInfo class, which retrieves various system information
such as operating system details, processor information, memory usage, and active window
details. It also provides methods to identify excluded applications and detect private
browser windows based on platform-specific mechanisms.
"""

import platform
import psutil
import subprocess

class SystemInfo:
    """Class for retrieving system information."""

    def __init__(self):
        """Initialize the SystemInfo with system details."""
        self.os_name = platform.system()
        self.os_release = platform.release()
        self.os_version = platform.version()
        self.machine = platform.machine()
        self.processor = platform.processor()
        self.architecture = platform.architecture()[0]
        self.cpu_count = psutil.cpu_count(logical=True)
        self.memory = psutil.virtual_memory().total  # In bytes

    def get_excluded_apps(self):
        """Get the list of excluded applications based on the operating system."""
        excluded_apps = []
        if self.os_name == "Darwin":  # macOS
            try:
                # Use AppleScript to get the list of excluded apps
                script = 'tell application "System Events" to get the name of every process whose background only is false'
                output = subprocess.check_output(["osascript", "-e", script]).decode("utf-8").strip()
                excluded_apps = output.split(", ")
            except subprocess.CalledProcessError:
                pass
        elif self.os_name == "Windows":
            try:
                # Use PowerShell to get the list of excluded apps
                command = 'Get-Process | Where-Object {$_.MainWindowTitle -ne ""} | Select-Object -ExpandProperty MainWindowTitle'
                output = subprocess.check_output(["powershell", "-Command", command]).decode("utf-8").strip()
                excluded_apps = output.split("\n")
            except subprocess.CalledProcessError:
                pass
        elif self.os_name == "Linux":
            try:
                # Use xdotool to get the list of excluded apps
                output = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--name", ""]).decode("utf-8").strip()
                excluded_apps = output.split("\n")
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        return excluded_apps
    
    def is_private_browser_window(self, window_title):
        """Check if the given window title indicates a private browser window."""
        private_keywords = ["Private Browsing", "Incognito", "InPrivate"]
        return any(keyword in window_title for keyword in private_keywords)

    def get_info(self, info_type):
        """Get the specified system information."""
        if info_type == "os":
            return f"{self.os_name} {self.os_release} ({self.os_version})"
        elif info_type == "machine":
            return f"{self.machine} - {self.processor}"
        elif info_type == "architecture":
            return f"Architecture: {self.architecture}"
        elif info_type == "cpu":
            return f"CPU Cores: {self.cpu_count}"
        elif info_type == "memory":
            # Convert bytes to GB for readability
            memory_gb = round(self.memory / (1024**3), 2)
            return f"Total System Memory: {memory_gb} GB"
        else:
            return "Invalid info type specified."

    def get_active_window(self):
        """Get the active window title based on the operating system."""
        if self.os_name == "Windows":
            import win32gui
            window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(window)
            return title
        elif self.os_name == "Darwin":  # macOS
            script = 'tell application "System Events" to get the name of the first process whose frontmost is true'
            output = subprocess.check_output(["osascript", "-e", script]).decode("utf-8").strip()
            return output
        else:  # Assume Unix-like systems (Linux, BSD, etc.)
            try:
                output = subprocess.check_output(["xdotool", "getwindowfocus", "getwindowname"]).decode("utf-8").strip()
                return output
            except FileNotFoundError:
                return "Unknown"