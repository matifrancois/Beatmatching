import librosa
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sps
import soundfile as sf
from IPython.display import Audio
from modified_psola import modified_psola
from detect_pitch import get_fundamental_frequency

def LPC_process(x, fs, order, window_time=None):
    """
    Gets LPC error coefficients for a given signal.
    """
    # Windowed LPC
    if window_time != None:
        # Window len in samples
        wlen = int(np.floor(window_time * 0.001 * fs))
        print(wlen)
        coefs = []
        error = []
        for w in range(len(x)//wlen):
            _c = librosa.lpc(x[(w*wlen):(w+1)*wlen], order=order)
            coefs.append(_c)
            error.append(sps.lfilter( _c, [1], x[(w*wlen):(w+1)*wlen])) # El filtro del error es all pole
            
    # Non-windowed LPC
    else:
        coefs = librosa.lpc(x, order=order)
        error = sps.lfilter(coefs, [1], x) # El filtro del error es all pole

    return np.array(coefs), np.array(error)

def LPC_rebuild(error_signal, coefs):
    """
    Rebuilds signal from LPC error filter coefficients, and error signal.
    """
    return sps.lfilter([1], coefs, error_signal)


# Originally PSOLA2
def psola(sample, peaks, scale):
    new_signal = np.zeros(int(len(sample)*scale)+10)
    overlap = 0.5

    for x in range(len(peaks)-1):
        period = peaks[x+1] - peaks[x]
        new_period = int(period * scale)
        z = int(peaks[x] * scale)

        hwindow = np.hamming(int(period + overlap*period*2))
        i = 0
        u = -int(period*overlap)
        for y in range(peaks[x]-int(period*overlap), peaks[x]):
            if z+u > 0 and z+u < len(new_signal):
                new_signal[z+u] += sample[y] * hwindow[i]
                i += 1
                u += 1

        u = 0
        for y in range(peaks[x], peaks[x]+period):
            if z+u > 0 and z+u < len(new_signal):
                new_signal[z+u] += sample[y] * hwindow[i]
                i += 1
                u += 1

        #overlap
        u = int(peaks[x]+period)
        for y in range(peaks[x]+period, peaks[x]+int(period*overlap)):
            if z+u > 0 and z+u < len(new_signal):
                new_signal[z+u] += sample[y] * hwindow[i]
                i += 1
                u += 1
    return new_signal


def get_pitch_marks(sample):
    peaks, _ = sps.find_peaks(sample)
    return peaks