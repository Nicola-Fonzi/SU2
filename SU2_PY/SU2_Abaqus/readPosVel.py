from abaqus_modules import *
import pickle
from FSI_tools.FSI_utils import Point

def readPosVel(partName,iStepForce,iStepFSI,initialize):

    if initialize:
      odb = None
    else:
      odbFile = 'Job-{}-{}.odb'.format(iStepForce,iStepFSI)
      odb = openOdb(path=odbFile)
      stepName = 'Step-{}-{}'.format(iStepForce,iStepFSI)
      lastFrame = odb.steps[stepName].frames[-1]
      displacement = lastFrame.fieldOutputs['U']
      
    node = pickle.load(open('node.p','rb'))
    nPoint = len(node)
    
    for iPoint in range(nPoint):
      coord0 = node[iPoint].GetCoord0()
      if odb:
        label = node[iPoint].GetID()
        region = odb.rootAssembly.instances[partName+'-1'].nodeSets['NODE-'+str(label)]
        v = displacement.getSubset(region=region).values[0]
        X_disp = v.data[0]
        Y_disp = v.data[1]
        Z_disp = v.data[2]
      else:
        X_disp = 0
        Y_disp = 0
        Z_disp = 0
      X_vel = 0		# Static analysis
      Y_vel = 0		# Static analysis
      Z_vel = 0		# Static analysis
      node[iPoint].SetCoord((X_disp+coord0[0],Y_disp+coord0[1],Z_disp+coord0[2]))
      node[iPoint].SetVel((X_vel,Y_vel,Z_vel))

      if initialize:
        node[iPoint].SetCoord_n((X_disp+coord0[0],Y_disp+coord0[1],Z_disp+coord0[2]))
        node[iPoint].SetVel_n((X_vel,Y_vel,Z_vel))
    
	pickle.dump(node, open('node.p','wb'))


if __name__ == "__main__":
    partName = sys.argv[-4]
    iStepForce = int(sys.argv[-3])
    iStepFSI = int(sys.argv[-2])
    if sys.argv[-1] == 'True':
      initialize = True
    elif sys.argv[-1] == 'False':
      initialize = False
    else:
      raise Exception('error')	# TODO
    readPosVel(partName,iStepForce,iStepFSI,initialize)