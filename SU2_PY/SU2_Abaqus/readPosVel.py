#!/usr/bin/env python

## \file readPosVel.py
#  \brief Reader for nodes positions
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
from FSI_tools.FSI_utils import Point

def readPosVel(partName,iStepForce,iStepFSI):

    odbFile = 'Job-{}-{}.odb'.format(iStepForce,iStepFSI)
    odb = openOdb(path=odbFile)
    stepName = 'Step-{}-{}'.format(iStepForce,iStepFSI)
    lastFrame = odb.steps[stepName].frames[-1]
    displacement = lastFrame.fieldOutputs['U']
    
    node = pickle.load(open('node.p', 'rb'))
    nPoint = len(node)
    
    for iPoint in range(nPoint):
      coord0 = node[iPoint].GetCoord0()
      label = node[iPoint].GetID()
      region = odb.rootAssembly.instances[partName+'-1'].nodeSets['NODE-'+str(label)]
      v = displacement.getSubset(region=region).values[0]
      X_disp = v.data[0]
      Y_disp = v.data[1]
      Z_disp = v.data[2]

      X_vel = 0		# Static analysis
      Y_vel = 0		# Static analysis
      Z_vel = 0		# Static analysis
      node[iPoint].SetCoord((X_disp+coord0[0],Y_disp+coord0[1],Z_disp+coord0[2]))
      node[iPoint].SetVel((X_vel,Y_vel,Z_vel))
    
    pickle.dump(node, open('node.p', 'wb'))


if __name__ == "__main__":
    partName = sys.argv[-3]
    iStepForce = int(sys.argv[-2])
    iStepFSI = int(sys.argv[-1])
    readPosVel(partName,iStepForce,iStepFSI)