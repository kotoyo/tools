import numpy as np

#___________________________________________________
def get_nufatetype(pdg) :
    """
    conversion from int pdg code to 
    nuFATE's flavor index.
    nufate index:
        NuE 1, NuEBar -1
        NuMu 2, NuMuBar -2
        NuTau 3, NuTauBar -3
 
    Parameters
    ----------
    pdg : int 
        NuE 12, NuEBar -12 
        NuMu 14, NuMuBar -14 
        NuTau 16, NuTauBar -16 

    """
    return int((abs(pdg)%10)/2) * (pdg/abs(pdg))

#___________________________________________________
def get_default_flux(fluxtype, pdg, enodes, coszen) :

    from icecube import dataclasses
    from icecube import NewNuFlux
    import DefTools as DefT

    gamma = 2.3
    ptype = DefT.GetI3ParticleType(pdg)
    
    if fluxtype == "conv" :
        nnf = NewNuFlux.makeFlux("honda2006")
        nnf.relative_kaon_contribution = 1.0
        nnf.knee_reweighting_model="gaisserH3a_elbert"
        flux = np.array([nnf.getFlux(ptype,e,coszen) for e in enodes])
        return flux

    elif fluxtype == "prompt" :
        nnf = NewNuFlux.makeFlux("sarcevic_std")
        nnf.knee_reweighting_model="gaisserH3a_elbert"
        flux = np.array([nnf.getFlux(ptype,e,coszen) for e in enodes])
        return flux
    
    else :
        flux = 1e-18*np.array([(e/1e5)**-gamma for e in enodes])
        return flux

        
        




'''
pdgs = [-12, 12, -14, 14, -16, 16]
for p in pdgs :
   print("nufate index for %d is %d" % (p, get_nufatetype(p))) 
'''
