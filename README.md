# Multi-Microphone Audio Signal Analyzer

## Overview
The **Multi-Microphone Audio Signal Analyzer** is a Python-based tool designed to visualize and analyze audio signals captured from multiple microphones in real-time. The application plots both the audio waveform and frequency spectrum for each microphone and includes a whistle detection feature that identifies and timestamps whistles within a specified frequency range.

## Features
- **Real-time audio visualization**: Displays audio waveforms and frequency spectra for each microphone.
- **Multi-microphone support**: Handles input from multiple microphones simultaneously.
- **Whistle detection**: Detects whistles based on amplitude thresholds and frequency range.
- **First-detection reporting**: Identifies which microphone detected the whistle first.

## Requirements
- Python 3.7 or later
- Required Python packages:
  - `pyaudio`
  - `numpy`
  - `matplotlib`

## Setup and Installation
1. **Install Python**: Ensure Python is installed on your system. Download it from [python.org](https://www.python.org/downloads/).
2. **Install dependencies**:
   ```bash
   pip install pyaudio numpy matplotlib
   ```
3. **Microphone device IDs**:
   - Update the `MIC_DEVICE_IDS` list in the script with the device IDs of your microphones. You can use PyAudio's `get_device_info_by_index()` method to find these IDs.

## Usage
1. Save the script to a file (e.g., `multi_microphone_analyzer.py`).
2. Run the script using:
   ```bash
   python multi_microphone_analyzer.py
   ```
3. The program will:
   - Visualize the audio waveforms and frequency spectra in real-time.
   - Detect whistles and display which microphone detected the whistle along with the timestamp.
   - Print the microphone that detected the first whistle when all microphones detect a whistle.

## Customization
- **Number of microphones**: Update the `NUM_MICROPHONES` variable to match the number of microphones you are using.
- **Whistle detection threshold**: Adjust the `whistle_threshold` variable to fine-tune the whistle detection sensitivity.
- **Whistle frequency range**: Modify the `whistle_freq_range` tuple to match the desired frequency range for whistle detection.
- **Plot limits**: Change the `set_xlim` and `set_ylim` values in the plotting section to adjust the visual scale.

## Notes
- Ensure that the device IDs in `MIC_DEVICE_IDS` correspond to connected microphones.
- Audio latency may vary depending on your hardware.
- Use high-quality microphones for better whistle detection accuracy.

## Example Output
The program generates a live visualization of:
1. **Audio Waveform**: The time-domain representation of the audio signal.
2. **Frequency Spectrum**: The magnitude of frequency components in the audio signal.

Upon detecting a whistle:
- A message is printed to the console indicating the microphone and timestamp of the detection.
- The program reports the first microphone to detect the whistle when all microphones register a whistle event.

## Troubleshooting
- **No audio input**: Verify that the microphones are properly connected and their device IDs are correctly configured.
- **PyAudio installation issues**: On some systems, additional dependencies may be required for PyAudio. Refer to [PyAudio installation documentation](https://pypi.org/project/PyAudio/).

## License
This project is licensed under the MIT License.

---

Happy coding! 🎤


 
