#!/usr/bin/python
import datetime
import time
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import coords as C
import numpy as np
import math
import sys
from datetime import datetime
from scipy.stats import norm
import pylab
pylab.rcParams['legend.loc'] = 'best'
from matplotlib.ticker import NullFormatter
from matplotlib.font_manager import FontProperties

###################### INITIAL SETUP STEPS ######################

if len(sys.argv) != 7:
    print 'python TraP_source_overview.py <database> <dataset_id> <release> <sigma> <plt_all> <plt_freqs>'
    exit()
database = sys.argv[1]
dataset_id = str(sys.argv[2])
release = str(sys.argv[3])
sigma = float(sys.argv[4])
plt_all = sys.argv[5]
plt_freqs = sys.argv[6]

if release!='0' and release!='1m' and release!='1p':
    print 'This script is for either Cycle0 (0) or Release 1 MonetDB (1m) or Release 1 Postgres (1p) databases, please specify 0, 1m or 1p.'
    exit()

# Setting up the general lists and dictionaries needed
trans_runcat=[]
trans_data=[]

###################### DEFINE SUBROUTINES ######################

def plothist(x, name,filename,sigma,freq):
    param=norm.fit(x)
    range_x=np.linspace(min(x),max(x),1000)
    fit=norm.pdf(range_x,loc=param[0],scale=param[1])
    plt.plot(range_x,fit, 'r-')
    plt.hist(x,bins=50,normed=1,histtype='stepfilled')
    sigcut = param[1]*sigma+param[0]
    plt.axvline(x=sigcut, linewidth=2, color='k', linestyle='--')
    plt.title('%s mean: %.3f sd: %.3f' % (name, param[0], param[1]))
    plt.text((sigcut-(0.3*param[1])), 1, r'%.1f $\sigma$: %.3f' % (sigma,sigcut), rotation=90)
    plt.xlabel(name)
    plt.savefig(filename+'_1gauss_'+str(freq)+'MHz.png')
    plt.close()
    return sigcut

def plotfig(trans_data, a, b, xlabel, ylabel, plotname,sigcut_etanu,sigcut_Vnu,frequencies):
    print('plotting figure: '+plotname)
    plt.figure()
    x1=[]
    x2=[]
    y1=[]
    y2=[]
    n1=0
    n2=0
    x=0    
    if a == 1:
        xmin=0.1
        xmax=1000.0
    elif a == 2:
        xmin=0.0
        xmax=1.05
    elif a == 3:
        xmin=0.01
        xmax=5.0
    elif a == 4:
        xmin=0.05
        xmax=200.0
    elif a == 5:
        xmin=0.5
        xmax=7.5
    if b == 1:
        ymin=0.1
        ymax=1000.0
    elif b == 2:
        ymin=0.0
        ymax=1.05
    elif b == 3:
        ymin=0.01
        ymax=5.0
    elif b == 4:
        ymin=5.0
        ymax=105.0
    elif b == 5:
        ymin=0.5
        ymax=7.5
    col=['r','b','g','y']
    for i in range(len(frequencies)):
        xdata=[trans_data[x][a] for x in range(len(trans_data)) if trans_data[x][6]==frequencies[i]]
        ydata=[trans_data[x][b] for x in range(len(trans_data)) if trans_data[x][6]==frequencies[i]]
        plt.scatter(xdata, ydata,color=col[i], s=5)
    plt.xlabel(xlabel)
    plt.legend(frequencies)
    if a == 1 or a == 3 or a == 4:
        plt.xscale('log')
    if b == 1 or b == 3:
        plt.yscale('log')
    if a == 1:
        plt.axvline(x=sigcut_etanu, linewidth=2, color='k', linestyle='--')
    if a == 3:
        plt.axvline(x=sigcut_Vnu, linewidth=2, color='k', linestyle='--')
    if b == 1:
        plt.axhline(y=sigcut_etanu, linewidth=2, color='k', linestyle='--')
    if b == 3:
        plt.axhline(y=sigcut_Vnu, linewidth=2, color='k', linestyle='--')
    plt.axis([xmin,xmax,ymin,ymax])
    plt.ylabel(ylabel)
    plt.savefig('transients_'+plotname+'.png')
    plt.close()

