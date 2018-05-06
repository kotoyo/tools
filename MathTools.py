import bisect
import numpy as np
import scipy.optimize
import math as m

#---------------------------------------------------
def get_sigma_percent(sigma) :
    if sigma == 1:
        return 68.27
    if sigma == 3:
        return 95.45
    if sigma == 5:
        return 99.73
    print("sigma %f is not supported" % (sigma))

#---------------------------------------------------
def calc_add_errors(xvals1, error1, xvals2, error2) :
    '''
    Calculate error for xvals1 + xvals2
    '''
    if (xvals1.shape != xvals2.shape) :
        print("shape doesn't match")

    add = xvals1 + xvals2
    w2s = error1*error1 + error2*error2
    err = np.sqrt(w2s)
    return add, err

#---------------------------------------------------
def calc_divide_errors(xvals1, error1, xvals2, error2) :
    '''
    Calculate error for xvals1 / xvals2
    '''
    if (xvals1.shape != xvals2.shape) :
        print("shape doesn't match")

    ashape = xvals1.shape
    dim = len(ashape)
    ratios = np.zeros(ashape) 
    sigmas = np.zeros(ashape) 

    if dim == 1: 
        for i, x1 in enumerate(xvals1) :
            if xvals2[i] == 0 :
                ratios[i] = 0
                sigmas[i] = 0
            else :
                ratios[i] = xvals1[i] / xvals2[i] 
                sig2 = (xvals1[i]**2 * error2[i]**2 + xvals2[i]**2 * error1[i]**2) / (xvals2[i]**4)
                sigmas[i] = m.sqrt(sig2) 

    elif dim == 2: 
        for j, y1 in enumerate(xvals1) :
            for i, x1 in enumerate(y1) :
                if xvals2[j][i] == 0 :
                    ratios[j][i] = 0
                    sigmas[j][i] = 0
                else :
                    ratios[j][i] = x1 / xvals2[j][i] 
                    sig2 = (x1**2 * error2[j][i]**2 + xvals2[j][i]**2 * error1[j][i]**2) / (xvals2[j][i]**4)
                    sigmas[j][i] = m.sqrt(sig2) 

    return ratios, sigmas

#---------------------------------------------------
def gaussian(x, norm, mean, sigma): 
    '''
    Calculate gaussian 
    '''
    gauss = norm/m.sqrt(2.0*m.pi)/sigma * np.exp(-((x-mean)/sigma)**2/2)
    return(gauss)

#---------------------------------------------------
def gauss_residuals(param_fit, y, x):
    '''
    Calculate residual of y from a gaussian specified
    by the param_fit
    '''
    norm, mean, sigma = param_fit
    err = (y - (gaussian(x, norm, mean, sigma)))
    return(err)

#---------------------------------------------------
def solid_angle(mincoszen, maxcoszen, minazi = 0, maxazi = 2*m.pi) :
    return (maxcoszen - mincoszen) * (maxazi - minazi)

#---------------------------------------------------
def energy_integral(minelog, maxelog, gamma) :

    mine = 10**minelog 
    maxe = 10**maxelog 
    intg = 0

    if (gamma == 1) :
        # if E^-1 then integral over Emin and Emax is
        intg = m.log(maxe/mine);
    else :
        # if not E^-1 then integral over Emin and Emax is
        intg = (maxe**(1-gamma) - mine**(1-gamma))/(1-gamma)

    return intg
    
#---------------------------------------------------
def one_weight(prim_e, interaction_weight, 
               area_norm, gamma, minelog, maxelog, mincoszen, 
               maxcoszen, minazi=0., maxazi = 2*m.pi) :
    eintg = energy_integral(minelog, maxelog, gamma)
    solid = solid_angle(mincoszen, maxcoszen, minazi, maxazi)
    spectrum = prim_e ** (-gamma) 
    return (interaction_weight/spectrum) * (eintg * solid * area_norm)



