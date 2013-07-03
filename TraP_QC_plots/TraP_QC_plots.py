#!/usr/bin/python
#
# Usage: python TraP_QC_plots.py <database> <dataset_id>
#
# This script uses the output from TKP-Web when all images are forced to be rejected on their rms noise (set high_bound=1 in quality_check.parset). Provide the dataset id and then this script will automatically extract the required data... The script then creates the noise comparison plots for the whole dataset. Note, you need access to your databases from your computer. This uses the script dump_image_data.py
#
# Then it uses the fits files in the current directory (so make sure you put them all there...) to find the average ratio between the average flux of sources in that image and the sky model flux. Note, you need gsm.py and pyse running on your computer. 
#
# TODO - use the results in the database rather than rerunning the sourcefinder (will need to input 2 different obsids until TraP remembers the noise parameters for all images)
# Possible TODO - get TraP to run automatically instead of specifying values and running TraP manually...
#
# Author: Antonia Rowlinson
# E-mail: b.a.rowlinson@uva.nl
#

import os
import glob
import pyfits
import sys
import numpy as np
from datetime import datetime
import coords as C
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import optparse

def main(opts,args):
    database=sys.argv[1]
    dataset_id=str(sys.argv[2])
    maxbl = opts.maxbl
    detection = opts.detection
    analysis = opts.analysis
    grid=opts.grid
    radius=opts.radius
    deblend=opts.deblend
    deblend_nthresh=opts.nthresh
    sys_err=opts.sys_err
    search_radius=opts.search_radius
    flux_limit=opts.flux_limit
    max_theoretical_ratio_cut=opts.max_theoretical_ratio_cut

    # A-Team positions
    CasA=C.Position((350.866417,58.811778))
    CygA=C.Position((299.868153,40.733916))
    VirA=C.Position((187.705930,12.391123))

    # Create the noise plots
    os.system('python /home/antoniar/scripts/dump_image_data.py --dbname='+database+' '+dataset_id)

    image_info=[]
    image_data=open('ds_'+dataset_id+'_images.csv','r')
    list = image_data.readlines()
    image_data.close()
    frequencies=[]
    failed_images=[]
    for lines in list:
        row=lines.split(',')
        image=row[6].split('/')[6].rstrip()+'.fits'
        date=datetime.strptime(row[5].strip(),'%Y-%m-%d %H:%M:%S')
        freq=float(row[3].strip())/1e6
        if freq not in frequencies:
            frequencies.append(freq)
        beam = 206265*((300/freq)/(1000*maxbl))
        confusion=29.0E-6*math.pow(beam,1.54)*math.pow((freq/74.0),-0.7)
        theoretical=float(row[2].split(' ')[8].split('(')[1].split(')')[0].strip())
        ratio=float(row[2].split(' ')[4].strip())
        rms=theoretical*ratio
        pc = C.Position((float(row[1]), float(row[0])))
        posdif_CasA=float(str(CasA.angsep(pc)).split(' degrees')[0])
        posdif_CygA=float(str(CygA.angsep(pc)).split(' degrees')[0])
        posdif_VirA=float(str(VirA.angsep(pc)).split(' degrees')[0])
        if rms/theoretical < max_theoretical_ratio_cut:
            image_info.append([row[0],row[1],date,freq,rms,theoretical,ratio,confusion,rms/confusion,posdif_CasA,posdif_CygA,posdif_VirA,image])
        else:
            failed_images.append(row[6].split('/')[6].rstrip())

    freq='all'
    rms=[image_info[n][4] for n in range(len(image_info))]
    avg_rms=(sum(rms)/len(rms))
    rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
    plotfig(image_info, 2, 4, 'Observation Time (hours)', 'RMS (Jy/beam)', 'rms',avg_rms,rms_rms,'Frequency: '+str(freq))

    rms_ratio=[image_info[n][6] for n in range(len(image_info))]
    avg_rms_ratio=(sum(rms_ratio)/len(rms_ratio))
    rms_rms_ratio=math.sqrt((sum(n*n-(avg_rms_ratio*avg_rms_ratio) for n in rms_ratio))/len(rms_ratio))
    plotfig(image_info, 2, 6, 'Observation Time (hours)', 'RMS/Theoretical', 'theoretical',avg_rms_ratio,rms_rms_ratio,'Frequency: '+str(freq))

    rms_ratio2=[image_info[n][8] for n in range(len(image_info))]
    avg_rms_ratio2=(sum(rms_ratio2)/len(rms_ratio2))
    rms_rms_ratio2=math.sqrt((sum(n*n-(avg_rms_ratio2*avg_rms_ratio2) for n in rms_ratio2))/len(rms_ratio2))
    plotfig(image_info, 2, 8, 'Observation Time (hours)', 'RMS/Confusion', 'confusion',avg_rms_ratio2,rms_rms_ratio2,'Frequency: '+str(freq))

    for ateam in ['CasA', 'CygA', 'VirA']:
        if ateam == 'CasA':
            a=9
        elif ateam == 'CygA':
            a=10
        elif ateam == 'VirA':
            a=11
        plotfig2(image_info, a, 4, 'Separation (degrees)', 'RMS (Jy/beam)', ateam+'_'+str(freq),avg_rms,rms_rms,ateam+' - Frequency: '+str(freq))

    for freq in frequencies:
        rms=[image_info[n][4] for n in range(len(image_info)) if image_info[n][3]==freq]
        avg_rms=(sum(rms)/len(rms))
        rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
        plotfig(image_info, 2, 4, 'Observation Time (hours)', 'RMS (Jy/beam)', 'rms_'+str(int(freq)),avg_rms,rms_rms,'Frequency: '+str(int(freq)))
        rms_ratio=[image_info[n][6] for n in range(len(image_info)) if image_info[n][3]==freq]
        avg_rms_ratio=(sum(rms_ratio)/len(rms_ratio))
        rms_rms_ratio=math.sqrt((sum(n*n-(avg_rms_ratio*avg_rms_ratio) for n in rms_ratio))/len(rms_ratio))
        plotfig(image_info, 2, 6, 'Observation Time (hours)', 'RMS/Theoretical', 'theoretical_'+str(int(freq)),avg_rms_ratio,rms_rms_ratio,'Frequency: '+str(int(freq)))
        rms_ratio2=[image_info[n][8] for n in range(len(image_info)) if image_info[n][3]==freq]
        avg_rms_ratio2=(sum(rms_ratio2)/len(rms_ratio2))
        rms_rms_ratio2=math.sqrt((sum(n*n-(avg_rms_ratio2*avg_rms_ratio2) for n in rms_ratio2))/len(rms_ratio2))
        plotfig(image_info, 2, 8, 'Observation Time (hours)', 'RMS/Confusion', 'confusion_'+str(int(freq)),avg_rms_ratio2,rms_rms_ratio2,'Frequency: '+str(int(freq)))
        for ateam in ['CasA', 'CygA', 'VirA']:
            if ateam == 'CasA':
                a=9
            elif ateam == 'CygA':
                a=10
            elif ateam == 'VirA':
                a=11
            plotfig2(image_info, a, 4, 'Separation (degrees)', 'RMS (Jy/beam)', ateam+'_'+str(int(freq)),avg_rms,rms_rms,ateam+' - Frequency: '+str(int(freq)))

    # Flux plots

    fitsfiles=glob.glob("*.fits")
    frequencies=[]
    avg_int_flx_rat=[]
    for fits in fitsfiles:
        print 'Analysing image: '+fits
        hdulist = pyfits.open(fits)
        ra = hdulist[0].header['CRVAL1']
        dec = hdulist[0].header['CRVAL2']
        bmaj = hdulist[0].header['BMAJ']
        bmin = hdulist[0].header['BMIN']
        restfrq = hdulist[0].header['RESTFRQ']
        if restfrq not in frequencies:
            frequencies.append(restfrq)
        date = hdulist[0].header['DATE-OBS']
        info1 = hdulist[0].header['HISTORY*']
        info1_new = str(info1).split("cellx='")
        cellsize = str(info1_new[1]).split("arcsec")
        skymodel = fits+'.sky'
        os.system('gsm.py '+skymodel+' '+str(ra)+' '+str(dec)+' '+str(search_radius)+' '+str(flux_limit))
        os.system('pyse --detection='+str(detection)+' --analysis='+str(analysis)+' --grid='+str(grid)+' --radius='+str(radius)+' --deblend --deblend-thresholds='+str(deblend_nthresh)+' --force-beam --csv '+fits)
        date=date=datetime.strptime(date.strip()[:19],'%Y-%m-%dT%H:%M:%S')
        for lines in image_info:
            if fits == lines[12]:
                rms2=lines[4]
        num_lines = sum(1 for line in open(fits.split('.fits')[0]+'.csv'))
        if num_lines > 1:
            avg_int_flx_rat.append([date, restfrq, find_avg_int_flx_rat(fits+'.sky',flux_limit,restfrq,fits.split('.fits')[0]+'.csv'),rms2])

    for freq in frequencies:
        rms=[avg_int_flx_rat[n][2] for n in range(len(avg_int_flx_rat)) if avg_int_flx_rat[n][1]==freq]
        avg_rms=(sum(rms)/len(rms))
        rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
        rms2=[avg_int_flx_rat[n][3] for n in range(len(avg_int_flx_rat)) if avg_int_flx_rat[n][1]==freq]
        avg_rms2=(sum(rms2)/len(rms2))
        rms_rms2=math.sqrt((sum(n*n-(avg_rms2*avg_rms2) for n in rms2))/len(rms2))
        plotfig3(avg_int_flx_rat, 'Observation Time (hours)', 'Average Flux Ratio (Observed/Correct_sky)', 'flxrat_'+str(int(freq/1e6)),avg_rms,rms_rms,'Frequency: '+str(int(freq/1e6)), freq,avg_rms2,rms_rms2)

    print 'Failed images: %s' % ', '.join(str(val) for val in failed_images)
    print 'TraP quality control plots made :-)'


