#!/usr/bin/python
import datetime
from datetime import datetime
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import fileinput
import os
import coords as C
from glob import glob
import numpy as np
import mlpy
import math
from pylab import *

###################### INITIAL SETUP STEPS ######################

# General parameters...
detect_thresh='8'
analysis_thresh='4'
probability_thresh='0.0'
eta_lim='0'
v_lim='0'
minpoints='1'
skymodel='lsc_fake.skymodel'
test_data='/home/antoniar/simulated_datasets/single_flare'
database='antoniar3'
transient_position=C.Position('14:20:00 52:00:00').dd()
output_folder='plots'
trap='FALSE'

# Setting up the general lists and dictionaries needed
trans_runcat=[]
vlss_sources=[]
trans_data=[]

# Reading in the skymodel for later steps
vlss_data2=open(skymodel, 'r')
lines = iter(vlss_data2)
lines.next()
lines.next()
for line in lines:
    vlss_sources.append(line)
vlss_data2.close()
vlss_data=[]
for a in range(len(vlss_sources)):
    data=vlss_sources[a].split(', ')
    dec=data[3].replace('.',':', 2)
    position=data[2]+' '+dec
    x=(C.Position(position)).dd()
    vlss_data.append([x,float(data[4])])

###################### DEFINE SUBROUTINES ######################

def stats(x,y,plotname,test):
    print('calculating statistics for: '+plotname)
    test_results=[]
    svm=mlpy.LibLinear(solver_type='l2r_l2loss_svc_dual', C=50)
    svm.learn(x,y)
    w=svm.w()
    b=svm.bias()
    xx=np.arange(np.min(x[:,0]), np.max(x[:,0]), 0.01)
    yy=-(xx*w[0]+b)/(w[1])
    svm.save_model(plotname+'.model') 
    for i in range(len(test)):
        test_results.append([test[i], svm.pred_probability(test[i])])
    return (xx, yy, test_results)

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
    for x in range(len(trans_data)):
        if trans_data[x][0] in trans_runcat:
            plt.plot(trans_data[x][a], [trans_data[x][b]],'r.')
            x1.append([float(trans_data[x][a]),float(trans_data[x][b])])
            n1=n1+1
        if trans_data[x][0] not in trans_runcat:
            plt.plot(trans_data[x][a],trans_data[x][b],'b.')
            x2.append([float(trans_data[x][a]),float(trans_data[x][b])])
            n2=n2+1
    x2=np.array(x2)
    x1=np.array(x1)
    y1 = np.zeros(n1, dtype=np.int)
    y2 = np.ones(n2, dtype=np.int)
    x = np.concatenate((x1, x2), axis=0)
    y = np.concatenate((y1, y2))
    if a == 1 or a == 2 or a == 3:
        test1=np.power(10,np.arange(np.log10(np.min(x[:,0])),np.log10(np.max(x[:,0])),(np.log10(np.max(x[:,0]))-np.log10(np.min(x[:,0])))/2000))
    else:
        test1=np.arange(np.min(x[:,0]),np.max(x[:,0]),(np.max(x[:,0])-np.min(x[:,0]))/2000)
    if b == 1 or b == 2 or b == 3:
        test2=np.power(10,np.arange(np.log10(np.min(x[:,1])),np.log10(np.max(x[:,1])),(np.log10(np.max(x[:,1]))-np.log10(np.min(x[:,1])))/2000))
    else:
        test2=np.arange(np.min(x[:,1]),np.max(x[:,1]),(np.max(x[:,1])-np.min(x[:,1]))/2000)
    test=[]
    for w in range(len(test1)):
        for z in range(len(test2)):
            test.append([test1[w],test2[z]])
    xx, yy, test_results = stats(x,y,plotname,test)
    plt.plot(xx,yy,'g', lw=2)
    m=[test_results[i][0][0] for i in range(len(test_results))]
    n=[test_results[i][0][1] for i in range(len(test_results))]
    z=[test_results[i][1][0] for i in range(len(test_results))]
    mi = np.linspace(min(m),max(m))
    ni = np.linspace(min(n),max(n))
    M, N = np.meshgrid(mi, ni)
    Z = griddata(m,n,z,mi,ni)
    levels = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    cs = plt.contour(M, N, Z, levels, colors='k')
    fmt = {}
    strs = ['10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%' ]
    for l,s in zip( cs.levels, strs ):
        fmt[l] = s
    plt.xlabel(xlabel)
    if a == 1 or a == 2 or a == 3:
        plt.xscale('log')
    if b == 1 or b == 2 or b == 3:
        plt.yscale('log')
    plt.axis([np.min(x[:,0])*0.6,np.max(x[:,0])*1.1, np.min(x[:,1])*0.6,np.max(x[:,1])*1.1])
    plt.ylabel(ylabel)
    plt.clabel(cs, cs.levels[::2], inline=1,fmt=fmt, fontsize=9)
    savefig(output_folder+'/transients_'+plotname+'.png')
    close()

###################### RUNNING THROUGH INDIVIDUAL DATASETS ######################
os.system('mkdir '+output_folder)

