import generic_tools
import numpy as np
from multiprocessing import Pool
from scipy.interpolate import griddata
import operator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pylab
pylab.rcParams['legend.loc'] = 'best'
from matplotlib.ticker import NullFormatter
from matplotlib.font_manager import FontProperties


def trial_data(args):
    # Find the precision and recall for a given pair of thresholds
    data,sigma1,sigma2 = args
    
    # Sort data into transient and non-transient
    xvals = [float(x[0]) for x in data if float(x[6]) != 0.  if float(x[0]) > 0. if float(x[1]) > 0.]
    yvals = [float(x[1]) for x in data if float(x[6]) != 0.  if float(x[0]) > 0. if float(x[1]) > 0.]
    xstable = [float(x[0]) for x in data if float(x[6]) == 0.  if float(x[0]) > 0. if float(x[1]) > 0.]
    ystable = [float(x[1]) for x in data if float(x[6]) == 0.  if float(x[0]) > 0. if float(x[1]) > 0.]

    # Find the thresholds for a given sigma, by fitting data with a Gaussian model
    sigcutx,paramx,range_x = generic_tools.get_sigcut([np.log10(float(x[0])) for x in data if float(x[6]) == 0. if float(x[0]) > 0. if float(x[1]) > 0.],sigma1)
    sigcuty,paramy,range_y = generic_tools.get_sigcut([np.log10(float(x[1])) for x in data if float(x[6]) == 0. if float(x[0]) > 0. if float(x[1]) > 0.],sigma2)

    # Count up the different numbers of tn, tp, fp, fn
    fp=len([z for z in range(len(xstable)) if (xstable[z]>10.**sigcutx and ystable[z]>10.**sigcuty)]) # False Positive
    tn=len([z for z in range(len(xstable)) if (xstable[z]<10.**sigcutx or ystable[z]<10.**sigcuty)]) # True Negative
    tp=len([z for z in range(len(xvals)) if (xvals[z]>10.**sigcutx and yvals[z]>10.**sigcuty)]) # True Positive
    fn=len([z for z in range(len(xvals)) if (xvals[z]<10.**sigcutx or yvals[z]<10.**sigcuty)]) # False Negative

    # Use these values to calculate the precision and recall values
    precision, recall = generic_tools.precision_and_recall(tp,fp,fn)
    return [sigma1, sigma2, precision, recall]

def multiple_trials(data):
    # Find the precision and recall for all combinations of the sigma thresholds
    sigmas=np.arange(0.,4.0,(4./500.))
    pool = Pool(processes=4)              # start 4 worker processes
    inputs = range(2)
    for sigma1 in sigmas:
        print sigma1
        sigma_data = pool.map(trial_data, [(data,sigma1,sigma2) for sigma2 in sigmas])
        with open('sigma_data.txt','a') as f_handle:
            np.savetxt(f_handle,sigma_data)
        f_handle.close()
    pool.close()
    return

def check_method_works(xi,yi,zi1,zi2, data):
    trials = np.arange(0.,1.,1./100.)
    Z1=[]
    Z2=[]
    X=[]
    Y=[]
    for precis in trials:
        for recall in trials:
            combinations=[[xi[a][b],yi[a][b],zi1[a][b],zi2[a][b]] for a in range(len(zi1)) for b in range(len(zi1[0])) if zi1[a][b]>precis if zi2[a][b]>recall]
            temp = {str(a[0])+','+str(a[1]):(2*a[2]*a[3])/(a[2]+a[3]) for a in combinations}
            above_thresh_sigma=max(temp.iteritems(), key=operator.itemgetter(1))[0]
            above_thresh_sigma=[a for a in combinations if str(a[0])+','+str(a[1])==above_thresh_sigma][0]
            # Sort data into transient and non-transient
            xvals = [float(x[0]) for x in data if float(x[2]) != 0.]
            yvals = [float(x[1]) for x in data if float(x[2]) != 0.]
            xstable = [float(x[0]) for x in data if float(x[2]) == 0.]
            ystable = [float(x[1]) for x in data if float(x[2]) == 0.]
            # Find the thresholds for a given sigma, by fitting data with a Gaussian model
            sigcutx,paramx,range_x = generic_tools.get_sigcut([np.log10(float(x[0])) for x in data if float(x[0]) > 0. if float(x[1]) > 0.],above_thresh_sigma[0])
            sigcuty,paramy,range_y = generic_tools.get_sigcut([np.log10(float(x[1])) for x in data if float(x[0]) > 0. if float(x[1]) > 0.],above_thresh_sigma[1])
            # Count up the different numbers of tn, tp, fp, fn
            fp=len([z for z in range(len(xstable)) if (xstable[z]>sigcutx and ystable[z]>sigcuty)]) # False Positive
            tn=len([z for z in range(len(xstable)) if (xstable[z]<sigcutx or ystable[z]<sigcuty)]) # True Negative
            tp=len([z for z in range(len(xvals)) if (xvals[z]>sigcutx and yvals[z]>sigcuty)]) # True Positive
            fn=len([z for z in range(len(xvals)) if (xvals[z]<sigcutx or yvals[z]<sigcuty)]) # False Negative
            # Use these values to calculate the precision and recall values
            results1, results2 = generic_tools.precision_and_recall(tp,fp,fn)
            X.append(precis)
            Y.append(recall)
            Z1.append(results1)
            Z2.append(results2)
    xi,yi = np.mgrid[0:1:2000j, 0:1:2000j]
    zi1 = griddata((X, Y), Z1, (xi, yi), method='cubic')
    zi2 = griddata((X, Y), Z2, (xi, yi), method='cubic')
    # Plot results
    # Settings
    nullfmt   = NullFormatter()         # no labels
    fig = plt.figure(1,figsize=(5,10))
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    cax = fig.add_axes([0.1, 0.95, 0.8, 0.03])
    fig.subplots_adjust(hspace = .001, wspace = 0.001)
    levels=np.arange(0.0,1.1,0.1)
    levels2=[0.1, 0.3, 0.5, 0.7, 0.9]
    ax2.set_xlabel(r'Input Precision')
    ax1.set_ylabel(r'Input Recall')
    ax2.set_ylabel(r'Input Recall')
    fontP = FontProperties()
    fontP.set_size('x-small')
    ax1.set_xlim([0.0,1.0])
    ax2.set_xlim([0.0,1.0])
    ax1.set_ylim([0.0,0.999])
    ax2.set_ylim([0.0,0.999])
    ax1.xaxis.set_major_formatter(nullfmt)
    ax2.set_xlim( ax1.get_xlim() )
    #Plotting data
    ax1.text(2.5, 3.5, 'Precision', bbox=dict(facecolor='white'))
    ax2.text(2.5, 3.5, 'Recall', bbox=dict(facecolor='white'))
    CS1 = ax1.contourf(xi,yi,zi1,levels, cmap=plt.get_cmap('Blues'),alpha=1)
    CS2 = ax2.contourf(xi,yi,zi2,levels, cmap=plt.get_cmap('Blues'),alpha=1)
    fig.colorbar(CS2, cax, orientation='horizontal')
    ax1.axvline(x=above_thresh_sigma[0], linewidth=2, color='k', linestyle='--')
    ax2.axvline(x=above_thresh_sigma[0], linewidth=2, color='k', linestyle='--')
    ax1.axhline(y=above_thresh_sigma[1], linewidth=2, color='k', linestyle='--')
    ax2.axhline(y=above_thresh_sigma[1], linewidth=2, color='k', linestyle='--')
    plt.savefig('sim_check_precisions_and_recalls.png')
    plt.close()


