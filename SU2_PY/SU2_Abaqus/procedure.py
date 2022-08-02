import os
from math import *


#if CSD_Solver == 'AEROELASTIC ???':
#      from SU2_Abaqus import pysu2_abaqus
import pysu2_abaqus


CSD_ConFile = 'solid_abq.cfg'
SolidSolver = pysu2_abaqus.Solver(CSD_ConFile,False)


#FSIInterface = FSI.Interface(FSI_config, FluidSolver, SolidSolver, have_MPI)		#SolidSolver non usato!


#FSIInterface.connect(FSI_config, FluidSolver, SolidSolver)
solidInterfaceIdentifier = SolidSolver.getFSIMarkerID()
nLocalSolidInterfaceNodes = SolidSolver.getNumberOfSolidInterfaceNodes(solidInterfaceIdentifier)
#if SolidSolver.IsAHaloNode(self.solidInterfaceIdentifier, iVertex): ...		# TODO halo


#FSIInterface.interfaceMapping(FluidSolver, SolidSolver, FSI_config)
for iVertex in range(nLocalSolidInterfaceNodes):
  GlobalIndex = SolidSolver.getVertexGlobalIndex(solidInterfaceIdentifier, iVertex)
  posx, posy, posz = SolidSolver.getInterfaceNodePosInit(solidInterfaceIdentifier, iVertex)


#FSIInterface.UnsteadyFSI(FSI_config, FluidSolver, SolidSolver)		# modify name!!
SolidSolver.setInitialDisplacements()
#FSIInterface.getSolidInterfaceDisplacement(SolidSolver)
for iVertex in range(nLocalSolidInterfaceNodes):
  GlobalIndex = SolidSolver.getVertexGlobalIndex(solidInterfaceIdentifier, iVertex)
  newDispx, newDispy, newDispz = SolidSolver.getInterfaceNodeDisp(solidInterfaceIdentifier, iVertex)
# --- External temporal loop --- #
deltaT = 0.50		# fictitious time step
totTime = 1.0		# physical simulation time
NbFSIIterMax = 3	# maximum number of FSI iteration (for each time step)
FSITolerance = 0.00001		# f/s interface tolerance
NbTimeIter = int(totTime/deltaT)		# number of time iterations
time = 0.0					# initial time
TimeIter = 0				# initial time iteration
varCoordNorm = 0.0			# FSI residual
FSIConv = False				# FSI convergence flag
while TimeIter <= NbTimeIter:

      NbFSIIter = NbFSIIterMax
      FSIIter = 0
      FSIConv = False

      # --- Internal FSI loop --- #
      while FSIIter <= (NbFSIIter-1):

              print("\n>>>> Time iteration {} / FSI iteration {} <<<<".format(TimeIter,FSIIter))

              # --- Mesh morphing step (displacements interpolation, displacements communication, and mesh morpher call) --- #
              print('\nPerforming dynamic mesh deformation (ALE)...\n')
              # --- Fluid solver call for FSI subiteration --- #
              print('\nLaunching fluid solver for one single dual-time iteration...')

              # --- Surface fluid loads interpolation and communication --- #
              print('\nProcessing interface fluid loads...\n')
              #FSIInterface.setSolidInterfaceLoads(SolidSolver, FSI_config)
              GlobalIndex = int()
              localIndex = 0
              for iVertex in range(nLocalSolidInterfaceNodes):
                GlobalIndex = SolidSolver.getVertexGlobalIndex(solidInterfaceIdentifier, iVertex)
                Fx = 0.1*(TimeIter+0.3)
                Fy = 0.2*(FSIIter+0.1)
                Fz = 0.3*(FSIIter+0.1)
                SolidSolver.applyload(iVertex, Fx, Fy, Fz)
                localIndex += 1

              # --- Solid solver call for FSI subiteration --- #
              print('\nLaunching solid solver for a single time iteration...\n')
              SolidSolver.run(time)

              # --- Compute and monitor the FSI residual --- #
              #varCoordNorm = FSIInterface.computeSolidInterfaceResidual(SolidSolver)
              varCoordNorm = sqrt(1.0/(FSIIter+1))
              print('\nFSI displacement norm : {}\n'.format(varCoordNorm))
  
              if varCoordNorm < FSITolerance:
                FSIConv = True
                break

              # --- Relax the solid position --- #
              print('\nProcessing interface displacements...\n')

              FSIIter += 1
      # --- End OF FSI loop --- #

      # --- Update the FSI history file --- #
      #FSIInterface.writeFSIHistory(TimeIter, time, varCoordNorm, FSIConv)

      # --- Output the solid solution before thr next time step --- #
      SolidSolver.writeSolution(time, TimeIter, FSIIter)

      # --- Displacement predictor for the next time step and update of the solid solution --- #
      #FSIInterface.displacementPredictor(FSI_config, SolidSolver, deltaT)	# sostituire con qualcosa altro??

      SolidSolver.updateSolution()

      TimeIter += 1
      time += deltaT
#--- End of the temporal loop --- #





stop

#FSIInterface.SteadyFSI(FSI_config, FluidSolver, SolidSolver)
SolidSolver.setInitialDisplacements()
#FSIInterface.getSolidInterfaceDisplacement(SolidSolver)
for iVertex in range(nLocalSolidInterfaceNodes):
  GlobalIndex = SolidSolver.getVertexGlobalIndex(solidInterfaceIdentifier, iVertex)
  newDispx, newDispy, newDispz = SolidSolver.getInterfaceNodeDisp(solidInterfaceIdentifier, iVertex)
# --- Internal FSI loop --- #
FSIIter = 0
NbFSIIterMax = 3
FSITolerance = 0.00001
while FSIIter < NbFSIIterMax:
  print("\n>>>> FSI iteration {} <<<<".format(FSIIter))
  print('\nLaunching fluid solver for a steady computation...')
  # --- Surface fluid loads interpolation and communication ---#
  #FSIInterface.setSolidInterfaceLoads(SolidSolver, FSI_config)
  GlobalIndex = int()
  localIndex = 0
  for iVertex in range(nLocalSolidInterfaceNodes):
    GlobalIndex = SolidSolver.getVertexGlobalIndex(solidInterfaceIdentifier, iVertex)
    Fx = 1.*(FSIIter+0.3)
    Fy = 2.*(FSIIter+0.3)
    Fz = 3.*(FSIIter+0.3)
    SolidSolver.applyload(iVertex, Fx, Fy, Fz)
    localIndex += 1
  # --- Solid solver call for FSI subiteration --- #
  print('\nLaunching solid solver for a static computation...\n')
  SolidSolver.run(0.0)
  SolidSolver.writeSolution(0.0, 0, FSIIter)
  # --- Compute and monitor the FSI residual --- #
  #varCoordNorm = FSIInterface.computeSolidInterfaceResidual(SolidSolver)
  varCoordNorm = sqrt(1.0/(FSIIter+1))
  for iVertex in range(nLocalSolidInterfaceNodes):
    predDispx, predDispy, predDispz = SolidSolver.getInterfaceNodeDisp(solidInterfaceIdentifier, iVertex)
  print('\nFSI displacement norm : {}\n'.format(varCoordNorm))
  if varCoordNorm < FSITolerance:
    break
  # --- Relax the solid displacement and update the solid solution --- #
  print('\nProcessing interface displacements...\n')
  SolidSolver.updateSolution()
  #
  FSIIter += 1



#FSIInterface.MapModes(FSI_config, FluidSolver, SolidSolver)	# non serve (cosi come non servono i metodi di SolidSolver chiamati al suo interno --> rimuoverli)


#SolidSolver.exit()

















