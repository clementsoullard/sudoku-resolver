# This Library takes wave file and serializes it recognition formatsit as an array. 
from scipy.io import wavfile # get the api
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import gaussian
from scipy.signal.windows import tukey
import os
import scipy.signal as signal
from math import log2
from math import pow

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import square, ShortTimeFFT

# Constants
# The scale of note
notescale=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
# The log2 increment of a semi-tone log2(2)/12= 1/12
increment=1/12
# The tolerant to wha we consider "in-tune" (a little less than a quarter of a tone)
tolerance=1/30
# The log2 representation of the A440 that is used as reference for our scale.
alog=log2(440)
#The bin boundary in frequency for each tone
bornes=[]

notes=[]

# This takes as an input a filename of a wav file and 
def serialize(filename):
    fs,y = wavfile.read(filename) # load the data
    y=y.T[0]*1000
    FFT_WINDOW_SECONDS = 1/2 # how many seconds of audio make up an FFT window
    windowsize=int(fs*FFT_WINDOW_SECONDS)
    win = tukey(windowsize)  # symmetric Gaussian window
    SFT = ShortTimeFFT(win, hop=fs//10, fs=fs,  scale_to='psd')
    Sx2 = SFT.spectrogram(y)
    x=[i/10 for i in range (len(y)*10//fs)]
    Sx_dB = 10 * np.log10(np.fmax(Sx2, 1e-5))  # limit range to -40 dB

# Initialize the gloabl var that will be used to convert vibrating frequencies into a note. 
def buildScale():
    # This create some bins for a scale with for each note a lower bound and an upper bound. 
    # construction all notes fundamental frequency interval above A3
    # you can compupte the span above A in octave with the formula
    # (range - distance to above C) /2   ==> 39-3 / 12 = 3
    for i in range(39):
        lowerbound=pow(2,alog+increment*i-tolerance)
        upperbound=pow(2,alog+increment*i+tolerance)
        bornes.extend([lowerbound,upperbound])
    bornes.extend([upperbound])
    # construction all notes fundamental frequency interval below A3
    # you can compupte the span below A in octave with the formula
    # (range - distance to below C) /2   ==> 46 - 10 / 2
    for i in range(1,46):
        lowerbound=pow(2,alog-increment*i-tolerance)
        upperbound=pow(2,alog-increment*i+tolerance)
        bornes.extend([lowerbound,upperbound])
    
    bornes.extend([0])
    bornes.sort()
    
    keyboard=["Out of bound lower"]
    for i in range (0,7):
        for j in notescale:
            notename=j+str(i)
            keyboard.append(notename)
    keyboard.append("Outbound upper")