# Functions needed for the different sections of the analysis

def plotfig(trans_data, a, b, xlabel, ylabel, plotname,avg,rms,title):
    print('plotting figure: '+plotname)
    plt.figure()
    x1=[]
    x2=[]
    y1=[]
    y2=[]
    n1=0
    n2=0
    x=0
    start_time = min(trans_data[x][a] for x in range(len(trans_data)))
    for x in range(len(trans_data)):
        dt=str(abs(trans_data[x][a]-start_time)).split(':')
        dt=float(dt[0])+float(dt[1])/60+float(dt[2])/3600
        plt.plot(dt, [trans_data[x][b]],'r.')
    ymin=min(trans_data[x][b] for x in range(len(trans_data)))*0.7
    ymax=max(trans_data[x][b] for x in range(len(trans_data)))*1.1
    plt.axhline(y=avg, linewidth=1, color='b')
    plt.axhline(y=avg+rms, linewidth=1, color='b', linestyle='--')
    plt.axhline(y=avg-rms, linewidth=1, color='b', linestyle='--')
    plt.xlabel(xlabel)
    plt.annotate('Mean: '+str(round(avg,3)), xy=(24.3, avg*1.1),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms,3)), xy=(24.3, (rms+avg)*1.1),  xycoords='data', color='b')
    plt.axis([-1,30,ymin,ymax])
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(plotname+'.png')
    plt.close()


