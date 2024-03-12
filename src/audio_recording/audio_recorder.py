import pyaudio
import wave
import os
import numpy as np
import threading
import time
import uuid

# OUTPUT AUDIO FUNCTIONALITY IS CURRENTLY ON HOLD DUE TO LIMITATIONS WITH MACOS
# WILL BE IMPLEMENTED LATER AS IT REQUIRES AN INSTALLATION OF THIRD PARTY SOFTWARE

class AudioRecorder:
    system_info = None

    def __init__(self, system_info, output_dir="/Users/sethrose/Documents/Development/Repositories/time-capsule/recordings/audio", sample_rate=16000, channels=1, threshold=0.1, silence_duration=1.0):
        if AudioRecorder.system_info is None and system_info is not None:
            AudioRecorder.system_info = system_info
        self.output_dir = output_dir
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_format = pyaudio.paInt16
        self.frames_per_buffer = 1024
        self.threshold = threshold
        self.silence_duration = silence_duration

        self.p = pyaudio.PyAudio()
        for i in range(self.p.get_device_count()):
            dev_info = self.p.get_device_info_by_index(i)
            print(f"Device {i}: {dev_info['name']} - Input Channels: {dev_info['maxInputChannels']} - Output Channels: {dev_info['maxOutputChannels']}")

        self.input_device_index = self.p.get_default_input_device_info()["index"]

        self.recording = False
        self.input_frames = []

    def start_recording(self):
        self.recording = True
        self.input_frames = []
        
        input_thread = threading.Thread(target=self._record_input)
        
        input_thread.start()
        
        input_thread.join()
        
        self._save_recordings()

    def stop_recording(self):
        self.recording = False

    def _record_input(self):
        stream = self.p.open(format=self.audio_format,
                             channels=self.channels,
                             rate=self.sample_rate,
                             input=True,
                             frames_per_buffer=self.frames_per_buffer,
                             input_device_index=self.input_device_index)

        while self.recording:
            data = stream.read(self.frames_per_buffer)
            self.input_frames.append(data)

        stream.stop_stream()
        stream.close()

    def _save_recordings(self):
        input_audio = np.frombuffer(b''.join(self.input_frames), dtype=np.int16)

        # Apply voice activity detection
        input_audio_vad = self._apply_vad(input_audio)

        # Compress and save the recordings
        timestamp = int(time.time())
        input_filename = f"input_{timestamp}.wav"

        input_filepath = os.path.join(self.output_dir, input_filename)

        self._compress_audio(input_audio_vad, input_filepath)

    def _apply_vad(self, audio):
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
        # Save the audio as a WAV file
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.audio_format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio.tobytes())

    def __del__(self):
        self.p.terminate()