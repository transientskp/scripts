import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pylab
pylab.rcParams['legend.loc'] = 'best'
from matplotlib.ticker import NullFormatter
from matplotlib.font_manager import FontProperties
import generic_tools

def sort_data(data):
    # find the best and worst expected detection significances for the sources and extract the detection threshold
    best=[float(x[-3]) for x in data]
    worst=[float(x[-4]) for x in data]
    detection_threshold=max([float(x[-2]) for x in data if float(x[-2])!=0])
    return best,worst,detection_threshold

def find_sigma_margin(best_data, worst_data, best_sim, worst_sim, detection_threshold):
    # find the precision, recall and F-score for different margins using the best and worst expected significances
    
    sigma_thresh=np.arange(0.,100.,1)
    best_plot_data=[]
    worst_plot_data=[]
    for sigma in sigma_thresh:
        best_tp=len([a for a in best_sim if a>=(detection_threshold+sigma)])
        best_fn=len([a for a in best_sim if a<(detection_threshold+sigma)])
        best_fp=len([a for a in best_data if a>=(detection_threshold+sigma)])
        best_tn=len([a for a in best_data if a<(detection_threshold+sigma)])
        worst_tp=len([a for a in worst_sim if a>=(detection_threshold+sigma)])
        worst_fn=len([a for a in worst_sim if a<(detection_threshold+sigma)])
        worst_fp=len([a for a in worst_data if a>=(detection_threshold+sigma)])
        worst_tn=len([a for a in worst_data if a<(detection_threshold+sigma)])
        best_precision,best_recall = generic_tools.precision_and_recall(best_tp,best_fp,best_fn)
        worst_precision,worst_recall = generic_tools.precision_and_recall(worst_tp,worst_fp,worst_fn)
        if best_precision==0 or best_recall==0:
            best_plot_data.append([sigma,best_precision,best_recall,0])
        else:
            best_plot_data.append([sigma,best_precision,best_recall,(2*best_precision*best_recall)/(best_precision+best_recall)])
        if worst_precision==0 or best_recall==0:
            worst_plot_data.append([sigma,worst_precision,worst_recall,0])
        else:
            worst_plot_data.append([sigma,worst_precision,worst_recall,(2*worst_precision*worst_recall)/(worst_precision+worst_recall)])
    return best_plot_data, worst_plot_data

def plot_hist(x,x2,detection_threshold,label):
    # plot histograms showing the input stable sources and the simulated transient sources
    
    plt.figure(figsize=(12,10))
    plt.xscale('log')
    bins=np.logspace(np.log10(min(x)), np.log10(max(x2)), num=50, endpoint=True, base=10.0)
    plt.hist(x, bins=bins, histtype='stepfilled', color='b')
    plt.hist(x2, bins=bins, histtype='step', linewidth=2, color='r')
    plt.xlabel(r'Expected detection significance of source ($\sigma$)', fontsize=24)
    plt.axvline(x=detection_threshold, linestyle='--', linewidth=2, color='k')
    plt.savefig(label+'_sigma_histogram.png')
    plt.close()
    return

def plot_diagnostic(best_data,worst_data):
    # plot a diagnostic plot illustrating the precision, recall and F-score as a function of increasing sigma margin
    # identify the sigma margin which optimises the precision and recall
    
    plt.figure(figsize=(12,12))
    plt.plot([a[0] for a in worst_data],[a[1] for a in worst_data], 'r-')
    plt.plot([a[0] for a in worst_data],[a[2] for a in worst_data], 'b-')
    plt.plot([a[0] for a in worst_data],[a[3] for a in worst_data], 'k-')
    plt.plot([a[0] for a in best_data],[a[1] for a in best_data], 'r--')
    plt.plot([a[0] for a in best_data],[a[2] for a in best_data], 'b--')
    plt.plot([a[0] for a in best_data],[a[3] for a in best_data], 'k--')
    worst_maxF=max([a[3] for a in worst_data])
    best_maxF=max([a[3] for a in best_data])
    sigWorst=[a for a in worst_data if a[3]==worst_maxF][0]
    sigBest=[a for a in best_data if a[3]==best_maxF][0]
    plt.xlabel(r'$\sigma$ margin', fontsize=24)
    plt.xscale('log')
    print 'Best sigma parameters:'
    print 'Worst RMS = '+str(sigWorst[0])+' Precision = '+str(sigWorst[1])+' Recall = '+str(sigWorst[2])
    print 'Best RMS = '+str(sigBest[0])+' Precision = '+str(sigBest[1])+' Recall = '+str(sigBest[2])
    plt.savefig('sigma_margin_diagnostic.png')
    plt.close()
    return sigWorst[0], sigBest[0]