def create_scatter_hist(trans_data,sigma): 
    nullfmt   = NullFormatter()         # no labels
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left+width+0.02
    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]
    fig = plt.figure(1,figsize=(8,8))
    axScatter = fig.add_subplot(223, position=rect_scatter)
    plt.xlabel(r'$log_{10}(\eta_{\nu})$', fontsize=16)
    plt.ylabel(r'$log_{10}(V_{\nu})$', fontsize=16)
    axHistx=fig.add_subplot(221, position=rect_histx)
    axHisty=fig.add_subplot(224, position=rect_histy)
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    col=['r','b','g','y']
    for i in range(len(frequencies)):
        xdata=[np.log10(trans_data[n][1]) for n in range(len(trans_data)) if trans_data[n][6]==frequencies[i] if trans_data[n][1] > 0 if trans_data[n][3] > 0]
        ydata=[np.log10(trans_data[n][3]) for n in range(len(trans_data)) if trans_data[n][6]==frequencies[i] if trans_data[n][1] > 0 if trans_data[n][3] > 0]
        axScatter.scatter(xdata, ydata,color=col[i], s=5.)
    axScatter.legend(frequencies,loc=4)
    x=[np.log10(trans_data[n][1]) for n in range(len(trans_data)) if trans_data[n][1] > 0 if trans_data[n][3] > 0]
    y=[np.log10(trans_data[n][3]) for n in range(len(trans_data)) if trans_data[n][1] > 0 if trans_data[n][3] > 0]
    bins = 50
    param=norm.fit(x)
    range_x=np.linspace(min(x),max(x),1000)
    fit=norm.pdf(range_x,loc=param[0],scale=param[1])
    sigcutx = param[1]*sigma+param[0]
    axHistx.axvline(x=sigcutx, linewidth=2, color='k', linestyle='--')
    axHistx.plot(range_x,fit, 'k:', linewidth=2)
    param2=norm.fit(y)
    range_y=np.linspace(min(y),max(y),1000)
    fit2=norm.pdf(range_y,loc=param2[0],scale=param2[1])
    sigcuty = param2[1]*sigma+param2[0]
    axHisty.axhline(y=sigcuty, linewidth=2, color='k', linestyle='--')
    axScatter.axhline(y=sigcuty, linewidth=2, color='k', linestyle='--')
    axScatter.axvline(x=sigcutx, linewidth=2, color='k', linestyle='--')
    axHisty.plot(fit2, range_y, 'k:', linewidth=2)
    axHistx.hist(x, bins=bins, normed=1, histtype='stepfilled', color='b')
    axHisty.hist(y, bins=bins, normed=1, histtype='stepfilled', orientation='horizontal', color='b')
    axHistx.set_xlim( axScatter.get_xlim() )
    axHisty.set_ylim( axScatter.get_ylim() )
#    xvals=[-3., -2., -1., 0., 1., 2., 3.]
#    xtxts=[str(10.**a) for a in xvals]
#    yvals=[-2., -1., 0.]
#    ytxts=[str(10.**a) for a in xvals]
#    axScatter.set_xticks(xvals)
#    axScatter.set_xticklabels(xtxts)
#    axScatter.set_yticks(yvals)
#    axScatter.set_yticklabels(ytxts)
    plt.savefig('scatter_hist.png')
    plt.close()
    return

