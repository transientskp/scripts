import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.stats import norm
import pylab
pylab.rcParams['legend.loc'] = 'best'
from matplotlib.ticker import NullFormatter
from matplotlib.font_manager import FontProperties
import generic_tools

def make_colours(frequencies):
    cm = matplotlib.cm.get_cmap('jet')
    col = [cm(1.*i/len(frequencies)) for i in range(len(frequencies))]
    return col

def create_scatter_hist(data,sigcutx,sigcuty,paramx,paramy,range_x,range_y,dataset_id,frequencies): 
    print('plotting figure: scatter histogram plot')
    bins = 50

    # Setting up the plot
    nullfmt   = NullFormatter()         # no labels
    fontP = FontProperties()
    fontP.set_size('x-small')
    col = make_colours(frequencies)
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left+width+0.02
    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]
    fig = plt.figure(1,figsize=(8,8))
    axScatter = fig.add_subplot(223, position=rect_scatter)
    plt.xlabel(r'$\eta_{\nu}$', fontsize=16)
    plt.ylabel(r'$V_{\nu}$', fontsize=16)
    axHistx=fig.add_subplot(221, position=rect_histx)
    axHisty=fig.add_subplot(224, position=rect_histy)

    # Plotting data
    for i in range(len(frequencies)):
        xdata_var=[data[n][0] for n in range(len(data)) if data[n][2]==frequencies[i] if data[n][-1]=='2']
        ydata_var=[data[n][1] for n in range(len(data)) if data[n][2]==frequencies[i] if data[n][-1]=='2']
        xdata_tran=[data[n][0] for n in range(len(data)) if data[n][2]==frequencies[i] if data[n][-1]=='1']
        ydata_tran=[data[n][1] for n in range(len(data)) if data[n][2]==frequencies[i] if data[n][-1]=='1']
        xdata_pos=[data[n][0] for n in range(len(data)) if data[n][2]==frequencies[i] if data[n][-1]=='0']
        ydata_pos=[data[n][1] for n in range(len(data)) if data[n][2]==frequencies[i] if data[n][-1]=='0']
        if frequencies[i]=='stable':
            axScatter.scatter(xdata_var, ydata_var,color='0.75', s=5., zorder=1)           
            axScatter.scatter(xdata_tran, ydata_tran,color='0.75', s=5., zorder=1, marker='*')           
            axScatter.scatter(xdata_pos, ydata_pos,color='0.75', s=5., zorder=1, marker='v')           
        else:
            axScatter.scatter(xdata_var, ydata_var,color=col[i], s=5.)
            axScatter.scatter(xdata_tran, ydata_tran,color=col[i], s=5., marker='*')           
            axScatter.scatter(xdata_pos, ydata_pos,color=col[i], s=5., marker='v')           
    if 'stable' in frequencies or 'FP' in frequencies:
        x=[data[n][0] for n in range(len(data)) if (data[n][2]=='stable' or data[n][2]=='FP' or data[n][2]=='TN') if data[n][-1]=='2']
        y=[data[n][1] for n in range(len(data)) if (data[n][2]=='stable' or data[n][2]=='FP' or data[n][2]=='TN') if data[n][-1]=='2']
    else:
        x=[data[n][0] for n in range(len(data)) if data[n][-1]=='2']
        y=[data[n][1] for n in range(len(data)) if data[n][-1]=='2']
    print data[0]
    print x[0]
    axHistx.hist(x, bins=bins, normed=1, histtype='stepfilled', color='b')
    axHistx.hist(x, bins=generic_tools.bayesian_blocks(x), normed=1, histtype='step', color='k')
    axHisty.hist(y, bins=bins, normed=1, histtype='stepfilled', orientation='horizontal', color='b')
    axScatter.legend(frequencies,loc=4, prop=fontP)

    # Plotting lines representing thresholds (unless no thresholds)
    if sigcutx != 0 or sigcuty != 0:
        axHistx.axvline(x=sigcutx, linewidth=2, color='k', linestyle='--')
        axHisty.axhline(y=sigcuty, linewidth=2, color='k', linestyle='--')
        axScatter.axhline(y=sigcuty, linewidth=2, color='k', linestyle='--')
        axScatter.axvline(x=sigcutx, linewidth=2, color='k', linestyle='--')

    # Plotting the Gaussian fits
    fit=norm.pdf(range_x,loc=paramx[0],scale=paramx[1])
    axHistx.plot(range_x,fit, 'k:', linewidth=2)
    fit2=norm.pdf(range_y,loc=paramy[0],scale=paramy[1])
    axHisty.plot(fit2, range_y, 'k:', linewidth=2)

    # Final plot settings
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)
    axHistx.axes.yaxis.set_ticklabels([])
    axHisty.axes.xaxis.set_ticklabels([])
    axHistx.set_xlim( axScatter.get_xlim() )
    axHisty.set_ylim( axScatter.get_ylim() )
    xmin=int(min([data[n][0] for n in range(len(data))]))
    xmax=int(max([data[n][0] for n in range(len(data))]))+1
    ymin=int(min([data[n][1] for n in range(len(data))]))
    ymax=int(max([data[n][1] for n in range(len(data))]))+1
    xvals=range(xmin,xmax)
    xtxts=[r'$10^{'+str(a)+'}$' for a in xvals]
    yvals=range(ymin,ymax)
    ytxts=[r'$10^{'+str(a)+'}$' for a in yvals]
    axScatter.set_xticks(xvals)
    axScatter.set_xticklabels(xtxts)
    axScatter.set_yticks(yvals)
    axScatter.set_yticklabels(ytxts)
    plt.savefig('ds'+str(dataset_id)+'_scatter_hist.png')
    plt.close()

    return


