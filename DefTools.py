from enum import Enum
import numpy as np

Na = 6.02214076e+23 # mol-1, 20190520  
 
#-------------------------------------------------
class ParticleType(Enum) :
    '''
    typedef for interaction type
    This definition must be same as NuGen's definition
    '''
    EMinus   = 11  
    EPlus    = -11  
    NuE      = 12  
    NuEBar   = -12  
    MuMinus  = 13  
    MuPlus   = -13  
    NuMu     = 14  
    NuMuBar  = -14  
    TauMinus = 15  
    TauPlus  = -15  
    NuTau    = 16  
    NuTauBar = -16  
    Hadron   = -2000001006  

#-------------------------------------------------
def GetI3ParticleType(pdg) :
    from icecube import dataclasses

    if pdg == 11 :
        return dataclasses.I3Particle.EMinus
    elif pdg == -11 :
        return dataclasses.I3Particle.EMinus
    elif pdg == 12 :
        return dataclasses.I3Particle.NuE
    elif pdg == -12 :
        return dataclasses.I3Particle.NuEBar
    elif pdg == 13 :
        return dataclasses.I3Particle.MuMinus
    elif pdg == -13 :
        return dataclasses.I3Particle.MuPlus
    elif pdg == 14 :
        return dataclasses.I3Particle.NuMu
    elif pdg == -14 :
        return dataclasses.I3Particle.NuMuBar
    elif pdg == 15 :
        return dataclasses.I3Particle.TauMinus
    elif pdg == -15 :
        return dataclasses.I3Particle.TauPlus
    elif pdg == 16 :
        return dataclasses.I3Particle.NuTau
    elif pdg == -16 :
        return dataclasses.I3Particle.NuTauBar
    elif pdg == -2000001006 :
        return dataclasses.I3Particle.Hadron
    else :
        print("Particletype ", pdg, " doens't found")

#-------------------------------------------------
def IsNu(pdgcode) :
    nutypes = [ParticleType.NuE.value, 
               ParticleType.NuMu.value, 
               ParticleType.NuTau.value]
    if abs(pdgcode) in nutypes :
        return True
    return False

#-------------------------------------------------
def IsHadron(pdgcode) :
    if pdgcode == ParticleType.Hadron.value:
        return True
    return False

#-------------------------------------------------
def IsLepton(pdgcode) :
    leptype = [ParticleType.EMinus.value,
               ParticleType.NuE.value,
               ParticleType.MuMinus.value, 
               ParticleType.NuMu.value, 
               ParticleType.TauMinus.value, 
               ParticleType.NuTau.value] 
    if abs(pdgcode) in leptype:
        return True
    return False

#-------------------------------------------------
def IsChargedLepton(pdgcode) :
    charged = [ParticleType.EMinus.value,
               ParticleType.MuMinus.value, 
               ParticleType.TauMinus.value]
    if abs(pdgcode) in charged:
        return True
    return False

#-------------------------------------------------
def IsCharged(pdgcode) :
    return (IsChargedLepton(pdgcode) or IsHadron(pdgcode)) 

#-------------------------------------------------
def IsCharged(pdgcode) :
    return (IsChargedLepton(pdgcode) or IsHadron(pdgcode)) 



