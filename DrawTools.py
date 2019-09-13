import bisect
import numpy as np
import scipy.optimize

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
from matplotlib import colors 
import matplotlib.pyplot as plt

import MathTools as MT
import HistTools as HT

#plt.style.use('presentation')

# change default linewidth
#mpl.rc('figure.subplot', hspace=0.5, wspace=0.5, bottom=0.2, top=0.8)
mpl.rcParams['figure.figsize'] = "11,5"
#mpl.rcParams['figure.figsize'] = "6,5"
#mpl.rcParams['font.size'] = 14
#mpl.rcParams['font.size'] = 8 
#mpl.rcParams['font.size'] = 6 
mpl.rcParams['font.family'] = 'sans-selif'
mpl.rcParams['font.weight'] = 'bold'
mpl.rcParams['lines.linewidth'] = 2.0
mpl.rcParams['axes.facecolor'] = 'white'

colors_10 = ['#1f77b4',
          '#ff7f0e',
          '#2ca02c',
          '#d62728',
          '#9467bd',
          '#8c564b',
          '#e377c2',
          '#7f7f7f',
          '#bcbd22',
          '#17becf',
          '#1a55FF']

colors_20 = ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd","#c5b0d5", "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"]

#global_legendfontsize = 6
global_legendfontsize = 10

global_min = 1e-30


def mkdir(dirname, overwrite=True) :
    import os
    import shutil
    if overwrite and os.path.exists(dirname) : 
        shutil.rmtree(dirname)
    if not os.path.exists(dirname) :
        os.makedirs(dirname)

def htmlheader(title, cutstring="") :
    """
    generates header of html

    Parameters
    ----------
    title : string
        webpage title

    cutstring : string
        cut condition

    Returns
    ----------
    header : string

    """
    header = "<!DOCTYPE html PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN'>\n";

    header += "<html>\n";
    header += "<head>\n";
    header += "<meta content='text/html; charset=UTF_8' http-equiv='content-type'>\n";
    header = header + "<title>" + title + "</title>\n";
    header += "</head>\n";
    header += "<body>\n";
    header = header + "<h1>" + title + "</h1>\n";
    header += "<hr style='width: 100%; height: 2px;'>\n";
    header += "<h2>Cuts</h2>\n";
    header = header + cutstring + "\n";
    return header;

def htmlfooter() :
    """
    generates footer of html

    Returns
    -------
    footer : string

    """
    hooter = "</body>\n</html>";
    return hooter;

def savefig(dirname, figname):
    """
    save current figure to figname under dirname,
    also generates html link to the figure.

    Parameter
    ---------
    dirname : string
        directory path to the figure

    figname : string
        name of figure, must be identical among figs saved in the same directory

    Returns
    -------
    html : string

    """
    html = "<img src='" + figname + "'>\n"
    plt.savefig(dirname+figname)
    return html


def oned_format (binedges, yval) :
    """
    Convert histogram to array of points of x and y
    to draw the hist with plt.plot.
    Use it to change linestyle of histogram 
    (I don't know how to do it with plt.hist) 

    Parameters
    ----------
    binedges : list or numpy array
        just set return bin-edges from numpy.histogram
        size of binedges must be len(yval) + 1

    yval : list or numpy array
        yvalues 
        
    Returns    
    -------
    x : list
        array of x-value
    y : list
        array of y-value

    """

    x = []
    y = []
    ymin = min(yval.tolist())
    if len(yval) >= len(binedges) :
        print("size of binedges must be larger than yval")
        return x, y
    for index, value in enumerate(yval) :
        x.append(binedges[index])
        x.append(binedges[index+1])
        y.append(value)
        y.append(value)

    # append zeros to close histos
    x.insert(0, x[0])
    y.insert(0, ymin*0.5)
    x.append(x[-1])
    y.append(ymin*0.5)

    return x, y