def create_diagnostic(trans_data,sigcut_etanu,sigcut_Vnu,frequencies,dataset_id):
    print('plotting figure: diagnostic plots')

    # Setting up the plot
    nullfmt   = NullFormatter()         # no labels
    fig = plt.figure(1,figsize=(8,8))
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    fontP = FontProperties()
    fontP.set_size('x-small')
    fig.subplots_adjust(hspace = .001, wspace = 0.001)
    ax1.set_ylabel(r'$\eta_\nu$')
    ax3.set_ylabel(r'$V_\nu$')
    ax3.set_xlabel('Max Flux (Jy)')
    ax4.set_xlabel('MaxFlux / Average Flux')
    col = make_colours(frequencies)

    # Plotting data
    for i in range(len(frequencies)):
        xdata_ax3=[trans_data[x][2] for x in range(len(trans_data)) if trans_data[x][4]==frequencies[i]]
        xdata_ax4=[trans_data[x][3] for x in range(len(trans_data)) if trans_data[x][4]==frequencies[i]]
        ydata_ax1=[trans_data[x][0] for x in range(len(trans_data)) if trans_data[x][4]==frequencies[i]]
        ydata_ax3=[trans_data[x][1] for x in range(len(trans_data)) if trans_data[x][4]==frequencies[i]]
        if frequencies[i]=='stable':
            ax1.scatter(xdata_ax3, ydata_ax1,color='0.75', s=5., zorder=1)
            ax2.scatter(xdata_ax4, ydata_ax1,color='0.75', s=5., zorder=1)
            ax3.scatter(xdata_ax3, ydata_ax3,color='0.75', s=5., zorder=1)
            ax4.scatter(xdata_ax4, ydata_ax3,color='0.75', s=5., zorder=1)
        else:
            ax1.scatter(xdata_ax3, ydata_ax1,color=col[i], s=5.)
            ax2.scatter(xdata_ax4, ydata_ax1,color=col[i], s=5.)
            ax3.scatter(xdata_ax3, ydata_ax3,color=col[i], s=5.)
            ax4.scatter(xdata_ax4, ydata_ax3,color=col[i], s=5.)
    ax4.legend(frequencies, loc=4, prop=fontP)

    # Plotting lines representing thresholds (unless no thresholds)
    if sigcut_etanu != 0 or sigcut_Vnu != 0:
        ax1.axhline(y=10.**sigcut_etanu, linewidth=2, color='k', linestyle='--')
        ax2.axhline(y=10.**sigcut_etanu, linewidth=2, color='k', linestyle='--')
        ax3.axhline(y=10.**sigcut_Vnu, linewidth=2, color='k', linestyle='--')
        ax4.axhline(y=10.**sigcut_Vnu, linewidth=2, color='k', linestyle='--')

    # Plotting settings
    xmin_ax3=int(np.log10(min([trans_data[x][2] for x in range(len(trans_data))])))-1
    xmax_ax3=int(np.log10(max([trans_data[x][2] for x in range(len(trans_data))])))+0.5
    xmin_ax4=int(np.log10(min([trans_data[x][3] for x in range(len(trans_data))])))-0.5
    xmax_ax4=int(np.log10(max([trans_data[x][3] for x in range(len(trans_data))])))+0.5
    ymin_ax1=int(np.log10(min([trans_data[x][0] for x in range(len(trans_data))])))-0.5
    ymax_ax1=int(np.log10(max([trans_data[x][0] for x in range(len(trans_data))])))+1
    ymin_ax3=int(np.log10(min([trans_data[x][1] for x in range(len(trans_data))])))-0.5
    ymax_ax3=int(np.log10(max([trans_data[x][1] for x in range(len(trans_data))])))+1
    xvals_ax3=range(int(xmin_ax3),int(xmax_ax3))
    xtxts_ax3=[r'$10^{'+str(a)+'}$' for a in xvals_ax3]
    xvals_ax4=range(int(xmin_ax4),int(xmax_ax4))
    xtxts_ax4=[r'$10^{'+str(a)+'}$' for a in xvals_ax4]
    yvals_ax1=range(int(ymin_ax1),int(ymax_ax1))
    ytxts_ax1=[r'$10^{'+str(a)+'}$' for a in yvals_ax1]
    yvals_ax3=range(int(ymin_ax3),int(ymax_ax3))
    ytxts_ax3=[r'$10^{'+str(a)+'}$' for a in yvals_ax3]
    ax3.set_xticks([10.**x for x in xvals_ax3])
    ax3.set_xticklabels(xtxts_ax3)
    ax4.set_xticks(xvals_ax4)
    ax4.set_xticklabels(xtxts_ax4)
    ax1.set_yticks([10.**y for y in yvals_ax1])
    ax1.set_yticklabels(ytxts_ax1)
    ax3.set_yticks([10.**y for y in yvals_ax3])
    ax3.set_yticklabels(ytxts_ax3)
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xscale('log')
    ax3.set_yscale('log')
    ax3.set_xscale('log')
    ax4.set_yscale('log')
    ax4.set_xscale('log')
    ax1.set_ylim(10.**(ymin_ax1),10.**(ymax_ax1))
    ax3.set_ylim(10.**(ymin_ax3),10.**(ymax_ax3))
    ax3.set_xlim(10.**(xmin_ax3),10.**(xmax_ax3))
    ax4.set_xlim(10.**(xmin_ax4),10.**(xmax_ax4))
    ax1.set_xlim( ax3.get_xlim() )
    ax4.set_ylim( ax3.get_ylim() )
    ax2.set_xlim( ax4.get_xlim() )
    ax2.set_ylim( ax1.get_ylim() )
    ax1.xaxis.set_major_formatter(nullfmt)
    ax4.yaxis.set_major_formatter(nullfmt)
    ax2.xaxis.set_major_formatter(nullfmt)
    ax2.yaxis.set_major_formatter(nullfmt)
    plt.savefig('ds'+str(dataset_id)+'_diagnostic_plots.png')
    plt.close()

    return
