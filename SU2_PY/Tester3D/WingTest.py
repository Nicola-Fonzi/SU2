#!/usr/bin/env python

## \file SolidSolverTester.py
#  \brief Structural solver tester (one or two degree of freedom) used for testing the Py wrapper for external FSI coupling.
#  \author David Thomas
#  \version 7.0.6 "Blackbird"
#
# SU2 Project Website: https://su2code.github.io
#
# The SU2 Project is maintained by the SU2 Foundation
# (http://su2foundation.org)
#
# Copyright 2012-2020, SU2 Contributors (cf. AUTHORS.md)
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

import os, sys, shutil, copy
import numpy as np
import scipy as sp
import scipy.linalg as linalg
from math import *
from FSI_tools.switch import switch

# ----------------------------------------------------------------------
#  Config class
# ----------------------------------------------------------------------

class RefSystem:

  def __init__(self):
    self.CID = 0
    self.RID = 0
    self.AX = 0.
    self.AY = 0.
    self.AZ = 0.

  def SetOrigin(self,A):
    self.AX, self.AY, self.AZ =  A

  def SetCID(self,CID):
    self.CID = CID

  def SetRID(self,RID):
    self.RID = RID

  def GetOrigin(self):
    return np.array([self.AX,self.AY,self.AZ])

  def GetRID(self):
    return self.RID

  def GetCID(self):
    return self.CID

class Point:
  """ Description. """

  def __init__(self):
    self.Coord0 = np.zeros((3,1))
    self.Coord = np.zeros((3,1))
    self.Coord_n = np.zeros((3,1))
    self.Vel = np.zeros((3,1))
    self.Vel_n = np.zeros((3,1))
    self.Force = np.zeros((3,1))
    self.ID = 0
    self.CP = 0
    self.CD = 0

  def GetCoord0(self):
    return self.Coord0

  def GetCoord(self):
    return self.Coord

  def GetCoord_n(self):
    return self.Coord_n

  def GetVel(self):
    return self.Vel

  def GetVel_n(self):
    return self.Vel_n

  def GetForce(self):
    return self.Force

  def GetID(self):
    return self.ID

  def GetCP(self):
    return self.CP

  def GetCD(self):
    return self.CD

  def SetCoord0(self, val_Coord):
    x, y, z = val_Coord
    self.Coord0[0] = x
    self.Coord0[1] = y
    self.Coord0[2] = z

  def SetCoord(self, val_Coord):
    x, y, z = val_Coord
    self.Coord[0] = x
    self.Coord[1] = y
    self.Coord[2] = z

  def SetCoord_n(self, val_Coord):
    x, y, z = val_Coord
    self.Coord_n[0] = x
    self.Coord_n[1] = y
    self.Coord_n[2] = z

  def SetVel(self, val_Vel):
    vx, vy, vz = val_Vel
    self.Vel[0] = vx
    self.Vel[1] = vy
    self.Vel[2] = vz

  def SetVel_n(self, val_Vel):
    vx, vy, vz = val_Vel
    self.Vel_n[0] = vx
    self.Vel_n[1] = vy
    self.Vel_n[2] = vz

  def SetForce(self, val_Force):
    fx, fy, fz = val_Force
    self.Force[0] = fx
    self.Force[1] = fy
    self.Force[2] = fz

  def SetID(self, ID):
    self.ID = ID

  def SetCP(self,CP):
    self.CP = CP

  def SetCD(self,CD):
    self.CD = CD

  def updateCoordVel(self):
    self.Coord_n = np.copy(self.Coord)
    self.Vel_n = np.copy(self.Vel)

