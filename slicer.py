import os.path
from argparse import ArgumentParser
import time

import librosa
import numpy as np
import soundfile
from scipy.ndimage import maximum_filter1d, uniform_filter1d


def timeit(func):
    def run(*args, **kwargs):
        t = time.time()
        res = func(*args, **kwargs)
        print('executing \'%s\' cost %.3fs' % (func.__name__, time.time() - t))
        return res
    return run


# @timeit
def _window_maximum(arr, win_sz):
    return maximum_filter1d(arr, size=win_sz)[win_sz // 2: win_sz // 2 + arr.shape[0] - win_sz + 1]


# @timeit
def _window_rms(arr, win_sz):
    filtered = np.sqrt(uniform_filter1d(np.power(arr, 2), win_sz) - np.power(uniform_filter1d(arr, win_sz), 2))
    return filtered[win_sz // 2: win_sz // 2 + arr.shape[0] - win_sz + 1]


def level2db(levels, eps=1e-12):
    return 20 * np.log10(np.clip(levels, a_min=eps, a_max=1))


def _apply_slice(audio, begin, end):
    if len(audio.shape) > 1:
        return audio[:, begin: end]
    else:
        return audio[begin: end]


class Slicer:
    def __init__(self,
                 sr: int,
                 db_threshold: float = -40,
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

    @timeit
    def slice(self, audio):
        if len(audio.shape) > 1:
            samples = librosa.to_mono(audio)
        else:
            samples = audio
        if samples.shape[0] <= self.min_samples:
            return [audio]
        # get absolute amplitudes
        abs_amp = np.abs(samples - np.mean(samples))
        # calculate local maximum with large window
        win_max_db = level2db(_window_maximum(abs_amp, win_sz=self.win_ln))
        sil_tags = []
        left = right = 0
        while right < win_max_db.shape[0]:
            if win_max_db[right] < self.db_threshold:
                right += 1
            elif left == right:
                left += 1
                right += 1
            else:
                if left == 0:
                    split_loc_l = left
                else:
                    sil_left_n = min(self.max_silence, (right + self.win_ln - left) // 2)
                    rms_db_left = level2db(_window_rms(samples[left: left + sil_left_n], win_sz=self.win_sn))
                    split_win_l = left + np.argmin(rms_db_left)
                    split_loc_l = split_win_l + np.argmin(abs_amp[split_win_l: split_win_l + self.win_sn])
                if len(sil_tags) != 0 and split_loc_l - sil_tags[-1][1] < self.min_samples and right < win_max_db.shape[0] - 1:
                    right += 1
                    left = right
                    continue
                if right == win_max_db.shape[0] - 1:
                    split_loc_r = right + self.win_ln
                else:
                    sil_right_n = min(self.max_silence, (right + self.win_ln - left) // 2)
                    rms_db_right = level2db(_window_rms(samples[right + self.win_ln - sil_right_n: right + self.win_ln], win_sz=self.win_sn))
                    split_win_r = right + self.win_ln - sil_right_n + np.argmin(rms_db_right)
                    split_loc_r = split_win_r + np.argmin(abs_amp[split_win_r: split_win_r + self.win_sn])
                sil_tags.append((split_loc_l, split_loc_r))
                right += 1
                left = right
        if left != right:
            sil_left_n = min(self.max_silence, (right + self.win_ln - left) // 2)
            rms_db_left = level2db(_window_rms(samples[left: left + sil_left_n], win_sz=self.win_sn))
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
    parser = ArgumentParser()
    parser.add_argument('audio', type=str, help='The audio to be sliced')
    parser.add_argument('--out', type=str, help='Output directory of the sliced audio clips')
    parser.add_argument('--db_thresh', type=float, required=False, default=-40, help='The dB threshold for silence detection')
    parser.add_argument('--min_len', type=int, required=False, default=5000, help='The minimum milliseconds required for each sliced audio clip')
    parser.add_argument('--win_l', type=int, required=False, default=300, help='Size of the large sliding window, presented in milliseconds')
    parser.add_argument('--win_s', type=int, required=False, default=20, help='Size of the small sliding window, presented in milliseconds')
    parser.add_argument('--max_sil_kept', type=int, required=False, default=500, help='The maximum silence length kept around the sliced audio, presented in milliseconds')
    args = parser.parse_args()
    out = args.out
    if out is None:
        out = os.path.dirname(os.path.abspath(args.audio))
    audio, sr = librosa.load(args.audio, sr=None)
    slicer = Slicer(
        sr=sr,
        db_threshold=args.db_thresh,
        min_length=args.min_len,
        win_l=args.win_l,
        win_s=args.win_s,
        max_silence_kept=args.max_sil_kept
    )
    chunks = slicer.slice(audio)
    if not os.path.exists(out):
        os.makedirs(out)
    for i, chunk in enumerate(chunks):
        soundfile.write(os.path.join(out, f'%s_%d.wav' % (os.path.basename(args.audio).rsplit('.', maxsplit=1)[0], i)), chunk, sr)


if __name__ == '__main__':
    main()
