from abaqus_modules import *
import pickle
from FSI_tools.FSI_utils import Point

def createStep(modelName,iStepForce,iStepFSI):

    pathName = '{}.cae'.format(modelName)
    openMdb(pathName=pathName)
    
    myModel = mdb.models[modelName]
    
    stepName = 'Step-{}-{}'.format(iStepForce,iStepFSI)
    if iStepForce == 0 and iStepFSI == 0:
      #type = ANALYSIS
      myModel.StaticStep(name=stepName, previous='Initial', initialInc=0.01, nlgeom=ON)
    else:
      #type = RESTART
      previous = myModel.steps.keys()[-1]
      myModel.StaticStep(name=stepName, previous=previous, initialInc=0.01)
      restartJob = 'Job-' + previous.split('-',1)[-1]
      myModel.setValues(restartJob=restartJob, restartStep=previous)
      #myModel.steps[stepName].Restart(frequency=999, numberIntervals=0, 
      #    overlay=ON, timeMarks=OFF)
    myModel.steps[stepName].Restart(frequency=0, numberIntervals=1, 
        overlay=ON, timeMarks=OFF)
	
    pathName = '{}.cae'.format(modelName)
    mdb.saveAs(pathName=pathName)


if __name__ == "__main__":
    modelName = sys.argv[-3]
    iStepForce = int(sys.argv[-2])
    iStepFSI = int(sys.argv[-1])
    createStep(modelName,iStepForce,iStepFSI)