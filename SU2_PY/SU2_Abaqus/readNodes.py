#!/usr/bin/env python

## \file readNodes.py
#  \brief Reader for nodes database
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
import pickle
from FSI_tools.FSI_utils import Point

def readNodes(modelName,inputFileName,partName,FSI_marker):
    
    
    mdb.ModelFromInputFile(name=modelName, inputFileName=inputFileName)
    myModel = mdb.models[modelName]
    myPart = myModel.parts[partName]

    nodes = myPart.nodes
    
    dict_index = {}
    for i in range(len(nodes)):
      label = nodes[i].label
      dict_index[label] = i
    
    node = []
    nPoint = int()
    
    for label in dict_index:
      index = dict_index[label]
      myPart.Set(name='NODE-'+str(label), nodes=nodes[index:index+1])
      
      node.append(Point())
      ID = label
      x = nodes[index].coordinates[0]
      y = nodes[index].coordinates[1]
      z = nodes[index].coordinates[2]
      node[nPoint].SetCoord((x,y,z))
      node[nPoint].SetID(ID)
      node[nPoint].SetCoord0((x,y,z))
      node[nPoint].SetCoord_n((x,y,z))
      nPoint += 1
    
    #pos = line.find('CORD2R')
    #if pos == 30:
    #  line = line.strip('\r\n')
    #  self.refsystems.append(RefSystem())
    #  line = line[30:]
    #  CID = int(line[8:16])
    #  self.refsystems[self.nRefSys].SetCID(CID)
    #  RID = int(line[16:24])
    #  if RID!=0:
    #    raise Exception('ERROR: Reference system {} must be defined with respect to global reference system'.format(CID))
    #  self.refsystems[self.nRefSys].SetRID(RID)
    #  AX = nastran_float(line[24:32])
    #  AY = nastran_float(line[32:40])
    #  AZ = nastran_float(line[40:48])
    #  BX = nastran_float(line[48:56])
    #  BY = nastran_float(line[56:64])
    #  BZ = nastran_float(line[64:72])
    #  z_direction = np.array([BX-AX,BY-AY,BZ-AZ])
    #  z_direction = z_direction/linalg.norm(z_direction)
    #  line = meshfile.readline()
    #  line = line.strip('\r\n')
    #  line = line[30:]
    #  CX = nastran_float(line[8:16])
    #  CY = nastran_float(line[16:24])
    #  CZ = nastran_float(line[24:32])
    #  y_direction = np.cross(z_direction,[CX-AX,CY-AY,CZ-AZ])
    #  y_direction = y_direction/linalg.norm(y_direction)
    #  x_direction = np.cross(y_direction,z_direction)
    #  x_direction = x_direction/linalg.norm(x_direction)
    #  self.refsystems[self.nRefSys].SetRotMatrix(x_direction,y_direction,z_direction)
    #  self.refsystems[self.nRefSys].SetOrigin((AX,AY,AZ))
    #  self.nRefSys += 1
    #  continue
    
    markers = {}
    nMarker = int()
    
    for markerTag in myPart.sets.keys():
      if FSI_marker == markerTag:	# TODO meglio (per evitare di controllare tutti i set)
        markers[markerTag] = []
        for item_node in myPart.sets[markerTag].nodes:
          ID = item_node.label
          for iPoint in range(nPoint):
            if node[iPoint].GetID() == ID:
              break
          if (iPoint == (nPoint-1)) and (node[iPoint].GetID() != ID):
            raise Exception("Point {} in the set {} was not found in the mesh".format(ID,markerTag))
          markers[markerTag].append(iPoint)
        nMarker += 1

    pickle.dump(node, open('node.p','wb'))
    pickle.dump(markers, open('markers.p','wb'))
    
    pathName = '{}.cae'.format(modelName)
    mdb.saveAs(pathName=pathName)


if __name__ == "__main__":
    modelName = sys.argv[-4]
    inputFileName = sys.argv[-3]
    partName = sys.argv[-2]
    FSI_marker = sys.argv[-1]
    readNodes(modelName,inputFileName,partName,FSI_marker)