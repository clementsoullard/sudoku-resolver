import midiprocessor as midip
import guessnote as guessnote
from importlib import reload 
reload(midip)
reload(guessnote)

#
# This build a machine learning dataset
# 
def buildLearningDataset(radicalFileName):
    Y=midip.buildY('midicontent/'+radicalFileName+'.mid')
    X=guessnote.prepareInputX('wavcontent/'+radicalFileName+'.wav',tolerance=1/40,attenuationfloordb=-5)
    X=X-X.min()
    X=X/X.max()
    
    ymaxindex=np.max(np.where(Y.sum(axis=0)>0))
    xmaxindex=np.max(np.where(X.sum(axis=0)>0))
    
    if ymaxindex>xmaxindex:   
        print(X.shape,Y.shape,xmaxindex)
        Y=Y[:,:xmaxindex]
        X=X[:,:xmaxindex]
        print(X.shape,Y.shape,xmaxindex)
    else:
        Y=Y[:,:ymaxindex]
        X=X[:,:ymaxindex]
    
    np.save("learningdataset/"+radicalFileName+"Y.npy",Y)
    np.save("learningdataset/"+radicalFileName+"X.npy",X)