# src/screen_recording/screen_recorder.py
"""
Screen recording module for the Time Capsule application.

This module provides the ScreenRecorder class, which captures screenshots at a specified
interval, performs OCR on the captured screenshots, and saves the extracted text along
with timestamps and metadata. It also handles preprocessing of the screenshots and
cleaning of the extracted text.
"""

import mss
import mss.tools
import time
from PIL import Image
from datetime import datetime
import os
import threading
import pytesseract
from utils.tokenization_utils import TokenizationUtils
import logging
import signal
from queue import Queue, Empty
import cv2
import numpy as np
from colorama import Fore, Style

class ScreenRecorder:
    """Class for screen recording and OCR processing."""

    system_info = None

    def __init__(self, system_info, fps=None, output_dir=None):
        """
        Initialize the ScreenRecorder.

        Args:
            system_info (SystemInfo): System information object.
            fps (float, optional): Frames per second for screen capture. Defaults to None.
            output_dir (str, optional): Output directory for saving screenshots. Defaults to None.
        """
        if ScreenRecorder.system_info is None and system_info is not None:
            ScreenRecorder.system_info = system_info

        self.fps = float(os.getenv('SCREENSHOT_FPS', 0.5)) if fps is None else fps
        self.save_dir = os.getenv('SCREENSHOTS_OUTPUT_DIR', '/path/to/screenshots/') if output_dir is None else output_dir
        self.running = False
        self.tokenization_utils = TokenizationUtils(output_dir)
        self.logger = logging.getLogger(__name__)
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        self.screenshot_queue = Queue()
        self.batch_size = 10

    def start_recording(self):
        """Start the screen recording and OCR processing threads."""
        if not self.running:
            self.running = True
            self.recorder_thread = threading.Thread(target=self._record)
            self.ocr_thread = threading.Thread(target=self.process_screenshots)
            self.recorder_thread.start()
            self.ocr_thread.start()
            self.logger.info(f"{Fore.GREEN}▶️ Screen Recording Service: Started{Style.RESET_ALL}")
            self.logger.debug(f"{Fore.BLUE}🎥 Screen Recording threads started{Style.RESET_ALL}")

    def _record(self):
        """Continuously capture screenshots at the specified interval."""
        with mss.mss() as sct:
            monitors = sct.monitors[1:]
            self.logger.debug(f"{Fore.CYAN}🖥️ Number of monitors detected: {len(monitors)}{Style.RESET_ALL}")

            while self.running:
                self.capture_screenshots(monitors)
                time.sleep(1 / self.fps)

    def capture_screenshots(self, monitors):
        """Capture screenshots from each monitor and add them to the processing queue."""
        with mss.mss() as sct:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

            excluded_apps = ScreenRecorder.system_info.get_excluded_apps()
            self.logger.debug(f"{Fore.YELLOW}⚠️ Excluded apps: {excluded_apps}{Style.RESET_ALL}")

            for i, monitor in enumerate(monitors, start=1):
                screenshot = sct.grab(monitor)

                current_window = ScreenRecorder.system_info.get_active_window()
                self.logger.debug(f"{Fore.MAGENTA}🖥️ Current window: {current_window}{Style.RESET_ALL}")

                if current_window in excluded_apps or ScreenRecorder.system_info.is_private_browser_window(current_window):
                    self.logger.debug(f"{Fore.YELLOW}⚠️ Skipping screenshot of excluded app or private browser window{Style.RESET_ALL}")
                    continue

                self.screenshot_queue.put((screenshot, timestamp, i))

    def process_screenshots(self):
        """Process the captured screenshots in batches and perform OCR."""
        while self.running:
            try:
                screenshots = []
                while len(screenshots) < self.batch_size:
                    screenshot = self.screenshot_queue.get(timeout=1)
                    screenshots.append(screenshot)

                self.logger.debug(f"{Fore.BLUE}🖼️ Processing {len(screenshots)} screenshots{Style.RESET_ALL}")
                images = []
                for screenshot, timestamp, monitor in screenshots:
                    image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    preprocessed_image = self.preprocess_image(image)
                    images.append((preprocessed_image, timestamp, monitor))

                for image, timestamp, monitor in images:
                    text = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                    words = text['text']
                    normalized_text = ' '.join(word for word in words if word.strip())
                    self.logger.debug(f"{Fore.GREEN}📝 OCR output: {normalized_text}{Style.RESET_ALL}")

                    metadata = {"timestamp": timestamp, "monitor": monitor}
                    cleaned_text = self.clean_text(normalized_text)
                    self.tokenization_utils.process_ocr_text(cleaned_text, timestamp, metadata)

            except Empty:
                continue

            except Exception as e:
                self.logger.exception(f"{Fore.RED}❌ Error processing screenshots: {str(e)}{Style.RESET_ALL}")

    def preprocess_image(self, image):
        """Preprocess the image to enhance OCR accuracy."""
        # Convert the image to grayscale
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

        # Apply adaptive thresholding to improve contrast
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Remove noise and smooth the image
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        # Convert the OpenCV image back to PIL format
        preprocessed_image = Image.fromarray(opening)

        return preprocessed_image

    def clean_text(self, text):
        """Clean the extracted text by removing unwanted characters and normalizing."""
        cleaned_text = ''.join(c for c in text if c.isalnum() or c.isspace()).lower()
        return cleaned_text

    def handle_signal(self, signum, frame):
        """Handle signal for graceful shutdown."""
        self.logger.info(f"{Fore.YELLOW}⚠️ Received signal {signum}. Initiating graceful shutdown...{Style.RESET_ALL}")
        self.stop_recording()
        self.logger.info(f"{Fore.GREEN}✅ Graceful shutdown complete.{Style.RESET_ALL}")