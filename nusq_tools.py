import numpy as np

#___________________________________________________
# unit conversion
GeV = 1.0
eV = GeV * 1e-9

#___________________________________________________
def get_nusqtype(ptype) :
    """
    conversion from int pdg code or I3Particle type to 
    nuSQuIDS's nuindex and flavorindex
    returns nuindex, flavorindex
    """
    if ptype == 12 :
        return 0, 0
    if ptype == -12 :
        return 1, 0
    if ptype == 14 :
        return 0, 1
    if ptype == -14 :
        return 1, 1
    if ptype == 16 :
        return 0, 2
    if ptype == -16 :
        return 1, 2

#___________________________________________________
def get_initial_spectrum(coszen, ebins_GeV, flavorindex, fluxobj, delta=0, nnu_per_flavor=2, numnu=3, typeindex=-1) :
    """ Generate initial state for nuSQuIDs multi energy
    
    Parameters
    ----------

    coszen : float
        coszenith of track

    ebins_GeV : numpy array
        energy bins in GeV

    flavorindex : int
        0 for NuE flavor, 1 for NuMu flavor, 
        2 for NuTau flavor

    fluxobj : int or float or obj
        0 : constant flux = 1
        float : powerlaw index 
        obj : NewNuFlux obj
 
    delta : float
        CR index change, active only for NewNuFlux

    nnu_per_flavor : int
        number of neutrinos per flavor
        default is 2 for neutrino and anti-neutrino

    numnu : int
        number of neutrino flavors 
        default is 3 for NuE, NuMu, NuTau

    typeindex: int
        -1 for both Nu and NuBar,
        0 for both Nu, 1 for NuBar

    Return
    ----------

    inistate : 3-dim numpy array 

    """
    if type(fluxobj) != float or type(fluxobj) != int :
        from icecube import NewNuFlux
        import nusq_icetray_tools as NIT

    inistate = np.zeros((len(ebins_GeV), nnu_per_flavor, numnu))
    for ei, e in enumerate(ebins_GeV) : # energy in GeV
        for ri in range(nnu_per_flavor) : # neutrino or anti-neutrino
            if ri < 0 or ri == typeindex :
                for fi in range(numnu):       # 0:NuE flavor, 1:NuMu flavor, 2:NuTau flavor
                    flux = 0
                    if fi == flavorindex:
                        if type(fluxobj) == float or type(fluxobj) == int :
                            flux = 1e-18*(e/1e5)**(-float(fluxobj))
                        else :
                            ptype = NIT.get_ptype(ri, fi)
                            flux = fluxobj.getFlux(ptype,e,coszen) * e**delta
                    # update flux
                    inistate[ei][ri][fi] = flux

    return inistate



#___________________________________________________
def get_initial_spectrum_Atm(coszenbins, ebins_GeV, flavorindex, fluxobj, delta=0, nnu_per_flavor=2, numnu=3, typeindex = -1) :
    """ Generate initial state for nuSQuIDsAtm
    
    Parameters
    ----------

    coszenbins : numpy array
        cosine zenith bins

    ebins_GeV : numpy array
        energy bins in GeV

    flavorindex : int
        0 for NuE flavor, 1 for NuMu flavor, 
        2 for NuTau flavor

    fluxobj : int or float or obj
        0 : constant flux = 1
        float : powerlaw index 
        obj : NewNuFlux obj
 
    delta : float
        CR index change, active only for NewNuFlux

    nnu_per_flavor : int
        number of neutrinos per flavor
        default is 2 for neutrino and anti-neutrino

    numnu : int
        number of neutrino flavors 
        default is 3 for NuE, NuMu, NuTau

    typeindex: int
        -1 for both Nu and NuBar,
        0 for both Nu, 1 for NuBar

    Return
    ----------

    inistate : 4-dim numpy array 

    """
    if type(fluxobj) != float or type(fluxobj) != int :
        from icecube import NewNuFlux
        import nusq_icetray_tools as NIT

    inistate = np.zeros((len(coszenbins),len(ebins_GeV), nnu_per_flavor, numnu))
    for ci, c in enumerate(coszenbins) :
        for ei, e in enumerate(ebins_GeV) : # energy in GeV
            for ri in range(nnu_per_flavor) : # neutrino or anti-neutrino
                if ri < 0 or ri == typeindex :
                    for fi in range(numnu):       # 0:NuE flavor, 1:NuMu flavor, 2:NuTau flavor
                        flux = 0
                        if fi == flavorindex:
                            if type(fluxobj) == float or type(fluxobj) == int :
                                flux = 1e-18*(e/1e5)**(-float(fluxobj))
                            else :
                                ptype = NIT.get_ptype(ri, fi)
                                flux = fluxobj.getFlux(ptype,e,c) * e**delta
                        # update flux
                        inistate[ci][ei][ri][fi] = flux

    return inistate

#___________________________________________________
def get_endstate(nsq_multi, ebins_eV, nnu_per_flavor=2, numnu=3) :
    """ Generate initial state for nuSQuIDs multi energy
    
    Parameters
    ----------
    
    nsq_multi: nuSQuIDs multi energy object

    ebins_eV : numpy array
        energy bins in eV

    nnu_per_flavor : int
        number of neutrinos per flavor
        default is 2 for neutrino and anti-neutrino

    numnu : int
        number of neutrino flavors 
        default is 3 for NuE, NuMu, NuTau

    Return
    ----------

    endstate : 3-dim numpy array 

    """

    endstate = np.zeros((nsq_multi.GetNumE(), nnu_per_flavor, numnu))
    for ei, e in enumerate(ebins_eV) : # use energy in eV for nuSQuIDS
        for ri in range(nnu_per_flavor) : # neutrino or anti-neutrino
            for fi in range(numnu):       # 0:NuE flavor, 1:NuMu flavor, 2:NuTau flavor
                endstate[ei][ri][fi] = nsq_multi.EvalFlavor(fi, e, ri)

    return endstate

#___________________________________________________
def get_endstate_Atm(nsq_atm, coszenbins, ebins_eV, nnu_per_flavor=2, numnu=3) :
    """ Generate initial state for nuSQuIDsAtm
    
    Parameters
    ----------
    
    nsq_atm : nuSQuIDsAtm object

    coszenbins : numpy array
        cosine zenith bins

    ebins_eV : numpy array
        energy bins in eV

    nnu_per_flavor : int
        number of neutrinos per flavor
        default is 2 for neutrino and anti-neutrino

    numnu : int
        number of neutrino flavors 
        default is 3 for NuE, NuMu, NuTau

    Return
    ----------

    endstate : 4-dim numpy array 

    """

    endstate = np.zeros((nsq_atm.GetNumCos(),nsq_atm.GetNumE(), nnu_per_flavor, numnu))
    for ci, c in enumerate(coszenbins) :
        for ei, e in enumerate(ebins_eV) : # use energy in eV for nuSQuIDS
            for ri in range(nnu_per_flavor) : # neutrino or anti-neutrino
                for fi in range(numnu):       # 0:NuE flavor, 1:NuMu flavor, 2:NuTau flavor
                    endstate[ci][ei][ri][fi] = nsq_atm.EvalFlavor(fi, c, e, ri)

    return endstate