for folders in glob(test_data+'/*'):
    total_flux_ratio={}
    total_avg_flux_ratio={}
    total_flux_ratio_err={}
    total_time_diff={}
    image_dir=folders.split('/')[5]
    transient_quiescent_flux=float(image_dir.split('Jy')[1].split('_')[1]) # Obtains quiescent flux
    if transient_quiescent_flux==0:
        transient_quiescent_flux=0.1 # Simply to stop a division by zero later when dividing by skymodel... Although this has been taken out...
    vlss_data.append([transient_position, transient_quiescent_flux]) # Add transient to skymodel data
    if trap == 'TRUE':
        os.system('./manage.py initjob '+image_dir)    
        file1 = image_dir+'/images_to_process.py'
    ### Adding correct parameters to the parsets and files used by TraP (not pretty but works)
        for line in fileinput.input(file1, inplace=1):
            print line.replace('images = sorted( glob.glob(os.path.expanduser("/home/gijs/Data/small_multifreq/*.fits")) )','images = sorted( glob.glob(os.path.expanduser("'+test_data+'/'+image_dir+'/*.corr")) )')
        file2 = image_dir+'/parsets/quality_check.parset'
        for line in fileinput.input(file2, inplace=1):
            print line.replace('sigma = 3               # sigma value used for iterave clipping image before RMS calculation','sigma = 5               # sigma value used for iterave clipping image before RMS calculation')
        for line in fileinput.input(file2, inplace=1):
            print line.replace('#intgr_time = 18654      # integration time in seconds','intgr_time = 660      # integration time in seconds')
        for line in fileinput.input(file2, inplace=1):
            line = line.strip()
            if line == '': continue
            print line
        file3 = image_dir+'/parsets/sourcefinder.parset'
        for line in fileinput.input(file3, inplace=1):
            print line.replace('detection.threshold = 15','detection.threshold = '+detect_thresh)
        for line in fileinput.input(file3, inplace=1):
            print line.replace('analysis.threshold = 5','analysis.threshold = '+analysis_thresh)
        for line in fileinput.input(file3, inplace=1):
            print line.replace('association.radius = 1','association.radius = 2.7')
        for line in fileinput.input(file3, inplace=1):
            print line.replace('margin = 10','#margin = 10')
        for line in fileinput.input(file3, inplace=1):
            print line.replace('radius = 280','radius = 230')
        for line in fileinput.input(file3, inplace=1):
            line = line.strip()
            if line == '': continue
            print line
        file4 = image_dir+'/parsets/persistence.parset'
        for line in fileinput.input(file4, inplace=1):
            print line.replace('description = TRAP dataset','description = '+image_dir)
        for line in fileinput.input(file4, inplace=1):
            print line.replace('mongo_host = localhost','#mongo_host = localhost')
        for line in fileinput.input(file4, inplace=1):
            print line.replace('#mongo_host = pc-swinbank.science.uva.nl','mongo_host = pc-swinbank.science.uva.nl')
        for line in fileinput.input(file4, inplace=1):
            line = line.strip()
            if line == '': continue
            print line
        file5 = image_dir+'/parsets/transientsearch.parset'
        for line in fileinput.input(file5, inplace=1):
            print line.replace('probability.threshold = 0.5','probability.threshold = '+probability_thresh)
        for line in fileinput.input(file5, inplace=1):
            print line.replace('probability.eta_lim = 0.0','probability.eta_lim = '+eta_lim)
        for line in fileinput.input(file5, inplace=1):
            print line.replace('probability.V_lim = 0.00','probability.V_lim = '+v_lim)
        for line in fileinput.input(file5, inplace=1):
            print line.replace('probability.minpoints = 1','probability.minpoints = '+minpoints)       
        for line in fileinput.input(file5, inplace=1):
            line = line.strip()
            if line == '': continue
            print line
    ### Running TraP! :-)
        os.system('time ./manage.py run '+image_dir+' > '+image_dir+'/traplog')

    ### Getting dataset id - not pretty but works!
    f = open(image_dir+'/traplog', 'r')
    for line in f:
            if 'dataset_id' in line:
                dataset_id=line.split('dataset_id = ')[1].rstrip()
                break
    ### Getting the data from the Database - Thanks Tim!
    os.system('python ~antoniar/scripts/dump_transient_runcat.py --dbname='+database+' '+dataset_id)
    os.system('mv ds_* '+output_folder)
    ### Reading in the data from the output files of above script
    transients=[]
    data=open(output_folder+'/ds_'+dataset_id+'_transients.csv','r')
    for lines in data:
        lines=lines.rstrip()
        transients.append(lines.split(','))
    data.close()
    sources=[]
    data=open(output_folder+'/ds_'+dataset_id+'_sources.csv','r')
    for lines in data:
        lines=lines.rstrip()
        sources.append(lines.split(','))
    data.close()
    runcat=0
    ### Reading the lightcurves of each individual source in the dataset
    new_source={}
    for a in range(len(sources)):
        new_runcat=sources[a][5]
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
            date.append(datetime.strptime(new_source[keys][b][7],  '%Y-%m-%d %I:%M:%S'))
        oldest=min(date)
        time_diff=[]
        for c in range(len(date)):
            time1=time.mktime(date[c].timetuple())
            time2=time.mktime(oldest.timetuple())
            time3=(time1-time2)
            time_diff.append(time3)