def diagnostic_plots(trans_data,sigcut_etanu,sigcut_Vnu,frequencies):
    print('plotting figure: diagnostic plots')
    nullfmt   = NullFormatter()         # no labels
    fig = plt.figure(1,figsize=(8,8))
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    fig.subplots_adjust(hspace = .001, wspace = 0.001)
    ax1.set_ylim(10.**(-4.5),10.**(4.5))
    ax3.set_ylim(10.**(-2.5),10.**(0.7))
    ax3.set_xlim(0.1,80)
    ax4.set_xlim(0.5,10)
    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax2.set_yscale('log')
    ax3.set_yscale('log')
    ax3.set_xscale('log')
    ax4.set_yscale('log')
    ax1.xaxis.set_major_formatter(nullfmt)
    ax4.yaxis.set_major_formatter(nullfmt)
    ax2.xaxis.set_major_formatter(nullfmt)
    ax2.yaxis.set_major_formatter(nullfmt)
    ax1.set_xlim( ax3.get_xlim() )
    ax4.set_ylim( ax3.get_ylim() )
    ax2.set_xlim( ax4.get_xlim() )
    ax2.set_ylim( ax1.get_ylim() )
    ax1.set_ylabel(r'$\eta_\nu$')
    ax3.set_ylabel(r'$V_\nu$')
    ax3.set_xlabel('Max Flux (Jy)')
    ax4.set_xlabel('MaxFlux / Average Flux')
    col=['r','b','c','y']
    for i in range(len(frequencies)):
        xdata_ax3=[trans_data[x][4] for x in range(len(trans_data)) if trans_data[x][6]==frequencies[i]]
        xdata_ax4=[trans_data[x][5] for x in range(len(trans_data)) if trans_data[x][6]==frequencies[i]]
        ydata_ax1=[trans_data[x][1] for x in range(len(trans_data)) if trans_data[x][6]==frequencies[i]]
        ydata_ax3=[trans_data[x][3] for x in range(len(trans_data)) if trans_data[x][6]==frequencies[i]]
        ax1.scatter(xdata_ax3, ydata_ax1,color=col[i], s=5.)
        ax2.scatter(xdata_ax4, ydata_ax1,color=col[i], s=5.)
        ax3.scatter(xdata_ax3, ydata_ax3,color=col[i], s=5.)
        ax4.scatter(xdata_ax4, ydata_ax3,color=col[i], s=5.)
    fontP = FontProperties()
    fontP.set_size('x-small')
    ax4.legend(frequencies, loc=4, prop=fontP)
    ax1.axhline(y=sigcut_etanu, linewidth=2, color='k', linestyle='--')
    ax2.axhline(y=sigcut_etanu, linewidth=2, color='k', linestyle='--')
    ax3.axhline(y=sigcut_Vnu, linewidth=2, color='k', linestyle='--')
    ax4.axhline(y=sigcut_Vnu, linewidth=2, color='k', linestyle='--')
    plt.savefig('diagnostic_plots.png')
    plt.close()


def plt_colour_colour(trans_data,freq):
    freq.sort()
    nullfmt   = NullFormatter()         # no labels
    fig = plt.figure(1,figsize=(8,8))
    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)
    fig.subplots_adjust(hspace = .001, wspace = 0.001)
