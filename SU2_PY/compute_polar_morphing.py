#!/usr/bin/env python

## \file fsi_computation.py
#  \brief Python wrapper code for FSI computation by coupling a third-party structural solver to SU2.
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
#
#
# Authors: Nicola Fonzi, Vittorio Cavalieri

import fsi_computation as run
import numpy as np
from math import *
import os
import shutil

def main():

    # Main variables
    Nalpha = 10
    NactuationStep = 5
    HOME = os.getcwd()
    FluidCfg = HOME+"/fluid"
    SolidCfg = HOME+"/solid"

    # Initialisation
    alpha = np.linspace(0.0,10.0,Nalpha)

    for AoA in alpha:
        os.chdir(HOME)
        HOMEALPHA = os.getcwd()+"/Alpha={:2.1f}".format(AoA)
        os.mkdir(HOMEALPHA)
        writeFluidCfg(AoA,FluidCfg)
        for actuation in range(NactuationStep):
            os.chdir(HOMEALPHA)
            writeSolidCfg(actuation,SolidCfg)
            HOMEACT = os.getcwd()+"/Actuation={:2.1f}".format(actuation)
            os.mkdir(HOMEACT)
            shutil.copyfile(HOME+"/fluid_new.cfg",HOMEACT+"/fluid_new.cfg")
            shutil.copyfile(HOME+"/solid_new.cfg",HOMEACT+"/solid_new.cfg")
            os.chdir(HOMEACT)
            run.main()
    os.remove(HOME+"/fluid_new.cfg")
    os.remove(HOME+"/solid_new.cfg")

def replace_line(file_name, line_num, text):
    lines = open(file_name+".cfg", 'r').readlines()
    lines[line_num] = text
    out = open(file_name+"_new.cfg", 'w')
    out.writelines(lines)
    out.close()

def writeFluidCfg(alpha,FluidCfg):
    line_num = 0
    with open(FluidCfg+".cfg") as configfile:
      while 1:
        line = configfile.readline()
        if not line:
          break
        pos = line.find('AoA')
        if pos  >=  0:
          break
        line_num = line_num + 1
    replace_line(FluidCfg,line_num,"A0A = "+str(alpha))

def writeSolidCfg(actuation,SolidCfg):
    line_num = 0
    with open(SolidCfg+".cfg") as configfile:
      while 1:
        line = configfile.readline()
        if not line:
          break
        pos = line.find('INITIAL_MODES')
        if pos  >=  0:
          break
        line_num = line_num + 1
    replace_line(SolidCfg,line_num,"INITIAL_MODES = {"+str(actuation)+":1.0}")


if __name__ == '__main__':
    main()
