import time
import logging
import signal
from utils.system_info import SystemInfo
from src.screen_recording.screen_recorder import ScreenRecorder
from src.audio_recording.audio_recorder import AudioRecorder
from src.text.text_capture import TextCapture

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("time_capsule.log"),
            logging.StreamHandler()
        ]
    )

def handle_signal(signum, frame):
    logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
    screen_recorder.stop_recording()
    audio_recorder.stop_recording()
    text_capture.stop_capture()

    logger.info("Graceful shutdown complete.")

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    system_info = SystemInfo()

    logger.info("Recording Process: Initializing Services...")
    screen_recorder = ScreenRecorder(system_info=system_info)
    text_capture = TextCapture(system_info=system_info)
    audio_recorder = AudioRecorder(system_info=system_info)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info("Recording Process: Starting Individual Services...")

    screen_recorder.start_recording()
    audio_recorder.start_recording()
    text_capture.start_capture()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        handle_signal(signal.SIGINT, None)