#    ax1.set_ylim(10.**(-4.5),10.**(4.5))
#    ax1.set_yscale('log')
    ax3.yaxis.set_major_formatter(nullfmt)
    ax2.yaxis.set_major_formatter(nullfmt)
    ax1.set_ylim( ax3.get_ylim() )
    ax2.set_ylim( ax3.get_ylim() )
    ax1.set_ylabel(str(freq[0])+'/'+str(freq[1]))
    ax1.set_xlabel(str(freq[1])+'/'+str(freq[2]))
    ax2.set_xlabel(str(freq[1])+'/'+str(freq[3]))
    ax3.set_xlabel(str(freq[2])+'/'+str(freq[3]))
    f0f1 = {trans_data[f0][0]:trans_data[f0][4]/trans_data[f1][4]
           for f0 in range(len(trans_data)) 
           for f1 in range(len(trans_data))
           if trans_data[f0][0]==trans_data[f1][0]
           if trans_data[f0][6]==freq[0] 
           if trans_data[f1][6]==freq[1]}
    f0f2 = {trans_data[f0][0]:trans_data[f0][4]/trans_data[f1][4]
           for f0 in range(len(trans_data)) 
           for f1 in range(len(trans_data))
           if trans_data[f0][0]==trans_data[f1][0]
           if trans_data[f0][6]==freq[0] 
           if trans_data[f1][6]==freq[2]}
    f0f3 = {trans_data[f0][0]:trans_data[f0][4]/trans_data[f1][4]
           for f0 in range(len(trans_data)) 
           for f1 in range(len(trans_data))
           if trans_data[f0][0]==trans_data[f1][0]
           if trans_data[f0][6]==freq[0] 
           if trans_data[f1][6]==freq[3]}
    f1f2 = {trans_data[f0][0]:trans_data[f0][4]/trans_data[f1][4]
           for f0 in range(len(trans_data)) 
           for f1 in range(len(trans_data))
           if trans_data[f0][0]==trans_data[f1][0]
           if trans_data[f0][6]==freq[1] 
           if trans_data[f1][6]==freq[2]}
    f1f3 = {trans_data[f0][0]:trans_data[f0][4]/trans_data[f1][4]
           for f0 in range(len(trans_data)) 
           for f1 in range(len(trans_data))
           if trans_data[f0][0]==trans_data[f1][0]
           if trans_data[f0][6]==freq[1] 
           if trans_data[f1][6]==freq[3]}
    f2f3 = {trans_data[f0][0]:trans_data[f0][4]/trans_data[f1][4]
           for f0 in range(len(trans_data)) 
           for f1 in range(len(trans_data))
           if trans_data[f0][0]==trans_data[f1][0]
           if trans_data[f0][6]==freq[2] 
           if trans_data[f1][6]==freq[3]}

    print len(f0f1)
    print len(f1f2)
    print len(f1f3)
    print len(f2f3)

    flx =[[f0f1[key],f1f2[key]] for key in f0f1.keys() if key in f1f2.keys()]
    x=[f[1] for f in flx]
    y=[f[0] for f in flx]
    ax1.scatter(x,y,s=5.)
    flx =[[f0f1[key],f1f3[key]] for key in f0f1.keys() if key in f1f3.keys()]
    x=[f[1] for f in flx]
    y=[f[0] for f in flx]
    ax2.scatter(x,y,s=5.)
    flx =[[f0f1[key],f2f3[key]] for key in f0f1.keys() if key in f2f3.keys()]
    x=[f[1] for f in flx]
    y=[f[0] for f in flx]
    ax3.scatter(x,y,s=5.)
    plt.show()
    exit()


#(freq1/freq2) v. (freq2/freq3)

def plt_colour_flux(trans_data,freq1,freq2):
#(freq1/freq2) v. freq2
    exit()










###################### RUNNING THROUGH INDIVIDUAL DATASETS ######################
total_flux_ratio={}
total_avg_flux_ratio={}
total_flux_ratio_err={}
total_time_diff={}
 
## Getting the data from the Database - Thanks Tim!
if release == '0':
    import dump_transient_runcat_v0
    from dump_transient_runcat_v0 import dump_trans
    dump_trans(database,dataset_id)
elif release == '1m':
    import dump_transient_runcat_v1
    from dump_transient_runcat_v1 import dump_trans
    dump_trans(database,dataset_id)
elif release == '1p':
    import dump_transient_runcat_v1_postgres
    from dump_transient_runcat_v1_postgres import dump_trans
    dump_trans(database,dataset_id)
else:
    print 'ERROR in release number'
    exit()

### Reading in the data from the output files of above script
transients=[]
data=open('ds_'+dataset_id+'_transients.csv','r')
for lines in data:
    lines=lines.rstrip()
    transients.append(lines.split(','))
data.close()
sources=[]
data=open('ds_'+dataset_id+'_sources.csv','r')
for lines in data:
    lines=lines.rstrip()
    sources.append(lines.split(','))
