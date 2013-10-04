#!/usr/bin/python

import os, errno, time, sys, pylab
from scipy import *
from scipy import optimize
from scipy import special
from scipy import stats
import numpy as np
import matplotlib.cm as cm
import matplotlib.ticker as ticker
from datetime import datetime
import logging, csv

#import monetdb.sql as db
#from monetdb.sql import Error as Error

#host = sys.argv[1] # number of sources per image
#ns = int(sys.argv[2]) # number of sources per image
#iter = int(sys.argv[3]) # number of images to process

dbversion = '2013-sp3'
machine = 'napels'
basesources = 10
images = 10000
basedir = '/export/scratch2/bscheers/lofar/release1/performance'
bdir = basedir + '/' + dbversion + '/' + machine + '/' + str(basesources) + 'x' + str(images)
logdir = bdir + '/log'
plotdir = bdir + '/plot'

def plot_accumulated_query_runtimes():
    """
    Plot it
    """
    
    plotfiles = []
    
    fig = pylab.figure(figsize=(12,8))
    ax = fig.add_subplot(111)
    for i in range(len(ax.get_xticklabels())):
        ax.get_xticklabels()[i].set_size('x-large')
    for i in range(len(ax.get_yticklabels())):
        ax.get_yticklabels()[i].set_size('x-large')
    pylab.grid(True)
    
    # all files are csv. imgid, querytime, query+committime
    logfiles = [
               #"_associate_extracted_sources.log"
               #,"isrejected.log"
               #,"insert_image.log"
               #,"insert_extracted_sources.log"
               "_check_meridian_wrap.log"
               ,"_insert_temprunningcatalog.log" # 3
               ,"_flag_many_to_many_tempruncat.log"
               ,"_insert_1_to_many_runcat.log"
               ,"_insert_1_to_many_runcat_flux.log"
               ,"_insert_1_to_many_basepoint_assoc.log"
               ,"_insert_1_to_many_skyrgn.log"
               ,"_insert_1_to_many_monitoringlist.log"
               ,"_insert_1_to_many_transient.log"
               ,"_delete_1_to_many_inactive_assoc.log"
               ,"_delete_1_to_many_inactive_runcat_flux.log"
               ,"_flag_1_to_many_inactive_runcat.log"
               ,"_flag_1_to_many_inactive_tempruncat.log"
               ,"_delete_1_to_many_inactive_assocskyrgn.log"
               ,"_delete_1_to_many_inactive_monitoringlist.log"
               ,"_delete_1_to_many_inactive_transient.log"
               ,"_insert_1_to_1_assoc.log" # 5
               ,"_update_1_to_1_runcat.log"  # 1
               ,"_update_1_to_1_runcat_flux.log" # 2
               ,"_insert_1_to_1_runcat_flux.log"
               ,"_insert_new_runcat.log" #
               ,"_insert_new_runcat_flux.log"
               ,"_insert_new_runcat_skyrgn_assocs_a.log"
               ,"_insert_new_runcat_skyrgn_assocs_b.log"
               ,"_insert_new_assoc.log"
               ,"_insert_new_monitoringlist.log" # 4
               ,"_insert_new_transient.log" # 6
               ##,"_empty_temprunningcatalog.log"
               ,"_delete_inactive_runcat.log"
               ##,"_select_updated_variability_indices.log"
               ]

    clrs = ['b','r','c','m','y','k','chartreuse']
    lss = ['-','--','-.',':']
    #mrks = ['.','o','*','+','x','D']
    for i, f in enumerate(logfiles):
        #print logdir + "/" +f
        row = np.genfromtxt(logdir + "/" +f, dtype=float, delimiter=',')
        imgfl = zip(*row)[0]
        imgid = [int(fl) for fl in imgfl]
        assoc_query = list(zip(*row)[1])
        assoc_commit = list(zip(*row)[2])
        #assoc_bbp = list([int(bbp) for bbp in zip(*row)[3]])
        accum_q = []
        accum_c = []
        #accum_b = []
        sum_q = 0.
        sum_c = 0.
        #sum_b = 0.
        for j in range(len(assoc_query)):
            sum_q += assoc_query[j]
            sum_c += assoc_commit[j]
            #sum_b += assoc_bbp[j]
            accum_q.append(sum_q)
            accum_c.append(sum_c)
            #accum_b.append(sum_b)
        
        clr = clrs[i % len(clrs)]
        ls = lss[i / len(clrs)]
        #mrk = mrks[i / len(clrs)]
        if f.startswith('_'):
            f = f[1:]
        lbl = '' + f[:-4]
        print clr,ls,lbl
        #print clr,mrk,lbl

        #ax.plot(accum_c[:2000], linewidth=2, color=clr, linestyle=ls, label=lbl)
        #ax.plot(accum_c, linewidth=2, color=clr, linestyle=ls, label=lbl)
        #ax.set_label(lbl)
        ax.plot(accum_c, linewidth=2, color=clr, linestyle=ls, label=lbl)
        #ax.plot(accum_c, linewidth=2, color=clr, linestyle='-', marker=mrk, mec=clr, label=lbl)
        #ax.plot(accum_b, linewidth=2, color=clr, linestyle=ls, label=lbl)
    
    #ax.set_xlim([0,50000])
    #ax.set_xlim([0,2000])
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%1.1f')%(x*1e-4)))
    #ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%d')%(x*1e-4)))
    ax.set_xlabel(r'Query call ($\times\,10,000$)', size='x-large')
    #ax.set_xlabel(r'Query call', size='xx-large')
    
    #ax.set_ylim([0,4000])
    #ax.set_ylim([0,1200])
    #ax.set_ylim([0,16000])
    #ax.set_ylim([0,1.8])
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%1.3f')%(y*1e-4)))
    #ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%d')%(y*1e-4)))
    ax.set_ylabel(r'Accumulated run time [s] ($\times\,10,000$)', size='x-large')
    #ax.set_ylabel(r'Accumulated run time [s]', size='xx-large')
    #ax.set_ylabel(r'Accumulated number of transient bats', size='x-large')
    
    ax.legend(numpoints=1, loc='upper left', fontsize='x-small')
    #ax.legend(numpoints=1, loc='upper left', fontsize='small')
    #mytitle = "SourceAssociation_top6Q_" + \
    mytitle = "SourceAssociation_" + \
                dbversion + "_" + machine + "_local_" + \
                str(basesources) + "x" + str(images)
    #mytitle = "Source Association; 6 Most Intensive Queries; Feb2013-SP3; napels (local), 10x10,000"
    #mytitle = "Source Association; 29-1 Queries; Feb2013-SP3; napels (local), 10x10,000"
    #ax.set_title(r'Source Association; $29-1$ Queries; Feb2013-SP3; napels (local), $10\times10,000$')
    ax.set_title(mytitle)
    #ax.legend(numpoints=1, loc='upper right', fontsize='x-small')
    #ax.legend(numpoints=1, loc='upper left')
    fname = mytitle + '.eps'
    plotfiles.append(plotdir + '/' + fname)
    pylab.savefig(plotfiles[-1],dpi=600)
    print plotfiles[-1]
    
    return plotfiles

plot_accumulated_query_runtimes()