def ymin_ymax(yvals, scale="") :
    """
    Calculate yrange of for given array of y
    Used to specify y_range of 1D histogram plot

    Parameters
    ----------
    yvals : numpy array
        y-values for 1D histogram

    scale : string
        specify "log" for plots with log scale in y-axis

    Returns
    -------
    range : list
        list of [xmin, xmax]

    """

    global global_min
    ymax = max(yvals.tolist())
    ymin = min(yvals.tolist()) 

    if scale == "log":
        ymax *= 10
        if (ymin <= 0) :
            cut = (yvals>0)
            #print yvals
            ymin = min(yvals[cut].tolist())
        #ymin *= 0.2 
    else :
        ymax *= 1.3
        #ymin *= 0.7 

    return [ymin, ymax]


class DrawDatum() :
    """
    Datum class for drawing, applicable for 1D and 2D
    histograms. This class is used by all draw_*** 
    functions.
    One DrawDatum represents one histogram, so 
    if 3 histogram will be in one figure, define
    3 DrawDatum object for each histogram.
    To set a histogram, use set_DrawDatum function.
    """
    def __init__(self) :
        self.val = np.zeros(1)
        self.xmeshgrid = np.zeros(1)
        self.xbinedges = np.zeros(1)
        self.xbins = np.zeros(1)
        self.ymeshgrid = np.zeros(1)
        self.ybinedges = np.zeros(1)
        self.ybins = np.zeros(1)
        self.err = np.zeros(1) # weighted err
        self.staterr = np.zeros(1) # statistical err
        self.color = "red"
        self.linestyle = "-"
        self.title= "none"

        # for 1D gaussian fit
        self.norm = 1
        self.mean = 0
        self.sigma = 1

    def fit_gauss(self) :
        param0 = (self.norm, self.mean, self.sigma)
        xbins = np.array(0.5*self.xbinedges[:-1]+self.xbinedges[1:])
        param_output = scipy.optimize.leastsq(MT.gauss_residuals, param0, args=(self.val, xbins), full_output=True)
        self.norm = param_output[0][0]
        self.mean = param_output[0][1]
        self.sigma = param_output[0][2]
        print("gauss fit result : norm = %f, mean = %f, sigma = %f" % (self.norm, self.mean, self.sigma))



def set_DrawDatum(xarray, key, nbins=100, weights=[], x_range=[-1, -1], xbins =[], color="black", linestyle="-") :
    """
    Make DrawDatum object for 1D histogram

    Parameters
    ----------
    xarray : numpy array
        array of values that you want to make a histogram

    key : string
        name or description of the histogram, used in the label in legend

    nbins : int
        number of bins for the histogram

    weights : numpy array
        weight parameter for histogram

    x_range : list
        range of x axis 

    xbins : numpy array
        if you want to give your own xbins, set it.

    color : string
        name of color for drawing 
 
    linestyle : string
        line style marker

    Returns
    -------
    datum : DrawDatum object


    """
    datum = DrawDatum()
    datum.title = key
    datum.val, bins, datum.err, datum.staterr = HT.make_1D_hist(xarray, nbins=nbins, weights=weights, x_range=x_range, xbins=xbins)
    datum.xbinedges = bins
    datum.xbins = 0.5*(bins[1:]+bins[:-1])
    datum.color = color
    datum.linestyle = linestyle
    return datum


