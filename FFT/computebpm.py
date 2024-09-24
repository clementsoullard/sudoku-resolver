from scipy.io import wavfile # get the api
from scipy.signal  import decimate
import numpy as np
from scipy.signal import butter
from scipy import signal
from scipy.interpolate import CubicSpline



# Return the estimated BPM for the file.
def computebpm(wavpath,percentileflottaison=85):
    SAMPLING_FREQUENCY, data = wavfile.read(wavpath) # load the sampling rate and the audio data
    DECIMATION_FACTOR=5
    audio = data.T[0] # this is a two channel soundtrack, get the first track
    audio=decimate(audio,DECIMATION_FACTOR)
    print("Max audio avant filtre",np.max(audio))
    sos = butter(2, 100, 'low', fs=SAMPLING_FREQUENCY, output='sos')
    audio = signal.sosfilt(sos, audio)
    print("Max audio après filtre",np.max(audio))
    SAMPLING_FREQUENCY=SAMPLING_FREQUENCY//5
    print("Frequence d'échantillonage",SAMPLING_FREQUENCY)
    print("Nombre de sample",len(audio))
    #Calcul de la convolution (mouyenne mobile)
    AVGMEAN_WINDOWSIZE=SAMPLING_FREQUENCY//5
    totfft=np.zeros(len(audio))
    audio1=audio.astype(float)
    audio1=audio1/np.max(audio1)
    audio1=audio1*audio1
    convolute=np.sqrt(np.convolve(audio1,np.ones(AVGMEAN_WINDOWSIZE)/AVGMEAN_WINDOWSIZE,mode='same'))
    # Calcule de la spline de frontière beat
    # La moyenne mobile est calculée sur un nombre de seconde
    # durée de la moyenne pour la ligne de flotasons
    NBSECFLOTTAISON=15
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
    print("Nombre de points de franchissement positif de la ligne de flottaison",len(indexes[0]))
    diffsp=np.convolve(indexes[0],diffpatt,mode="valid")/SAMPLING_FREQUENCY
    # Conversion en bpm des intervalles
    invdiffsp=60/diffsp
    bins=np.histogram(invdiffsp,bins=50,range=[10,220])
    min=bins[1][np.argmax(bins[0])]
    max=bins[1][np.argmax(bins[0])+1]
    print("Bpm",np.mean(invdiffsp[(invdiffsp>min) & (invdiffsp<max)])*2)
    

