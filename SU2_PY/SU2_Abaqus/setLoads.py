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
# Copyright 2012-2023, SU2 Contributors (cf. AUTHORS.md)
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

def setLoads(modelName,device,flexPartName,rigidPartName,actSetName,span,dim,time,actType,actLoad0,actLoad,sliderAngle,stroke,inputPointX,inputPointY,inputPointZ,iStepForce,iStepFSI):

    pathName = '{}.cae'.format(modelName)
    openMdb(pathName=pathName)
    myModel = mdb.models[modelName]
    myFlexPart = myModel.parts[flexPartName]
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


    if device == 'TE' and sliderAngle != 0. and iStepForce == 0 and iStepFSI == 0:
      input_point_skin = np.array([inputPointX,inputPointY,inputPointZ])
      csys_point1 = input_point_skin + [cos(sliderAngle), sin(sliderAngle), 0]
      csys_point2 = input_point_skin + [-sin(sliderAngle), cos(sliderAngle), 0]
      myFlexPart.DatumCsysByThreePoints(name='Datum csys-1', coordSysType=CARTESIAN, 
        origin=input_point_skin, point1=csys_point1, point2=csys_point2)
      keys = myAssembly.datums.keys()
      for key in keys:
        if myAssembly.datums[key].axis1.direction[0] < 1.0:
          localCsys = myAssembly.datums[key]
          break
      region = myAssembly.instances[flexPartName+'-1'].surfaces[actSetName]
      if actType == 'FORCE':
        force_unit_length = 0.000001
        myModel.ShellEdgeLoad(name=loadname_dummy, createStepName=stepName, 
          region=region, magnitude=force_unit_length, directionVector=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)), 
          distributionType=UNIFORM, field='', localCsys=localCsys, 
          traction=GENERAL, follower=OFF, resultant=ON)

    if device == 'TE':
      localCsys = None
      if sliderAngle != 0. and iStepForce > 0 and iStepFSI == 0:
        keys = myAssembly.datums.keys()
        for key in keys:
          if myAssembly.datums[key].axis1.direction[0] < 1.0:
            localCsys = myAssembly.datums[key]

    if iStepForce == 1 and iStepFSI == 0:
      for bc in myModel.boundaryConditions.values():
        if bc.region[0] == actSetName:		# improve?
          bc.deactivate(stepName)
      if device == 'TE':
        region = myAssembly.instances[flexPartName+'-1'].sets[actSetName]
        myModel.DisplacementBC(name='slider', createStepName=stepName, 
          region=region, u1=UNSET, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0, 
          amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
          localCsys=localCsys)
      if actType == 'FORCE' and sliderAngle != 0.:
          myModel.loads[loadname_dummy].deactivate(stepName)

    if iStepForce > 0:
      if device == 'TE':
        loadname = 'ActLoad'
        if iStepFSI == 0:
            if actType == 'FORCE':
              force = (actLoad0 + time * (actLoad - actLoad0))
              force_unit_length = force / span
              if iStepForce == 1:
                region = myAssembly.instances[flexPartName+'-1'].surfaces[actSetName]
                myModel.ShellEdgeLoad(name=loadname, createStepName=stepName, 
                  region=region, magnitude=force_unit_length, directionVector=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)), 
                  distributionType=UNIFORM, field='', localCsys=localCsys, 
                  traction=GENERAL, follower=OFF, resultant=ON)
              elif iStepForce > 1:
                myModel.loads[loadname].setValuesInStep(stepName=stepName, magnitude=force_unit_length)
              with open(fname, 'w') as f:
                f.write(str(force))
                fname = 'AF_{}.txt'.format(iStepForce)
            if actType == 'DISPLACEMENT':
              displ = time * stroke
              if iStepForce == 1:
                region = myAssembly.instances[flexPartName+'-1'].sets[actSetName]
                myModel.DisplacementBC(name=loadname, createStepName=stepName, 
                  region=region, u1=displ, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
                  amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
                  localCsys=localCsys)
              if iStepForce > 1:
                myModel.boundaryConditions[loadname].setValuesInStep(stepName=stepName, u1=displ)
      elif device == 'LE':
        name = 'ActRot'
        if iStepFSI == 0:
          rot = (actLoad0 + time * (actLoad - actLoad0))
          if iStepForce == 1:
            for bc in myModel.boundaryConditions.values():
              if bc.region[0] == actSetName:		# improve?
                key = bc.localCsys
            region = myAssembly.sets[actSetName]
            localCsys = myAssembly.datums[key]
            myModel.DisplacementBC(name=name, createStepName=stepName, 
                region=region, u1=0.0, u2=0.0, u3=0.0, ur1=rot, ur2=0.0, ur3=0.0, 
                amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
                localCsys=localCsys)
          elif iStepForce > 1:
            myModel.boundaryConditions[name].setValuesInStep(stepName=stepName, ur1=rot)

    for iPoint in nodeList:
      Force = node[iPoint].GetForce()
      if dim == 2:
        Force = Force * span
      label = node[iPoint].GetID()
      loadname = 'Load-{}'.format(label)
      if iStepFSI == 0 and iStepForce == 0:
        name = 'NODE-'+str(label)
        if label < 100000:
          if name in myAssembly.instances[flexPartName+'-1'].sets.keys():	# improve?
		    region = myAssembly.instances[flexPartName+'-1'].sets[name]
          else:
            region = myAssembly.sets[name]
        else:
          region = myAssembly.instances[rigidPartName+'-1'].sets[name]
        myModel.ConcentratedForce(name=loadname, createStepName=stepName, 
          region=region, cf1=float(Force[0]), cf2=float(Force[1]), cf3=float(Force[2]), distributionType=UNIFORM, 
          field='', localCsys=None)
      else:
        myModel.loads[loadname].setValuesInStep(stepName=stepName, cf1=float(Force[0]), cf2=float(Force[1]), cf3=float(Force[2]))


    pathName = '{}.cae'.format(modelName)
    mdb.saveAs(pathName=pathName)

if __name__ == "__main__":
    modelName = sys.argv[-18]
    device = sys.argv[-17]
    flexPartName = sys.argv[-16]
    rigidPartName = sys.argv[-15]
    actSetName = sys.argv[-14]
    span = float(sys.argv[-13])
    dim = int(sys.argv[-12])
    time = float(sys.argv[-11])
    actType = sys.argv[-10]
    actLoad0 = float(sys.argv[-9])
    actLoad = float(sys.argv[-8])
    sliderAngle = float(sys.argv[-7])
    stroke = float(sys.argv[-6])
    inputPointX = float(sys.argv[-5])
    inputPointY = float(sys.argv[-4])
    inputPointZ = float(sys.argv[-3])
    iStepForce = int(sys.argv[-2])
    iStepFSI = int(sys.argv[-1])
    setLoads(modelName,device,flexPartName,rigidPartName,actSetName,span,dim,time,actType,actLoad0,actLoad,sliderAngle,stroke,inputPointX,inputPointY,inputPointZ,iStepForce,iStepFSI)