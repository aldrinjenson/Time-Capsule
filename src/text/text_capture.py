# src/text/text_capture.py
"""
Text capture module for the Time Capsule application.

This module provides the TextCapture class, which captures typed text across different
applications, detects context switches based on various events, and saves the captured
text periodically with timestamps and metadata. It integrates with the system information
to retrieve active window details and system metrics.
"""

import os
import time
from pynput import keyboard, mouse
from datetime import datetime
from utils.tokenization_utils import TokenizationUtils
import logging
from colorama import Fore, Style

class TextCapture:
    """Class for capturing and processing typed text."""

    system_info = None

    def __init__(self, system_info, output_dir=None):
        """
        Initialize the TextCapture.

        Args:
            system_info (SystemInfo): System information object.
            output_dir (str, optional): Output directory for saving captured text. Defaults to None.
        """
        if TextCapture.system_info is None and system_info is not None:
            TextCapture.system_info = system_info
        self.output_dir = os.getenv('TEXT_OUTPUT_DIR', '/path/to/text/') if output_dir is None else output_dir
        self.current_minute = None
        self.key_listener = None
        self.mouse_listener = None
        self.current_phrase = ""
        self.tokenization_utils = TokenizationUtils(output_dir)
        self.last_activity_time = time.time()
        self.inactivity_threshold = 5  # Inactivity threshold in seconds
        self.current_window = None
        self.last_click_time = 0
        self.click_threshold = 1  # Click threshold in seconds
        self.logger = logging.getLogger(__name__)

    def start_capture(self):
        """Start the text capture listeners."""
        try:
            self.key_listener = keyboard.Listener(on_press=self.on_key_press)
            self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
            self.key_listener.start()
            self.mouse_listener.start()
            self.logger.info(f"{Fore.GREEN}▶️ Text Capture Service: Started{Style.RESET_ALL}")
            self.logger.debug(f"{Fore.BLUE}⌨️ Text Capture listeners started{Style.RESET_ALL}")
        except Exception as e:
            self.logger.exception(f"{Fore.RED}❌ Error starting text capture: {str(e)}{Style.RESET_ALL}")

    def on_key_press(self, key):
        """Handle key press events and capture typed text."""
        current_minute = datetime.now().strftime("%Y-%m-%d_%H%M")
        self.logger.debug(f"{Fore.MAGENTA}⌨️ Key pressed: {key}{Style.RESET_ALL}")

        if self.current_minute is None:
            self.current_minute = current_minute
        elif self.current_minute != current_minute:
            self.save_current_phrase()
            self.current_minute = current_minute

        try:
            char = key.char
            self.current_phrase += char
            self.last_activity_time = time.time()

            if key in [keyboard.Key.alt_l, keyboard.Key.cmd, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                self.save_current_phrase(context_switch=True)
            elif key == keyboard.Key.enter:
                self.current_phrase += "\n"
                self.save_current_phrase(context_switch=True)

        except AttributeError:
            if key == keyboard.Key.space:
                self.current_phrase += " "
            elif key == keyboard.Key.backspace:
                self.current_phrase = self.current_phrase[:-1]
            elif key == keyboard.Key.tab:
                self.current_phrase += "\t"

        if time.time() - self.last_activity_time >= self.inactivity_threshold:
            self.save_current_phrase(context_switch=True)
            self.last_activity_time = time.time()

    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events and detect context switches."""
        if pressed:
            current_time = time.time()
            if current_time - self.last_click_time >= self.click_threshold:
                self.save_current_phrase(context_switch=True)
                self.last_click_time = current_time

    def save_current_phrase(self, context_switch=False):
        """Save the current phrase with metadata and tokenization."""
        if self.current_phrase.strip():
            timestamp = datetime.now().isoformat()

            os_info = TextCapture.system_info.get_info("os")
            machine_info = TextCapture.system_info.get_info("machine")
            architecture_info = TextCapture.system_info.get_info("architecture")
            cpu_info = TextCapture.system_info.get_info("cpu")
            memory_info = TextCapture.system_info.get_info("memory")
            active_window = TextCapture.system_info.get_active_window()

            metadata = {
                "os": os_info,
                "machine": machine_info,
                "architecture": architecture_info,
                "cpu": cpu_info,
                "memory": memory_info,
                "window": active_window
            }

            try:
                self.tokenization_utils.process_text_capture(self.current_phrase, timestamp, metadata, context_switch)
                self.current_phrase = ""
                self.logger.debug(f"{Fore.GREEN}✅ Saved current phrase: {self.current_phrase}{Style.RESET_ALL}")
            except Exception as e:
                self.logger.exception(f"{Fore.RED}❌ Error saving current phrase: {str(e)}{Style.RESET_ALL}")

    def stop_capture(self):
        """Stop the text capture listeners."""
        if self.key_listener:
            self.key_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        self.logger.info(f"{Fore.YELLOW}🛑 Text Capture Service: Stopped{Style.RESET_ALL}")