#        plt.figure()
#        plt.errorbar(time_diff, flux, yerr=flux_err, fmt='o')
#        plt.title("Flux Lightcurve Runcat ID: "+keys)
#        plt.xlabel("Time since start (s)")
#        plt.ylabel("Flux (Jy)")
#        savefig(output_folder+'/'+keys+'_lightcurve.png')
#        close()
        position2=C.Position((float(new_source[keys][0][9]), float(new_source[keys][0][8])))
        posdif_old=100000
        ### For each individual source find the skymodel counterpart and remember which is the inserted transient
        for src in range(len(vlss_data)):
            if vlss_data[src][1] > 2:
                posdif=position2.angsep(C.Position(vlss_data[src][0]))
                if posdif < posdif_old:
                    flx=float(vlss_data[src][1])
                    posdif_old=posdif
                    if position2.angsep(C.Position('14:20:00 52:00:00'))<0.05:
                        if keys not in trans_runcat:
                            trans_runcat.append(keys)
        ### Calculate the ratios...
        flux_ratio = [x / flx for x in flux] 
        avg_flux_ratio_err=[]
        avg_flux_ratio = [x / (sum(flux)/len(flux)) for x in flux]
        ### Collate and store the transient parameters (these are across all the pipeline runs for the final figures)
        for n in range(len(transients)):
            if keys == transients[n][5]:
                trans_data.append([keys, transients[n][3], transients[n][6], transients[n][10], max(flux), max(flux_ratio), max(avg_flux_ratio)])
        ### For each individual source plot a flux ratio lightcurve (extracted/average)
        for i in range(len(flux_ratio)):
            avg_flux_ratio_err.append(avg_flux_ratio[i]*flux_err[i]/flux[i])
#        plt.figure()
#        plt.errorbar(time_diff, avg_flux_ratio, yerr=avg_flux_ratio_err, fmt='o')
#        plt.title("Average Flux Ratio Lightcurve for Runcat ID: "+keys)
#        plt.xlabel("Time since start (s)")
#        plt.ylabel("Flux (Extracted/Average)")
#        savefig(output_folder+'/'+keys+'_avgflxratio_lightcurve.png')
#        close()
        ### Remember each individual source for plotting together
        total_time_diff[keys]=time_diff
        total_flux_ratio[keys]=flux_ratio
        total_avg_flux_ratio[keys]=avg_flux_ratio
    ### Create the total flux ratio lightcurve plots showing each extracted source as a line
    for keys in total_time_diff:
        time_diff=total_time_diff[keys]
        flux_ratio=total_flux_ratio[keys]
        avg_flux_ratio=total_avg_flux_ratio[keys]
        data = zip(time_diff, flux_ratio, avg_flux_ratio)
        data.sort()
        sorted_time_diff, sorted_flux_ratio, sorted_avg_flux_ratio = zip(*data)
        plt.plot(sorted_time_diff, sorted_avg_flux_ratio)
    plt.figure()
    plt.title("Average Flux Ratio Lightcurve for all sources ")
    plt.xlabel("Time since start (s)")
    plt.ylabel("Flux (Extracted/Average)")
    savefig(output_folder+'/'+dataset_id+'_total_avgflxratio_lightcurve.png')
    close()

###################### WRITE OUT TRANSIENT DATA TO FILE ######################

output=open('transient_data.txt','w')
output.writelines( "%s\n" % item for item in trans_data )
output.close()

###################### CREATING ALL TRANSIENT PLOTS ######################

label={1: r'$\eta_\nu$', 2: 'Significance', 3: r'V$_\nu$', 4: 'Max Flux (Jy)', 5: 'Max Flux Ratio (extracted/skymodel)', 6: 'Max Flux Ratio (extracted/average)'}
plotname={1: 'etanu', 2: 'signif', 3: 'Vv', 4: 'flux', 5: 'flxratsky', 6: 'flxrat'}
plotfig(trans_data, 4, 1, label[4], label[1], plotname[4]+'_'+plotname[1])
plotfig(trans_data, 4, 3, label[4], label[3], plotname[4]+'_'+plotname[3])
plotfig(trans_data, 6, 1, label[6], label[1], plotname[6]+'_'+plotname[1])
plotfig(trans_data, 6, 3, label[6], label[3], plotname[6]+'_'+plotname[3])
plotfig(trans_data, 1, 3, label[1], label[3], plotname[1]+'_'+plotname[3])

### If inserted transient is not detected, create this error file:
output2 = open('undetected_transients.txt','w')
output2.write('Inserted transients not detected: \n')        
stuff=[]
for m in range(len(trans_data)):
    stuff.append(trans_data[m][0])
for n in trans_runcat:
    if n not in stuff:
        output2.write(n+'\n')
output2.close()
###
print('Completed successfully :-)')


