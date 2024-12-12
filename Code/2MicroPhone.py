import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
from tkinter import TclError
from datetime import datetime

# Constants
CHUNK = 1024 * 2             # Samples per frame
FORMAT = pyaudio.paInt16     # Audio format (bytes per sample?)
CHANNELS = 2                 # Two channels for two microphones
RATE = 44100                 # Samples per second

# Create matplotlib figure and axes
fig, axs = plt.subplots(2, 2, figsize=(15, 10))

# PyAudio class instance
p = pyaudio.PyAudio()

# Stream objects to get data from two microphones
streams = [p.open(
    format=FORMAT,
    channels=1,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
) for _ in range(CHANNELS)]

# Variables for plotting
x = np.arange(0, 2 * CHUNK, 2)
lines_waveform = [[axs[i, j].plot(x, np.random.rand(CHUNK), '-', lw=2)[0] for j in range(2)] for i in range(2)]
lines_spectrum = [axs[1, j].semilogx(np.linspace(0, RATE / 2, CHUNK // 2), np.zeros(CHUNK // 2), '-', lw=2)[0] for j in range(2)]

# Basic formatting for the axes
for ax_row in axs:
    for ax in ax_row:
        ax.set_ylim(-2, 2)

for ax in axs[1]:
    ax.set_xlim(1000, 6000)
    ax.set_ylim(0, 1500)
    ax.set_xlabel('Frequency [Hz]')

axs[0, 0].set_title('Microphone 1 - AUDIO WAVEFORM')
axs[0, 1].set_title('Microphone 2 - AUDIO WAVEFORM')
axs[0, 0].set_ylabel('Volume')
axs[1, 0].set_ylabel('Amplitude')

# Show the plot
plt.tight_layout()
plt.show(block=False)

print('Stream started')

# For measuring frame rate
frame_count = 0
start_time = time.time()

# Define whistle detection parameters
whistle_threshold = 250  # Adjust this threshold based on your whistle intensity
whistle_freq_range = (3000, 6000)

while True:
    for i in range(CHANNELS):
        # Binary data
        data = streams[i].read(CHUNK)

        # Convert binary data to numpy array
        data_np = np.frombuffer(data, dtype=np.int16) / (2 ** 15)

        # Update waveform plot
        lines_waveform[0][i].set_ydata(data_np)

        # Compute Fourier transform
        spectrum = np.fft.fft(data_np)
        magnitude = np.abs(spectrum[:CHUNK//2]) * 2 
        spectrum_scaled = magnitude * 2

        # Update spectrum plot
        lines_spectrum[i].set_ydata(spectrum_scaled)
        
        # Whistle detection
        whistle_magnitude = magnitude[(np.linspace(0, RATE / 2, CHUNK // 2) >= whistle_freq_range[0]) & 
                                      (np.linspace(0, RATE / 2, CHUNK // 2) <= whistle_freq_range[1])]
        if np.max(whistle_magnitude) > whistle_threshold:
            whistle_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Whistle detected on Microphone {i+1} at: {whistle_time}")

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
