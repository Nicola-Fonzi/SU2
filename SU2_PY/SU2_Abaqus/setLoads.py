from pysu2_utils import *
from abaqus_modules import *
import pickle
import numpy as np

def setLoads(modelName,partName,setName,time,Fx,Fy,Fz,iStepForce,iStepFSI):

    pathName = '{}.cae'.format(modelName)
    openMdb(pathName=pathName)
    myModel = mdb.models[modelName]
    stepName = 'Step-{}-{}'.format(iStepForce,iStepFSI)

    node = pickle.load(open('node.p','rb'))
    nodeList = pickle.load(open('nodeList.p','rb'))
    f = open("debug.txt", "w")
    f.write('{}\n'.format(len(nodeList)))

    if iStepFSI > 0 or iStepForce > 0:
      previous = myModel.steps.keys()[-2]
      for iPoint in nodeList:
        label = node[iPoint].GetID()
        loadname = 'Load-{}-{}'.format(label,previous.split('-',1)[-1])	# invertire?
        if loadname in myModel.loads.keys():
          myModel.loads[loadname].deactivate(stepName)	# necessario perche devo cambiare step??

    if iStepForce == 1 and iStepFSI == 0:
      for bc in myModel.boundaryConditions.values():
        if bc.region[0] == 'SLIDER':		# HC
          bc.deactivate(stepName)
      region = myModel.rootAssembly.instances[partName+'-1'].sets['SLIDER']		# HC
      myModel.DisplacementBC(name='slider', createStepName=stepName, 
        region=region, u1=UNSET, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0, 
        amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
        localCsys=None)

    if iStepForce > 0 and iStepFSI == 0:
      ActForce = time * np.array([Fx,Fy,Fz])
      region = myModel.rootAssembly.instances[partName+'-1'].sets[setName]
      loadname = 'ActForce-{}'.format(iStepForce)
      myModel.ConcentratedForce(name=loadname, createStepName=stepName, 
        region=region, cf1=float(ActForce[0]), cf2=float(ActForce[1]), cf3=float(ActForce[2]), distributionType=UNIFORM, 
        field='', localCsys=None)
    if iStepForce > 1 and iStepFSI == 0:
      loadname = 'ActForce-{}'.format(iStepForce-1)
      myModel.loads[loadname].deactivate(stepName)

    for iPoint in nodeList:
      Force = node[iPoint].GetForce()
      f.write('{} {} {}\n'.format(Force[0],Force[1],Force[2]))
      if np.any(Force):
        label = node[iPoint].GetID()
        region = myModel.rootAssembly.instances[partName+'-1'].sets['NODE-'+str(label)]
        f.write('Before creating ConcentratedForce\n')
        loadname = 'Load-{}-{}-{}'.format(label,iStepForce,iStepFSI)		# invertire?
        myModel.ConcentratedForce(name=loadname, createStepName=stepName, 
          region=region, cf1=float(Force[0]), cf2=float(Force[1]), cf3=float(Force[2]), distributionType=UNIFORM, 
          field='', localCsys=None)

    f.close()
    pathName = '{}.cae'.format(modelName)
    mdb.saveAs(pathName=pathName)

if __name__ == "__main__":
    modelName = sys.argv[-9]
    partName = sys.argv[-8]
    setName = sys.argv[-7]
    time = float(sys.argv[-6])
    Fx = float(sys.argv[-5])
    Fy = float(sys.argv[-4])
    Fz = float(sys.argv[-3])
    iStepForce = int(sys.argv[-2])
    iStepFSI = int(sys.argv[-1])
    setLoads(modelName,partName,setName,time,Fx,Fy,Fz,iStepForce,iStepFSI)