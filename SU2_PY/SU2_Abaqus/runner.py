from abaqus_modules import *


def runner(modelName,iStepForce,iStepFSI):
    
    pathName = '{}.cae'.format(modelName)
    openMdb(pathName=pathName)
    
    #jobName = modelName
    f = open("debug.txt", "w")
    #f.write(modelName)
    #f.write('\n')
    #f.write(inputFileName)
    #f.write('\n')
    #f.write(str(len(mdb.jobs)))
    #f.close()
    
    stepName = 'Step-{}-{}'.format(iStepForce,iStepFSI)
    if iStepForce == 0 and iStepFSI == 0:			# migliorare criterio??
      type = ANALYSIS
      f.write('iStepForce = {}, iStepFSI = {}: type = ANALYSIS\n'.format(iStepForce,iStepFSI))
    else:
      type = RESTART
      f.write('iStepForce = {}, iStepFSI = {}: type = RESTART\n'.format(iStepForce,iStepFSI))
    
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
    	#command = 'rm ' + filename
    	#command = 'del ' + filename
        command = 'IF EXIST {} ( del {} )'.format(filename,filename)
        os.system(command)
    
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