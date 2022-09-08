# Audio Slicer
Python script that slices audios with silence detection

## Algorithm

### Silence detection

This script uses maximum amplitude to measure and detect silence parts in the audio. A **large sliding window** is used to calculate the max amplitude of each specific area in the original audio by convolution. All areas with a maximum amplitude below the threshold will be regarded as silence.

### Audio slicing

Once silence parts are detected, this script uses RMS (root mean score) to determine the specific position where the audio will be sliced. A **small sliding window** is used to search for the best positions to slice the audio, i. e. the position with lowest RMS value. Long silence parts will be deleted.

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
    db_threshold=-30,
    min_length=5000,
    win_l=400,
    win_s=20,
    max_silence_kept=500
)
chunks = slicer.slice(audio)
for i, chunk in enumerate(chunks):
    soundfile.write(f'clips/example_{i}.wav', chunk, sr)  # Save sliced audio files with soundfile
```

### Using CLI

The script can be run with CLI as below:

```shell
python slicer.py audio [--out OUT] [--db_thresh DB_THRESH] [--min_len MIN_LEN] [--win_l WIN_L] [--win_s WIN_S] [--max_sil_kept MAX_SIL_KEPT]
```

where `audio` refers to the audio to be sliced, `--out` defaults to the same directory as the audio, and other options have default values as listed [here](#Parameters).

## Parameters

### sr

Sampling rate of the input audio.

### db_threshold

The amplitude threshold presented in dB. Areas where all amplitudes are below this threshold will be regarded as silence. Increase this value if your audio is noisy. Defaults to -40.

### min_length

The minimum length required for each sliced audio clip, presented in milliseconds. Defaults to 5000.

### win_l

Size of the large sliding window, presented in milliseconds. Set this value smaller if your audio contains only short breaks. The smaller this value is, the more sliced audio clips this script is likely to generate. Note that this value must be smaller than min_length and larger than win_s. Defaults to 300.

### win_s

Size of the small sliding window, presented in milliseconds. Normally it is not necessary to modify this value. Defaults to 20.

### max_silence_kept

The maximum silence length kept around the sliced audio, presented in milliseconds. Adjust this value according to your needs. Note that setting this value does not mean that silence parts in the sliced audio have exactly the given length. The algorithm will search for the best position to slice, as described above. Defaults to 1000.

## Performance

This script contains an $O(n)$ main loop on the Python level, where $n$ refers to the count of audio samples. Besides this bottleneck, all heavy calculation is done by `numpy` and `scipy` on the C++ level. Thus, this script achieves an RTF (Real-Time Factor) about 0.02~0.10 on an Intel i7 8750H CPU. In addition, as the `Slicer` class is thread-safe, using multi-threading may further speed up the process.
