
import numpy as np
import lmfit
#from scipy.optimize import minimize
#from scipy.special import factorial
#from scipy.special import i0e as scipyi0e
import scipy.special as sc
from scipy.stats import poisson
from itertools import product
import matplotlib as mpl
import copy
import matplotlib.pyplot as plt
import aid_functions as aid
import pandas as pd
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable

###############target functions and distributions ##############################
def get_logLikelihood1DPoisson(params, func, xdata, ydata, sign = 1, 
    modelkwargs = {}):
    """return log-likelihood. for 1D binned data function
    maximize this function to obtain most likely fit"""
    #want to modify function such that it just takes modelkwargs
    #and not xdata, ydata, then accordingly fitfunctions and surface functions
    #can be generalised
    model = func(xdata, params, **modelkwargs)
    #fcatorial returns inf if ydata > 175, use gammaln instead
    #l = np.sum(-model + ydata * np.log(model) - np.log(factorial(ydata)))
    l = np.sum(-model + ydata * np.log(model) - sc.gammaln(ydata+1))
    return l * sign

def ncChidistr(r, mu, sig, A, offset):
    """calculates non-centered Chi Distributionxx"""
    return A * r / sig**2 * np.exp(- 0.5 * ((r - mu)/sig)**2) \
        * sc.i0e( mu * r / sig**2) \
        + offset
def gauss1D(x, mu, sig, A, offset):
    pdf = np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
    return A * pdf / np.sum(pdf) + offset
def gauss1D_p(x, p):
    return gauss1D(x, p['mu'], p['sig'], p['A'], p['offset'])
def Npoisson(x, p):
    model = np.zeros(x.shape)
    v = p.valuesdict()
    N = 0
    while "mu%i" % N in v:
        model += v['A%i' % N] * poisson.pmf(x, v['mu%i' % N])
        N += 1
    model += v['bg']
    return model
def NncChidistr(x, p):
    """takes lmfit Parameter object and generates as many ncChiDistr as there 
    are mu%i"""
    model = np.zeros(x.shape)
    v = p.valuesdict()
    N = 0
    while "mu%i" % N in v:
        model += ncChidistr(x, v['mu%i' % N], v['sig%i' % N], v['A%i' % N], 0)
        N += 1
    model += v['bg']
    return model

    
########### parameter estimates ###############################################
def genPeakEst(Npeaks, x, y):
    """
    returns lmfit parameter object for Npeaks ncChidistr
    """
    p = lmfit.Parameters()
    bg = np.mean(y) / 10
    mu = np.sum(x*y) / np.sum(y) #center of mass
    sig = np.sqrt(np.sum(y * (x - mu) ** 2) / np.sum(y)) # sigma
    A_max = np.sum(y)*10
    A = np.sum(y)
    p.add('bg', bg, True, 0, A_max)
    for i in range(Npeaks):
        p.add_many(('mu%i' % i, mu, True, 0, np.amax(y)),
                   ('A%i' % i, A, True, 0, A_max),
                   ('sig%i' % i, sig, True, 0, np.inf)
                   )
    return p

################## goodness of fit #############################################
def get_AIC(nFitVars, logLikelihood):
    """calculate Aikaike Information citerion"""
    return 2 * nFitVars - 2 * logLikelihood
def get_AICc(nFitVars, logLikelihood, samplesize):
    """corrected AIC, use for small samplesize"""
    k = nFitVars #shorthand
    n = samplesize #shorthand
    AIC = get_AIC(nFitVars, logLikelihood)
    return AIC + (2 * k ** 2 + 2 * k) / (n - k - 1)
def get_BIC(nFitVars, logLikelihood, samplesize):
    """calculate Bayesian information Criterion
    use for large sample sizes"""
    return np.log(samplesize) * nFitVars - 2 * logLikelihood
    
############## fitting functions ###############################################

# def fitNChidistr(p, bins, counts):
    # """fits a chi distribution to a set of distances
    # params are ordered: mu, sigma, amplitude, offset"""
    # #possible to make function generic to fit any distribution?
    # #even better: create object that contains the data, binwidth, maxbins etc.
    # print('Warning: function is depreciated. Instead use fitDistr()')
    # fitres = lmfit.minimize(get_logLikelihood1DPoisson, p, method = 'nelder',
        # args = (NncChidistr, bins, counts, -1))
    # logLikelihood = get_logLikelihood1DPoisson(fitres.params, NncChidistr, 
                                                # bins, counts)
    # samplesize = np.sum(counts)
    # AIC = get_AIC(fitres.nvarys, logLikelihood)
    # AICc = get_AICc(fitres.nvarys, logLikelihood, samplesize)
    # BIC = get_BIC(fitres.nvarys, logLikelihood, samplesize)
    # return fitres, AIC, AICc, BIC, logLikelihood
    
