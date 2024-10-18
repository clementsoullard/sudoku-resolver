from mido import tempo2bpm
import numpy as np
from mido import MidiFile

def convertMidiFile(filename,targetfilename):
    #targetfilename=filename.replace('.mid','Y.npy')    
    Y=buildY(filename)
    np.save(targetfilename,Y)
    

#This transforms a midi file to an Y representation
def buildY(filename,maxdurationinsec=300,intervalsampling=.1):
    mid = MidiFile(filename)
    currentTempo=500000
    tickPerBeat=mid.ticks_per_beat
    notes=np.zeros((102),np.int32)
    # An array to store notes from 0 to 60 s 
    Y=np.zeros((102,int(maxdurationinsec/intervalsampling)),np.int32)
    
    lastIndexTime=0

    for i, track in enumerate(mid.tracks):
        time=0
        print('Track {}: {}'.format(i, track.name))
        totalticks=0
        for msg in track:
            note=-1
            if not msg.is_meta:
                if msg.type=='note_on':
                    #print("note_on")
                    totalticks=totalticks+msg.time
                    # La note est ajoutée que si la batterie (canal 9 n'est pas concerné)
                    if msg.channel!=9:
                        if msg.velocity==0:
                            note=msg.note
                            notes[note]=0
                        else:
                            note=msg.note
                            notes[note]=1
            elif msg.type=='time_signature':
                print(msg)
            elif msg.type=='set_tempo':
                currentTempo=msg.tempo
                #print(totalticks,msg)
            time=time+msg.time*currentTempo/tickPerBeat
            #print(time)
            indextime=int(time*10//1000000)
            #print(indextime)
            #print("saut",indextime-lastIndexTime)
            if note>-1:
                #print("Note")
                Y[note,indextime]=1
            if (indextime-lastIndexTime)>1:
                #print("saut de",lastIndexTime,"à",indextime)
                for i in range(lastIndexTime+1,indextime):
                    #print("copie de", i-1,"vers",i)
                    Y[:,i]=Y[:,i-1]
                
            lastIndexTime=indextime
    return Y