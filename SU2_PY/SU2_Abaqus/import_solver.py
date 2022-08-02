import os
import inspect
import sys


execname = inspect.getframeinfo(inspect.currentframe()).filename
dir_path = os.path.dirname(os.path.abspath(execname))
sys.path.append(dir_path)

import pysu2_abaqus

CSD_ConFile = dir_path + '/' + 'solid_abq.cfg'
SolidSolver = pysu2_abaqus.Solver(CSD_ConFile,False)


import pickle
file = open('myobj.p', 'wb')
pickle.dump(SolidSolver.node, file)