#def fitChiDistr(dist, params0, bounds = None, outfile = '', binwidth = 2, 
                # maxbin = 60, plotshow = True):
    # """fits a chi distribution to a set of distances
    # params are ordered: mu, sigma, amplitude, offset"""
    # print('warning: function superceded by fitNChidistr')
    # counts, bin_edges, _ = plt.hist(dist, bins = np.arange(0, maxbin, binwidth))
    # Nbins = bin_edges.shape[0] - 1
    # bins = np.zeros(Nbins)
    # for i in range(Nbins):
        # bins[i] = (bin_edges[i] + bin_edges[i + 1]) / 2
    
    # fitres = minimize(get_logLikelihood1DPoisson, params0, args = (ncChidistr, bins, counts, -1), 
      # method = 'SLSQP', bounds = bounds, 
      # options = {'maxiter': 1000, 'ftol': 1e-6})
    
    # xgrid = np.arange(0,max(bins),0.1)
    # fit = ncChidistr(xgrid, *fitres.x)
    # plt.plot(xgrid, fit, label = 'MLE sigma fixed')
    # if plotshow:
        # plt.show()
        
    # if outfile:
        # savearray = np.array([xgrid, fit]).transpose()
        # header = 'xgrid\t fit'
        # np.savetxt(outfile, 
           # savearray,
           # fmt = '%.4f', 
           # header = header, 
           # delimiter = '\t')
        # print(os.path.splitext(outfile)[0])
        # fpath = os.path.splitext(outfile)[0] + '_fit_parameters.txt'
        # with open(fpath, 'wt') as f:
            # f.write('freefit\n')
            # f.write('mu, sigma, A, bg\n')
            # f.write(str(fitres.x) + '\n')
            # f.write(str(bounds) + '\n')
    # return fitres

    
def fitDistr(p, modelFunc, x, y, modelkwargs = {}, method = 'nelder'):
    """fits a distribution and return fit result and logLikelihood, Aikaike 
    and Bayesion info criteria"""
    fitres = lmfit.minimize(get_logLikelihood1DPoisson, p, method = method,
        args = (modelFunc, x, y, -1, modelkwargs))
    logLikelihood = get_logLikelihood1DPoisson(fitres.params, modelFunc, 
                                                x, y, modelkwargs = modelkwargs)
    samplesize = np.sum(y)
    AIC = get_AIC(fitres.nvarys, logLikelihood)
    AICc = get_AICc(fitres.nvarys, logLikelihood, samplesize)
    BIC = get_BIC(fitres.nvarys, logLikelihood, samplesize)
    return fitres, AIC, AICc, BIC, logLikelihood
    
def scanLikelihoodSurface(param_ranges, p, x, y, 
    modelFunc = NncChidistr, verbose = False, modelkwargs = {}):
    param_ticks=[]
    param_names=param_ranges.keys()
    for param_name in param_names:
        param_ticks.append(param_ranges[param_name])
        
    nDshape = [len(sublist) for sublist in param_ticks]
    length = np.product(nDshape)
    logLikelihoodSurface = np.zeros(length)

    for i, point in enumerate(product(*param_ticks)):
        for j, name in enumerate(param_names):
            p[name].set(value = point[j], vary = False)
        try:
            *_, logLikelihood = fitDistr(p, modelFunc, x, y, modelkwargs)
        except ValueError:
            if verbose: print ('fit failed for ' + str(point))
            logLikelihood = np.nan
        logLikelihoodSurface[i] = logLikelihood
        if(i % 10 == 0):
            if verbose: print ('calculating point ' + str(point))
    return logLikelihoodSurface.reshape(nDshape)
    
########################## plot functions#######################################
    
