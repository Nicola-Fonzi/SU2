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