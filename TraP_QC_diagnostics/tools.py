#!/usr/bin/python
#
#
# Author: Antonia Rowlinson
# E-mail: b.a.rowlinson@uva.nl
#
from datetime import datetime
import tkp.utility.coordinates as coords
from scipy.stats import norm
from scipy.optimize import leastsq
import numpy as np
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import dump_image_data_v1
from dump_image_data_v1 import dump_images

def get_data(database, username, password, host, port, databaseType, dataset_id, dataset_id2):
#
# Calls a function to dump the image data from the TraP database into a CSV file
#
    dump_images(database, username, password, dataset_id, dataset_id2, databaseType, host, port)
#    if release == '1m':
#        dump_images(database,dataset_id, dataset_id2, 'monetdb', 'heastrodb', 52000)
#        return
#    elif release == '1p':
#        dump_images(database,dataset_id, dataset_id2, 'postgresql', 'heastrodb', 5432)
#        return
#    else:
#        print 'This script is for either Release 1 MonetDB (1m) or Release 1 Postgres (1p) databases, please specify 1m or 1p.'
#        exit()

def extract_data(dataset_id, CasA, CygA, VirA):
#
# Opens the CSV file output from get_data and reads the relevant data into an array
#
    image_info=[]
    image_data=open('ds_'+dataset_id+'_images.csv','r')
    list_img = image_data.readlines()
    image_data.close()
    frequencies=[]
    plt_ratios=True
    for lines in list_img: # Loop through all the images
        row=lines.split(',')
        image=row[9].split('/')[-1].rstrip()+'.fits' # Image name
        date=datetime.strptime(row[8].strip().split(".")[0],'%Y-%m-%d %H:%M:%S') # Time of observation (not currently used)
        freq=int((float(row[3].strip())/1e6) + 0.5) # Observation frequency, integer number in MHz
        if freq not in frequencies: # Keeping a record of which frequencies are in the dataset
            frequencies.append(freq)
        ellipticity=float(row[5])/float(row[6]) # Restoring beam ellipticity, Bmaj/Bmin
        if "rms value" in row[2]:
            theoretical=float(row[2].split(' ')[8].split('(')[1].split(')')[0].strip()) # Theoretical noise limit
            ratio=float(row[2].split(' ')[4].strip()) # Observed RMS / Theoretical noise (calculated by TraP)
            # RMS/Confusion limit for TraP              
            maxbl=6.
            beam = 206265.*((300./float(freq))/(1000*maxbl))
            confusion=29.0E-6*math.pow(beam,1.54)*math.pow((float(freq)/74.0),-0.7)
            confusion_ratio=confusion/float(row[7])
        else:
            theoretical=0.
            ratio=0.
            confusion=0.
            confusion_ratio=0.
            plt_ratios=False
        rms=float(row[7]) # Image RMS
        pc = [float(row[1]), float(row[0])]         # Separation of image centre relative to A-Team sources
        posdif_CasA=coords.angsep(CasA[0],CasA[1],pc[0],pc[1])/3600.
        posdif_CygA=coords.angsep(CygA[0],CygA[1],pc[0],pc[1])/3600.
        posdif_VirA=coords.angsep(VirA[0],VirA[1],pc[0],pc[1])/3600.
        # Input data into array: [RA, Dec, Obs date, Obs Freq, RMS noise, Theoretical noise, RMS/Theoretical, Restoring beam ellipticity, Seperation CasA, Seperation CygA, Seperation VirA, Image name, BMaj,confusion,confusion_ratio]
        image_info.append([row[0],row[1],date,freq,rms,theoretical,ratio,ellipticity,posdif_CasA,posdif_CygA,posdif_VirA,image,float(row[5]),confusion,confusion_ratio])
    return image_info, frequencies, plt_ratios

def fit_hist(data, sigma, xlabel, pltname, freq):
# fit a Gaussian distribution to the input data, output a plot and threshold for a given sigma
    if len(data) > 0:
        p=guess_p(data)
        mean, rms, threshold = plothist(data, xlabel, pltname, sigma,freq, p)
        return mean, rms, threshold
    else:
        return 0,0,0

