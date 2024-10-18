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
import re

import time



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

    

# Converts a Wav file to its note rpresentation as a mapfreq2note format
# This takes as an input 
# - a filename of a wav file  
# - The tolerance to what we consider "in-tune" (a little less than a quarter of a tone)
# - attenuationfloordb the power to consider as floor for noise expressed in Bel
def serialize(filename,targetfilename,tolerance,attenuationfloordb=-5):
    X=prepareInputX(filename,tolerance,attenuationfloordb=attenuationfloordb)
    np.save(targetfilename,X);
    print("End of serialization",targetfilename)
    print("Fichier de Wav",filename,"convertit en représentation npy",targetfilename)
    
# Return the Spectrogram and the SFT
# FFT_WINDOW_SECONDS = duration of the window for SFT analysis
def getSFFT(filename,attenuationfloordb,FFT_WINDOW_SECONDS = 1):
    fs,y = wavfile.read(filename) # load the data
    # In stereo case we only consider first channel
    if len(y.shape)>1:
        y=y.T[0]
    y=y/np.max(y)*2
    # how many seconds of audio make up an FFT window
    #windowsize=int(fs*FFT_WINDOW_SECONDS)
  #  win = tukey(windowsize)  # symmetric Gaussian window
    stackSx=[]
    freqs=[]
    #for i in [8.662,8.1658,9.177,9.723,15.4439]:
    for i in [16.3516,17.3239,18.3540,19.4454,30.8677]:
        #win=np.ones(int(fs/i))
        win=tukey(int(fs/i))
        SFT = ShortTimeFFT(win, hop=fs//10, fs=fs,  scale_to='psd')
        starttime= time.time()
        Sx2 = SFT.spectrogram(y)
        print('Spectro',time.time()-starttime)
        stackSx.append(Sx2)
        freqs.append(SFT.f)
    Sxstack=np.concatenate(stackSx)
    freqs=np.concatenate(freqs)
    # print('max Sx2',np.max(Sx2))
    #x=[i/10 for i in range (len(y)*10//fs)]
    Sx_dB = 10 * np.log10(np.fmax(Sxstack, pow(10,attenuationfloordb)))  # limit range to -40 dB   
    return freqs,Sx_dB


# Create the X file the file to feed the neural network
# the X format is the following 
# i is the frequencynote axis (axis=0) 
# j is the time axis (axis=0) 
# The frequencynote on line 0 gather the frequencies below zero
# The even i are the note gatethering frequencies inside the tolerance
# The uneven i are the frequencies between two notes and not inside the tolerance interval
def prepareInputX(filename,tolerance,attenuationfloordb=-5):
    getKeyboard()
    starttime= time.time()
    freqs, Sx_dB = getSFFT(filename,attenuationfloordb=attenuationfloordb)
    print('Fin d''analyse SFFTT',time.time()-starttime)
    bornes=buildScale(tolerance)
    starttime= time.time()
    X=mapFreq2Note(freqs,Sx_dB,bornes)
    print('Fin Map to note',time.time()-starttime)
    return X

    
# Map the SFFT result to the notes 
# The resulting matrix contains now some notes (not frequencies)
def mapFreq2Note(freqs,Sx_dB,bornes):
    inv_map = getMapFreq2Note(freqs,bornes)   
    # Nous prenons l'analyse FFT et la convertissons en une analyse note.
    # Construction du X qui servira à l'apprentissage profond.    
    notetable=np.full((len(bornes)+1,Sx_dB.shape[1]),-50.)
    # On parcours tous les instants du spectrogramme.
    for i in range(Sx_dB.shape[1]):
        #Pour chaque bin de fréquence (note ou intervalle entre note) nous aggrégeons sur la puissance maximale de de fréquence
        for k,v in inv_map.items():
            if len(v)>0:
                notetable[k,i]=np.max(Sx_dB[v,i])    
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
   # bornes.extend([-1])
    bornes.sort()
    return bornes
    
# The keyboard is the list of name of note indexed in the right order 
def getKeyboard():
    keyboard=["Out of bound lower"]
    for i in range (0,7):
        for j in notescale:
            notename=j+str(i)
            keyboard.append(notename)
    keyboard.append("Outbound upper")
    return keyboard
    
# Return the main notes for a given note freqinnotesrepresentation. 
def getMainNotes(X):
    #Note: keyboard would be converted with benefit in a class attribute
    keyboard=getKeyboard()
    tona=X.sum(axis=1)
    tona=tona-np.min(tona)
    tona=tona/np.max(tona)
    tona=tona[range(1,len(tona),2)]
    
    convolvevect=[-.25,-.25,1,-.25,-.25]
    tonaconvolved=np.convolve(tona,convolvevect,mode='same')
    tonaconvolved=tonaconvolved.clip(min=0)
    
    binsids=np.where(tonaconvolved>.2)[0]+1
    binsids=binsids%12
    binsids=np.unique(binsids)
    print(binsids)
    #print(int(5).dtype)
    #binsids=binsids.astype(int).tolist()
    #print(binsids)
    #print(keyboard)
    mainNotes=np.unique([re.sub("[0-9]$","",keyboard[i]) for i in binsids]) 
    print(mainNotes)
    return binsids-1

#
# Return the correspondancy table beetween an note and a set of frequencies in the SFourier transform
# 
def getMapFreq2Note(freqs,bornes):
    mapnote2freq={}
    lastidx=0
    for i,freq in enumerate(bornes[:-1]):   
        indexmax=np.searchsorted(freqs,freq)
    #    print(i,SFFT.f[lastidx:indexmax])
        mapnote2freq[i]=list(range(lastidx,indexmax))
        lastidx=indexmax
    return mapnote2freq
