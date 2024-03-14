# src/audio_recording/audio_recorder.py
"""
Audio recording module for the Time Capsule application.

This module provides the AudioRecorder class, which captures audio from the default
microphone, applies voice activity detection (VAD) to remove silent segments, and
saves the compressed audio files with timestamps. It integrates with the system
information to retrieve audio device details.
"""

import pyaudio
import wave
import os
import numpy as np
import threading
import time
import uuid
import logging
from colorama import Fore, Style

class AudioRecorder:
    """Class for audio recording and processing."""

    system_info = None

    def __init__(self, system_info, output_dir=None, sample_rate=None, channels=None, threshold=None, silence_duration=None):
        """
        Initialize the AudioRecorder.

        Args:
            system_info (SystemInfo): System information object.
            output_dir (str, optional): Output directory for saving audio files. Defaults to None.
            sample_rate (int, optional): Sample rate for audio recording. Defaults to None.
            channels (int, optional): Number of audio channels. Defaults to None.
            threshold (float, optional): Threshold for voice activity detection. Defaults to None.
            silence_duration (float, optional): Duration of silence for voice activity detection. Defaults to None.
        """
        if AudioRecorder.system_info is None and system_info is not None:
            AudioRecorder.system_info = system_info
        self.output_dir = os.getenv('AUDIO_OUTPUT_DIR', '/path/to/audio/') if output_dir is None else output_dir
        self.sample_rate = int(os.getenv('AUDIO_SAMPLE_RATE', 16000)) if sample_rate is None else sample_rate
        self.channels = int(os.getenv('AUDIO_CHANNELS', 1)) if channels is None else channels
        self.threshold = float(os.getenv('AUDIO_THRESHOLD', 0.1)) if threshold is None else threshold
        self.silence_duration = float(os.getenv('AUDIO_SILENCE_DURATION', 1.0)) if silence_duration is None else silence_duration
        self.audio_format = pyaudio.paInt16
        self.frames_per_buffer = 1024

        self.p = pyaudio.PyAudio()
        self.logger = logging.getLogger(__name__)

        self.logger.debug(f"{Fore.BLUE}🔍 Initializing audio devices...{Style.RESET_ALL}")
        for i in range(self.p.get_device_count()):
            dev_info = self.p.get_device_info_by_index(i)
            self.logger.debug(f"{Fore.CYAN}🎧 Device {i}: {dev_info['name']} - Input Channels: {dev_info['maxInputChannels']} - Output Channels: {dev_info['maxOutputChannels']}{Style.RESET_ALL}")

        self.input_device_index = self.p.get_default_input_device_info()["index"]

        self.recording = False
        self.input_frames = []

    def start_recording(self):
        """Start the audio recording thread."""
        self.recording = True
        self.input_frames = []

        input_thread = threading.Thread(target=self._record_input)

        input_thread.start()

        input_thread.join()

        self._save_recordings()
        self.logger.info(f"{Fore.GREEN}▶️ Audio Recording Service: Started{Style.RESET_ALL}")
        self.logger.debug(f"{Fore.BLUE}🎙️ Audio Recording thread started{Style.RESET_ALL}")

    def _record_input(self):
        """Record audio from the default input device."""
        stream = self.p.open(format=self.audio_format,
                             channels=self.channels,
                             rate=self.sample_rate,
                             input=True,
                             frames_per_buffer=self.frames_per_buffer,
                             input_device_index=self.input_device_index)
        self.logger.debug(f"{Fore.GREEN}🎙️ Audio stream opened{Style.RESET_ALL}")

        while self.recording:
            data = stream.read(self.frames_per_buffer)
            self.input_frames.append(data)

        stream.stop_stream()
        stream.close()
        self.logger.debug(f"{Fore.YELLOW}🛑 Audio stream closed{Style.RESET_ALL}")

    def _save_recordings(self):
        """Save the recorded audio with voice activity detection and compression."""
        input_audio = np.frombuffer(b''.join(self.input_frames), dtype=np.int16)
        self.logger.debug(f"{Fore.BLUE}💾 Saving audio recording of length {len(input_audio)} frames{Style.RESET_ALL}")

        input_audio_vad = self._apply_vad(input_audio)
        self.logger.debug(f"{Fore.MAGENTA}🎙️ Applying VAD to audio recording, new length {len(input_audio_vad)} frames{Style.RESET_ALL}")

        timestamp = int(time.time())
        input_filename = f"input_{timestamp}.wav"
        input_filepath = os.path.join(self.output_dir, input_filename)

        self._compress_audio(input_audio_vad, input_filepath)
        self.logger.debug(f"{Fore.GREEN}🗜️ Compressed audio saved to {input_filepath}{Style.RESET_ALL}")

    def _apply_vad(self, audio):
        """Apply voice activity detection to remove silent segments."""
        # Apply voice activity detection to remove silent segments
        audio_abs = np.abs(audio)
        audio_max = np.max(audio_abs)
        audio_norm = audio_abs / audio_max

        threshold = self.threshold
        silence_frames = int(self.silence_duration * self.sample_rate / self.frames_per_buffer)

        vad_frames = []
        silent_count = 0

        for frame in audio_norm:
            if frame > threshold:
                vad_frames.extend(audio[len(vad_frames):len(vad_frames) + self.frames_per_buffer])
                silent_count = 0
            else:
                silent_count += 1
                if silent_count <= silence_frames:
                    vad_frames.extend(audio[len(vad_frames):len(vad_frames) + self.frames_per_buffer])

        return np.array(vad_frames, dtype=np.int16)

    def _compress_audio(self, audio, filepath):
        """Compress the audio using FFmpeg."""
        # Save the audio as a WAV file
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.audio_format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio.tobytes())

        # Compress the WAV file using FFmpeg
        compressed_filepath = filepath.replace(".wav", ".mp3")
        command = f"ffmpeg -i {filepath} -b:a 192k {compressed_filepath}"
        os.system(command)

        # Remove the original WAV file
        os.remove(filepath)

    def __del__(self):
        """Clean up the PyAudio instance."""
        self.p.terminate()