data.close()
runcat=0
### Reading the lightcurves of each individual source in the dataset
new_source={}
frequencies=[]
earliest=datetime.strptime(sources[0][8], '%Y-%m-%d %H:%M:%S')
for a in range(len(sources)):
    new_runcat=sources[a][6]
    new_freq=int((float(sources[a][5])/1e6)+0.5)
    if new_runcat != runcat:
        runcat=new_runcat
        new_source[runcat]=[sources[a]]
    else:
        new_source[runcat]=new_source[runcat]+[sources[a]]
    if new_freq not in frequencies:
        frequencies.append(new_freq)
    if (earliest-datetime.strptime(sources[a][8], '%Y-%m-%d %H:%M:%S')).days<0:
        earliest=datetime.strptime(sources[a][8], '%Y-%m-%d %H:%M:%S')

### Creating plots for each individual source in the dataset
print len(new_source)

trans_data_all=[]
bands={}
for freq in frequencies:
    trans_data=[]
    for keys in new_source.keys():
        flux=[]
        flux_err=[]
        date=[]
        band=[]
        for b in range(len(new_source[keys])):
            if int((float(new_source[keys][b][5])/1e6)+0.5)==freq:
                band.append(new_source[keys][b][11])
                flux.append(float(new_source[keys][b][3]))
                flux_err.append(float(new_source[keys][b][4]))
                date.append(datetime.strptime(new_source[keys][b][8], '%Y-%m-%d %H:%M:%S'))

        bands[freq]=band
        if len(date)!=0:
            oldest=min(date)
            if plt_all == 'F':
                if abs((earliest-oldest).days)<=2:
                    time_diff=[]
                    for c in range(len(date)):
                        time1=time.mktime(date[c].timetuple())
                        time2=time.mktime(oldest.timetuple())
                        time3=(time1-time2)
                        time_diff.append(time3)
    ### Calculate the ratios...
                    avg_flux_ratio = [x / (sum(flux)/len(flux)) for x in flux]
    ### Collate and store the transient parameters (these are across all the pipeline runs for the final figures)
                    for n in range(len(transients)):
                        if keys == transients[n][5] and transients[n][9] in bands[freq]:
                            trans_data.append([keys, float(transients[n][3]), float(transients[n][6]), float(transients[n][10]), max(flux), max(avg_flux_ratio),freq])
                            trans_data_all.append([keys, float(transients[n][3]), float(transients[n][6]), float(transients[n][10]), max(flux), max(avg_flux_ratio), freq])
            else:
                time_diff=[]
                for c in range(len(date)):
                    time1=time.mktime(date[c].timetuple())
                    time2=time.mktime(oldest.timetuple())
                    time3=(time1-time2)
                    time_diff.append(time3)
    ### Calculate the ratios...
                avg_flux_ratio = [x/(sum(flux)/len(flux)) for x in flux]
    ### Collate and store the transient parameters (these are across all the pipeline runs for the final figures)
                for n in range(len(transients)):
                    if keys == transients[n][5] and transients[n][9] in bands[freq]:
                        trans_data.append([keys, float(transients[n][3]), float(transients[n][6]), float(transients[n][10]), max(flux), max(avg_flux_ratio),freq])
                        trans_data_all.append([keys, float(transients[n][3]), float(transients[n][6]), float(transients[n][10]), max(flux), max(avg_flux_ratio),freq])
    print len(trans_data_all)

    print 'Number of transients in sample: '+str(len(trans_data))+' at '+str(freq)+'MHz'
    


