import librosa
import numpy as np
import soundfile


def _const_conv1d(arr, k_sz, k_val):
    result = np.zeros(arr.shape[0] - k_sz + 1)
    total = np.sum(arr[: k_sz])
    result[0] = total * k_val
    for i in range(1, result.shape[0]):
        total = total - arr[i] + arr[i + k_sz - 1]
        result[i] = total * k_val
    return result
    # return np.convolve(arr, np.full(k_sz, k_val), mode='valid')


def _rms(audio, win_sz):
    return np.sqrt(_const_conv1d(np.power(audio, 2), win_sz, 1 / win_sz) - np.power(_const_conv1d(audio, win_sz, 1 / win_sz), 2))


def _apply_slice(audio, begin, end):
    if len(audio.shape) > 1:
        return audio[:, begin: end]
    else:
        return audio[begin: end]


class Slicer:
    def __init__(self,
                 sr: int,
                 db_threshold: float = -36,
                 min_length: int = 5000,
                 win_l: int = 300,
                 win_s: int = 20,
                 max_silence_kept: int = 1000):
        self.db_threshold = db_threshold
        self.min_samples = round(sr * min_length / 1000)
        self.win_ln = round(sr * win_l / 1000)
        self.win_sn = round(sr * win_s / 1000)
        if not min_length >= win_l >= win_s:
            raise ValueError('The following condition must be satisfied: min_length >= win_l >= win_s')

    def slice(self, audio):
        if len(audio.shape) > 1:
            samples = librosa.to_mono(audio)
        else:
            samples = audio
        # calculate RMS of each window
        rms_db_l = np.log10(np.clip(_rms(samples, win_sz=self.win_ln), a_min=1e-12, a_max=1)) * 20
        rms_db_s = np.log10(np.clip(_rms(samples, win_sz=self.win_sn), a_min=1e-12, a_max=1)) * 20
        tags = []
        left = right = 0
        while right < rms_db_l.shape[0]:
            if rms_db_l[right] < self.db_threshold:
                right += 1
            elif left == right:
                left += 1
                right += 1
            else:
                # TODO: discard silence parts
                split_win_m = left + np.argmin(rms_db_s[left: right + self.win_ln - self.win_sn])
                split_loc_m = split_win_m + np.argmin(rms_db_s[split_win_m: split_win_m + self.win_sn])
                if 0 < split_loc_m < samples.shape[0] - 1 and (len(tags) == 0 or split_loc_m - tags[-1] >= self.min_samples):
                    tags.append(split_loc_m)
                right += 1
                left = right
        if len(tags) == 0:
            return [audio]
        else:
            chunks = [_apply_slice(audio, 0, tags[0])]
            for i in range(1, len(tags)):
                chunks.append(_apply_slice(audio, tags[i - 1], tags[i]))
            chunks.append(_apply_slice(audio, tags[-1], samples.shape[0]))
            return chunks


def main():
    audio, sr = librosa.load(r'D:\Vocoder Datasets\颜绮萱\颜绮萱-2021干声\大鱼-速度140.wav', sr=None)
    slicer = Slicer(sr=sr, db_threshold=-40, min_length=5000, win_l=750, win_s=20)
    chunks = slicer.slice(audio)
    for i, chunk in enumerate(chunks):
        soundfile.write(fr'D:\Vocoder Datasets\slices\大鱼_{i}.wav', chunk, sr)


if __name__ == '__main__':
    main()
