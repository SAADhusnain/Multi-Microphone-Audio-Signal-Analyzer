import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
from tkinter import TclError
from datetime import datetime

# Constants
CHUNK = 1024 * 2             # Samples per frame
FORMAT = pyaudio.paInt16     # Audio format (bytes per sample?)
CHANNELS = 1                 # Single channel for microphone
RATE = 44100                 # Samples per second

# Create matplotlib figure and axes
fig, ax = plt.subplots(2, figsize=(15, 10))

# PyAudio class instance
p = pyaudio.PyAudio()

# Stream object to get data from microphone
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

# Variable for plotting
x = np.arange(0, 2 * CHUNK, 2)

# Create line objects for waveform and spectrum
line_waveform, = ax[0].plot(x, np.random.rand(CHUNK), '-', lw=2)
line_spectrum, = ax[1].semilogx(np.linspace(0, RATE / 2, CHUNK // 2), np.zeros(CHUNK // 2), '-', lw=2)

# Basic formatting for the axes
ax[0].set_title('AUDIO WAVEFORM')
ax[0].set_xlabel('Samples')
ax[0].set_ylabel('Volume')
ax[0].set_ylim(-2, 2)
ax[0].set_xlim(0, 2 * CHUNK)

ax[1].set_title('AUDIO SPECTRUM')
ax[1].set_xlabel('Frequency [Hz]')
ax[1].set_ylabel('Amplitude')
ax[1].set_xlim(1000, 6000)
ax[1].set_ylim(0, 1500)  # Set the minimum amplitude to a small value to avoid log(0)

# Show the plot
plt.show(block=False)

print('Stream started')

# For measuring frame rate
frame_count = 0
start_time = time.time()

# Define whistle detection parameters
whistle_threshold = 250  # Adjust this threshold based on your whistle intensity
whistle_freq_range = (3000, 6000)

while True:

    # Binary data
    data = stream.read(CHUNK)

    # Convert binary data to numpy array
    data_np = np.frombuffer(data, dtype=np.int16) / (2 ** 15)

    # Update waveform plot
    line_waveform.set_ydata(data_np)

    # Compute Fourier transform
    spectrum = np.fft.fft(data_np)
    magnitude = np.abs(spectrum[:CHUNK//2]) * 2 
    spectrum_scaled = magnitude * 2

    # Update spectrum plot
    line_spectrum.set_ydata(spectrum_scaled)
    
    # Whistle detection
    whistle_magnitude = magnitude[(np.linspace(0, RATE / 2, CHUNK // 2) >= whistle_freq_range[0]) & 
                                  (np.linspace(0, RATE / 2, CHUNK // 2) <= whistle_freq_range[1])]
    if np.max(whistle_magnitude) > whistle_threshold:
        whistle_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("Whistle detected at:", whistle_time)

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
