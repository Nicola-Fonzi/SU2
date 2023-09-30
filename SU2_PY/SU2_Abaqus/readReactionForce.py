#!/usr/bin/env python

## \file readReactionForce.py
#  \brief Reader for nodes positions
#  \authors Vittorio Cavalieri, Nicola Fonzi
#  \version 8.0.0 "Harrier"
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
from FSI_tools.FSI_utils import Point

def readReactionForce(device,flexPartName,actSetName,iStepForce,iStepFSI):

    odbFile = 'Job-{}-{}.odb'.format(iStepForce,iStepFSI)
    odb = openOdb(path=odbFile)
    stepName = 'Step-{}-{}'.format(iStepForce,iStepFSI)
    lastFrame = odb.steps[stepName].frames[-1]
    if device == 'TE':
      reaction_field = 'RF'
    elif device == 'LE':
      reaction_field = 'RM'
    reaction = lastFrame.fieldOutputs[reaction_field]

    datumCsyses = odb.rootAssembly.datumCsyses
    keys = datumCsyses.keys()
    for key in keys:
      if device == 'TE' and datumCsyses[key].xAxis[0] < 1.0:
        localCsys = datumCsyses[key]
        break
      elif device == 'LE' and 'SHAFT' in key.upper():
        localCsys = datumCsyses[key]
    reaction = reaction.getTransformedField(datumCsys=localCsys)

    if device == 'TE':
      region = odb.rootAssembly.instances[flexPartName+'-1'].nodeSets[actSetName]
    elif device == 'LE':
      region = odb.rootAssembly.nodeSets[actSetName]
    r = reaction.getSubset(region=region).values

    R1_tot = 0
    for r_i in r:
      R1_tot += r_i.data[0]

    fname = '{}_{}.txt'.format(reaction_field,iStepForce)
    with open(fname, 'w') as f:
      f.write(str(R1_tot))


if __name__ == "__main__":
    device = sys.argv[-5]
    flexPartName = sys.argv[-4]
    actSetName = sys.argv[-3]
    iStepForce = int(sys.argv[-2])
    iStepFSI = int(sys.argv[-1])
    readReactionForce(device,flexPartName,actSetName,iStepForce,iStepFSI)