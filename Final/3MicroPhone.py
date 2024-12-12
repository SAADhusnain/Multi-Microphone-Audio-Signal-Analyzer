import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
from tkinter import TclError
from datetime import datetime

# Constants
CHUNK = 1024 * 2             # Samples per frame
FORMAT = pyaudio.paInt16     # Audio format (bytes per sample)
RATE = 44100                 # Samples per second
NUM_MICROPHONES = 3          # Number of microphones
MIC_DEVICE_IDS = [1, 2, 4]   # Replace with the actual device IDs of your microphones

# PyAudio class instance
p = pyaudio.PyAudio()

# Create matplotlib figure and axes
fig, axs = plt.subplots(NUM_MICROPHONES, 2, figsize=(15, 15))

# Initialize streams and plots for each microphone
streams = []
lines_waveform = []
lines_spectrum = []

for i in range(NUM_MICROPHONES):
    # Open stream for each microphone
    stream = p.open(
        format=FORMAT,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=MIC_DEVICE_IDS[i]
    )
    streams.append(stream)

    # Variables for plotting
    x = np.arange(0, 2 * CHUNK, 2)
    lines_waveform.append(axs[i, 0].plot(x, np.random.rand(CHUNK), '-', lw=2)[0])
    lines_spectrum.append(axs[i, 1].semilogx(np.linspace(0, RATE / 2, CHUNK // 2), np.zeros(CHUNK // 2), '-', lw=2)[0])

    # Basic formatting for the axes
    axs[i, 0].set_ylim(-2, 2)
    axs[i, 0].set_xlim(0, 2 * CHUNK)
    axs[i, 1].set_xlim(1000, 6000)
    axs[i, 1].set_ylim(0, 1500)
    axs[i, 1].set_xlabel('Frequency [Hz]')
    axs[i, 0].set_ylabel('Volume')
    axs[i, 1].set_ylabel('Amplitude')
    axs[i, 0].set_title(f'Microphone {i + 1} - AUDIO WAVEFORM')
    axs[i, 1].set_title(f'Microphone {i + 1} - AUDIO SPECTRUM')

# Show the plot
plt.tight_layout()
plt.show(block=False)

print('Stream started')

# For measuring frame rate
frame_count = 0
start_time = time.time()

# Define whistle detection parameters
whistle_threshold = 150  # Adjust this threshold based on your whistle intensity
whistle_freq_range = (3000, 6000)

# Initialize variables for whistle detection
whistle_detected = [False] * NUM_MICROPHONES
whistle_timestamps = [None] * NUM_MICROPHONES
whistle_first_detected_time = None
whistle_first_microphone = None

while True:
    # Read data from all microphones
    all_data = [stream.read(CHUNK) for stream in streams]
    
    # Process data for each microphone
    for i in range(NUM_MICROPHONES):
        # Binary data
        data = all_data[i]

        # Convert binary data to numpy array
        data_np = np.frombuffer(data, dtype=np.int16) / (2 ** 15)

        # Update waveform plot
        lines_waveform[i].set_ydata(data_np)

        # Compute Fourier transform
        spectrum = np.fft.fft(data_np)
        magnitude = np.abs(spectrum[:CHUNK//2]) * 2 
        spectrum_scaled = magnitude * 2

        # Update spectrum plot
        lines_spectrum[i].set_ydata(spectrum_scaled)
        
        # Whistle detection
        whistle_magnitude = magnitude[(np.linspace(0, RATE / 2, CHUNK // 2) >= whistle_freq_range[0]) & 
                                      (np.linspace(0, RATE / 2, CHUNK // 2) <= whistle_freq_range[1])]
        if np.max(whistle_magnitude) > whistle_threshold and not whistle_detected[i]:
            whistle_detected[i] = True
            whistle_timestamps[i] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Whistle detected on Microphone {i+1} at: {whistle_timestamps[i]}")

            if whistle_first_detected_time is None or whistle_timestamps[i] < whistle_first_detected_time:
                whistle_first_detected_time = whistle_timestamps[i]
                whistle_first_microphone = i + 1

    # Report which microphone detected the whistle first
    if all(whistle_detected) and whistle_first_detected_time is not None:
        print(f"Microphone {whistle_first_microphone} detected the whistle first at {whistle_first_detected_time}.")
        whistle_detected = [False] * NUM_MICROPHONES  # Reset for the next whistle detection
        whistle_first_detected_time = None
        whistle_first_microphone = None

    # Update figure canvas
    try:
        fig.canvas.draw()
        fig.canvas.flush_events()
        frame_count += 1

    except TclError:
        # Calculate average frame rate
        frame_rate = frame_count / (time.time() - start_time)

        print('Stream stopped')
        print('Average frame rate = {:.0f} FPS'.format(frame_rate))
        break

# Close streams
for stream in streams:
    stream.stop_stream()
    stream.close()

# Close PyAudio
p.terminate()
