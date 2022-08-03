#!/usr/bin/env python

## \file pysu2_abaqus.py
#  \brief Structural solver using Abaqus models
#  \authors Nicola Fonzi, Vittorio Cavalieri, based on the work of David Thomas
#  \version 7.1.1 "Blackbird"
#
# SU2 Project Website: https://su2code.github.io
#
# The SU2 Project is maintained by the SU2 Foundation
# (http://su2foundation.org)
#
# Copyright 2012-2021, SU2 Contributors (cf. AUTHORS.md)
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

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy as np
import subprocess
import pickle
from FSI_tools.FSI_utils import Point
from FSI_tools.FSI_utils import RefSystem

# ----------------------------------------------------------------------
#  Solver class
# ----------------------------------------------------------------------

class Solver:
  """
  Structural solver main class.
  It contains all the required methods for the coupling with SU2.
  """

  def __init__(self, config_fileName, ImposedMotion):
    """
    Constructor of the structural solver class.
    """

    self.Config_file = config_fileName
    self.Config = {}

    print("\n")
    print(" Configuring the structural solver for FSI simulation ".center(80,"-"))
    self.__readConfig()

    self.Inp_file = self.Config['INP_FILE']
    self.Generator_file = self.Config['GENERATOR_FILE']
    self.Data_file = self.Config['DATA_FILE']
    self.FSI_marker = self.Config['MOVING_MARKER']
    self.Set_name = self.Config['SET_NAME']			# a cosa serve????
    self.Part_name = self.Config['PART_NAME']
    self.Unsteady = (self.Config['TIME_MARCHING']=="YES")
    self.ImposedMotion = ImposedMotion
    if self.Unsteady:
      print('Dynamic computation.')
      raise Exception('Not implemented.')


    self.ActForce = self.Config['ACT_FORCE']
    #self.deltaT = self.Config['DELTA_T']
    #self.rhoAlphaGen = self.Config['RHO']

    self.nPoint = int()
    self.nMarker = int()
    self.nRefSys = int()
    self.node = []
    self.markers = {}
    self.refsystems = []
    self.ImposedMotionToSet = True
    self.ImposedMotionFunction = []

    self.iStepForce = 0
    self.iStepFSI = -1
    self.lastTime = 0.0

    print("\n")
    print(" Opening/generating the model ".center(80,"-"))
    self.__readAbaqusModel()

    #print("\n")
    #print(" Setting the integration parameters ".center(80,"-"))
    #self.__setIntegrationParameters()
    #self.__setInitialConditions()
    #
    # Prepare the output file
    if self.Config["RESTART_SOL"]=="NO":
      histFile = open('StructHistoryModal.dat', "w")
      header = 'Time\t' + 'Time Iteration\t' + 'FSI Iteration\t'
      for i in range(3):
        header = header + 'u' + str(i+1) + '\t'
      header = header + '\n'
      histFile.write(header)
      histFile.close()
    else:
      raise Exception('Not implemented.')
      self.__setRestart()

  def __readConfig(self):
    """
    This method obtains the configuration options from the structural solver input
    file.
    """

    with open(self.Config_file) as configfile:
      while 1:
        line = configfile.readline()
        if not line:
          break

        # remove line returns
        line = line.strip('\r\n')
        # make sure it has useful data
        if (not "=" in line) or (line[0] == '%'):
          continue
        # split across equal sign
        line = line.split("=",1)
        this_param = line[0].strip()
        this_value = line[1].strip()

        #integer values
        if (this_param == "RESTART_ITER"):
          self.Config[this_param] = int(this_value)


        #float values
        elif (this_param == "DELTA_T") or \
             (this_param == "RHO"):
          self.Config[this_param] = float(this_value)


        #string values
        elif (this_param == "TIME_MARCHING") or \
             (this_param == "INP_FILE") or \
             (this_param == "GENERATOR_FILE") or \
             (this_param == "DATA_FILE") or \
             (this_param == "RESTART_SOL") or \
             (this_param == "MOVING_MARKER") or \
             (this_param == "PART_NAME") or \
             (this_param == "SET_NAME"):
          self.Config[this_param] = this_value


        #lists values
        elif (this_param == "ACT_FORCE"):
          self.Config[this_param] = eval(this_value)


        else:
          raise Exception('{} is an invalid option !'.format(this_param))



  def __readAbaqusModel(self):
      """
      This method reads the Abaqus model.
      """

      def runGenerator(data_file):
        raise Exception('TODO')
        return inp_file

      self.nMarker = 0
      self.nPoint = 0
      self.nRefSys = 0

      if self.Generator_file != 'none':
        self.Inp_file = runGenerator(self.Data_file)
      elif self.Inp_file == 'none':
        raise Exception('At least one between generator file and inp file must be provided')


      self.Model_name = self.Inp_file.split('.')[0]

      command = 'abaqus cae noGUI=readNodes.py -- {} {} {}'.format(self.Model_name,self.Inp_file,self.Part_name) # meglio??
      process = subprocess.call(command,shell=True)

      self.node = pickle.load(open('node.p','rb'))
      self.nPoint = len(self.node)
      self.markers = pickle.load(open('markers.p','rb'))
      self.nMarker = len(self.markers)

      #if not any(self.FSI_marker in key for key in self.markers.keys()):
      #    raise Exception("The FSI marker was not found in the available sets")
	  #
      #self.markers[self.FSI_marker].sort()
	  #
      #print("Number of points: {}".format(self.nPoint))
      #print("Number of markers: {}".format(self.nMarker))
      #print("Number of reference systems: {}".format(self.nRefSys))
      #print("Moving marker: {}".format(self.FSI_marker))
      #print("Number of points in the moving marker: {}".format(len(self.markers[self.FSI_marker])))

  def __checkBlankField(self, string):
    """
    This method considers that Nastran apply 0 when the reference system is not specified
    """

    if string == '        ':
      return int(0)
    else:
      return int(string)


  def __setIntegrationParameters(self):
    """
    This method uses the time step size to define the integration parameters.
    """

    self.alpha_m = (2.0*self.rhoAlphaGen-1.0)/(self.rhoAlphaGen+1.0)
    self.alpha_f = (self.rhoAlphaGen)/(self.rhoAlphaGen+1.0)
    self.gamma = 0.5+self.alpha_f-self.alpha_m
    self.beta = 0.25*(self.gamma+0.5)**2

    self.gammaPrime = self.gamma/(self.deltaT*self.beta)
    self.betaPrime = (1.0-self.alpha_m)/((self.deltaT**2)*self.beta*(1.0-self.alpha_f))

    print('Time integration with the alpha-generalized algorithm.')
    print('rho : {}'.format(self.rhoAlphaGen))
    print('alpha_m : {}'.format(self.alpha_m))
    print('alpha_f : {}'.format(self.alpha_f))
    print('gamma : {}'.format(self.gamma))
    print('beta : {}'.format(self.beta))
    print('gammaPrime : {}'.format(self.gammaPrime))
    print('betaPrime : {}'.format(self.betaPrime))

  def __setInitialConditions(self):
    """
    This method uses the list of initial modal amplitudes to set the initial conditions
    """

    print('Setting initial conditions.')

    print('Using modal amplitudes from config file')
    for imode in range(self.nDof):
        if imode in self.Config["INITIAL_MODES"].keys():
            self.q[imode] = float(self.Config["INITIAL_MODES"][imode])
            self.q_n[imode] = float(self.Config["INITIAL_MODES"][imode])

    RHS = np.zeros((self.nDof,1))
    RHS += self.F
    RHS -= self.C.dot(self.qdot)
    RHS -= self.K.dot(self.q)
    self.qddot = linalg.solve(self.M, RHS)
    self.qddot_n = np.copy(self.qddot)
    self.a = np.copy(self.qddot)
    self.a_n = np.copy(self.qddot)

  def __reset(self, vector):
    """
    This method set to zero any vector.
    """

    for ii in range(vector.shape[0]):
      vector[ii] = 0.0

  def __computeInterfacePosVel(self, initialize):
    """
    This method uses the mode shapes to compute, based on the modal velocities, the
    nodal velocities at the interface.
    """

    pickle.dump(self.node, open('node.p','wb'))

    command = 'abaqus cae noGUI=readPosVel.py -- {} {} {} {}'.format(self.Part_name,self.iStepForce,self.iStepFSI,initialize) # meglio??
    process = subprocess.call(command,shell=True)
    
    self.node = pickle.load(open('node.p','rb'))


  def __setRestart(self):
    """
    This method sets all the variables needed for the correct restart.
    """

    #read the Structhistory to obtain the mode amplitudes
    nM1Set = False
    nSet = False
    firstLineRead = False
    couplingLineRead = False

    with open('StructHistoryModal.dat','r') as file:
      print('Opened history file StructHistoryModal.dat.')
      line = file.readline()
      while 1:
        line = file.readline()
        if not line:
          break
        line = line.strip('\r\n').split()

        # The old time_0 for imposed motion can either be the first line of the StructHistoryModal, if TimeIterTreshold was -1 (immediate coupling), or the second line. In the former case, time_0 is 0.0, so it is easy to recognize it
        if not firstLineRead:
          firstLineRead = True
          if float(line[0])==0.0:
            couplingLineRead = True
            self.timeStartCoupling = 0.0
        else:
          if couplingLineRead:
            pass
          else:
            self.timeStartCoupling = float(line[0])
            couplingLineRead = True

        if int(line[1])==(self.Config["RESTART_ITER"]-2):
          index = 0
          for index_mode in range(self.nDof):
            self.q[index_mode] = float(line[index+3])
            self.qdot[index_mode] = float(line[index+4])
            self.qddot[index_mode] = float(line[index+5])
            index += 3
          del index
          #push back the mode amplitudes velocities and accelerations
          self.__computeInterfacePosVel(True)
          self.q_n = np.copy(self.q)
          self.qdot_n = np.copy(self.qdot)
          self.qddot_n = np.copy(self.qddot)
          self.a_n = np.copy(self.a)
          nM1Set = True
        if int(line[1])==(self.Config["RESTART_ITER"]-1):
          index = 0
          for index_mode in range(self.nDof):
            self.q[index_mode] = float(line[index+3])
            self.qdot[index_mode] = float(line[index+4])
            self.qddot[index_mode] = float(line[index+5])
            index += 3
          del index
          self.__computeInterfacePosVel(False)
          nSet = True
          break
          
    if (not nM1Set) or (not nSet):
      raise Exception('The restart iteration was not found in the structural history')


  def __temporalIteration(self,time):
    """
    This method integrates in time the solution.
    """
    #self.__reset(self.q)
    #self.__reset(self.qdot)
    #self.__reset(self.qddot)
    #self.__reset(self.a)

    if not self.ImposedMotion:

      if time > self.lastTime: 		# migliorare criterio?
        self.iStepForce += 1
        self.iStepFSI = 0
      else:
        self.iStepFSI += 1

      #print('Before createStep.py')
      command = 'abaqus cae noGUI=createStep.py -- {} {} {}'.format(self.Model_name, self.iStepForce, self.iStepFSI) # meglio??
      process = subprocess.call(command, shell=True)
      #print('After createStep.py')

      self.__SetLoads(time)

      #print('Before runner.py')
      command = 'abaqus cae noGUI=runner.py -- {} {} {}'.format(self.Model_name, self.iStepForce, self.iStepFSI) # meglio??
      process = subprocess.call(command, shell=True)
      #print('After runner.py')
	  
    self.lastTime = time		# qui?

    #else:
    #  if self.ImposedMotionToSet:
    #    raise Exception('Not implemented.')
    #    if self.Config["RESTART_SOL"] == "NO":                                   # If yes we already set it in the __setRestart function
    #      self.timeStartCoupling = time
    #    iImposedFunc = 0
    #    for imode in self.Config["IMPOSED_MODES"].keys():
    #      for isuperposed in range(len(self.Config["IMPOSED_MODES"][imode])):
    #        typeOfMotion = self.Config["IMPOSED_MODES"][imode][isuperposed]
    #        parameters = self.Config["IMPOSED_PARAMETERS"][imode][isuperposed]
    #        self.ImposedMotionFunction.append(ImposedMotionClass(self.timeStartCoupling, typeOfMotion, parameters, imode))
    #        iImposedFunc += 1
    #    self.ImposedMotionToSet = False
    #  for iImposedFunc in range(len(self.ImposedMotionFunction)):
    #    imode = self.ImposedMotionFunction[iImposedFunc].mode
    #    self.q[imode] += self.ImposedMotionFunction[iImposedFunc].GetDispl(time)
    #    self.qdot[imode] += self.ImposedMotionFunction[iImposedFunc].GetVel(time)
    #    self.qddot[imode] += self.ImposedMotionFunction[iImposedFunc].GetAcc(time)
    #  self.a = np.copy(self.qddot)


  def __SetLoads(self,time):
    """
    This method applies the nodal forces on the Abaqus mesh.
    """
    nodeList = self.markers[self.FSI_marker]
    pickle.dump(nodeList, open('nodeList.p','wb'))
    node = self.node
    pickle.dump(self.node, open('node.p','wb'))
    
    #command = 'abaqus cae noGUI=setLoads.py -- {} {} {}'.format(self.Model_name,self.Part_name,self.iStep) # meglio??
    command = 'abaqus cae noGUI=setLoads.py -- {} {} {} {} {} {} {} {} {}'.format(self.Model_name,self.Part_name,self.Set_name,time,self.ActForce[0],self.ActForce[1],self.ActForce[2],self.iStepForce,self.iStepFSI) # meglio??
    process = subprocess.call(command,shell=True)


  def exit(self):
    """
    This method cleanly exits the structural solver.
    """

    print("\n**************** Exiting the structural tester solver ****************")

  def run(self,time):
    """
    This method is the main function for advancing the solution of one time step.
    """
    self.__temporalIteration(time)
    
    header = 'Time\t'
    for i in range(3):
      header = header + 'u' + str(i+1) + '\t'
    header = header + '\n'
    print(header)
    line = '{:6.4f}'.format(time) + '\t'
    for i in range(3):
      line = line + '{:6.4f}'.format(float(i)) + '\t' + '{:6.4f}'.format(float(i)) + '\t' + '{:6.4f}'.format(float(i)) + '\t'	# TODO
    line =  line + '\n'
    print(line)
    self.__computeInterfacePosVel(False)

  def setInitialDisplacements(self):
    """
    This method provides public access to the method __computeInterfacePosVel and
    sets velocities for previous time steps.
    """

    self.__computeInterfacePosVel(True)

  def writeSolution(self, time, timeIter, FSIIter):
    """
    This method is the main function for output. It writes the file StructHistoryModal.dat
    """

    # Modal History
    histFile = open('StructHistoryModal.dat', "a")
    line = str(time) + '\t' + str(timeIter) + '\t' + str(FSIIter) + '\t'
    for i in range(3):
      line = line + str(float(i)) + '\t'	# TODO
    line =  line + '\n'
    histFile.write(line)
    histFile.close()

  def updateSolution(self):
    """
    This method updates the solution.
    """

    #self.q_n = np.copy(self.q)
    #self.qdot_n = np.copy(self.qdot)
    #self.qddot_n = np.copy(self.qddot)
    #self.a_n = np.copy(self.a)
    #self.__reset(self.q)
    #self.__reset(self.qdot)
    #self.__reset(self.qddot)
    #self.__reset(self.a)

    for iPoint in range(self.nPoint):
      self.node[iPoint].updateCoordVel()


  def applyload(self, iVertex, fx, fy, fz):
    """
    This method can be accessed from outside to set the nodal forces.
    """
    iPoint = self.getVertexGlobalIndex(self.FSI_marker, iVertex)
    #print('{}\n'.format(fx))
    self.node[iPoint].SetForce((fx,fy,fz))
    

  def getFSIMarkerID(self):
    """
    This method provides the ID of the interface marker
    """
    return self.FSI_marker

  def getNumberOfSolidInterfaceNodes(self, markerID):

    return len(self.markers[markerID])

  def getVertexGlobalIndex(self, markerID, iVertex):   # TODO This solver is serial, thus global=local

    return self.markers[markerID][iVertex]

  def getInterfaceNodePosInit(self, markerID, iVertex):

    iPoint = self.markers[markerID][iVertex]
    Coord0 = self.node[iPoint].GetCoord0()
    return Coord0

  def getInterfaceNodeDisp(self, markerID, iVertex):

    iPoint = self.markers[markerID][iVertex]
    Coord = self.node[iPoint].GetCoord()
    Coord0 = self.node[iPoint].GetCoord0()
    return (Coord-Coord0)

  def getInterfaceNodeVel(self, markerID, iVertex):

    iPoint = self.markers[markerID][iVertex]
    Vel = self.node[iPoint].GetVel()
    return Vel

  def getInterfaceNodeVelNm1(self, markerID, iVertex):

    iPoint = self.markers[markerID][iVertex]
    Vel = self.node[iPoint].GetVel_n()
    return Vel

  def IsAHaloNode(self, markerID, iVertex):

    iPoint = self.markers[markerID][iVertex]
    halo = False  # TODO when in parallel we will need to define this
    return halo
