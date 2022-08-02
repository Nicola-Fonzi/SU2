from pysu2_utils import *
from abaqus_modules import *
import pickle

def readNodes(modelName,inputFileName,partName):
    
    
    mdb.ModelFromInputFile(name=modelName, inputFileName=inputFileName)
    myModel = mdb.models[modelName]
    
    nodes = myModel.parts[partName].nodes
    
    dict_index = {}
    for i in range(len(nodes)):
      label = nodes[i].label
      dict_index[label] = i
    
    node = []
    nPoint = int()
    
    for label in dict_index:
      index = dict_index[label]
      myModel.parts[partName].Set(name='NODE-'+str(label), nodes=nodes[index:index+1])
    
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
    
    for markerTag in myModel.parts[partName].sets.keys():
      if 'SET' in markerTag:	# TODO meglio (per evitare di controllare tutti i set)
        markers[markerTag] = []
        for item_node in myModel.parts[partName].sets[markerTag].nodes:
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
    modelName = sys.argv[-3]
    inputFileName = sys.argv[-2]
    partName = sys.argv[-1]
    readNodes(modelName,inputFileName,partName)