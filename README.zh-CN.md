# 音频切片机
这是一个 Python 脚本，通过静音检测来分割音频

## 算法

### 静音检测

这个脚本使用最大振幅来检测音频的静音部分。**大滑动窗口**用于通过卷积计算原始音频中每个特定区域的最大振幅。最大振幅低于阈值的所有区域将被视为静音。

### 音频切片

一旦检测到静音部分，脚本将使用RMS（均方根分数）来确定音频将被切片的特定位置。**小滑动窗口**用于搜索切开音频的最佳位置，即RMS 值最低的位置。长静音部分将被删除。

## 安装依赖

```shell
pip install librosa
pip install soundfile  # Optional. You can use any library you like to write audio files.
```

或者

```shell
pip install -r requirements.txt
```

## 用法

### 使用 Python 调用

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

### 使用命令行

可以使用以下命令运行脚本：

```shell
python slicer.py audio [--out OUT] [--db_thresh DB_THRESH] [--min_len MIN_LEN] [--win_l WIN_L] [--win_s WIN_S] [--max_sil_kept MAX_SIL_KEPT]
```

其中“audio”指的是要切片的音频，“--out”默认为与音频相同的目录，其他选项的默认值如[此处](#参数)所示。

## 参数

### sr

输入音频的采样率。

### db_threshold

振幅阈值以 dB 表示。所有振幅低于该阈值的区域将被视为静音。如果音频有噪音，请提高此值。默认值为 -40。

### min_length


每个音频切片所需的最小长度，单位为毫秒。默认值为 5000。

### win_l

大滑动窗口的大小，单位为毫秒。如果音频仅包含较短的停顿，请将此值调小。该值越小，此脚本可能生成的音频片段片段就越多。请注意，该值必须小于 min_length 且大于 win_s。默认值为 300。

### win_s

小滑动窗口的大小，单位为毫秒。通常不需要修改此值。默认值为 20。

### max_silence_kept

切片音频头尾出最多被保留的静音长度，单位为毫秒。根据需要调整此值。请注意，设置此值并不意味着切片音频中的静音部分恰好具有给定的长度。如上所述，该算法将搜索最佳切片位置。默认值为 1000。

## 性能

此脚本在 Python 层面包含一个时间复杂度为 $ O (n) $ 的主循环，其中  $ n $ 是音频的总采样数。除了这个瓶颈之外，所有繁重的计算都是由C++ 层面的 NumPy 和 SciPy 完成的。因此，此脚本在 Intel i7 8750H CPU 上能实现约 0.02~0.10 的 RTF（实时因子）。此外，由于 `Slicer` 类是线程安全的，使用多线程可能会进一步提高运行速度。