def plotLikelihoodSurface(surface_copy, param_ranges, skip = 2, outname = '', 
    title = '', figsize = None, isplotpdf = True):
    """utility function, works only in 2D"""
    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    spacing = 0.005
    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom + height + spacing, width, 0.2]
    rect_histy = [left + width + spacing, bottom, 0.2, height]
    
    #this workaround seems no longer needed, instead $ r_{loc}$ latex style 
    #work directly.
    #really ugly workaround
    #mpl.rcParams['text.usetex'] = True
    print('removed text.usetex = True statement, check that code is still functional' +\
        'then clean this statement')
    keyy, keyx = param_ranges.keys()
    x = param_ranges[keyx]
    y = param_ranges[keyy]
    xmin = min(x)
    xmax = max(x)
    ymin = min(y)
    ymax = max(y)
    surface = copy.deepcopy(surface_copy)
    if figsize:
        fig = plt.figure(figsize = figsize)
    else:
        fig = plt.figure()
    ax = fig.add_axes(rect_scatter)
    ax_x = fig.add_axes(rect_histx, sharex=ax)
    ax_y = fig.add_axes(rect_histy, sharey=ax)
    
    bestfit = np.nanmax(surface.flatten())
    if isplotpdf:
        #make into pdf
        #scale to 0 log to avoid running out of floating point precision
        surface += bestfit 
        surface = np.exp(surface)
        #mirror image horizontally
        surface = surface[::-1]
        #normalize pdf surface to represents the likelihood per nm^2 (for mu vs sigma)
        #or per nm per photon count (for A vs mu)
        dx = param_ranges[keyx][1]-param_ranges[keyx][0]
        dy = param_ranges[keyy][1]-param_ranges[keyy][0]
        surface /= np.sum(surface) * dx * dy
        pmax = np.max(surface.flatten())
        #adapt contourlevels
        contourlevels = [pmax * 0.135, pmax * 0.60, pmax]
        vmin = 0
        vmax = pmax
        
    else:
        contourlevels = [bestfit -2, bestfit-0.5, bestfit]
        vmin = bestfit-5
        vmax = bestfit
    pdf_x = np.sum(surface, axis = 0)
    pdf_y = np.sum(surface, axis = 1)[::-1]
    pdf_x /= max(pdf_x)
    pdf_y /= max(pdf_y)
    aspect = (xmax - xmin) / (ymax - ymin)
    im = ax.imshow(surface, cmap = 'gray', extent = [xmin, xmax, ymin, ymax], aspect = aspect, vmin = vmin, vmax = vmax)
    CS = ax.contour(surface, levels = contourlevels, colors = 'r', linestyles = 'dashed', extent = [xmin, xmax, ymax, ymin])
    labels = ['13.5% pmax', '60% pmax', 'pmax']
    
    fmt = {}
    for l, s in zip(CS.levels, labels):
        fmt[l] = s
    ax.clabel(CS, fmt = fmt)

    #match Anders' nomenclature
    def fancyAxisLabel(key, setLabelFunc): #function only exists in this scope
        if 'sig' in key:
            setLabelFunc('$\sigma_{\chi,%c}[nm]$' % key[-1])
        elif 'mu' in key:
            setLabelFunc('$R_{mp,%c}^{loc}[nm]$' % key[-1])
        else:
            setLabelFunc(key)
    fancyAxisLabel(keyx, ax.set_xlabel)
    fancyAxisLabel(keyy, ax.set_ylabel)
    def fancyTickLabel(key, setTickFunc, setTickLabelFunc, skip):
        labels = ['%.1f' % x for x in param_ranges[key][::skip]]
        ticks = [x for x in param_ranges[key][::skip]]
        #ticks = [ x for x in range(len(param_ranges[key]))[::skip]]
        #append final value
        labels.append('%.1f' % max(param_ranges[key]))
        ticks.append(len(param_ranges[key])-1)
        setTickFunc(ticks)
        setTickLabelFunc(labels)
    fancyTickLabel(keyx, ax.set_xticks, ax.set_xticklabels, skip)
    fancyTickLabel(keyy, ax.set_yticks, ax.set_yticklabels, skip)
    # ax_x.set_title(title)
    #add colorbar
    #divider = make_axes_locatable(ax)
    #cax = divider.append_axes('right', size='5%', pad=0.05)
    #fig.colorbar(im, cax=cax, orientation='vertical')
    
    #make side projection of 1D pdf
    def getborder(pdf, axoffset, step):
        _, cidx = aid.find_nearest(pdf, 1)
        _, lidx = aid.find_nearest(pdf[:cidx], np.exp(-0.5))
        _, ridx = aid.find_nearest(pdf[cidx:], np.exp(-0.5))
        ridx += cidx
        lborder = lidx * step + axoffset
        rborder = ridx * step + axoffset
        center = cidx * step + axoffset
        return lborder, rborder, center
    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    lborder, rborder, center = getborder(pdf_x, param_ranges[keyx][0], dx)
    #ax.plot([70, 80], [np.exp(-0.5), np.exp(-0.5)], 'y--',label = '1 \u03C3')
    ax_x.plot( [lborder, lborder], [np.exp(-0.5), 0] , 'r--')
    ax_x.plot( [rborder, rborder], [np.exp(-0.5), 0] , 'r--')
    ax_x.text(lborder, np.exp(-0.5), '%.2f' %lborder, horizontalalignment='right', fontsize = 10)
    ax_x.text(rborder, np.exp(-0.5), '%.2f' %rborder, fontsize = 10)
    ax_x.text(center, 1, '%.2f' %center,  horizontalalignment='center', fontsize = 10)
    ax_x.fill_between(x, pdf_x, edgecolor = 'k', facecolor = 'grey')
    ax_x.set_ylim(0,1.5)
    ax_x.set_yticks([1])

    lborder, rborder, center = getborder(pdf_y, param_ranges[keyy][0], dy)
    ax_y.plot([np.exp(-0.5), 0], [lborder, lborder], 'r--')
    ax_y.plot([np.exp(-0.5), 0], [rborder, rborder], 'r--')
    ax_y.text(np.exp(-0.5), lborder, '%.2f' %lborder, fontsize = 10, va = 'top')
    ax_y.text(np.exp(-0.5), rborder, '%.2f' %rborder, fontsize = 10)
    ax_y.text(1, center, '%.2f' %center, fontsize = 10, va = 'center')
    ax_y.fill_between(pdf_y, y, edgecolor = 'k', facecolor = 'grey')
    ax_y.set_ylim((ymin, ymax))
    ax_y.set_xlim(0,1.5)
    ax_y.set_xticks([1])
    
    #save and plot
    if outname:
        plt.savefig(outname, dpi = 300, bbox_inches = 'tight')
    plt.show()
    mpl.rcParams['text.usetex'] = False
    

    