def plotfig2(trans_data, a, b, xlabel, ylabel, plotname,avg,rms,title):
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
        plt.plot([trans_data[x][a]], [trans_data[x][b]],'r.')
    xmin=min(trans_data[x][a] for x in range(len(trans_data)))*0.7
    xmax=max(trans_data[x][a] for x in range(len(trans_data)))*1.3
    ymin=min(trans_data[x][b] for x in range(len(trans_data)))*0.7
    ymax=max(trans_data[x][b] for x in range(len(trans_data)))*1.1
    plt.axhline(y=avg, linewidth=1, color='b')
    plt.axhline(y=avg+rms, linewidth=1, color='b', linestyle='--')
    plt.axhline(y=avg-rms, linewidth=1, color='b', linestyle='--')
    plt.xlabel(xlabel)
    plt.annotate('Mean: '+str(round(avg,3)), xy=(xmax*0.8, avg*1.1),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms,3)), xy=(xmax*0.8, (rms+avg)*1.1),  xycoords='data', color='b')
    plt.axis([xmin,xmax,ymin,ymax])
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(plotname+'.png')
    plt.close()


def extract_sky(vlss,min_flux,restfrq):
    vlss_sources=[]
    vlss_data=open(vlss, 'r')
    lines = iter(vlss_data)
    line1=vlss_data.readline()
    frq=float(line1.split("'")[1])
    lines = iter(vlss_data)
    lines.next()
    lines.next()
    for line in lines:
        vlss_sources.append(line)
    vlss_data.close()
    srcs_vlss=[]
    for a in vlss_sources:
        nums=a.split(', ')
        if float(nums[4]) > min_flux:
            dec=nums[3]
            dec=dec.replace('.',':', 2)
            position= nums[2] + ' ' + dec
            f=nums[9].split('[')
            A1 = float(f[1].split(']')[0])
            A2 = 0
            if len(nums)>10 and ']' in nums[10]: A2 = float(nums[10].split(']')[0])
            if A2 == 0:
                new=float(nums[4])*(np.power(restfrq,A1))/(np.power(frq,A1))
            else:
                new=float(nums[4])*((np.power(restfrq,A1))+(np.power((restfrq*restfrq),A2)))/((np.power(frq,A1))+(np.power((frq*frq),A2)))
            srcs_vlss.append([C.Position(position),new])
    return srcs_vlss

