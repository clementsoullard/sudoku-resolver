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
# The log2 representation of the A440 that is used as reference for our scale.
alog=log2(440)
#The bin boundary in frequency for each tone
bornes=[]

# Construction de la table mappant table vers index de note.
mapftonote={}

def mapFreq2Note(SFT):
    # Nous cherchons à mapper un fréquence de la FFT vers une note.
    mapftonote={}
    for i,f in enumerate(SFT.f):
        index=np.searchsorted(bornes,f)
        mapftonote[i]=index
    # Nous inversons la mapping pour permettre une surjection des fréquence vers une note
    inv_map = {}
    for k, v in mapftonote.items():
        inv_map[v] = inv_map.get(v, []) + [k]
    print(mapftonote)
    

# This takes as an input 
# - a filename of a wav file  
# The tolerance to what we consider "in-tune" (a little less than a quarter of a tone)
# attenuationfloordb the power to consider as floor for noise
def serialize(filename,tolerance,attenuationfloordb=-5):
    # Do not need to be computed every time, but leaving for now
    buildScale(tolerance)
    fs,y = wavfile.read(filename) # load the data
    y=y.T[0]
    y=y/np.max(y)*2
    FFT_WINDOW_SECONDS = 1/2 # how many seconds of audio make up an FFT window
    windowsize=int(fs*FFT_WINDOW_SECONDS)
    win = tukey(windowsize)  # symmetric Gaussian window
    SFT = ShortTimeFFT(win, hop=fs//10, fs=fs,  scale_to='psd')
    Sx2 = SFT.spectrogram(y)
    print('max Sx2',np.max(Sx2))
    #x=[i/10 for i in range (len(y)*10//fs)]
    Sx_dB = 10 * np.log10(np.fmax(Sx2, pow(10,attenuationfloordb)))  # limit range to -40 dB   
    print('max Sx_dB',np.max(Sx_dB))
    targetfilename=filename.replace(".wav",".npy")
    prepareInputX(SFT,Sx_dB,targetfilename)
    

# Create the X file the file to feed the neural network
def prepareInputX(SFT,Sx_dB,targetfilename):
    X=mapFreq2Note(SFT,Sx_dB)
    print("Serializing file",targetfilename)
    np.save(targetfilename,X);
    
# Map the FFT to the notes as per the construction
def mapFreq2Note(SFT,Sx_dB):
    # Construction de la table mappant table vers index de note.
    mapftonote={}
    # Nous cherchons à mapper un fréquence de la FFT vers une note.
    for i,f in enumerate(SFT.f):
        index=np.searchsorted(bornes,f)
        mapftonote[i]=index
    # Nous inversons la mapping pour permettre une surjection des fréquence vers une note
    inv_map = {}   
    for k, v in mapftonote.items():
        inv_map[v] = inv_map.get(v, []) + [k]
    # Nous prenons l'analyse FFT et la convertissons en une analyse note.
    # Construction du X qui servira à l'apprentissage profond.    
    notetable=np.full((len(bornes)+1,Sx_dB.shape[1]),-50.)
    # On parcours tous les instants du spectrogramme.
    for i in range(Sx_dB.shape[1]):
        #Pour chaque bin de fréquence (note ou intervalle entre note) nous aggrégeons sur la puissance maximale de de fréquence
        for k,v in inv_map.items():
            notetable[k,i]=np.max(Sx_dB[v,i])
    #print("inv_map",inv_map)
    return notetable

# Initialize the gloabl var that will be used to convert vibrating frequencies into a note. 
def buildScale(tolerance):
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
    #Adding the lower bound
    bornes.extend([-1])
    bornes.sort()
    
    keyboard=["Out of bound lower"]
    for i in range (0,7):
        for j in notescale:
            notename=j+str(i)
            keyboard.append(notename)
    keyboard.append("Outbound upper")