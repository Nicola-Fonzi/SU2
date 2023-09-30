#!/usr/bin/env python

## \file FSI_utils.py
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

import numpy as np

class Point:
  """
  Class containing data regarding all the structural nodes.
  Coord0: Coordinates at the initial time iteration.
  Coord: Coordinates at the current time iteration.
  Coord_n: Coordinates at the previous time iteration.
  Vel: Velocity at the current time iteration.
  Vel_n: Velocity at the previous time iteration.
  Force: Nodal force provided by the aerodynamics.
  ID: ID of the node.
  CP: Coordinate system definition of the position.
  CD: Coordinate system definition of the output coming from Nastran.
  """

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


class RefSystem:

  def __init__(self):
    self.CID = 0
    self.RID = 0
    self.Origin = np.array([[0.],[0.],[0.]])
    self.Rot = np.array([[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]])

  def SetOrigin(self,A):
    AX , AY , AZ = A
    self.Origin[0] =  AX
    self.Origin[1] =  AY
    self.Origin[2] =  AZ

  def SetRotMatrix(self,x,y,z):
    self.Rot = np.array([[x[0],y[0],z[0]],[x[1],y[1],z[1]],[x[2],y[2],z[2]]])

  def SetCID(self,CID):
    self.CID = CID

  def SetRID(self,RID):
    self.RID = RID

  def GetOrigin(self):
    return self.Origin

  def GetRotMatrix(self):
    return self.Rot

  def GetRID(self):
    return self.RID

  def GetCID(self):
    return self.CID