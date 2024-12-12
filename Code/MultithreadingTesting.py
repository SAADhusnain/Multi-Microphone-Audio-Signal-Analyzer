import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
import multiprocessing
from datetime import datetime
from queue import Empty

# Constants
CHUNK = 1024 * 4             # Increase the chunk size to reduce the frequency of reads
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

# Function to process data for each microphone in a separate process
def process_microphone_data(i, stop_flag, whistle_detected, whistle_timestamps, 
                            whistle_first_detected_time, whistle_first_microphone, frame_count, queue, 
                            whistle_threshold, whistle_freq_range):
    stream = streams[i]
    
    while not stop_flag.is_set():
        # Read data from microphone
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
        except IOError as e:
            print(f"Error reading stream {i}: {e}")
            continue

        # Convert binary data to numpy array
        data_np = np.frombuffer(data, dtype=np.int16) / (2 ** 15)

        # Compute Fourier transform
        spectrum = np.fft.fft(data_np)
        magnitude = np.abs(spectrum[:CHUNK // 2]) * 2 
        spectrum_scaled = magnitude * 2

        # Whistle detection
        whistle_magnitude = magnitude[(np.linspace(0, RATE / 2, CHUNK // 2) >= whistle_freq_range[0]) & 
                                      (np.linspace(0, RATE / 2, CHUNK // 2) <= whistle_freq_range[1])]
        if np.max(whistle_magnitude) > whistle_threshold and not whistle_detected[i]:
            whistle_detected[i] = True
            whistle_timestamps[i] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Whistle detected on Microphone {i+1} at: {whistle_timestamps[i]}")

            if whistle_first_detected_time.value == '' or whistle_timestamps[i] < whistle_first_detected_time.value:
                whistle_first_detected_time.value = whistle_timestamps[i]
                whistle_first_microphone.value = i + 1

        # Report which microphone detected the whistle first
        if all(whistle_detected) and whistle_first_detected_time.value != '':
            print(f"Microphone {whistle_first_microphone.value} detected the whistle first at {whistle_first_detected_time.value}.")
            stop_flag.set()  # Set the stop flag to stop the processes and main loop

        # Put data in the queue
        if not queue.full():
            queue.put((i, data_np, spectrum_scaled))
        frame_count.value += 1

if __name__ == '__main__':
    # For measuring frame rate
    frame_count = multiprocessing.Value('i', 0)
    start_time = time.time()

    # Define whistle detection parameters
    whistle_threshold = 150  # Adjust this threshold based on your whistle intensity
    whistle_freq_range = (3000, 6000)

    # Initialize variables for whistle detection using Manager
    manager = multiprocessing.Manager()
    whistle_detected = manager.list([False] * NUM_MICROPHONES)
    whistle_timestamps = manager.list([''] * NUM_MICROPHONES)
    whistle_first_detected_time = manager.Value('u', '')
    whistle_first_microphone = manager.Value('i', -1)

    # Queue for inter-process communication
    queue = multiprocessing.Queue(maxsize=20)

    # Flag to indicate when to stop
    stop_flag = multiprocessing.Event()

    # Create and start processes for each microphone
    processes = []
    for i in range(NUM_MICROPHONES):
        p = multiprocessing.Process(target=process_microphone_data, args=(i, stop_flag, whistle_detected, whistle_timestamps, 
                                                                          whistle_first_detected_time, whistle_first_microphone, 
                                                                          frame_count, queue, whistle_threshold, whistle_freq_range))
        processes.append(p)
        p.start()

    # Main loop for updating the plot in the main process
    try:
        while not stop_flag.is_set():
            # Process items from the queue in batches
            batch_data = []
            while not queue.empty() and len(batch_data) < NUM_MICROPHONES:
                try:
                    batch_data.append(queue.get_nowait())
                except Empty:
                    pass
            
            for i, data_np, spectrum_scaled in batch_data:
                # Update waveform plot
                lines_waveform[i].set_ydata(data_np)

                # Update spectrum plot
                lines_spectrum[i].set_ydata(spectrum_scaled)

            if batch_data:
                # Update figure canvas once per batch
                fig.canvas.draw()
                fig.canvas.flush_events()
            
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Interrupted, closing streams and terminating PyAudio")

    # Close streams
    for stream in streams:
        stream.stop_stream()
        stream.close()

    # Close PyAudio
    p.terminate()

    # Wait for all processes to finish
    for process in processes:
        process.join()

    # Print average frame rate
    frame_rate = frame_count.value / (time.time() - start_time)
    print('Stream stopped')
    print('Average frame rate = {:.0f} FPS'.format(frame_rate))