def find_best_sigmas(precis_thresh,recall_thresh,data,tests):
    # Gridding the data for precision and recall
    X=[float(x[0]) for x in data]
    Y=[float(x[1]) for x in data]
    Z1=[float(x[2]) for x in data]
    Z2=[float(x[3]) for x in data]
    xi,yi = np.mgrid[0:4:2000j, 0:4:2000j]
    zi1 = griddata((X, Y), Z1, (xi, yi), method='cubic', fill_value=1.)
    zi2 = griddata((X, Y), Z2, (xi, yi), method='cubic', fill_value=0.)
    # Find all the combinations of x and y which are above the two thresholds
    combinations=[[xi[a][b],yi[a][b],zi1[a][b],zi2[a][b]] for a in range(len(zi1)) for b in range(len(zi1[0])) if zi1[a][b]>precis_thresh if zi2[a][b]>recall_thresh]

    # Calculate the F-score and find the combination with the highest F-Score 
    #(this gives the best performance in both precision and recall of the options that are above the thresholds)
    temp = {str(a[0])+','+str(a[1]):(2*a[2]*a[3])/(a[2]+a[3]) for a in combinations}
    above_thresh_sigma=max(temp.iteritems(), key=operator.itemgetter(1))[0]
    above_thresh_sigma=[a for a in combinations if str(a[0])+','+str(a[1])==above_thresh_sigma][0]

    if tests:
        check_method_works(xi,yi,zi1,zi2,data)

    # Plot results
    # Settings
    nullfmt   = NullFormatter()         # no labels
    fig = plt.figure(1,figsize=(5,10))
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    cax = fig.add_axes([0.1, 0.95, 0.8, 0.03])
    fig.subplots_adjust(hspace = .001, wspace = 0.001)
    levels=np.arange(0.0,1.1,0.1)
    levels2=[0.1, 0.3, 0.5, 0.7, 0.9]
    ax2.set_xlabel(r'$\sigma$ threshold ($\eta_{\nu}$)')
    ax1.set_ylabel(r'$\sigma$ threshold ($V_{\nu}$)')
    ax2.set_ylabel(r'$\sigma$ threshold ($V_{\nu}$)')
    fontP = FontProperties()
    fontP.set_size('x-small')
    ax1.set_xlim([0.0,4.0])
    ax2.set_xlim([0.0,4.0])
    ax1.set_ylim([0.0,3.99])
    ax2.set_ylim([0.0,3.99])
    ax1.xaxis.set_major_formatter(nullfmt)
    ax2.set_xlim( ax1.get_xlim() )
    #Plotting data
    ax1.text(2.5, 3.5, 'Precision', bbox=dict(facecolor='white'))
    ax2.text(2.5, 3.5, 'Recall', bbox=dict(facecolor='white'))
    CS1 = ax1.contourf(xi,yi,zi1,levels, cmap=plt.get_cmap('Blues'),alpha=1)
    CS2 = ax2.contourf(xi,yi,zi2,levels, cmap=plt.get_cmap('Blues'),alpha=1)
    fig.colorbar(CS2, cax, orientation='horizontal')
    ax1.axvline(x=above_thresh_sigma[0], linewidth=2, color='k', linestyle='--')
    ax2.axvline(x=above_thresh_sigma[0], linewidth=2, color='k', linestyle='--')
    ax1.axhline(y=above_thresh_sigma[1], linewidth=2, color='k', linestyle='--')
    ax2.axhline(y=above_thresh_sigma[1], linewidth=2, color='k', linestyle='--')
    plt.savefig('sim_precisions_and_recalls.png')
    plt.close()

    return above_thresh_sigma[0],above_thresh_sigma[1]

