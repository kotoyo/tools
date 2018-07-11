import numpy as np
from icecube import dataclasses

#___________________________________________________
def get_ptype(nuindex, flavorindex) :
    """ conversion from nuSQuIDS's nuindex & flavorindex to I3Particle
    """
    if flavorindex == 0 :
        if nuindex == 0 :
           return dataclasses.I3Particle.NuE
        elif nuindex == 1 :
           return dataclasses.I3Particle.NuEBar
    elif flavorindex == 1 :
        if nuindex == 0 :
           return dataclasses.I3Particle.NuMu
        elif nuindex == 1 :
           return dataclasses.I3Particle.NuMuBar
    elif flavorindex == 2 :
        if nuindex == 0 :
           return dataclasses.I3Particle.NuTau
        elif nuindex == 1 :
           return dataclasses.I3Particle.NuTauBar

#___________________________________________________
def get_nusqtype(ptype) :
    """
    conversion from int pdg code or I3Particle type to 
    nuSQuIDS's nuindex and flavorindex
    returns nuindex, flavorindex
    """
    if ptype == 12 or ptype == dataclasses.I3Particle.NuE :
        return 0, 0
    if ptype == -12 or ptype == dataclasses.I3Particle.NuEBar :
        return 1, 0
    if ptype == 14 or ptype == dataclasses.I3Particle.NuMu :
        return 0, 1
    if ptype == -14 or ptype == dataclasses.I3Particle.NuMuBar :
        return 1, 1
    if ptype == 16 or ptype == dataclasses.I3Particle.NuTau :
        return 0, 2
    if ptype == -16 or ptype == dataclasses.I3Particle.NuTauBar :
        return 1, 2


