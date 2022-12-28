#!/usr/bin/env python

## \file imposed_motion.py
#  \brief Class containing possible imposed motions
#  \authors Nicola Fonzi, Vittorio Cavalieri
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

import math

# ----------------------------------------------------------------------
#  Classes
# ----------------------------------------------------------------------

class ImposedMotionClass:

  def __init__(self, time0, typeOfMotion, parameters, mode):

    self.time0 = time0
    self.typeOfMotion = typeOfMotion
    self.mode = mode

    self.amplitude = parameters["AMPLITUDE"]
    self.timeStart = parameters["TIME_START"]
    if "TIME_STOP" in parameters.keys():
      self.timeStop  = parameters["TIME_STOP"]
    else:
      self.timeStop = math.inf

    if self.typeOfMotion == "SINUSOIDAL":
      self.bias = parameters["BIAS"]
      self.frequency = parameters["FREQUENCY"]

    elif self.typeOfMotion == "BLENDED_STEP":
      self.kmax = parameters["K_MAX"]
      self.vinf = parameters["V_INF"]
      self.lref = parameters["L_REF"]
      self.tmax = 2*math.pi/self.kmax*self.lref/self.vinf
      self.omega0 = 1/2*self.kmax

    elif self.typeOfMotion == "BLENDED_PULSE":
      self.kmax = parameters["K_MAX"]
      self.vinf = parameters["V_INF"]
      self.lref = parameters["L_REF"]
      self.tmax = 2 * math.pi / self.kmax * self.lref / self.vinf
      self.omega0 = 1 / 2 * self.kmax
      self.r = parameters["R"]

    elif self.typeOfMotion == "COSINUSOIDAL":
      self.bias = parameters["BIAS"]
      self.frequency = parameters["FREQUENCY"]

    elif self.typeOfMotion == "HARMONIC_EXPONENTIAL":
      self.bias = parameters["BIAS"]
      self.frequency = parameters["FREQUENCY"]
      self.decay = parameters["DECAY"]

    else:
      raise Exception('Imposed function {} not found, please implement it in pysu2_nastran.py'.format(self.typeOfMotion))


  def GetDispl(self, time):
    time = time - self.time0 - self.timeStart
    if self.typeOfMotion == "SINUSOIDAL":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      return self.bias+self.amplitude*math.sin(2*math.pi*self.frequency*time)

    if self.typeOfMotion == "BLENDED_STEP":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      if time < self.tmax:
        return self.amplitude/2.0*(1.0-math.cos(self.omega0*time*self.vinf/self.lref))
      return self.amplitude

    if self.typeOfMotion == "BLENDED_PULSE":
      if (time < 0.0) or (time > self.tmax):
        return 0.0
      if time < self.tmax*self.r:
        modifiedTime = time/(self.r*self.tmax)*math.pi
      else:
        modifiedTime = math.pi + (time-self.r*self.tmax)/(self.r*self.tmax)*math.pi
      return self.amplitude/2.0*(1.0-math.cos(modifiedTime))

    if self.typeOfMotion == 'COSINUSOIDAL':
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      return self.bias+self.amplitude*(1-math.cos(2*math.pi*self.frequency*time))

    if self.typeOfMotion == "HARMONIC_EXPONENTIAL":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      return self.bias+self.amplitude*math.exp(self.decay*time)*(1-math.cos(2*math.pi*self.frequency*time))


  def GetVel(self, time):
    time = time - self.time0 - self.timeStart

    if self.typeOfMotion == "SINUSOIDAL":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      return self.amplitude*math.cos(2*math.pi*self.frequency*time)*2*math.pi*self.frequency

    if self.typeOfMotion == "BLENDED_STEP":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      if time < self.tmax:
        return self.amplitude/2.0*math.sin(self.omega0*time*self.vinf/self.lref)*(self.omega0*self.vinf/self.lref)
      return 0.0

    if self.typeOfMotion == "BLENDED_PULSE":
      if (time < 0.0) or (time > self.tmax):
        return 0.0
      if time < self.tmax * self.r:
        modifiedTime = time / (self.r * self.tmax) * math.pi
      else:
        modifiedTime = math.pi + (time - self.r * self.tmax) / (self.r * self.tmax) * math.pi
      return self.amplitude/2.0*math.sin(modifiedTime)*(math.pi / (self.r * self.tmax))

    if self.typeOfMotion == "COSINUSOIDAL":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      return self.amplitude*math.sin(2*math.pi*self.frequency*time)*2*math.pi*self.frequency

    if self.typeOfMotion == "HARMONIC_EXPONENTIAL":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      return self.amplitude*(self.decay*math.exp(self.decay*time)*(1-math.cos(2*math.pi*self.frequency*time))
             + math.exp(self.decay*time)*2*math.pi*self.frequency*math.sin(2*math.pi*self.frequency*time))

  def GetAcc(self, time):
    time = time - self.time0 - self.timeStart

    if self.typeOfMotion == "SINUSOIDAL":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      return -self.amplitude*math.sin(2*math.pi*self.frequency*time)*(2*math.pi*self.frequency)**2

    if self.typeOfMotion == "BLENDED_STEP":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      if time < self.tmax:
        return self.amplitude/2.0*math.cos(self.omega0*time*self.vinf/self.lref)*(self.omega0*self.vinf/self.lref)**2
      return 0.0

    if self.typeOfMotion == "BLENDED_PULSE":
      if (time < 0.0) or (time > self.tmax):
        return 0.0
      if time < self.tmax * self.r:
        modifiedTime = time / (self.r * self.tmax) * math.pi
      else:
        modifiedTime = math.pi + (time - self.r * self.tmax) / (self.r * self.tmax) * math.pi
      return self.amplitude/2.0*math.cos(modifiedTime)*(math.pi / (self.r * self.tmax))**2

    if self.typeOfMotion == "COSINUSOIDAL":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      return self.amplitude*math.cos(2*math.pi*self.frequency*time)*(2*math.pi*self.frequency)**2

    if self.typeOfMotion == "HARMONIC_EXPONENTIAL":
      if (time < 0.0) or (time > self.timeStop):
        return 0.0
      return self.amplitude*(self.decay**2*math.exp(self.decay*time)*(1-math.cos(2*math.pi*self.frequency*time))
             + 2*self.decay*math.exp(self.decay*time)*2*math.pi*self.frequency*math.sin(2*math.pi*self.frequency*time)
             + (2*math.pi*self.frequency)**2*math.exp(self.decay*time)*math.cos(2*math.pi*self.frequency*time))