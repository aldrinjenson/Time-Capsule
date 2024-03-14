# main.py
"""
Main entry point of the Time Capsule application.

This module initializes and starts the various services of the Time Capsule application,
including screen recording, audio recording, and text capture. It sets up logging,
handles graceful shutdown, and manages the overall execution of the application.
"""

import os
import time
import logging
import signal
from dotenv import load_dotenv
from utils.system_info import SystemInfo
from src.screen_recording.screen_recorder import ScreenRecorder
from src.audio_recording.audio_recorder import AudioRecorder
from src.text.text_capture import TextCapture
from colorama import Fore, Style

# Load environment variables from .env file
load_dotenv()

def setup_logging():
    """Set up logging configuration based on environment variables."""
    log_levels = [
        ('CRITICAL', logging.CRITICAL),
        ('ERROR', logging.ERROR),
        ('WARNING', logging.WARNING),
        ('INFO', logging.INFO),
        ('DEBUG', logging.DEBUG)
    ]

    console_level = logging.CRITICAL
    for level_name, level_value in log_levels:
        if os.environ.get(f'LOG_LEVEL_{level_name}', 'False').lower() == 'true':
            console_level = level_value
            break

    # Create a file handler for logging to debug.log
    file_handler = logging.FileHandler("debug.log")
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler for displaying log messages based on the log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    # Create a formatter for log messages
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Configure the root logger with both handlers
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().setLevel(logging.DEBUG)

def handle_signal(signum, frame):
    """Signal handler for graceful shutdown."""
    logger.info(f"{Fore.YELLOW}⚠️ Received signal {signum}. Initiating graceful shutdown...{Style.RESET_ALL}")
    if 'screen_recorder' in globals():
        screen_recorder.stop_recording()
    if 'audio_recorder' in globals():
        audio_recorder.stop_recording()
    if 'text_capture' in globals():
        text_capture.stop_capture()
    logger.info(f"{Fore.GREEN}✅ Graceful shutdown complete.{Style.RESET_ALL}")

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    system_info = SystemInfo()
    logger.debug(f"{Fore.CYAN}💻 System Information: {system_info.get_info('os')}, {system_info.get_info('machine')}{Style.RESET_ALL}")

    logger.info(f"{Fore.GREEN}🚀 Recording Process: Initializing Services...{Style.RESET_ALL}")

    # Initialize and start the recorders based on the configuration
    if os.getenv('ENABLE_AUDIO_RECORDING', 'True').lower() == 'true':
        logger.debug(f"{Fore.BLUE}🎙️ Initializing AudioRecorder{Style.RESET_ALL}")
        audio_recorder = AudioRecorder(
            system_info=system_info,
            output_dir=os.getenv('AUDIO_OUTPUT_DIR', '/path/to/audio/'),
            sample_rate=int(os.getenv('AUDIO_SAMPLE_RATE', 16000)),
            channels=int(os.getenv('AUDIO_CHANNELS', 1)),
            threshold=float(os.getenv('AUDIO_THRESHOLD', 0.1)),
            silence_duration=float(os.getenv('AUDIO_SILENCE_DURATION', 1.0))
        )
        logger.debug(f"{Fore.GREEN}▶️ Starting AudioRecorder{Style.RESET_ALL}")
        audio_recorder.start_recording()

    if os.getenv('ENABLE_VIDEO_RECORDING', 'True').lower() == 'true':
        logger.debug(f"{Fore.BLUE}🎥 Initializing ScreenRecorder{Style.RESET_ALL}")
        screen_recorder = ScreenRecorder(
            system_info=system_info,
            fps=float(os.getenv('SCREENSHOT_FPS', 0.5)),
            output_dir=os.getenv('SCREENSHOTS_OUTPUT_DIR', '/path/to/screenshots/')
        )
        logger.debug(f"{Fore.GREEN}▶️ Starting ScreenRecorder{Style.RESET_ALL}")
        screen_recorder.start_recording()

    if os.getenv('ENABLE_TEXT_RECORDING', 'True').lower() == 'true':
        logger.debug(f"{Fore.BLUE}⌨️ Initializing TextCapture{Style.RESET_ALL}")
        text_capture = TextCapture(
            system_info=system_info,
            output_dir=os.getenv('TEXT_OUTPUT_DIR', '/path/to/text/')
        )
        logger.debug(f"{Fore.GREEN}▶️ Starting TextCapture{Style.RESET_ALL}")
        text_capture.start_capture()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info(f"{Fore.GREEN}✅ Recording Process: Services started successfully{Style.RESET_ALL}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_signal(signal.SIGINT, None)