def extract_pyse(pyse, min_flux):
    pyse_sources=[]
    srcs_pyse=[]
    pyse_data=open(pyse, 'r')
    lines = iter(pyse_data)
    lines.next() 
    for line in lines:
        pyse_sources.append(line)
    pyse_data.close()
    for b in pyse_sources:
        nums2=b.split(', ')
        if float(nums2[10]) > min_flux:
            x2 = C.Position((float(nums2[0]), float(nums2[2])))
            srcs_pyse.append([x2,nums2[10]])
    return srcs_pyse

def source_assoc(srcs_vlss,srcs_pyse):
    intflxrat=np.zeros(len(srcs_pyse))
    for a in range(len(srcs_pyse)):
        posdif_old=1000000
        for b in range(len(srcs_vlss)):
            posdif=srcs_pyse[a][0].angsep(srcs_vlss[b][0])
            if posdif < posdif_old:
                posdif_old = posdif
                intflxrat[a]=float(srcs_pyse[a][1])/float(srcs_vlss[b][1])
    return intflxrat

def find_avg_int_flx_rat(vlss,min_flux,restfrq,pyse):
    srcs_vlss=extract_sky(vlss,min_flux,restfrq)
    srcs_pyse=extract_pyse(pyse,min_flux)
    intflxrat=source_assoc(srcs_vlss,srcs_pyse)
    avgintflxrat = sum(intflxrat)/float(len(intflxrat))
    return avgintflxrat

