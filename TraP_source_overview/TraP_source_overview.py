#!/usr/bin/python
import datetime
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import coords as C
import numpy as np
import math
import sys
from datetime import datetime


###################### INITIAL SETUP STEPS ######################

if len(sys.argv) != 3:
    print 'python TraP_source_overview.py <database> <dataset_id>'
    exit()
database = sys.argv[1]
dataset_id = str(sys.argv[2])

# Setting up the general lists and dictionaries needed
trans_runcat=[]
trans_data=[]


###################### DEFINE SUBROUTINES ######################


def plotfig(trans_data, a, b, xlabel, ylabel, plotname):
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
        xmin=0.0
        xmax=105.0
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
    for x in range(len(trans_data)):
        plt.plot(trans_data[x][a], [trans_data[x][b]],'r.')
    plt.xlabel(xlabel)
    if a == 1 or a == 3:
        plt.xscale('log')
    if b == 1 or b == 3:
        plt.yscale('log')
    plt.axis([xmin,xmax,ymin,ymax])
    plt.ylabel(ylabel)
    plt.savefig('transients_'+plotname+'.png')
    plt.close()

###################### RUNNING THROUGH INDIVIDUAL DATASETS ######################
total_flux_ratio={}
total_avg_flux_ratio={}
total_flux_ratio_err={}
total_time_diff={}
 
### Getting the data from the Database - Thanks Tim!
os.system('python /home/antoniar/scripts/dump_transient_runcat.py --dbname='+database+' '+dataset_id)
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
for a in range(len(sources)):
    new_runcat=sources[a][6]
    if new_runcat != runcat:
        runcat=new_runcat
        new_source[runcat]=[sources[a]]
    else:
        new_source[runcat]=new_source[runcat]+[sources[a]]

### Creating plots for each individual source in the dataset
for keys in new_source.keys():
    flux=[]
    flux_err=[]
    date=[]
    for b in range(len(new_source[keys])):
        flux.append(float(new_source[keys][b][3]))
        flux_err.append(float(new_source[keys][b][4]))
        date.append(datetime.strptime(new_source[keys][b][8], '%Y-%m-%d %H:%M:%S'))
    oldest=min(date)
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
        if keys == transients[n][5]:
            trans_data.append([keys, float(transients[n][3]), float(transients[n][6]), float(transients[n][10]), max(flux), max(avg_flux_ratio)])

###################### CREATING ALL TRANSIENT PLOTS ######################

label={1: r'$\eta_\nu$', 2: 'Significance', 3: r'V$_\nu$', 4: 'Max Flux (Jy)', 5: 'Max Flux Ratio (extracted/average)'}
plotname={1: 'etanu', 2: 'signif', 3: 'Vv', 4: 'flux', 5: 'flxrat'}
plotfig(trans_data, 4, 1, label[4], label[1], plotname[4]+'_'+plotname[1])
plotfig(trans_data, 4, 3, label[4], label[3], plotname[4]+'_'+plotname[3])
plotfig(trans_data, 5, 1, label[5], label[1], plotname[5]+'_'+plotname[1])
plotfig(trans_data, 5, 3, label[5], label[3], plotname[5]+'_'+plotname[3])
plotfig(trans_data, 1, 3, label[1], label[3], plotname[1]+'_'+plotname[3])
plotfig(trans_data, 4, 2, label[4], label[2], plotname[4]+'_'+plotname[2])
plotfig(trans_data, 5, 2, label[5], label[2], plotname[5]+'_'+plotname[2])
plotfig(trans_data, 1, 2, label[1], label[2], plotname[1]+'_'+plotname[2])
plotfig(trans_data, 3, 2, label[3], label[2], plotname[3]+'_'+plotname[2])


output3 = open('trans_data.txt','w')
output3.write('#Trans_id,eta_nu,signif,V_nu,flux,fluxrat \n')
for x in range(len(trans_data)):
    string='%s' % ', '.join(str(val) for val in trans_data[x])
    output3.write(string+'\n')
output3.close()

print('Completed successfully :-)')