def plotdistr(dist, bins, fit = None, fitFunc = NncChidistr, title = '',
    modelout = '', plotout = '', grid = False, modelkwargs = {}, figsize = None):
    """plots a histogrammed disttribution with bin position bins and 
    counts in each bin. fit is an lmfit.MinimizerResult object, if it is given,
    a model is plotted too.
    plot and data export modalities are integrated."""
    mpl.rcParams['text.usetex'] = False
    if figsize:
        plt.figure(figsize = figsize)
    binwidth = bins[1] - bins[0]
    if fit:
        #dstep = 0.1
        dstep = binwidth
        x = np.arange(0,max(bins),dstep)
        p = fit.params
        #unsure whether dstep is needed, debug!
        model = fitFunc(x, p, **modelkwargs) #/ dstep
        plt.plot(x, model, 'k', label = 'model')
        i = 0
        if fitFunc == NncChidistr:
            while True:
                try:
                    model = ncChidistr(x, p['mu%i' % i], p['sig%i' % i], p['A%i' % i], 0)
                    plt.plot(x,model, '--', label = 'nc\u03C7%i' % i)
                    i+=1
                except KeyError:
                    bg = np.ones(len(x))*p['bg']
                    plt.plot(x, bg, '--')
                    break
        
    plt.hist(dist, bins = bins, color = 'c')
    plt.xlabel(r'$d_{loc} [nm]$')
    plt.ylabel('localisation events / %.1f nm' % binwidth)
    plt.title(title)
    plt.legend()
    if grid:
        plt.grid()
    if plotout:
        plt.savefig(plotout, dpi = 300, bbox_inches = 'tight')
    if modelout:
        dictout = {}
        dictout['grid'] = x
        dictout['model'] = model
        aid.saveDict(dictout, modelout)
        fpath = os.path.splitext(modelout)[0] + '_fit_parameters.txt'
        with open(fpath, 'wt') as f:
            f.write(lmfit.fit_report(fit))
    plt.show()
    
################### utility functions ##########################################
    
def whichChiIsBest(bins, counts, verbose = False):
    """utility function"""
    fitresL = []
    AICL = []
    BICL = []
    for N in range(4):
        try:
            p = genPeakEst(N, bins, counts)
            fitres, AIC, _, BIC, _ = fitDistr(p, NncChidistr, bins, counts)
            #fitres, AIC, _, BIC, _ = fitNChidistr(p, bins, counts)
        except ValueError:
            print('fit for %i peaks failed' %N)
            break
        fitresL.append(fitres)
        AICL.append(AIC)
        BICL.append(BIC)
    
    bestfit = np.argmin(AICL)
    if verbose:
        for i, AIC in enumerate(AICL):
            print('AIC is %.1f for %i peaks' % (AIC, i))
        for i, BIC in enumerate(BICL):
            print('BIC is %.1f for %i peaks' % (BIC, i))
    return fitresL[bestfit]
    
def exportChiComponents(outname, bins, p_all):
    """utility function"""
    dataFrame = pd.DataFrame({'xgrid':bins})
    for i in range(10):#no more than ten populations are exported
        try:
            p = lmfit.Parameters()
            p.add('bg', 0, False, 0, 10)
            p['mu0'] = p_all['mu' + str(i)]
            p['sig0'] = p_all['sig' + str(i)]
            p['A0'] = p_all['A' + str(i)]
            model = NncChidistr(bins, p)
            dataFrame['ncChi_pop'+str(i)] = model
            print(p)
            #gen fit and export
        except KeyError:
            break
    dataFrame.to_csv(outname)
    return dataFrame

# 