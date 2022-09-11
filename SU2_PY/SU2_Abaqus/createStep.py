#!/usr/bin/env python

## \file createStep.py
#  \brief Creation of the run for Abaqus solver
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

from abaqus_modules import *
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