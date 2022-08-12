#!/usr/bin/env python

## \file pysu2_abaqus.py
#  \brief Structural solver using Abaqus models
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

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy as np
import subprocess
import pickle
from FSI_tools.FSI_utils import Point

# ----------------------------------------------------------------------
#  Solver class
# ----------------------------------------------------------------------

class Solver:
  """
  Structural solver main class.
  It contains all the required methods for the coupling with SU2.
  """

  def __init__(self, config_fileName):
    """
    Constructor of the structural solver class.
    """

    self.Config_file = config_fileName
    self.Config = {}

    print("\n")
    print(" Configuring the structural solver for FSI simulation ".center(80, "-"))
    self.__readConfig()

    self.Inp_file = self.Config['INP_FILE']
    self.Generator_file = self.Config['GENERATOR_FILE']
    self.Data_file = self.Config['DATA_FILE']
    self.FSI_marker = self.Config['MOVING_MARKER']
    self.Set_name = self.Config['SET_NAME']
    self.Part_name = self.Config['PART_NAME']


    self.ActLoad = self.Config['ACT_LOAD']
    self.SliderAngle = self.Config['SLIDER_ANGLE']
    inputPoint = self.Config['INPUT_POINT']
    self.InputPointX = inputPoint[0]
    self.InputPointY = inputPoint[1]
    self.InputPointZ = inputPoint[2]

    self.nPoint = int()
    self.nMarker = int()
    self.node = []
    self.markers = {}

    self.iStepForce = 0
    self.iStepFSI = -1
    self.lastTime = 0.0

    print("\n")
    print(" Opening/generating the model ".center(80,"-"))
    self.__readAbaqusModel()


    # Prepare the output file
    histFile = open('StructHistory.dat', "w")
    header = 'Time\t' + 'Time Iteration\t' + 'FSI Iteration\t' + 'Vertical Displacement\n'
    histFile.write(header)
    histFile.close()

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
        line = line.split("=", 1)
        this_param = line[0].strip()
        this_value = line[1].strip()

        #float values
        if (this_param == "ACT_LOAD") or \
             (this_param == "SLIDER_ANGLE"):
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
        elif (this_param == "INPUT_POINT"):
          self.Config[this_param] = eval(this_value)


        else:
          raise Exception('{} is an invalid option !'.format(this_param))


  def __runGenerator(data_file):
    raise Exception('TODO')
    return inp_file

  def __readAbaqusModel(self):
      """
      This method reads the Abaqus model.
      """

      self.nMarker = 0
      self.nPoint = 0
      self.nRefSys = 0

      if self.Generator_file != 'none':
        self.Inp_file = self.__runGenerator(self.Data_file)
      elif self.Inp_file == 'none':
        raise Exception('At least one between generator file and inp file must be provided')


      self.Model_name = self.Inp_file.split('.')[0]
      self.__runAbaqusScript('readNodes', self.Model_name, self.Inp_file, self.Part_name, self.FSI_marker)

      self.node = pickle.load(open('node.p', 'rb'))
      self.nPoint = len(self.node)
      self.markers = pickle.load(open('markers.p', 'rb'))
      self.nMarker = len(self.markers)

      if not any(self.FSI_marker in key for key in self.markers.keys()):
        raise Exception("The FSI marker was not found in the available sets")

      self.markers[self.FSI_marker].sort()

      print("Number of points: {}".format(self.nPoint))
      print("Number of markers: {}".format(self.nMarker))
      print("Moving marker: {}".format(self.FSI_marker))
      print("Number of points in the moving marker: {}".format(len(self.markers[self.FSI_marker])))


  def __runAbaqusScript(self,pyfun,*args):
      """
      This method runs a python script from the command line without the Abaqus/CAE GUI.
      """
      n = len(args)
      str = 'abaqus cae noGUI=SU2_Abaqus/{}.py --' + n*' {}'
      command = str.format(pyfun, *args)
      process = subprocess.call(command, shell=True)

  def __computeInterfacePosVel(self, initialize):
    """
    This method extracts from the ODB the nodal positions and velocities at the interface.
    """

    pickle.dump(self.node, open('node.p', 'wb'))
    self.__runAbaqusScript('readPosVel', self.Part_name, self.iStepForce, self.iStepFSI, initialize)
    self.node = pickle.load(open('node.p', 'rb'))

  def __temporalIteration(self, time):
    """
    This method integrates in time the solution.
    """

    if time > self.lastTime:
      self.iStepForce += 1
      self.iStepFSI = 0
    else:
      self.iStepFSI += 1

    self.__runAbaqusScript('createStep', self.Model_name, self.iStepForce, self.iStepFSI)

    self.__SetLoads(time)

    self.__runAbaqusScript('runner', self.Model_name, self.iStepForce, self.iStepFSI)

    self.lastTime = time

  def __SetLoads(self, time):
    """
    This method applies the nodal forces on the Abaqus mesh.
    """
    nodeList = self.markers[self.FSI_marker]
    pickle.dump(nodeList, open('nodeList.p', 'wb'))
    pickle.dump(self.node, open('node.p', 'wb'))
    self.__runAbaqusScript('setLoads', self.Model_name, self.Part_name, self.Set_name, time, self.ActLoad,
                           self.SliderAngle, self.InputPointX, self.InputPointY, self.InputPointZ, self.iStepForce, self.iStepFSI)


  def exit(self):
    """
    This method cleanly exits the structural solver.
    """

    print("\n**************** Exiting the Abaqus structural solver ****************")

  def run(self, time):
    """
    This method is the main function for advancing the solution of one time step.
    """
    self.__temporalIteration(time)

    print("Calling Abaqus solver.")

    self.__computeInterfacePosVel(False)

  def setInitialDisplacements(self):
    """
    This method provides public access to the method __computeInterfacePosVel and
    sets velocities for previous time steps.
    """

    self.__computeInterfacePosVel(True)

  def writeSolution(self, time, timeIter, FSIIter):
    """
    This method is the main function for output. It writes the file StructHistory.dat
    """

    # Vertical Displacement History
    histFile = open('StructHistory.dat', "a")
    iVertexDummy = 10	# TODO: use index of trailing-edge tip
    xDisp, yDisp, zDisp = self.getInterfaceNodeDisp(self.getFSIMarkerID(), iVertexDummy)
    line = str(time) + '\t' + str(timeIter) + '\t' + str(FSIIter) + '\t' + '{:6.4g}'.format(yDisp[0]) + '\n'
    histFile.write(line)
    histFile.close()

  def updateSolution(self):
    """
    This method updates the solution.
    """

    for iPoint in range(self.nPoint):
      self.node[iPoint].updateCoordVel()


  def applyload(self, iVertex, fx, fy, fz):
    """
    This method can be accessed from outside to set the nodal forces.
    """
    iPoint = self.getVertexGlobalIndex(self.FSI_marker, iVertex)
    self.node[iPoint].SetForce((fx, fy, fz))
    

  def getFSIMarkerID(self):
    """
    This method provides the ID of the interface marker
    """
    return self.FSI_marker

  def getNumberOfSolidInterfaceNodes(self, markerID):

    return len(self.markers[markerID])

  def getVertexGlobalIndex(self, markerID, iVertex):

    # This solver is serial, thus global=local
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

    # There are no halo nodes in this solver as it is serial
    iPoint = self.markers[markerID][iVertex]
    halo = False
    return halo
