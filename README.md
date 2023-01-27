# Audio Slicer

Python script that slices audio with silence detection

---

This is the 2.0 version of audio slicer, which provides:

- Great improvements on speed (400x compared to previous 15x)
- Enhanced slicing logic with fewer errors

The 1.0 version can be found [here](https://github.com/openvpi/audio-slicer/tree/old).

GUI version can be found [here](https://github.com/flutydeer/audio-slicer).

## Algorithm

### Silence detection

This script uses RMS (root mean score) to measure the quiteness of the audio and detect silent parts. RMS values of each frame (frame length set as **hop size**) are calculated and all frames with an RMS below the **threshold** will be regarded as silent frames.

### Audio slicing

Once the valid (sound) part reached **min length** since last slice and a silent part longer than **min interval** are detected, the audio will be sliced apart from the frame(s) with the lowest RMS value within the silent area. Long silence parts may be deleted.

## Requirements

### If you are using Python API

```bash
pip install numpy
```

### If you are using CLI

```shell
pip install librosa
pip install soundfile
```

or

```shell
pip install -r requirements.txt
```

## Usage

### Using Python API

```python
import librosa  # Optional. Use any library you like to read audio files.
import soundfile  # Optional. Use any library you like to write audio files.

from slicer2 import Slicer

audio, sr = librosa.load('example.wav', sr=None, mono=False)  # Load an audio file with librosa.
slicer = Slicer(
    sr=sr,
    threshold=-40,
    min_length=5000,
    min_interval=300,
    hop_size=10,
    max_sil_kept=500
)
chunks = slicer.slice(audio)
for i, chunk in enumerate(chunks):
    if len(chunk.shape) > 1:
        chunk = chunk.T  # Swap axes if the audio is stereo.
    soundfile.write(f'clips/example_{i}.wav', chunk, sr)  # Save sliced audio files with soundfile.
```

### Using CLI

The script can be run with CLI as below:

```bash
python slicer2.py audio [--out OUT] [--db_thresh DB_THRESH] [--min_length MIN_LENGTH] [--min_interval MIN_INTERVAL] [--hop_size HOP_SIZE] [--max_sil_kept MAX_SIL_KEPT]
```

where `audio` refers to the audio to be sliced, `--out` defaults to the same directory as the audio, and other options have default values as listed [here](#Parameters).

## Parameters

### sr

Sampling rate of the input audio.

### db_threshold

The RMS threshold presented in dB. Areas where all RMS values are below this threshold will be regarded as silence. Increase this value if your audio is noisy. Defaults to -40.

### min_length

The minimum length required for each sliced audio clip, presented in milliseconds. Defaults to 5000.

### min_interval

The minimum length for a silence part to be sliced, presented in milliseconds. Set this value smaller if your audio contains only short breaks. The smaller this value is, the more sliced audio clips this script is likely to generate. Note that this value must be smaller than min_length and larger than hop_size. Defaults to 300.

### hop_size

Length of each RMS frame, presented in milliseconds. Increasing this value will increase the precision of slicing, but will slow down the process. Defaults to 10.

### max_silence_kept

The maximum silence length kept around the sliced audio, presented in milliseconds. Adjust this value according to your needs. Note that setting this value does not mean that silence parts in the sliced audio have exactly the given length. The algorithm will search for the best position to slice, as described above. Defaults to 1000.

## Performance

This script runs over 400x faster than real-time on an Intel i7 8750H CPU. Speed may vary according to your CPU and your disk. Though `Slicer` is thread-safe, multi-threading does not seem neccessary due to the I/O bottleneck.

