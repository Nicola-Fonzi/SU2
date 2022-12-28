#!/usr/bin/env python

## \file readReactionForce.py
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

def readReactionForce(partName,setName,iStepForce,iStepFSI):

    odbFile = 'Job-{}-{}.odb'.format(iStepForce,iStepFSI)
    odb = openOdb(path=odbFile)
    stepName = 'Step-{}-{}'.format(iStepForce,iStepFSI)
    lastFrame = odb.steps[stepName].frames[-1]
    reaction_force = lastFrame.fieldOutputs['RF']

    datumCsyses = odb.rootAssembly.datumCsyses
    keys = datumCsyses.keys()
    for key in keys:
      if datumCsyses[key].xAxis[0] < 1.0:
        localCsys = datumCsyses[key]
        reaction_force = reaction_force.getTransformedField(datumCsys=localCsys)
        break

    region = odb.rootAssembly.instances[partName+'-1'].nodeSets[setName]
    rf = reaction_force.getSubset(region=region).values
    
    RF1_tot = 0
    for f in rf:
      RF1_tot += f.data[0]
    
    with open('RF1.txt', 'w') as f:
      f.write(str(RF1_tot))


if __name__ == "__main__":
    partName = sys.argv[-4]
    setName = sys.argv[-3]
    iStepForce = int(sys.argv[-2])
    iStepFSI = int(sys.argv[-1])
    readReactionForce(partName,setName,iStepForce,iStepFSI)