def plotfig3(trans_data, xlabel, ylabel, plotname,avg,rms,title,freq,avg2,rms2):
    print('plotting figure: '+plotname)
    plt.figure()
    x1=[]
    x2=[]
    y1=[]
    y2=[]
    n1=0
    n2=0
    x=0
    start_time = min(trans_data[x][0] for x in range(len(trans_data)))
    for x in range(len(trans_data)):
        if trans_data[x][1] == freq:
            dt=str(abs(trans_data[x][0]-start_time)).split(':')
            dt=float(dt[0])+float(dt[1])/60+float(dt[2])/3600
            print dt
            plt.plot(dt, [trans_data[x][2]],'r.')
    ymin=min(trans_data[x][2] for x in range(len(trans_data)))*0.7
    ymax=max(trans_data[x][2] for x in range(len(trans_data)))*1.1
    plt.axhline(y=avg, linewidth=1, color='b')
    plt.axhline(y=avg+rms, linewidth=1, color='b', linestyle='--')
    plt.axhline(y=avg-rms, linewidth=1, color='b', linestyle='--')
    plt.xlabel(xlabel)
    plt.annotate('Mean: '+str(round(avg,3)), xy=(24.3, avg*1.1),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms,3)), xy=(24.3, (rms+avg)*1.1),  xycoords='data', color='b')
    plt.axis([-1,30,ymin,ymax])
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(plotname+'.png')
    plt.close()
    plt.figure()
    xmin=min(trans_data[x][3] for x in range(len(trans_data)))*0.7
    xmax=max(trans_data[x][3] for x in range(len(trans_data)))*1.1
    for x in range(len(trans_data)):
        plt.plot(trans_data[x][3],trans_data[x][2],'r.')
    plt.axhline(y=avg, linewidth=1, color='b')
    plt.axhline(y=avg+rms, linewidth=1, color='b', linestyle='--')
    plt.axhline(y=avg-rms, linewidth=1, color='b', linestyle='--')
    plt.axvline(x=avg2, linewidth=1, color='b')
    plt.axvline(x=avg2+rms2, linewidth=1, color='b', linestyle='--')
    plt.xlabel('RMS (Jy/beam)')
    plt.annotate('Mean: '+str(round(avg,3)), xy=(xmax*0.8, avg*1.1),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms,3)), xy=(xmax*0.8, (rms+avg)*1.1),  xycoords='data', color='b')
    plt.annotate('Mean: '+str(round(avg2,3)), xy=(avg2*1.1, ymax*0.8),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms2,3)), xy=((avg2)*1.1, ymax*0.85),  xycoords='data', color='b')
    plt.axis([xmin,xmax,ymin,ymax])
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(plotname+'_rms.png')
    plt.close()


opt = optparse.OptionParser()
opt.add_option('-b','--maxbl',help='Maximum baseline used in imaging (km)',default='6',type='int')
opt.add_option('-d','--detection',help='PySE detection threshold',default='8',type='float')
opt.add_option('-a','--analysis',help='PYSE analysis threshold',default='3',type='float')
opt.add_option('-g','--grid',help='PySE grid size',default='50',type='int')
opt.add_option('-r','--radius',help='PySE radius used for sourcefinding (pixels)',default='250',type='int')
opt.add_option('-l','--deblend',help='PySE deblend on/off',default='True',type='string')
opt.add_option('-t','--nthresh',help='PySE number of deblend thresholds',default='90',type='int')
opt.add_option('-s','--sys_err',help='Systematic position error (arcsec)',default='10',type='float')
opt.add_option('-c','--search_radius',help='Radius used in gsm.py to find skymodel (degrees)',default='5', type='float')
opt.add_option('-f','--flux_limit',help='Min flux used for analysis of flux ratios (Jy)',default='0.5',type='float')
opt.add_option('-m','--max_theoretical_ratio_cut',help='Cut on theoretical noise ratio to remove images where AWImager failed',default='500',type='float')


opts,args = opt.parse_args()

if len(sys.argv) != 3:
    print 'python TraP_QC_plots.py [arguments] <database> <dataset_id>'
else:
    main(opts,args)