def res(p, y, x):
# calculate residuals between data and Gaussian model
  m1, sd1, a = p
  y_fit = a*norm2(x, m1, sd1)
  err = y - y_fit
  return err

def guess_p(x):
# estimate the mean and rms as initial inputs to the Gaussian fitting
    median = np.median(x)
    temp=[n*n-(median*median) for n in x]
    rms = math.sqrt((abs(sum(temp))/len(x)))
    return [median, rms, math.sqrt(len(x))]

def norm2(x, mean, sd):
# creates a normal distribution in a simple array for plotting
    normdist = []
    for i in range(len(x)):
        normdist += [1.0/(sd*np.sqrt(2*np.pi))*np.exp(-(x[i] - mean)**2/(2*sd**2))]
    return np.array(normdist)
    
def plothist(x, name,filename,sigma,freq,p):
#
# Create a histogram of the data and fit a Gaussian distribution to it
#
    hist_x=np.histogram(x,bins=50) # histogram of data
    range_x=[hist_x[1][n]+(hist_x[1][n+1]-hist_x[1][n])/2. for n in range(len(hist_x[1])-1)]
    plt.hist(x,bins=50,histtype='stepfilled')
    plsq = leastsq(res, p, args = (hist_x[0], range_x)) # fit Gaussian to data
    fit2 = plsq[0][2]*norm2(range_x, plsq[0][0], plsq[0][1]) # create Gaussian distribution for plotting on graph
    plt.plot(range_x,fit2, 'r-', linewidth=3)
    sigcut=plsq[0][0]+plsq[0][1]*sigma # max threshold defined as (mean + RMS * sigma)
    sigcut2=plsq[0][0]-plsq[0][1]*sigma # min threshold defined as (mean - RMS * sigma)
    plt.axvline(x=sigcut, linewidth=2, color='k',linestyle='--')
    plt.axvline(x=sigcut2, linewidth=2, color='k', linestyle='--')
    print min(range_x),max(range_x)
    xvals=np.arange(int(min(range_x)),int(max(range_x)+1.5),1)
    xlabs=[str(10.**a) for a in xvals]
    plt.xticks(xvals,xlabs)
    plt.xlabel(name)
    plt.ylabel('Number of images')
    plt.savefig(filename+'_'+str(freq)+'MHz.png')
    plt.close()
    return plsq[0][0], plsq[0][1], sigcut

def plotfig_ATeam(trans_data, a, b, xlabel, ylabel, plotname,min_sep,avg):
    plt.figure()
    xvals=[trans_data[x][a] for x in range(len(trans_data))]
    yvals=[trans_data[x][b] for x in range(len(trans_data))]
    plt.plot(xvals,yvals,'r.',zorder=1)
    xmin=min(trans_data[x][a] for x in range(len(trans_data)))*0.7
    xmax=max(trans_data[x][a] for x in range(len(trans_data)))*1.3
    ymin=min(trans_data[x][b] for x in range(len(trans_data)))*0.7
    ymax=max(trans_data[x][b] for x in range(len(trans_data)))*1.1
    bin_size = ((xmax/1.3) - (xmin/0.7)) / 200.
    bins = [(x*bin_size)+(xmin/0.7) for x in range(200)]
    yavg=[]
    ysig=[]
    xbins_to_pop=[]
    count=0
    bins_tmp=bins
    for xbin in range(len(bins_tmp)):
        ydata=[trans_data[x][b] for x in range(len(trans_data)) if trans_data[x][a] >= bins_tmp[xbin] if trans_data[x][a] < bins_tmp[xbin]+bin_size]
        if len(ydata) != 0:
            yscatter=math.sqrt(sum([y**2.-np.mean(ydata)**2. for y in ydata])/len(ydata))
            yavg.append(np.mean(ydata))
            ysig.append(yscatter)
        else:
            xbins_to_pop.append(xbin)
    new_bins = [bins[x] for x in range(len(bins)) if x not in xbins_to_pop]
    bins=[b2+(bin_size/2.) for b2 in new_bins]
    nums=6
    max_cutoff=20.
    for k in range(len(new_bins)):
        if yavg[k]<avg:
            if k>nums:
                if new_bins[k]+1. < max_cutoff:
                    min_sep=int(round(new_bins[k],0)+1.)
            break
    plt.xlabel(xlabel)
    plt.errorbar(bins,yavg,fmt='.',color='k',linestyle='-',zorder=50)
    plt.axis([xmin,xmax,ymin,ymax])
    plt.ylabel(ylabel)
    plt.axhline(y=avg, linewidth=1, color='b')
    plt.savefig(plotname+'.png')
    plt.close()
    return min_sep

