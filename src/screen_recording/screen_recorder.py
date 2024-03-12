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

class ScreenRecorder:
    system_info = None

    def __init__(self, system_info, fps=0.5, output_dir="/Users/sethrose/Documents/Development/Repositories/time-capsule/recordings/text/"):
        if ScreenRecorder.system_info is None and system_info is not None:
            ScreenRecorder.system_info = system_info

        self.fps = fps
        self.running = False
        self.save_dir = "/Users/sethrose/Documents/Development/Repositories/time-capsule/recordings/screenshots/"
        self.tokenization_utils = TokenizationUtils(output_dir)
        self.logger = logging.getLogger(__name__)
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        self.screenshot_queue = Queue()
        self.batch_size = 10

    def start_recording(self):
        if not self.running:
            self.running = True
            self.recorder_thread = threading.Thread(target=self._record)
            self.ocr_thread = threading.Thread(target=self._process_screenshots)
            self.recorder_thread.start()
            self.ocr_thread.start()
            self.logger.info("Screen Recording Service: Started")

    def _record(self):
        with mss.mss() as sct:
            monitors = sct.monitors[1:]

            while self.running:
                self.capture_screenshots(monitors)
                time.sleep(1 / self.fps)

    def stop_recording(self):
        self.running = False
        self.recorder_thread.join()
        self.ocr_thread.join()
        self.logger.info("Screen Recording Service: Stopped")

    def capture_screenshots(self, monitors):
        with mss.mss() as sct:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

            for i, monitor in enumerate(monitors, start=1):
                screenshot = sct.grab(monitor)
                filename = f"screenshot_{timestamp}_monitor_{i}.png"
                filepath = os.path.join(self.save_dir, filename)
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)

                self.screenshot_queue.put(filepath)

    def _process_screenshots(self):
        screenshots = []

        while self.running or not self.screenshot_queue.empty():
            try:
                screenshot = self.screenshot_queue.get(timeout=1)
                screenshots.append(screenshot)

                if len(screenshots) >= self.batch_size:
                    self.process_screenshots(screenshots)
                    screenshots = []

            except Empty:
                continue

        if screenshots:
            self.process_screenshots(screenshots)

    def process_screenshots(self, screenshots):
        try:
            self.logger.debug("Starting screenshot preprocessing...")
            images = []
            for screenshot in screenshots:
                image = Image.open(screenshot)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                preprocessed_image = self.preprocess_image(image)
                images.append(preprocessed_image)
            self.logger.debug("Screenshot preprocessing completed.")

            for screenshot, image in zip(screenshots, images):
                text = pytesseract.image_to_string(image)
                self.logger.debug(f"OCR output: {text}")  # Verify that OCR output is not empty

                metadata = self.extract_metadata(screenshot)
                self.tokenization_utils.process_ocr_text(text, metadata["timestamp"], metadata)
                self.delete_screenshot(screenshot)

        except Exception as e:
            self.logger.error(f"Error processing screenshots: {str(e)}")

    def preprocess_image(self, image):
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

    def extract_metadata(self, image_path: str) -> dict:
        # Extract relevant metadata from the image filename or path
        # Modify this method based on your filename or path convention
        filename = os.path.basename(image_path)
        timestamp = "_".join(filename.split("_")[1:3])  # Extract timestamp and monitor number
        monitor = filename.split("_")[-1].split(".")[0]  # Extract monitor number
        return {"timestamp": timestamp, "monitor": monitor}

    def delete_screenshot(self, image_path: str):
        try:
            os.remove(image_path)
        except Exception as e:
            self.logger.error(f"Error deleting screenshot {image_path}: {str(e)}")

    def handle_signal(self, signum, frame):
        self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.stop_recording()
        self.logger.info("Graceful shutdown complete.")