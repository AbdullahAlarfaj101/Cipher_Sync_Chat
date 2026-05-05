import pyaudio
import wave
import io
import threading


class SecureAudioHandler:
    def __init__(self):
        # Standard audio stream configuration
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1  # Mono audio to minimize payload size
        self.RATE = 44100  # 44.1 kHz sample rate (CD Quality)

        self.p = pyaudio.PyAudio()
        self.is_recording = False
        self.frames = []
        self._record_thread = None

    # ==========================================
    # 1. In-Memory Recording System
    # ==========================================

    def start_recording(self):
        """Initiates audio recording in a dedicated background thread."""
        if self.is_recording:
            return

        self.is_recording = True
        self.frames = []
        self._record_thread = threading.Thread(target=self._record_process)
        self._record_thread.start()
        print("System: Secure audio recording started...")

    def _record_process(self):
        """Background process to capture the microphone audio stream."""
        stream = self.p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             frames_per_buffer=self.CHUNK)

        while self.is_recording:
            try:
                # exception_on_overflow=False prevents stream dropping on slower hardware
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"System Error: Audio stream interrupted: {e}")
                break

        stream.stop_stream()
        stream.close()

    def stop_recording_and_get_bytes(self) -> bytes:
        """
        Terminates recording and compiles captured frames into a fully structured 
        WAV file entirely within memory (RAM), returning bytes for encryption.
        """
        self.is_recording = False
        if self._record_thread:
            self._record_thread.join()

        print("System: Recording stopped. Processing in-memory audio buffer...")

        # Initialize an in-memory byte buffer
        audio_buffer = io.BytesIO()

        # Construct WAV file structure within the memory buffer
        wf = wave.open(audio_buffer, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        # Clear temporary frame buffer
        self.frames = []

        # Return the compiled byte stream
        return audio_buffer.getvalue()

    # ==========================================
    # 2. Direct-from-RAM Playback System
    # ==========================================

    def play_audio_bytes(self, audio_bytes: bytes):
        """Streams decrypted audio bytes directly from memory to the output device."""

        def _play_process():
            print("System: Initiating secure audio playback...")
            
            # Load byte stream as a virtual file
            audio_buffer = io.BytesIO(audio_bytes)
            wf = wave.open(audio_buffer, 'rb')

            stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)

            # Read and output stream in chunks
            data = wf.readframes(self.CHUNK)
            while data:
                stream.write(data)
                data = wf.readframes(self.CHUNK)

            stream.stop_stream()
            stream.close()
            print("System: Audio playback concluded.")

        # Execute playback in an isolated thread to maintain UI responsiveness
        threading.Thread(target=_play_process).start()

    def cleanup(self):
        """Terminates the PyAudio instance gracefully during application shutdown."""
        self.p.terminate()
