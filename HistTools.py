import numpy as np
import MathTools as MT

#--------------------------------------------------------------------
def make_1D_hist(xvals, nx, weights=[], x_range=(-1, -1), xbins=[]) :
    '''
    Generate 1D histogram with weighted error 
    and standard deviation (for now it is sqrt(yval))
    '''
    (xmin, xmax) = x_range
    if (xmin == xmax) :
        xmin = min(xvals.tolist())
        xmax = max(xvals.tolist())
        diff = xmax - xmin
        xmin -= 0.05*diff
        xmax += 0.05*diff
    if len(weights) == 0 :
        weights = np.ones(len(xvals))

    yval = []
    if len(xbins) > 0 :
        yval, bins = np.histogram(xvals, bins=xbins, weights=weights)
    else :
        yval, bins = np.histogram(xvals, nx, weights=weights, range=(xmin,xmax))

    w2s = np.zeros(len(yval))
    #print yval
    #print weights 

    # calc weighted errors
    #print bins
    for i, v in enumerate(xvals) :
        if v < xmin or v > xmax :
            continue
        index = bisect.bisect_left(bins, v)
        index -= 1
        #print("v %f index %d binmin %f binmax %f" %(v, index, bins[index], bins[index+1]))
        w2 = weights[i]**2
        w2s[index] += w2

    # convert sum(w2) to sigma
    errors = [m.sqrt(ww) for ww in w2s]
    #print errors

    # generate statistical standard deviation (1 sigma)
    staterrs = np.sqrt(yval)
   
    return yval, bins, errors, staterrs


#--------------------------------------------------------------------
def get_2DHist_axis(xmin, xmax,ymin, ymax, nx, ny) :
    '''
    Generate 2D histogram's drawing axis.
    '''
    xaxis, yaxis = np.mgrid[xmin:xmax:(nx+1)*1j, ymin:ymax:(ny+1)*1j]
    return xaxis, yaxis

#--------------------------------------------------------------------
def get_2DHist_axis_from_bins(xbins,ybins) :
    '''
    Generate 2D histogram's drawing axis.
    Note that the order of return values and
    arguments of np.meshgrid must be this order
    to get correct figure with plt.pcolormesh.
    '''
    yaxis, xaxis = np.meshgrid[ybins, xbins]
    return xaxis, yaxis


#--------------------------------------------------------------------
def make_2D_hist(xvals, yvals, nx, ny, weights=[], x_range=(-1,-1), y_range=(-1,-1)) :
    '''
    Generate 2D histogram with weighted error 
    and standard deviation (for now it is sqrt(yval))
    returns :
    xmeshgrid (2D)
    ymeshgrid (2D)
    weights (2D)
    weighted errors for mean value (2D)
    statistical errors (2D)
    xbins (1D) = xmeshgrid[0]
    ybins (1D) = ymeshgrid[0]
    '''

    xmin = x_range[0]
    xmax = x_range[1]
    ymin = y_range[0]
    ymax = y_range[1]

    if (xmin == xmax) :
        xmin = min(xvals.tolist())
        xmax = max(xvals.tolist())
    if (ymin == ymax) :
        ymin = min(yvals.tolist())
        ymax = max(yvals.tolist())

    dx = float(xmax - xmin) / nx
    dy = float(ymax - ymin) / ny
    zval = np.zeros((nx, ny))
    w2s = np.zeros(zval.shape)

    if len(weights) == 0 :
        weights = np.ones(xvals.shape)

    #assert(len(xvals) == len(yvals)) 
    #assert(len(xvals) == len(weights))

    print xvals, yvals 
    i = 0
    for i, xvalue in enumerate(xvals) :
        yvalue = yvals[i]
        weight = weights[i]

        if xvalue < xmin or xvalue > xmax :
            continue
        if yvalue < ymin or yvalue > ymax :
            continue

        xi = int((xvalue - xmin)/dx)
        if xi >= nx :
            xi = nx -1
        yi = int((yvalue - ymin)/dy)
        if yi >= ny :
            yi = ny -1
        zval[xi,yi] += weight 
        w2s[xi,yi] += weight**2

    xmeshgrid, ymeshgrid = get_2DHist_axis(xmin, xmax, ymin, ymax, nx, ny)

    # convert sum(w2) to sigma
    errors = np.sqrt(w2s)

    # calculate statistical errors
    staterrs = np.sqrt(zval)
   
    return xmeshgrid, ymeshgrid, zval, errors, staterrs, xmeshgrid[:,0], ymeshgrid[0]


#--------------------------------------------------------------------
def projection(val2d, ax) :
    val_proj = np.sum(val2d, axis=ax)
    return val_proj
 
def projection_x(xval2d) :
    # to project on x-axis, make sum along y-axis (axis = 1)
    return projection(xval2d, 1)

def projection_y(yval2d) :
    # to project on y-axis, make sum along x-axis (axis = 0)
    return projection(yval2d, 0)

#--------------------------------------------------------------------
def cumulative(weights) :
    '''
    calculate cumulative, weights must be 1D array.
    '''
    nbins = len(weights)
    cumulative = np.zeros(nbins)
    total = 0
    for i in range(nbins) :
        total += 1.0*weights[i] # make sure it's float.
        cumulative[i] = total
    return cumulative

def percentile(cumulative, axisval, percent) :
    '''
    supports only 1dim array for cumulative and axisval
    '''
    ratio = 0.01*percent
    index_hi = 0
    index_lo = 0

    if cumulative[-1] <= 0 :
        return 0

    norm = 1.0 / cumulative[-1]
    cumu = norm * cumulative
    #print "cumu = " , cumu
    for i, val in enumerate(cumu) :
        if val > ratio : 
            index_hi = i
            break
    #print "index_hi ", index_hi

    if index_hi == 0:
        return axisval[0]

    # linear interpolation
    #print "axisval ", axisval
    index_lo = index_hi -1
    ax_lo = axisval[index_lo]
    ax_hi = axisval[index_hi]
    p_lo = cumu[index_lo]
    p_hi = cumu[index_hi]

    return (ratio - p_lo)/(p_hi - p_lo) * (ax_hi - ax_lo) + ax_lo

def median_y(ybins, weights, sigma = 1.0) :
    '''
    get median and error of y values in each
    x bin.
    ybins is a return value of make_2D_hist
    it is n+1 array, ignore first bin.
    '''
    yvals = ybins[1:]

    nxbins = weights.shape[0]
    medians = np.zeros(nxbins)
    lowedges = np.zeros(nxbins)
    hiedges = np.zeros(nxbins)

    sigpercent = MT.get_sigma_percent(sigma)
    s_lo = 0.5*(100 - sigpercent)
    s_hi = 100 - s_lo

    for i in range(nxbins) :
        weights_i = weights[i][:]
        cumu = cumulative(weights_i)
        med = percentile(cumu, yvals, 50)
        #print "med", med
        medians[i] = percentile(cumu, yvals, 50)
        lowedges[i] = percentile(cumu, yvals, s_lo)
        hiedges[i] = percentile(cumu, yvals, s_hi)
        
    return medians, lowedges, hiedges

