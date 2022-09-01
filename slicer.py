import librosa
import numpy as np
import soundfile


def _const_conv1d(arr, k_sz, k_val):
    result = np.zeros(arr.shape[0] - k_sz + 1)
    total = np.sum(arr[: k_sz])
    result[0] = total * k_val
    for i in range(1, result.shape[0]):
        total = total - arr[i - 1] + arr[i + k_sz - 1]
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
                 max_silence_kept: int = 500):
        self.db_threshold = db_threshold
        self.min_samples = round(sr * min_length / 1000)
        self.win_ln = round(sr * win_l / 1000)
        self.win_sn = round(sr * win_s / 1000)
        self.max_silence = round(sr * max_silence_kept / 1000)
        if not self.min_samples >= self.win_ln >= self.win_sn:
            raise ValueError('The following condition must be satisfied: min_length >= win_l >= win_s')
        if not self.max_silence >= self.win_sn:
            raise ValueError('The following condition must be satisfied: max_silence_kept >= win_s')

    def slice(self, audio):
        if len(audio.shape) > 1:
            samples = librosa.to_mono(audio)
        else:
            samples = audio
        if samples.shape[0] <= self.min_samples:
            return [audio]
        # calculate RMS with large window
        rms_db_l = np.log10(np.clip(_rms(samples, win_sz=self.win_ln), a_min=1e-12, a_max=1)) * 20
        # get absolute amplitudes
        abs_amp = np.abs(samples - np.mean(samples))
        # rms_db_s = np.log10(np.clip(_rms(samples, win_sz=self.win_sn), a_min=1e-12, a_max=1)) * 20
        sil_tags = []
        left = right = 0
        while right < rms_db_l.shape[0]:
            if rms_db_l[right] < self.db_threshold:
                right += 1
            elif left == right:
                left += 1
                right += 1
            else:
                if left == 0:
                    split_loc_l = left
                else:
                    sil_left_n = min(self.max_silence, (right + self.win_ln - left) // 2)
                    rms_db_left = np.log10(np.clip(_rms(samples[left: left + sil_left_n], win_sz=self.win_sn), a_min=1e-12, a_max=1)) * 20
                    split_win_l = left + np.argmin(rms_db_left)
                    split_loc_l = split_win_l + np.argmin(abs_amp[split_win_l: split_win_l + self.win_sn])
                if len(sil_tags) != 0 and split_loc_l - sil_tags[-1][1] < self.min_samples and right < rms_db_l.shape[0] - 1:
                    right += 1
                    left = right
                    continue
                if right == rms_db_l.shape[0] - 1:
                    split_loc_r = right + self.win_ln
                else:
                    sil_right_n = min(self.max_silence, (right + self.win_ln - left) // 2)
                    rms_db_right = np.log10(np.clip(_rms(samples[right + self.win_ln - sil_right_n: right + self.win_ln], win_sz=self.win_sn), a_min=1e-12, a_max=1)) * 20
                    split_win_r = right + self.win_ln - sil_right_n + np.argmin(rms_db_right)
                    split_loc_r = split_win_r + np.argmin(abs_amp[split_win_r: split_win_r + self.win_sn])
                sil_tags.append((split_loc_l, split_loc_r))
                right += 1
                left = right
        if left != right:
            sil_left_n = min(self.max_silence, (right + self.win_ln - left) // 2)
            rms_db_left = np.log10(
                np.clip(_rms(samples[left: left + sil_left_n], win_sz=self.win_sn), a_min=1e-12, a_max=1)) * 20
            split_win_l = left + np.argmin(rms_db_left)
            split_loc_l = split_win_l + np.argmin(abs_amp[split_win_l: split_win_l + self.win_sn])
            sil_tags.append((split_loc_l, samples.shape[0]))
        if len(sil_tags) == 0:
            return [audio]
        else:
            chunks = []
            if sil_tags[0][0] > 0:
                chunks.append(_apply_slice(audio, 0, sil_tags[0][0]))
            for i in range(0, len(sil_tags) - 1):
                chunks.append(_apply_slice(audio, sil_tags[i][1], sil_tags[i + 1][0]))
            if sil_tags[-1][1] < samples.shape[0] - 1:
                chunks.append(_apply_slice(audio, sil_tags[-1][1], samples.shape[0]))
            return chunks


def main():
    audio, sr = librosa.load('example.wav', sr=None)
    slicer = Slicer(sr=sr, db_threshold=-40, min_length=5000, win_l=400, win_s=20, max_silence_kept=500)
    chunks = slicer.slice(audio)
    for i, chunk in enumerate(chunks):
        soundfile.write(f'example_{i}.wav', chunk, sr)


if __name__ == '__main__':
    main()