def set_DrawDatum2D(xarray, yarray, key, nxbins, nybins, weights=[], x_range=[-1,-1], y_range=[-1,-1]) :
    """
    Make DrawDatum object for 2D histogram

    Parameters
    ----------
    xarray : numpy array
        array of values for xaxis that you want to make a histogram

    yarray : numpy array
        array of values for yaxis that you want to make a histogram

    key : string
        name or description of the histogram, used in the label in legend

    nxbins : int
        number of bins for xaxis for the histogram

    nybins : int
        number of bins for yaxis for the histogram

    weights : numpy array
        weight parameter for histogram

    x_range : list 
        range of x axis 

    y_range : list
        range of y axis 

    Returns
    -------
    datum : DrawDatum object

    """
    datum = DrawDatum()
    datum.title = key
    datum.xmeshgrid, datum.ymeshgrid, datum.val, datum.err, datum.staterr, xbins, ybins = HT.make_2D_hist(xarray, yarray, nxbins, nybins, weights=weights, x_range=x_range, y_range=y_range)

    datum.xbinedges = datum.xmeshgrid[:,0]
    datum.xbins = 0.5*(datum.xbinedges[1:]+datum.xbinedges[:-1])
    datum.ybinedges = datum.ymeshgrid[0]
    datum.ybins = 0.5*(datum.ybinedges[1:]+datum.ybinedges[:-1])
    return datum


def draw_fitgauss(figid, data) :
    """
    function to draw gaussian function from 
    fit value of slices of 2D histogram.

    TODO : may be doesn't work anymore?

    Parameters
    ----------
    figid : int
        figid to draw the gaussian

    data : DrawDatum object 
        data must be generated with set_DrawDatum2D

    """
    fig = plt.figure(figid)
    ax1 = plt.subplot(1,1,1)
    data.fit_gauss()
    fity = MT.gaussian(data.xmeshgrid, data.norm, data.mean, data.sigma)
    label = "fitgaus : N=%2.2f M=%2.2f S=%2.2f" %(data.norm, data.mean, data.sigma)
    ax1.plot(data.xmeshgrid, fity, ":", color=data.color, label=label)
    plt.legend(loc="best")

def draw_1D(figid, data, axislabels=["x-label","y-label"], xscale='linear', yscale='log', figtitle="", yrange='', figsize=(6,5)) :
    """
    Draw 1D histogram plot from DrawDatum objects.
    To superimpose multiple DrawDatum into one figure,
    set identical figid for each draw_1D call.

    Parameters
    ----------

    figid : int
        unique id for the figure

    data : DrawDatum object
        DrawDatum you want to draw

    axislabels : list of string
        labels for xaxis and yaxis

    xscale : string
        x axis scale, will be set with set_xscale()

    yscale : string
        y axis scale, will be set with set_yscale()
    
    figtitle : string
        title of the figure

    yrange : list or string
        if empty string, it automatically calculate the best yrange.
        to give yrange manually, set yrange=(ymin, ymax).

    figsize : tuple 
        should be in format of (x_size, y_size)

    """
    fig = plt.figure(figid, figsize=figsize)
    ax1 = plt.subplot(1,1,1)
    if yrange=='' :
        yrange = ymin_ymax(data.val, scale=yscale) 
    x, y = oned_format(data.xbinedges, data.val)
    total = sum(data.val)
    ax1.plot(x, y, data.linestyle, color=data.color, label=data.title + " (" + str(total) + "evts)")
    ax1.set_title(figtitle)
    ax1.set_xscale(xscale)
    ax1.set_yscale(yscale)
    ax1.set_xlabel(axislabels[0])
    ax1.set_ylabel(axislabels[1])
    ax1.set_ylim(yrange)
    plt.legend(loc="best")

