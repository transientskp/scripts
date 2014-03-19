#!/usr/bin/python
import matplotlib
import matplotlib.pyplot as plt
#from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import math
import sys
from scipy.stats import norm
import pylab
pylab.rcParams['legend.loc'] = 'best'
from matplotlib.ticker import NullFormatter

def create_scatter_hist(x,y,sigma):
    nullfmt   = NullFormatter()         # no labels
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left+width+0.02
    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]
    fig = plt.figure(1,figsize=(12,12))
    axScatter = fig.add_subplot(223, position=rect_scatter)
    plt.xlabel(r'$\eta_{\nu}$', fontsize=16)
    plt.ylabel(r'$V_{\nu}$', fontsize=16)
    axHistx=fig.add_subplot(221, position=rect_histx)
    axHisty=fig.add_subplot(224, position=rect_histy)
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)
    axScatter.scatter(x, y)
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
    xvals=[-3., -2., -1., 0., 1., 2., 3.]
    xtxts=[str(10.**a) for a in xvals]
    yvals=[-2., -1., 0.]
    ytxts=[str(10.**a) for a in xvals]
    axScatter.set_xticks(xvals)
    axScatter.set_xticklabels(xtxts)
    axScatter.set_yticks(yvals)
    axScatter.set_yticklabels(ytxts)
    plt.savefig('scatter_hist.png')
    return


def plothist(x, name,filename,sigma):
    param=norm.fit(x)
    range_x=np.linspace(min(x),max(x),1000)
    fit=norm.pdf(range_x,loc=param[0],scale=param[1])
    plt.plot(range_x,fit, 'b--', linewidth=2)
    plt.hist(x,bins=50,normed=1,histtype='stepfilled')
    sigcut = param[1]*sigma+param[0]
    plt.axvline(x=sigcut, linewidth=2, color='k', linestyle='--')
    plt.title('%s mean: %.3f sd: %.3f' % (name, param[0], param[1]))
    plt.text((sigcut-(0.3*param[1])), 1, r'%.1f $\sigma$: %.3f' % (sigma,sigcut), rotation=90)
    plt.xlabel(name)
    plt.savefig(filename+'.png')
    plt.close()
    return sigcut

def dump_data(release,database,dataset_id):
    ### Getting the data from the Database - Thanks Tim!
    if release == '0':
        import dump_transients_v0
        from dump_transients_v0 import dump_trans
        dump_trans(database,dataset_id)
    elif release == '1m':
        import dump_transients_v1
        from dump_transients_v1 import dump_trans
        dump_trans(database,dataset_id)
    elif release == '1p':
        import dump_transients_v1_postgres
        from dump_transients_v1_postgres import dump_trans
        dump_trans(database,dataset_id)
    else:
        print 'ERROR in release number'
        exit()

def detect_anomaly(trans_data,sigma):
    data=[np.log10(x[1]) for x in trans_data if x[1]>0 if x[2]>0]
    sigcut_etanu=10.**(plothist(data,r'log($\eta_\nu$)','etanu_hist',sigma))
    data2=[np.log10(x[2]) for x in trans_data if x[2]>0 if x[1]>0]
    sigcut_Vnu=10.**(plothist(data2,r'log(V$_\nu$)','Vnu_hist',sigma))    
    create_scatter_hist(data,data2,sigma)
    both=0
    eta=0
    V=0
    output = open('anomalous_both.txt','w')
    output2 = open('anomalous_etanu_only.txt','w')
    output3 = open('anomalous_Vnu_only.txt','w')
    for trans in trans_data:
        if trans[1] > sigcut_etanu and trans[2] > sigcut_Vnu:
            both=both+1
            string='%s' % ', '.join(str(val) for val in trans)
            output.write(string+'\n')
        if trans[1] > sigcut_etanu:
            eta=eta+1
            string='%s' % ', '.join(str(val) for val in trans)
            output2.write(string+'\n')
        if trans[2] > sigcut_Vnu:
            V=V+1
            string='%s' % ', '.join(str(val) for val in trans)
            output3.write(string+'\n')
    output.close()
    output2.close()
    output3.close()
    print 'Both anomalous: '+str(both)
    print 'Eta anomalous: '+str(eta)
    print 'V anomalous: '+str(V)
    print('Completed successfully :-)')
    return
