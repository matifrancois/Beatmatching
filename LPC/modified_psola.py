import librosa 
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from math import ceil

class pitch_centered_segment:
    def __init__(self, P , t , samples_windowed):
        self.pitch = P
        self.t = t
        self.samples_windowed = samples_windowed

def plot_peaks(x,peaks):
    plt.plot(x)
    plt.plot(peaks, x[peaks], "x")
    plt.plot(np.zeros_like(x), "--", color="gray")
    plt.show()

def modified_psola(x,pitch_samples, speed):
    total_time = len(x)
    total_new_time = ceil(total_time*(1/speed))
    new_audio = np.zeros(total_new_time)
    peaks, _ = find_peaks(x, height=0, distance = pitch_samples-int(0.16*pitch_samples))
    #plot_peaks(x,peaks) # debugging
    w = np.hamming(2*pitch_samples+1)
    
    pitch_centered = []

    for i,peak in enumerate(peaks):
        if peak-pitch_samples>=0 and peak+pitch_samples <= len(x) - 1: 
            samples_windowed = x[peak-pitch_samples:peak+pitch_samples+1]*w
            pitch_centered.append(pitch_centered_segment(pitch_samples, peak, samples_windowed))
   
    
    pitch_centered_modified = []
    for i, centered in enumerate(pitch_centered):
        if speed >= 1:    # funciona bien para x1,x2,x4, falta agregar lo demas
            num, den = speed.as_integer_ratio()
            if den > i%num:
                pitch_centered_modified.append(pitch_centered[i])

    for i, centered in enumerate(pitch_centered_modified):
        t_ = ceil(centered.t * (1/speed))
        if t_-pitch_samples>=0 and t_+pitch_samples <= len(new_audio) - 1: 
            new_audio[t_-pitch_samples:t_+pitch_samples+1] += centered.samples_windowed
    return new_audio