def draw_1D_errors(figid, data, axislabels=["x-label","y-label"], xscale='linear', yscale='log', figtitle="", yrange='', errtype='weighted', figsize=(6,5)) :
    '''
    Draw 1D histogram plot from DrawDatum objects
    with error bars.
    By default the error bars are weighted err, or set
    errtype='std' for standard deviation err.
    To superimpose multiple DrawDatum into one figure,
    set identical figid for each draw_1D call.

    Parameters
    ----------

    figid : int
        unique id for the figure

    data : DrawDatum object
        DrawDatum you want to draw

    axislabels : list of string
        labels for xaxis and yaxis

    xscale : string
        x axis scale, will be set with set_xscale()

    yscale : string
        y axis scale, will be set with set_yscale()
    
    figtitle : string
        title of the figure

    yrange : list or string
        if empty string, it automatically calculate the best yrange.
        to give yrange manually, set yrange=(ymin, ymax).

    errtype : string
        if errtype = "weighted", error bar is calculated with weighted method (default)
        else : just 1 sigma standard deviation of y value is used for error bars.

    figsize : tuple 
        should be in format of (x_size, y_size)

 
    '''

    fig = plt.figure(figid, figsize=figsize)
    if yrange=='' :
        yrange = ymin_ymax(data.val, scale=yscale) 
    ax1 = plt.subplot(1,1,1)
    ax1.set_title(figtitle)
    if errtype == "weighted" :
        ax1.errorbar(data.xmeshgrid, data.val, yerr=data.err, color=data.color, label=data.title, fmt=data.linestyle )
    else:
        ax1.errorbar(data.xmeshgrid, data.val, yerr=data.staterr, color=data.color, label=data.title, fmt=data.linestyle )
    ax1.set_xscale(xscale)
    ax1.set_yscale(yscale)
    ax1.set_xlabel(axislabels[0])
    ax1.set_ylabel(axislabels[1])
    ax1.set_ylim(yrange)
    plt.legend(loc="best")

def draw_1D_comparison(figid, data, basedata, xlabel, xscale='linear', yscale='log',figtitle="", yrange='', errtype='weighted', yrscale = 'linear', yrrange = [0.2, 2.0], figtype="horizontal", grid="None", figsize = (11,5)) :
    """
    Draw 1D histogram plot from DrawDatum objects
    with error bars and ratio plot of data and basedata.
    By default the error bars are weighted err, or set
    errtype='std' for standard deviation err.
    To get a reasonable ratio plot, you have to specify
    same bins for data and basedata. Somehow giving bins parameter
    to set_DrawDatum doesn't work as expected, for now, use x_range
    parameter and nx to get same bins.

    Parameters
    ----------

    figid : int
        unique id for the figure

    data : list 
        list of DrawDatum you want to draw

    basedata : DrawDatum object
        this data is the base data to compare with others

    xlabel : string
        label of x axis

    xscale : string
        x axis scale, will be set with set_xscale()

    yscale : string
        y axis scale, will be set with set_yscale()

    figtitle : string
        title of the figure

    yrange : list or string
        if empty string, it automatically calculate the best yrange.
        to give yrange manually, set yrange=[ymin, ymax].

    errtype : string
        if errtype = "weighted", error bar is calculated with weighted method (default)
        else : just 1 sigma standard deviation of y value is used for error bars.
        
    yrscale : string
        y axis scale for ratio plot, will be set with set_yscale()

    yrrange : list
        y axis range for ratio plot

    figtype : string
        if "horizontal", plot and ratio plot is arrigned in horizontal.
        else, plot and ratio plot is arrigned in vertical.

    grid : string
        "x"    set grid for x axis only
        "y"    set grid for y axis only
        "both" set grid for x and y
        "None" no grid

    Returns
    -------
    fig : figure object    
    ax[0] : axis object for plot
    ax[1] : axis object for ratio plot

    """
    fig = plt.figure(figid, figsize=figsize)
    if yrange=='' :
        yrange = ymin_ymax(basedata.val, scale=yscale) 

    ax = ""
    if figtype == "horizontal" :
        fig, ax = plt.subplots(1, 2, sharex=False)
    else :
        fig, ax = plt.subplots(2, 1, sharex=True)
        fig.subplots_adjust(hspace=0)

    #print figtitle
    ax[0].set_title(figtitle)
    for d in data :
        #print d.val
        yrange2 = ymin_ymax(d.val, scale=yscale)
        if (yrange2[0] < yrange[0]) :
            yrange[0] = yrange2[0]
        if (yrange2[1] > yrange[1]) :
            yrange[1] = yrange2[1]
        if errtype == 'weighted':
            ax[0].errorbar(d.xbins, d.val, yerr=d.err, color=d.color, label=d.title, fmt=d.linestyle )
        else :
            ax[0].errorbar(d.xbins, d.val, yerr=d.staterr, color=d.color, label=d.title, fmt=d.linestyle )
    ax[0].set_xscale(xscale)
    ax[0].set_yscale(yscale)
    ax[0].set_xlabel(xlabel)
    ax[0].set_ylim(yrange)

    if grid != "None" :
        ax[0].grid(True, axis=grid)

    ax[0].legend(loc="best", fontsize=global_legendfontsize)

    for d in data :
        if errtype == 'weighted':
            ratio, sigma = MT.calc_divide_errors(d.val, d.err, basedata.val, basedata.err)
        else :
            ratio, sigma = MT.calc_divide_errors(d.val, d.staterr, basedata.val, basedata.staterr)
        ratiolabel = d.title + "/" + basedata.title
        ax[1].errorbar(d.xbins, ratio, yerr=sigma, color=d.color, label=ratiolabel, fmt=d.linestyle )
    ax[1].set_xlabel(xlabel)
    ax[1].set_yscale(yrscale)
    ax[1].set_ylim(yrrange)
    if grid != "None" :
        ax[1].grid(True, axis=grid)

    ax[1].legend(loc="upper left", fontsize=global_legendfontsize)
    return fig, ax[0], ax[1]