###################### CREATING ALL TRANSIENT PLOTS ######################

    if plt_freqs == 'T':
        label={1: r'$\eta_\nu$', 2: 'Significance', 3: r'V$_\nu$', 4: 'Max Flux (Jy)', 5: 'Max Flux Ratio (extracted/average)'}
        plotname={1: 'etanu', 2: 'signif', 3: 'Vv', 4: 'flux', 5: 'flxrat'}
        data=[np.log10(x[1]) for x in trans_data if x[1]>0]
        sigcut_etanu=10.**(plothist(data,r'log($\eta_\nu$)','etanu_hist',sigma,freq))
        data=[np.log10(x[3]) for x in trans_data if x[3]>0]
        sigcut_Vnu=10.**(plothist(data,r'log(V$_\nu$)','Vnu_hist',sigma,freq))
        plotfig(trans_data, 4, 1, label[4], label[1], plotname[4]+'_'+plotname[1]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
        plotfig(trans_data, 4, 3, label[4], label[3], plotname[4]+'_'+plotname[3]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
        plotfig(trans_data, 5, 1, label[5], label[1], plotname[5]+'_'+plotname[1]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
        plotfig(trans_data, 5, 3, label[5], label[3], plotname[5]+'_'+plotname[3]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
        plotfig(trans_data, 1, 3, label[1], label[3], plotname[1]+'_'+plotname[3]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
        plotfig(trans_data, 4, 2, label[4], label[2], plotname[4]+'_'+plotname[2]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
        plotfig(trans_data, 5, 2, label[5], label[2], plotname[5]+'_'+plotname[2]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
        plotfig(trans_data, 1, 2, label[1], label[2], plotname[1]+'_'+plotname[2]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
        plotfig(trans_data, 3, 2, label[3], label[2], plotname[3]+'_'+plotname[2]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
    output3 = open('trans_data_'+str(freq)+'.txt','w')
    output3.write('#Trans_id,eta_nu,signif,V_nu,flux,fluxrat \n')
    for x in range(len(trans_data)):
        string='%s' % ', '.join(str(val) for val in trans_data[x])
        output3.write(string+'\n')
    output3.close()
trans_data=trans_data_all
###plt_colour_colour(trans_data,frequencies)

###################### CREATING ALL TRANSIENT PLOTS ######################
frequencies.sort()
label={1: r'$\eta_\nu$', 2: 'Significance', 3: r'V$_\nu$', 4: 'Max Flux (Jy)', 5: 'Max Flux Ratio (extracted/average)'}
plotname={1: 'etanu', 2: 'signif', 3: 'Vv', 4: 'flux', 5: 'flxrat'}
freq='all'
data=[np.log10(x[1]) for x in trans_data if x[1]>0]
sigcut_etanu=10.**(plothist(data,r'log($\eta_\nu$)','etanu_hist',sigma,freq))
data=[np.log10(x[3]) for x in trans_data if x[3]>0]
sigcut_Vnu=10.**(plothist(data,r'log(V$_\nu$)','Vnu_hist',sigma,freq))
create_scatter_hist(trans_data,sigma)

diagnostic_plots(trans_data,sigcut_etanu, sigcut_Vnu, frequencies)

plotfig(trans_data, 4, 1, label[4], label[1], plotname[4]+'_'+plotname[1]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
plotfig(trans_data, 4, 3, label[4], label[3], plotname[4]+'_'+plotname[3]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
plotfig(trans_data, 5, 1, label[5], label[1], plotname[5]+'_'+plotname[1]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
plotfig(trans_data, 5, 3, label[5], label[3], plotname[5]+'_'+plotname[3]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
plotfig(trans_data, 1, 3, label[1], label[3], plotname[1]+'_'+plotname[3]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
plotfig(trans_data, 4, 2, label[4], label[2], plotname[4]+'_'+plotname[2]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
plotfig(trans_data, 5, 2, label[5], label[2], plotname[5]+'_'+plotname[2]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
plotfig(trans_data, 1, 2, label[1], label[2], plotname[1]+'_'+plotname[2]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)
plotfig(trans_data, 3, 2, label[3], label[2], plotname[3]+'_'+plotname[2]+'_'+str(freq)+'MHz',sigcut_etanu, sigcut_Vnu, frequencies)

output3 = open('trans_data_'+str(freq)+'.txt','w')
output3.write('#Trans_id,eta_nu,signif,V_nu,flux,fluxrat \n')
for x in range(len(trans_data)):
    string='%s' % ', '.join(str(val) for val in trans_data[x])
    output3.write(string+'\n')
output3.close()

print('Completed successfully :-)')
