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

from SU2_Abaqus.abaqus_modules import *
import pickle
from FSI_tools.FSI_utils import Point

def readNodes(modelName,inputFileName,flexPartName,rigidPartName,monitorSet,FSI_marker,saveCaeFlag):
    
    
    mdb.ModelFromInputFile(name=modelName, inputFileName=inputFileName)
    myModel = mdb.models[modelName]
    myFlexPart = myModel.parts[flexPartName]
    if rigidPartName != 'none':
      myRigidPart = myModel.parts[rigidPartName]
    else:
      myRigidPart = None
    myAssembly = myModel.rootAssembly

    node = []
    nPoint = int()
    ID_monitor = None

    features = list()
    if myRigidPart is None:
      if not (FSI_marker in myFlexPart.sets.keys() or FSI_marker in myAssembly.sets.keys()):
        raise Exception("Set {} was not found in the part nor in the assembly".format(FSI_marker))
      elif FSI_marker in myFlexPart.sets.keys():
        features.append(myFlexPart)
      else:
        features.append(myAssembly)
    else:
      if not (FSI_marker in myFlexPart.sets.keys() or FSI_marker in myRigidPart.sets.keys()):
        raise Exception("Set {} was not found in the parts".format(FSI_marker))
      if FSI_marker in myFlexPart.sets.keys():
        features.append(myFlexPart)
      if FSI_marker in myRigidPart.sets.keys():
        features.append(myRigidPart)


    for myFeature in features:
      if myFeature.name == rigidPartName:
        offset = 100000
      else:
        offset = 0
      nodes = myFeature.sets[FSI_marker].nodes
    
      dict_index = {}
      for i in range(len(nodes)):
        label = nodes[i].label
        dict_index[label] = i


      for label in dict_index:
        index = dict_index[label]
        
        myFeature.Set(name='NODE-'+str(offset+label), nodes=nodes[index:index+1])
	  
        if (myFeature.name != rigidPartName) and (ID_monitor is None) and (label == myFeature.sets[monitorSet].nodes[0].label):
          ID_monitor = label
	  
        node.append(Point())
        ID = offset + label
        x = nodes[index].coordinates[0]
        y = nodes[index].coordinates[1]
        z = nodes[index].coordinates[2]
        node[nPoint].SetCoord((x,y,z))
        node[nPoint].SetID(ID)
        node[nPoint].SetCoord0((x,y,z))
        node[nPoint].SetCoord_n((x,y,z))
        nPoint += 1
    
    if ID_monitor is None:
      raise Exception("MONITOR_SET {} was not found".format(monitorSet))
    
    markers = {}
    nMarker = int()
    
    markerTag = FSI_marker
    markers[markerTag] = []
    for myFeature in features:
      if myFeature.name == rigidPartName:
        offset = 100000
      else:
        offset = 0
      for item_node in myFeature.sets[markerTag].nodes:
        ID = offset + item_node.label
        for iPoint in range(nPoint):
          if node[iPoint].GetID() == ID:
            break
        if (iPoint == (nPoint-1)) and (node[iPoint].GetID() != ID):
          raise Exception("Point {} in the set {} was not found in the mesh".format(ID, markerTag))
        markers[markerTag].append(iPoint)
        if ID == ID_monitor:
          iVertex_monitor = len(markers[markerTag])-1

    pickle.dump(node, open('node.p', 'wb'))
    pickle.dump(markers, open('markers.p', 'wb'))
    
    nodeList = markers[FSI_marker]
    pickle.dump(nodeList, open('nodeList.p', 'wb'))
    
    with open('monitor.txt', 'w') as f:
      f.write(str(iVertex_monitor))

    if saveCaeFlag:
      pathName = '{}.cae'.format(modelName)
      mdb.saveAs(pathName=pathName)


if __name__ == "__main__":
    modelName = sys.argv[-7]
    inputFileName = sys.argv[-6]
    flexPartName = sys.argv[-5]
    rigidPartName = sys.argv[-4]
    monitorSet = sys.argv[-3]
    FSI_marker = sys.argv[-2]
    if sys.argv[-1] == 'True':
      saveCaeFlag = True
    else:
      saveCaeFlag = False
    readNodes(modelName,inputFileName,flexPartName,rigidPartName,monitorSet,FSI_marker,saveCaeFlag)