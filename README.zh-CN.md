# Audio Slicer
这是一个python脚本，通过静音检测来分割音频

## 算法

### 静音检测

这个脚本使用最大振幅来测量和检测音频的静音部分.  **大滑动窗口** 用于通过卷积计算原始音频中每个特定区域的最大幅度。 最大振幅低于阈值的所有区域将被视为静音。

### 音频切片

一旦检测到静音部分，脚本将使用RMS（均方根分数）来确定音频将被切片的特定位置。**小滑动窗口**用于搜索音频切片的最佳位置，即RMS值最低的位置。长静音部分将被删除。

## 必备依赖

```shell
pip install librosa
pip install soundfile  # Optional. You can use any library you like to write audio files.
```

或者

```shell
pip install -r requirements.txt
```

## 用法

### 使用Python

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

### 使用CLl

The script can be run with CLI as below:

```shell
python slicer.py audio [--out OUT] [--db_thresh DB_THRESH] [--min_len MIN_LEN] [--win_l WIN_L] [--win_s WIN_S] [--max_sil_kept MAX_SIL_KEPT]
```

其中“audio”指的是要切片的音频，“--out”默认为与音频相同的目录，其他选项的默认值如下所示[这里](#参数).

## 参数

### sr

输入音频的采样率

### db_threshold

振幅阈值以dB表示。所有振幅低于该阈值的区域将被视为静音。如果音频有噪音，请增加此值。默认值为-40。

### min_length


每个切片音频剪辑所需的最小长度，以毫秒为单位。默认值为5000。

### win_l

大滑动窗口的大小，以毫秒为单位。如果音频仅包含短中断，请将此值设置得较小。该值越小，此脚本可能生成的音频片段片段就越多。请注意，该值必须小于min_length且大于win_s。默认值为300。

### win_s

小滑动窗口的大小，以毫秒为单位。通常不需要修改此值。默认值为20。

### max_silence_kept

切片音频周围保持的最大静音长度，以毫秒为单位。根据需要调整此值。请注意，设置此值并不意味着切片音频中的静音部分具有完全给定的长度。如上所述，该算法将搜索最佳切片位置。默认值为1000。

## 性能

此脚本包含Python级别的 $ O (n) $ main循环，其中  $ n $ 指音频样本的计数。除了这个瓶颈之外，所有繁重的计算都是由C++级别的“numpy”和“scipy”完成的。因此，此脚本在Intel i7 8750H CPU上实现了约0.02~0.10的RTF（实时因子）。此外，由于“Slicer”类是线程安全的，因此使用多线程可能会进一步加快进程。
