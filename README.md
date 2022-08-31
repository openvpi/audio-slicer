# audio-slicer
Python scripts that slice audios with silence detection

## Requirements

```shell
pip install librosa
pip install soundfile  # Optional. You can use any library you like to write wav files.
```

or:

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
slicer = Slicer(sr=sr, db_threshold=-40, min_length=5000, win_l=750, win_s=20)
chunks = slicer.slice(audio)
for i, chunk in enumerate(chunks):
    soundfile.write(f'example_{i}.wav', chunk, sr)  # Save sliced audio files with soundfile
```

### Using CLI

TODO