class Solver:
  """Description"""

  def __init__(self, config_fileName):
    """ Description. """

    self.Config_file = config_fileName
    self.Config = {}

    print("\n------------------------------ Configuring the structural tester solver for FSI simulation ------------------------------")
    self.__readConfig()

    self.Mesh_file = self.Config['MESH_FILE']
    self.Punch_file = self.Config['PUNCH_FILE']
    self.FSI_marker = self.Config['MOVING_MARKER']
    self.Unsteady = (self.Config['TIME_MARCHING']=="YES")
    if self.Unsteady:
      print('Dynamic computation.')
    self.nDof = self.Config['NMODES']
    print("Reading number of modes from file")


    # Structural properties
    print("Reading the modal and stiffnes matrix from file")
    self.ModalDamping = self.Config['MODAL_DAMPING']
    if self.ModalDamping == 0:
        print("The structural model in undamped")
    else:
        print("Assuming {}% of modal damping".format(self.ModalDamping*100))

    self.startTime = self.Config['START_TIME']
    self.stopTime = self.Config['STOP_TIME']
    self.deltaT = self.Config['DELTA_T']
    self.rhoAlphaGen = self.Config['RHO']

    self.nElem = int()
    self.nPoint = int()
    self.nMarker = int()
    self.nRefSys = int()
    self.node = []
    self.markers = {}
    self.refsystems = []

    print("\n------------------------------ Reading the mesh ------------------------------")
    self.__readNastranMesh()

    print("\n------------------------------ Creating the structural model ------------------------------")
    self.__setStructuralMatrices()

    print("\n------------------------------ Setting the integration parameters ------------------------------")
    self.__setIntegrationParameters()
    self.__setInitialConditions()

  def __readConfig(self):
    """ Description. """

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

        for case in switch(this_param):
          #integer values
          if case("NMODES")		:
            self.Config[this_param] = int(this_value)
            break

          #float values
          if case("DELTA_T")			: pass
          if case("START_TIME")		      	: pass
          if case("STOP_TIME")		      	: pass
          if case("MODAL_DAMPING")      : pass
          if case("RHO")	      		:
            self.Config[this_param] = float(this_value)
            break

          #string values
          if case("TIME_MARCHING")	: pass
          if case("MESH_FILE")			: pass
          if case("PUNCH_FILE")        : pass
          if case("MOVING_MARKER")		:
            self.Config[this_param] = this_value
            break

          #lists values
          if case("INITIAL_MODES"):
            self.Config[this_param] = eval(this_value)
            break

          if case():
            print(this_param + " is an invalid option !")
            break



  def __readNastranMesh(self):
      """ This function reads the nastran 3D mesh"""

      def nastran_float(s):
        if s.find('E') == -1:
          s = s.replace('-','e-')
          s = s.replace('+','e+')
          if s[0] == 'e':
            s = s[1:]
        return float(s)

      self.nMarker = 1
      self.nPoint = 0
      self.nRefSys = 0

      with open(self.Mesh_file,'r') as meshfile:
        print('Opened mesh file ' + self.Mesh_file + '.')
        while 1:
          line = meshfile.readline()
          if not line:
            break

          pos = line.find('GRID')
          if pos != -1 and pos  ==  30:
            line = line.strip('\r\n')
            self.node.append(Point())
            line = line[30:]
            ID = int(line[8:16])
            CP = int(line[16:24])
            x = nastran_float(line[24:32])
            y = nastran_float(line[32:40])
            z = nastran_float(line[40:48])
            if CP != 0:
              for iRefSys in range(self.nRefSys):
                if self.refsystems[iRefSys].GetCID()==CP:
                  break
              if self.refsystems[iRefSys].GetCID()!=CP:
                sys.exit('Definition reference {} system not found'.format(CP))
              DeltaPos = self.refsystems[iRefSys].GetOrigin()
              x = x+DeltaPos[0]
              y = y+DeltaPos[1]
              z = z+DeltaPos[2]
            CD = int(line[48:56])
            self.node[self.nPoint].SetCoord((x,y,z))
            self.node[self.nPoint].SetID(ID)
            self.node[self.nPoint].SetCP(CP)
            self.node[self.nPoint].SetCD(CD)
            self.node[self.nPoint].SetCoord0((x,y,z))
            self.node[self.nPoint].SetCoord_n((x,y,z))
            self.nPoint = self.nPoint+1
            continue

          pos = line.find('CORD2R')
          if pos != -1 and pos == 30:
            line = line.strip('\r\n')
            self.refsystems.append(RefSystem())
            line = line[30:]
            CID = int(line[8:16])
            self.refsystems[self.nRefSys].SetCID(CID)
            RID = int(line[16:24])
            self.refsystems[self.nRefSys].SetRID(RID)
            AX = nastran_float(line[24:32])
            AY = nastran_float(line[32:40])
            AZ = nastran_float(line[40:48])
            self.refsystems[self.nRefSys].SetOrigin((AX,AY,AZ))
            self.nRefSys = self.nRefSys+1
            continue

          pos = line.find("SET1")
          markerTag = self.Config['MOVING_MARKER']
          if pos != -1 and pos == 30:
              self.markers[markerTag] = []
              line = line.strip('\r\n')
              line = line[46:]
              line = line.split()
              existValue = True
              while existValue:
                  if line[0] == "+":
                      line = meshfile.readline()
                      line = line.strip('\r\n')
                      line = line[37:]
                      line = line.split()
                  ID = int(line.pop(0))
                  for iPoint in range(self.nPoint):
                      if self.node[iPoint].GetID() == ID:
                          break
                  self.markers[self.FSI_marker].append(iPoint)
                  existValue = len(line)>=1
              continue

      self.markers[self.FSI_marker].sort()
      print("Number of elements: {}".format(self.nElem))
      print("Number of point: {}".format(self.nPoint))
      print("Number of markers: {}".format(self.nMarker))
      print("Number of reference systems: {}".format(self.nRefSys))
      if len(self.markers) > 0:
        print("Moving marker(s):")
        for mark in self.markers.keys():
          print(mark)

  def __setStructuralMatrices(self):
    """ Descriptions. """

    self.M = np.zeros((self.nDof, self.nDof))
    self.K = np.zeros((self.nDof, self.nDof))
    self.C = np.zeros((self.nDof, self.nDof))

    self.q = np.zeros((self.nDof, 1))
    self.qdot = np.zeros((self.nDof, 1))
    self.qddot = np.zeros((self.nDof, 1))
    self.a = np.zeros((self.nDof, 1))

    self.q_n = np.zeros((self.nDof, 1))
    self.qdot_n = np.zeros((self.nDof, 1))
    self.qddot_n = np.zeros((self.nDof, 1))
    self.a_n = np.zeros((self.nDof, 1))

    self.F = np.zeros((self.nDof, 1))

    self.Ux = np.zeros((self.nPoint,self.nDof))
    self.Uy = np.zeros((self.nPoint,self.nDof))
    self.Uz = np.zeros((self.nPoint,self.nDof))

    with open(self.Punch_file,'r') as punchfile:
      print('Opened punch file ' + self.Punch_file + '.')
      while 1:
        line = punchfile.readline()
        if not line:
          break

        pos = line.find('MODE ')
        if pos != -1:
          line = line.strip('\r\n').split()
          n = int(line[5])
          imode = n-1
          k_i = float(line[2])
          self.M[imode][imode] = 1
          self.K[imode][imode] = k_i
          w_i = sqrt(k_i)
          self.C[imode][imode] = 2 * self.ModalDamping * w_i
          iPoint = 0
          for indexIter in range(self.nPoint):
            line = punchfile.readline()
            line = line.strip('\r\n').split()
            if line[1]=='G':
              ux = float(line[2])
              uy = float(line[3])
              uz = float(line[4])
              self.Ux[iPoint][imode] = ux
              self.Uy[iPoint][imode] = uy
              self.Uz[iPoint][imode] = uz
              iPoint = iPoint + 1
              line = punchfile.readline()
            if line[1]=='S':
              line = punchfile.readline()

          if n == self.nDof:
            break

    self.UxT = self.Ux.transpose()
    self.UyT = self.Uy.transpose()
    self.UzT = self.Uz.transpose()

    if n<self.nDof:
        print('ERROR: available {} degrees of freedom instead of {} as requested'.format(n,self.nDof))
        exit()
    else:
        print('Using {} degrees of freedom'.format(n))

  def __setIntegrationParameters(self):
    """ Description. """

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
    """ Description. """

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
    """ Description. """

    for ii in range(vector.shape[0]):
      vector[ii] = 0.0

  def __computeInterfacePosVel(self, initialize):
    """ Description. """

    # Multiply the modal matrices with modal amplitudes
    X_vel = self.Ux.dot(self.qdot)
    Y_vel = self.Uy.dot(self.qdot)
    Z_vel = self.Uz.dot(self.qdot)

    X_disp = self.Ux.dot(self.q)
    Y_disp = self.Uy.dot(self.q)
    Z_disp = self.Uz.dot(self.q)

    for iPoint in range(len(self.node)):
      coord0 = self.node[iPoint].GetCoord0()
      self.node[iPoint].SetCoord((X_disp[iPoint]+coord0[0],Y_disp[iPoint]+coord0[1],Z_disp[iPoint]+coord0[2]))
      self.node[iPoint].SetVel((X_vel[iPoint],Y_vel[iPoint],Z_vel[iPoint]))

      if initialize:
        self.node[iPoint].SetCoord_n((X_disp[iPoint]+coord0[0],Y_disp[iPoint]+coord0[1],Z_disp[iPoint]+coord0[2]))
        self.node[iPoint].SetVel_n((X_vel[iPoint],Y_vel[iPoint],Z_vel[iPoint]))

  def __temporalIteration(self):
    """ Description. """

    eps = 1e-6

    self.__SetLoads()

    # Prediction step
    self.__reset(self.qddot)
    self.__reset(self.a)

    self.a += (self.alpha_f)/(1-self.alpha_m)*self.qddot_n
    self.a -= (self.alpha_m)/(1-self.alpha_m)*self.a_n

    self.q = np.copy(self.q_n)
    self.q += self.deltaT*self.qdot_n
    self.q += (0.5-self.beta)*self.deltaT*self.deltaT*self.a_n
    self.q += self.deltaT*self.deltaT*self.beta*self.a

    self.qdot = np.copy(self.qdot_n)
    self.qdot += (1-self.gamma)*self.deltaT*self.a_n
    self.qdot += self.deltaT*self.gamma*self.a

    # Correction step
    res = self.__ComputeResidual()

    while linalg.norm(res) >= eps:
      St = self.__TangentOperator()
      Deltaq = -1*(linalg.solve(St,res))
      self.q += Deltaq
      self.qdot += self.gammaPrime*Deltaq
      self.qddot += self.betaPrime*Deltaq
      res = self.__ComputeResidual()

    self.a += (1-self.alpha_f)/(1-self.alpha_m)*self.qddot


  def __SetLoads(self):
    """ Description """
    makerID = list(self.markers.keys())
    makerID = makerID[0]
    nodeList = self.markers[makerID]
    FX = np.zeros((self.nPoint, 1))
    FY = np.zeros((self.nPoint, 1))
    FZ = np.zeros((self.nPoint, 1))
    for iPoint in nodeList:
      Force = self.node[iPoint].GetForce()
      FX[iPoint] = float(Force[0])
      FY[iPoint] = float(Force[1])
      FZ[iPoint] = float(Force[2])
    self.F = self.UxT.dot(FX) + self.UyT.dot(FY) + self.UzT.dot(FZ)

  def __ComputeResidual(self):
    """ Description. """

    res = self.M.dot(self.qddot) + self.C.dot(self.qdot) + self.K.dot(self.q) - self.F

    return res

  def __TangentOperator(self):
    """ Description. """

    # The problem is linear, so the tangent operator is straightforward.
    St = self.betaPrime*self.M + self.gammaPrime*self.C + self.K

    return St

  def exit(self):
    """ Description. """

    print("\n**************** Exiting the structural tester solver ****************")

  def run(self,t0,t1):
    """ Description. """
    self.__temporalIteration()
    header = 'Time\t'
    for imode in range(min([self.nDof,5])):
      header = header + 'q' + str(imode+1) + '\t' + 'qdot' + str(imode+1) + '\t' + 'qddot' + str(imode+1) + '\t'
    header = header + '\n'
    print(header)
    line = '{:6.4f}'.format(t1) + '\t'
    for imode in range(min([self.nDof,5])):
      line = line + '{:6.4f}'.format(float(self.q[imode])) + '\t' + '{:6.4f}'.format(float(self.qdot[imode])) + '\t' + '{:6.4f}'.format(float(self.qddot[imode])) + '\t'
    line =  line + '\n'
    print(line)
    self.__computeInterfacePosVel(False)

  def setInitialDisplacements(self):
    """ Description. """

    self.__computeInterfacePosVel(True)

  def writeSolution(self, time, FSIIter, TimeIter, NbTimeIter):
    """ Description. """

    # Modal History
    if time == 0:
      histFile = open('StructHistoryModal.dat', "w")
      header = 'Time\t'
      for imode in range(self.nDof):
        header = header + 'q' + str(imode+1) + '\t' + 'qdot' + str(imode+1) + '\t' + 'qddot' + str(imode+1) + '\t'
      header = header + '\n'
      histFile.write(header)
    else:
      histFile = open('StructHistoryModal.dat', "a")
    line = str(time) + '\t'
    for imode in range(self.nDof):
      line = line + str(float(self.q[imode])) + '\t' + str(float(self.qdot[imode])) + '\t' + str(float(self.qddot[imode])) + '\t'
    line =  line + '\n'
    histFile.write(line)
    histFile.close()

  def updateSolution(self):
    """ Description. """

    self.q_n = np.copy(self.q)
    self.qdot_n = np.copy(self.qdot)
    self.qddot_n = np.copy(self.qddot)
    self.a_n = np.copy(self.a)
    self.__reset(self.q)
    self.__reset(self.qdot)
    self.__reset(self.qddot)
    self.__reset(self.a)

    makerID = list(self.markers.keys())
    makerID = makerID[0]
    nodeList = self.markers[makerID]

    for iPoint in nodeList:
      self.node[iPoint].updateCoordVel()


  def applyload(self, iVertex, fx, fy, fz):
    """ Description """

    makerID = list(self.markers.keys())
    makerID = makerID[0]
    iPoint = self.getInterfaceNodeGlobalIndex(makerID, iVertex)
    self.node[iPoint].SetForce((fx,fy,fz))

  def getFSIMarkerID(self):
    """ Description. """
    L = list(self.markers)
    return L[0]

  def getNumberOfSolidInterfaceNodes(self, markerID):
    """ Description. """

    return len(self.markers[markerID])

  def getInterfaceNodeGlobalIndex(self, markerID, iVertex):
    """ Description. """

    return self.markers[markerID][iVertex]

  def getInterfaceNodePosX(self, markerID, iVertex):
    """ Desciption. """

    iPoint = self.markers[markerID][iVertex]
    Coord = self.node[iPoint].GetCoord()
    return float(Coord[0])

  def getInterfaceNodePosY(self, markerID, iVertex):
    """ Desciption. """

    iPoint = self.markers[markerID][iVertex]
    Coord = self.node[iPoint].GetCoord()
    return float(Coord[1])

  def getInterfaceNodePosZ(self, markerID, iVertex):
    """ Desciption. """

    iPoint = self.markers[markerID][iVertex]
    Coord = self.node[iPoint].GetCoord()
    return float(Coord[2])

  def getInterfaceNodeDispX(self, markerID, iVertex):
    """ Desciption. """

    iPoint = self.markers[markerID][iVertex]
    Coord = self.node[iPoint].GetCoord()
    Coord0 = self.node[iPoint].GetCoord0()
    return float(Coord[0]-Coord0[0])

  def getInterfaceNodeDispY(self, markerID, iVertex):
    """ Desciption. """

    iPoint = self.markers[markerID][iVertex]
    Coord = self.node[iPoint].GetCoord()
    Coord0 = self.node[iPoint].GetCoord0()
    return float(Coord[1]-Coord0[1])

  def getInterfaceNodeDispZ(self, markerID, iVertex):
    """ Desciption. """

    iPoint = self.markers[markerID][iVertex]
    Coord = self.node[iPoint].GetCoord()
    Coord0 = self.node[iPoint].GetCoord0()
    return float(Coord[2]-Coord0[2])

  def getInterfaceNodeVelX(self, markerID, iVertex):
    """ Description """

    iPoint = self.markers[markerID][iVertex]
    Vel = self.node[iPoint].GetVel()
    return float(Vel[0])

  def getInterfaceNodeVelY(self, markerID, iVertex):
    """ Description """

    iPoint = self.markers[markerID][iVertex]
    Vel = self.node[iPoint].GetVel()
    return float(Vel[1])

  def getInterfaceNodeVelZ(self, markerID, iVertex):
    """ Description """

    iPoint = self.markers[markerID][iVertex]
    Vel = self.node[iPoint].GetVel()
    return float(Vel[2])

  def getInterfaceNodeVelXNm1(self, markerID, iVertex):
    """ Description """

    iPoint = self.markers[markerID][iVertex]
    Vel = self.node[iPoint].GetVel_n()
    return float(Vel[0])

  def getInterfaceNodeVelYNm1(self, markerID, iVertex):
    """ Description """

    iPoint = self.markers[markerID][iVertex]
    Vel = self.node[iPoint].GetVel_n()
    return float(Vel[1])

  def getInterfaceNodeVelZNm1(self, markerID, iVertex):
    """ Description """

    iPoint = self.markers[markerID][iVertex]
    Vel = self.node[iPoint].GetVel_n()
    return float(Vel[2])
