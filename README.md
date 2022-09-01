# audio-slicer
Python scripts that slice audios with silence detection

## Algorithm

### Silence detection

This script uses RMS (root mean score) to measure and detect silence parts in the audio. A **large sliding window** is used to calculate the mean amplitude of each specific area in the original audio by convolution. All areas with RMS below the threshold will be regarded as silence.

### Audio slicing

The audio will be sliced through silence parts detected. A **small sliding window** is used to search for the best positions to slice the audio, i. e. the position with lowest RMS value. Long silence parts will be deleted.

## Requirements

```shell
pip install librosa
pip install soundfile  # Optional. You can use any library you like to write audio files.
```

or

```shell
pip install -r requirements.txt
```

## Usage

### Using Python class

```python
import librosa
import soundfile

from slicer import Slicer

audio, sr = librosa.load('example.wav', sr=None)  # Load an audio file with librosa
slicer = Slicer(
    sr=sr,
    db_threshold=-40,
    min_length=5000,
    win_l=400,
    win_s=20,
    max_silence_kept=500
)
chunks = slicer.slice(audio)
for i, chunk in enumerate(chunks):
    soundfile.write(f'example_{i}.wav', chunk, sr)  # Save sliced audio files with soundfile
```

### Using CLI

TODO

## Parameters

### sr

Sampling rate of the input audio.

### db_threshold

The RMS threshold presented in dB. Areas whose RMS values are below the threshold will be regarded as silence. Increase this value if your audio is noisy. Defaults to -36.

### min_length

The minimum length required for each sliced audio part, presented in milliseconds. Defaults to 5000.

### win_l

Size of the large sliding window, presented in milliseconds. Set this value smaller if your audio contains only short breaks. The smaller this value is, the more sliced audio parts this script is likely to generate. Note that this value must be smaller than min_length and larger than win_s. Defaults to 300.

### win_s

Size of the small sliding window, presented in milliseconds. Normally it is not necessary to modify this value. Defaults to 20.

### max_silence_kept

The maximum silence length kept around the sliced audio. Adjust this value according to your needs. Note: setting this value does not mean that silence parts in the sliced audio have exactly the fixed length. The algorithm will search for the best position to slice, as described above. Defaults to 1000.

## Note

This script may be quite slow due to convolution operations. As the Slicer class is thread-safe, using multi-threading can speed up the process.