def plotfig_scatter(trans_data, a, b, xlabel, ylabel, plotname):
    xvals=[trans_data[x][a] for x in range(len(trans_data))]
    yvals=[trans_data[x][b] for x in range(len(trans_data))]
    plt.figure()
    plt.plot(xvals, yvals,'r.')
    ymin=min(yvals)*0.9
    ymax=max(yvals)*1.1
    xmin=min(xvals)*0.9
    xmax=max(xvals)*1.1
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(plotname+'.png')
    plt.close()

def extract_sky(vlss_sources,restfrq,frq):
    srcs_vlss=[]
    for a in vlss_sources:
        nums=a.split(', ')
        dec=nums[3]
        dec=dec.replace('.',':', 2)
        position= nums[2] + ' ' + dec
        f=nums[9].split('[')
        A1 = float(f[1].split(']')[0])
        A2 = 0
        if len(nums)>10 and ']' in nums[10]: A2 = float(nums[10].split(']')[0])
        if A2 == 0:
            new=float(nums[4])*(np.power(restfrq,A1))/(np.power(float(frq),A1))
        else:
            new=float(nums[4])*((np.power(restfrq,A1))+(np.power((restfrq*restfrq),A2)))/((np.power(float(frq),A1))+(np.power((float(frq)*float(frq)),A2)))
        ra_tmp = nums[2].split(':')
        dec_tmp = dec.split(':')
        # Fix for rounding errors in the gsm.py skymodel which give the number of seconds as 60.
        if int(float(dec_tmp[2])) == 60:
            dec_tmp[2]=59.999
        if int(float(ra_tmp[2])) == 60:
            ra_tmp[2]=59.999
        position = [coords.hmstora(int(float(ra_tmp[0])),int(float(ra_tmp[1])),int(float(ra_tmp[2]))), coords.dmstodec(int(float(dec_tmp[0])),int(float(dec_tmp[1])),int(float(dec_tmp[2])))]
        srcs_vlss.append([position,new])
    return srcs_vlss

def source_assoc(srcs_vlss,srcs_pyse,bmaj):
    intflxrat=[]
    if len(srcs_pyse) > 0:
        for a in range(len(srcs_pyse)):
            posdif_old=bmaj*5.*3600.
            for b in range(len(srcs_vlss)):
                posdif = coords.angsep(srcs_pyse[a][1][0],srcs_pyse[a][1][1],srcs_vlss[b][0][0],srcs_vlss[b][0][1])
                if posdif < posdif_old:
                    posdif_old = posdif
                    intflxrat.append([float(srcs_pyse[a][2]),float(srcs_pyse[a][2])/float(srcs_vlss[b][1])])
    return intflxrat

def find_avg_int_flx_rat(srcs_vlss,srcs_pyse,bmaj):
    intflxrat=source_assoc(srcs_vlss,srcs_pyse,bmaj)
    if len(intflxrat)==0:
        return 0.0, 0.0
    else:
        avgintflxrat = np.mean([x[1] for x in intflxrat])
        rms = np.std([x[1] for x in intflxrat]) # math.sqrt((sum(n*n - (avgintflxrat*avgintflxrat) for n in intflxrat))/len(intflxrat))
        return avgintflxrat, rms

def extr_src_data(dataset_id):
    sources=[]
    data=open('ds_'+dataset_id+'_sources.csv','r')
    for lines in data:
        lines=lines.rstrip()
        src_data=lines.split(',')
        if src_data[3]=='0':
            sources.append([(src_data[10].split('/'))[-1]+'.fits',[float(src_data[12]),float(src_data[11])],src_data[4],src_data[5]])
    data.close()
    return sources
