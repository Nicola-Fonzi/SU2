#!/usr/bin/env python

## \file runner.py
#  \brief Launcher for Abaqus structural solution
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


def runner(modelName,iStepForce,iStepFSI):
    
    pathName = '{}.cae'.format(modelName)
    openMdb(pathName=pathName)
    
    stepName = 'Step-{}-{}'.format(iStepForce,iStepFSI)
    if iStepForce == 0 and iStepFSI == 0:
      type = ANALYSIS
    else:
      type = RESTART
    
    jobName = 'Job-{}-{}'.format(iStepForce,iStepFSI)
    myJob = mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF,
        explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF,
        memory=90, memoryUnits=PERCENTAGE, model=modelName, modelPrint=OFF,
        multiprocessingMode=DEFAULT, name=jobName, nodalOutputPrecision=SINGLE,
        numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=
        type, userSubroutine='', waitHours=0, waitMinutes=0)
    myJob.writeInput(consistencyChecking=OFF)
    myJob.submit(consistencyChecking=OFF)
    myJob.waitForCompletion()
    
    extensions = ['com','dat','ipm','log','msg','sim','sta','lck']
    for ext in extensions:
       filename = jobName + '.' + ext
       if os.path.exists(filename):
         os.remove(filename)
    
    pathName = '{}.cae'.format(modelName)
    mdb.saveAs(pathName=pathName)



if __name__ == "__main__":
	if len(sys.argv) > 0:
		modelName = sys.argv[-3]
		iStepForce = int(sys.argv[-2])
		iStepFSI = int(sys.argv[-1])
	else:
		raise Exception('iStepForce and iStepFSI must be provided')
	runner(modelName,iStepForce,iStepFSI)