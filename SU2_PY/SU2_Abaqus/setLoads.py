#!/usr/bin/env python

## \file setLoads.py
#  \brief Reader for nodes forces
#  \authors Vittorio Cavalieri, Nicola Fonzi
#  \version 7.3.1 "Blackbird"
#
# SU2 Project Website: https://su2code.github.io
#
# The SU2 Project is maintained by the SU2 Foundation
# (http://su2foundation.org)
#
# Copyright 2012-2022, SU2 Contributors (cf. AUTHORS.md)
#
# SU2 is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# SU2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with SU2. If not, see <http://www.gnu.org/licenses/>.

from SU2_Abaqus.abaqus_modules import *
import pickle
import json
import numpy as np
from FSI_tools.FSI_utils import Point

def setLoads(modelName,partName,setName,span,dim,time,actLoad,sliderAngle,inputPointX,inputPointY,inputPointZ,iStepForce,iStepFSI):

    pathName = '{}.cae'.format(modelName)
    openMdb(pathName=pathName)
    myModel = mdb.models[modelName]
    myPart = myModel.parts[partName]
    myAssembly = myModel.rootAssembly
    stepName = 'Step-{}-{}'.format(iStepForce,iStepFSI)
	
    if sliderAngle != 0.:
      loadname_dummy = 'dummy_load'

    node = pickle.load(open('node.p', 'rb'))
    nodeList = pickle.load(open('nodeList.p', 'rb'))
    dict_force = json.load(open('Force.txt'))
    for iPoint in nodeList:
      key = str(iPoint).decode("utf-8")
      fx, fy, fz = dict_force[key]
      node[iPoint].SetForce((fx, fy, fz))
    pickle.dump(node, open('node.p', 'wb'))


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

    loadname = 'ActLoad'
    if iStepFSI == 0:
      force_unit_length = time * actLoad
      if iStepForce == 1:
        region = myAssembly.instances[partName+'-1'].surfaces[setName]
        myModel.ShellEdgeLoad(name=loadname, createStepName=stepName, 
          region=region, magnitude=force_unit_length, directionVector=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)), 
          distributionType=UNIFORM, field='', localCsys=localCsys, 
          traction=GENERAL, follower=OFF, resultant=ON)
      elif iStepForce > 1:
        myModel.loads[loadname].setValuesInStep(stepName=stepName, magnitude=force_unit_length)

    for iPoint in nodeList:
      Force = node[iPoint].GetForce()
      if dim == 2:
        Force = Force * span
      label = node[iPoint].GetID()
      name = 'NODE-'+str(label)
      if name in myAssembly.instances[partName+'-1'].sets.keys():	# migliorare criterio
		region = myAssembly.instances[partName+'-1'].sets[name]
      else:
        region = myAssembly.sets[name]
      loadname = 'Load-{}'.format(label)
      if iStepFSI == 0 and iStepForce == 0:
        myModel.ConcentratedForce(name=loadname, createStepName=stepName, 
          region=region, cf1=float(Force[0]), cf2=float(Force[1]), cf3=float(Force[2]), distributionType=UNIFORM, 
          field='', localCsys=None)
      else:
        myModel.loads[loadname].setValuesInStep(stepName=stepName, cf1=float(Force[0]), cf2=float(Force[1]), cf3=float(Force[2]))


    pathName = '{}.cae'.format(modelName)
    mdb.saveAs(pathName=pathName)

if __name__ == "__main__":
    modelName = sys.argv[-13]
    partName = sys.argv[-12]
    setName = sys.argv[-11]
    span = float(sys.argv[-10])
    dim = int(sys.argv[-9])
    time = float(sys.argv[-8])
    actLoad = float(sys.argv[-7])
    sliderAngle = float(sys.argv[-6])
    inputPointX = float(sys.argv[-5])
    inputPointY = float(sys.argv[-4])
    inputPointZ = float(sys.argv[-3])
    iStepForce = int(sys.argv[-2])
    iStepFSI = int(sys.argv[-1])
    setLoads(modelName,partName,setName,span,dim,time,actLoad,sliderAngle,inputPointX,inputPointY,inputPointZ,iStepForce,iStepFSI)