from abaqus_modules import *
import pickle
import numpy as np
from FSI_tools.FSI_utils import Point

def setLoads(modelName,partName,setName,time,actLoad,sliderAngle,inputPointX,inputPointY,inputPointZ,iStepForce,iStepFSI):

    pathName = '{}.cae'.format(modelName)
    openMdb(pathName=pathName)
    myModel = mdb.models[modelName]
    myPart = myModel.parts[partName]
    myAssembly = myModel.rootAssembly
    stepName = 'Step-{}-{}'.format(iStepForce,iStepFSI)
	
    if sliderAngle != 0.:
      loadname_dummy = 'dummy_load'

    node = pickle.load(open('node.p','rb'))
    nodeList = pickle.load(open('nodeList.p','rb'))

    if iStepFSI > 0 or iStepForce > 0:
      previous = myModel.steps.keys()[-2]
      for iPoint in nodeList:
        label = node[iPoint].GetID()
        loadname = 'Load-{}-{}'.format(label,previous.split('-',1)[-1])	# invertire?
        if loadname in myModel.loads.keys():
          myModel.loads[loadname].deactivate(stepName)	# necessario perche devo cambiare step??

    if sliderAngle != 0. and iStepForce == 0 and iStepFSI == 0:
      input_point_skin = np.array([inputPointX,inputPointY,inputPointZ])
      csys_point1 = input_point_skin + [cos(sliderAngle), sin(sliderAngle), 0]
      csys_point2 = input_point_skin + [-sin(sliderAngle), cos(sliderAngle), 0]
      myPart.DatumCsysByThreePoints(name='Datum csys-1', coordSysType=CARTESIAN, 
        origin=input_point_skin, point1=csys_point1, point2=csys_point2)
      keys = myAssembly.datums.keys()
      for key in keys:
        if myAssembly.datums[key].axis1.direction[0] < 1.0:
          localCsys = myAssembly.datums[key]
          break
      force_unit_length = 0.000001
      region = myAssembly.instances[partName+'-1'].surfaces[setName]
      myModel.ShellEdgeLoad(name=loadname_dummy, createStepName=stepName, 
        region=region, magnitude=force_unit_length, directionVector=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)), 
        distributionType=UNIFORM, field='', localCsys=localCsys, 
        traction=GENERAL, follower=OFF, resultant=ON)

    localCsys = None
    if sliderAngle != 0. and iStepForce > 0 and iStepFSI == 0:
      keys = myAssembly.datums.keys()
      for key in keys:
        if myAssembly.datums[key].axis1.direction[0] < 1.0:
          localCsys = myAssembly.datums[key]

    if iStepForce == 1 and iStepFSI == 0:
      for bc in myModel.boundaryConditions.values():
        if bc.region[0] == setName:		# migliorare criterio
          bc.deactivate(stepName)
      region = myAssembly.instances[partName+'-1'].sets[setName]
      myModel.DisplacementBC(name='slider', createStepName=stepName, 
        region=region, u1=UNSET, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0, 
        amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
        localCsys=localCsys)
      if sliderAngle != 0.:
        myModel.loads[loadname_dummy].deactivate(stepName)

    if iStepForce > 0 and iStepFSI == 0:
      force_unit_length = time * actLoad
      region = myAssembly.instances[partName+'-1'].surfaces[setName]
      loadname = 'ActLoad-{}'.format(iStepForce)
      myModel.ShellEdgeLoad(name=loadname, createStepName=stepName, 
        region=region, magnitude=force_unit_length, directionVector=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)), 
        distributionType=UNIFORM, field='', localCsys=localCsys, 
        traction=GENERAL, follower=OFF, resultant=ON)
    if iStepForce > 1 and iStepFSI == 0:
      loadname = 'ActLoad-{}'.format(iStepForce-1)
      myModel.loads[loadname].deactivate(stepName)

    for iPoint in nodeList:
      Force = node[iPoint].GetForce()
      if np.any(Force):
        label = node[iPoint].GetID()
        region = myAssembly.instances[partName+'-1'].sets['NODE-'+str(label)]
        loadname = 'Load-{}-{}-{}'.format(label,iStepForce,iStepFSI)		# invertire?
        myModel.ConcentratedForce(name=loadname, createStepName=stepName, 
          region=region, cf1=float(Force[0]), cf2=float(Force[1]), cf3=float(Force[2]), distributionType=UNIFORM, 
          field='', localCsys=None)

    pathName = '{}.cae'.format(modelName)
    mdb.saveAs(pathName=pathName)

if __name__ == "__main__":
    modelName = sys.argv[-11]
    partName = sys.argv[-10]
    setName = sys.argv[-9]
    time = float(sys.argv[-8])
    actLoad = float(sys.argv[-7])
    sliderAngle = float(sys.argv[-6])
    inputPointX = float(sys.argv[-5])
    inputPointY = float(sys.argv[-4])
    inputPointZ = float(sys.argv[-3])
    iStepForce = int(sys.argv[-2])
    iStepFSI = int(sys.argv[-1])
    setLoads(modelName,partName,setName,time,actLoad,sliderAngle,inputPointX,inputPointY,inputPointZ,iStepForce,iStepFSI)