def draw_2D(figid, data, axislabels, norm=colors.LogNorm(), figtitle="", vmin=0, vmax=0) :
    # to make linear color set norm=colors.Normalize()
    # to make log color set norm=colors.LogNorm()
    fig = plt.figure(figid)
    ax1 = plt.subplot(1,1,1)

    if vmin == vmax :
        phist = ax1.pcolormesh(data.xmeshgrid, data.ymeshgrid, data.val, norm=norm)
    else:
        phist = ax1.pcolormesh(data.xmeshgrid, data.ymeshgrid, data.val, norm=norm, vmin=vmin, vmax=vmax)

    ax1.set_title(figtitle)
    ax1.set_xlabel(axislabels[0])
    ax1.set_ylabel(axislabels[1])

    plt.colorbar(phist)
    global global_legendfontsize
    plt.legend(loc="best", fontsize=global_legendfontsize)


def draw_2D_comparison(figid, data, basedata, axislabels, figtitle="", vrange=(0,0), rvrange=(0,2.0)) :
    fig = plt.figure(figid, figsize=(10,4))
    ax1 = plt.subplot(1,2,1)
    phist1 = ax1.pcolormesh(data.xmeshgrid, data.ymeshgrid, data.val)
    ax1.set_xlabel(axislabels[0])
    ax1.set_ylabel(axislabels[1])
    ax1.set_title(figtitle)
    plt.legend(loc="best", fontsize=global_legendfontsize)
    plt.colorbar(phist1)

    ax2 = plt.subplot(1,2,2)
    ratio = data.val / basedata.val
    ratiolabel = data.title + "/" + basedata.title
    phist2 = ax2.pcolormesh(data.xmeshgrid, data.ymeshgrid, ratio, vmin=rvrange[0], vmax=rvrange[1])
    ax2.set_xlabel(axislabels[0])
    ax2.set_ylabel(axislabels[1])
    ax2.set_title(ratiolabel)
    plt.legend(loc="best", fontsize=global_legendfontsize)
    plt.colorbar(phist2)
    plt.subplots_adjust(hspace=0.2, wspace=0.5)
 
def draw_2D_basic(ax, x, y, w, xlabel, ylabel, title, yscale="linear", xscale="linear", vmin=0, vmax=0) :
    c1 = ax.pcolormesh(x, y, w)
    if vmin != vmax :
        c1.set_clim(vmin=vmin, vmax=vmax)
    plt.colorbar(c1)
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)


