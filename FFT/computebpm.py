from scipy.io import wavfile # get the api
from scipy.signal  import decimate
import numpy as np
from scipy.signal import butter
from scipy import signal
from scipy.interpolate import CubicSpline
from scipy.io.wavfile import write

# Retourne les index des franchissements de la ligne de flottaison
def getFranchissements(audio,SAMPLING_FREQUENCY,percentileflottaison=85,convolutioninsec=.1,NBSECFLOTTAISON=15):
    audio1=audio.astype(float)
    audio1=audio1/np.max(audio1)
    audio1=audio1*audio1
    #Calcul de la convolution (mouyenne mobile)
    AVGMEAN_WINDOWSIZE=int(SAMPLING_FREQUENCY*convolutioninsec)
    convolute=np.sqrt(np.convolve(audio1,np.ones(AVGMEAN_WINDOWSIZE)/AVGMEAN_WINDOWSIZE,mode='same'))
    # Calcule de la spline de frontière beat
    # La moyenne mobile est calculée sur un nombre de seconde
    # durée de la moyenne pour la ligne de flotasons
    WINDOWSIZEINNBSAMPLE=int(SAMPLING_FREQUENCY*NBSECFLOTTAISON)
    N=len(convolute)
    print("Fenêtre d'échantillon pour la spline de flottaison",WINDOWSIZEINNBSAMPLE)
    begin=0
    seveper=np.zeros((2,N//WINDOWSIZEINNBSAMPLE+1))
    for i in range(WINDOWSIZEINNBSAMPLE,N,WINDOWSIZEINNBSAMPLE):
        sample=convolute[begin:i]
        y=np.percentile(sample,percentileflottaison)
        index=i//WINDOWSIZEINNBSAMPLE
        xi=(begin+i)/2/SAMPLING_FREQUENCY
        seveper[0,index]=xi
        seveper[1,index]=y
        begin=i
    #Interfpolation de la ligne de flottaison en spline
    x=[i/SAMPLING_FREQUENCY for i in range(len(audio1))]
    spl = CubicSpline(seveper[0],seveper[1])
    sply=spl(x)
    # Detection des fanchissement de la ligne de flottaison
    convolute=convolute>sply
    # detection positif de la ligne de flottaison
    diffpatt=np.array([1,-1])
    diff=np.convolve(convolute,diffpatt,mode="valid")
    indexes=np.where(diff==1)
    return indexes
    
# Apply a low pass filter
def applyFilter(audio,SAMPLING_FREQUENCY,lowcut=100):
    sos = butter(6, lowcut, 'low', fs=SAMPLING_FREQUENCY, output='sos')
    audio = signal.sosfilt(sos, audio)
    return audio
    
# Return the estimated BPM for the file.
def computebpm(wavpath,percentileflottaison=85):
    SAMPLING_FREQUENCY, data = wavfile.read(wavpath) # load the sampling rate and the audio data
    DECIMATION_FACTOR=5
    audio = data.T[0] # this is a two channel soundtrack, get the first track
    audio=decimate(audio,DECIMATION_FACTOR)
    print("Max audio avant filtre",np.max(audio))
    audio = applyFilter(audio,SAMPLING_FREQUENCY)
    print("Max audio après filtre",np.max(audio))
    SAMPLING_FREQUENCY=SAMPLING_FREQUENCY//5
    print("Frequence d'échantillonage",SAMPLING_FREQUENCY)
    print("Nombre de sample",len(audio))
    indexes=getFranchissements(audio,SAMPLING_FREQUENCY,percentileflottaison)
    invdiffsp=getSpaces(indexes[0])
    bins=np.histogram(invdiffsp,bins=50,range=[10,220])
    min=bins[1][np.argmax(bins[0])]
    max=bins[1][np.argmax(bins[0])+1]
    print("Bpm",np.mean(invdiffsp[(invdiffsp>min) & (invdiffsp<max)])*2)

# Return the spaces between indexes.
def getSpaces(indexes,SAMPLING_FREQUENCY):
    print("Nombre de points de franchissement positif de la ligne de flottaison",len(indexes))   
    diffpatt=np.array([1,-1])
    diffsp=np.convolve(indexes,diffpatt,mode="valid")/SAMPLING_FREQUENCY
    # Conversion en bpm des intervalles
    invdiffsp=60/diffsp
    return diffsp
    
# Add some bip in the file
def addBip(originalaudio,ORIGINAL_SAMPLING_FREQUENCY,bippos,destfilename):
    biplength=ORIGINAL_SAMPLING_FREQUENCY//10
    x=np.array([i/ORIGINAL_SAMPLING_FREQUENCY for i in range(biplength)])
    y=np.sin((x*440*2*np.pi))
    ii16 = np.iinfo(np.int16)
    y=(y*.7*ii16.max).astype(np.int16)
    for i in bippos:
        audiosample=originalaudio[i:i+biplength]
        audiosample=(audiosample//2+y//2)
        originalaudio[i:i+biplength]=audiosample
    write(destfilename, ORIGINAL_SAMPLING_FREQUENCY,originalaudio.astype(np.int16))



    

