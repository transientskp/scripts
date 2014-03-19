#!/usr/bin/python
#
# Usage: python TraP_QC_plots.py <database> <dataset_id>
#
# This script uses the output from TKP-Web when all images are forced to be rejected on their rms noise (set high_bound=1 in quality_check.parset). Provide the dataset id and then this script will automatically extract the required data... The script then creates the noise comparison plots for the whole dataset. Note, you need access to your databases from your computer. This uses the script dump_image_data.py
#
# Then it uses the fits files in the current directory (so make sure you put them all there...) to find the average ratio between the average flux of sources in that image and the sky model flux. Note, you need gsm.py and pyse.py running on your computer. 
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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import optparse
from scipy.stats import norm
from scipy.optimize import leastsq

def main(opts,args):
    max_flx_rat_cutoff=1e100
    min_sep=0.
    database=args[0]
    dataset_id=str(args[1])
    release=str(args[2])
    if release !='0' and release !='1':
        print 'This script is for either Cycle0 (0) or Release 1 (1) databases, please specify 0 or 1.'
        exit()
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
    sigma=opts.max_cut
    plt_frq=opts.plt_frq
    plt_all=opts.plt_all

    # A-Team positions
    CasA=C.Position((350.866417,58.811778))
    CygA=C.Position((299.868153,40.733916))
    VirA=C.Position((187.705930,12.391123))

    # Create the noise plots
    if release == '0':
        import dump_image_data_v0
        from dump_image_data_v0 import dump_images
        dump_images(database,dataset_id)
    elif release == '1':
        import dump_image_data_v1
        from dump_image_data_v1 import dump_images
        dump_images(database,dataset_id)
    else:
        print 'ERROR in release number'
        exit()

    image_info=[]
    image_data=open('ds_'+dataset_id+'_images.csv','r')
#    image_data=open('ds_999_images.csv','r')
    list = image_data.readlines()
    image_data.close()
    frequencies=[]
    failed_images=[]
    for lines in list:
        row=lines.split(',')
        image=row[8].split('/')[-1].rstrip()+'.fits'
        date=datetime.strptime(row[7].strip(),'%Y-%m-%d %H:%M:%S')
        freq=int((float(row[3].strip())/1e6) + 0.5)
        if freq not in frequencies:
            frequencies.append(freq)
        ellipticity=float(row[5])/float(row[6])
        beam = 206265*((300/float(freq))/(1000*maxbl))
        confusion=29.0E-6*math.pow(beam,1.54)*math.pow((float(freq)/74.0),-0.7)
        theoretical=float(row[2].split(' ')[8].split('(')[1].split(')')[0].strip())
        ratio=float(row[2].split(' ')[4].strip())
        rms=theoretical*ratio
        pc = C.Position((float(row[1]), float(row[0])))
        posdif_CasA=float(str(CasA.angsep(pc)).split(' degrees')[0])
        posdif_CygA=float(str(CygA.angsep(pc)).split(' degrees')[0])
        posdif_VirA=float(str(VirA.angsep(pc)).split(' degrees')[0])
        if rms/theoretical < max_flx_rat_cutoff:
            image_info.append([row[0],row[1],date,freq,rms,theoretical,ratio,confusion,rms/confusion,posdif_CasA,posdif_CygA,posdif_VirA,image,ellipticity])
        else:
            failed_images.append(row[8].split('/')[-1].rstrip())
    
    ellip=[image_info[n][13] for n in range(len(image_info))]
    plothist2(ellip,r'Ellipticity (B$_{maj}$/B$_{min}$)','ellipticity','all')


    freq='all'
    rms=[image_info[n][4] for n in range(len(image_info))]
    avg_rms=(sum(rms)/len(rms))
    rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
    if plt_all:
      plotfig(image_info, 2, 4, 'Observation Time (hours)', 'RMS (Jy/beam)', 'rms',avg_rms,rms_rms,'Frequency: '+str(freq))
      plotfig4(image_info, 13, 4, 'Ellipticity (Bmaj/Bmin)', 'RMS (Jy/beam)', 'rms_ellipticity',avg_rms,rms_rms,'Frequency: '+str(freq))
    rms_log=[np.log10(x) for x in rms]
    p=guess_p(rms_log)
    plothist(rms_log,r'Observed RMS (Jy)','rms',sigma,'all',p)

    rms_ratio=[image_info[n][6] for n in range(len(image_info))]
    avg_rms_ratio=(sum(rms_ratio)/len(rms_ratio))
    rms_rms_ratio=math.sqrt((sum(n*n-(avg_rms_ratio*avg_rms_ratio) for n in rms_ratio))/len(rms_ratio))
    rms_ratio_log=[np.log10(x) for x in rms_ratio]
    p=guess_p(rms_ratio_log)
    clip = int(plothist(rms_ratio_log,r'Observed RMS / Theoretical Noise','rms_ratio',sigma,'all',p)+0.5)
    if plt_all:
      plotfig(image_info, 2, 6, 'Observation Time (hours)', 'RMS/Theoretical', 'theoretical',avg_rms_ratio,rms_rms_ratio,'Frequency: '+str(freq))
      plotfig4(image_info, 13, 6, 'Ellipticity (Bmaj/Bmin)', 'RMS/Theoretical', 'theoretical_ellipticity',avg_rms_ratio,rms_rms_ratio,'Frequency: '+str(freq))
    rms_ratio_threshold=avg_rms_ratio+rms_rms_ratio 
    rms_ratio2=[image_info[n][8] for n in range(len(image_info))]
    avg_rms_ratio2=(sum(rms_ratio2)/len(rms_ratio2))
    rms_rms_ratio2=math.sqrt((sum(n*n-(avg_rms_ratio2*avg_rms_ratio2) for n in rms_ratio2))/len(rms_ratio2))
    if plt_all:
      plotfig(image_info, 2, 8, 'Observation Time (hours)', 'RMS/Confusion', 'confusion',avg_rms_ratio2,rms_rms_ratio2,'Frequency: '+str(freq))
      plotfig4(image_info, 13, 8, 'Ellipticity (Bmaj/Bmin)', 'RMS/Confusion', 'confusion_ellipticity',avg_rms_ratio2,rms_rms_ratio2,'Frequency: '+str(freq))
    rms_ratio_log=[np.log10(x) for x in rms_ratio2]
    p=guess_p(rms_ratio_log)
    plothist(rms_ratio_log,r'Observed RMS / Confusion Noise','rms_confusion_ratio',sigma,'all',p)

    rms2=[image_info[x][13] for x in range(len(image_info))]
    avg_rms2=(sum(rms2)/len(rms2))
    rms_rms2=math.sqrt((sum(n*n-(avg_rms2*avg_rms2) for n in rms2))/len(rms2))
    ellipticity_threshold=avg_rms2+rms_rms2
    if plt_all:
      plotfig(image_info, 2, 13, 'Observation Time (hours)', 'Ellipticity (Bmaj/Bmin)', 'ellipticity',avg_rms2,rms_rms2,'Frequency: '+str(freq))

    if plt_all:
      for ateam in ['CasA', 'CygA', 'VirA']:

        if ateam == 'CasA':
            a=9
        elif ateam == 'CygA':
            a=10
        elif ateam == 'VirA':
            a=11
        plotfig2(image_info, a, 4, 'Separation (degrees)', 'RMS (Jy/beam)', ateam+'_'+str(freq),avg_rms,rms_rms,ateam+' - Frequency: '+str(freq),min_sep)
        plotfig2(image_info, a, 13, 'Separation (degrees)', 'Ellipticity (Bmaj/Bmin)', ateam+'_ellipticity_'+str(freq),avg_rms2,rms_rms2,ateam+' - Frequency: '+str(freq),min_sep)
    if plt_frq and plt_all:
      for freq in frequencies:
        image_info2=[image_info[n] for n in range(len(image_info)) if int(image_info[n][3]+0.5)==freq]
        rms=[image_info[n][4] for n in range(len(image_info)) if int(image_info[n][3]+0.5)==freq]
        avg_rms=(sum(rms)/len(rms))
        rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
        plotfig(image_info2, 2, 4, 'Observation Time (hours)', 'RMS (Jy/beam)', 'rms_'+str(int(freq+0.5)),avg_rms,rms_rms,'Frequency: '+str(int(freq+0.5)))
        plotfig4(image_info2, 13, 4, 'Ellipticity (Bmaj/Bmin)', 'RMS (Jy/beam)', 'rms_ellipticity_'+str(int(freq+0.5)),avg_rms,rms_rms,'Frequency: '+str(int(freq+0.5)))
        rms_ratio=[image_info[n][6] for n in range(len(image_info)) if int(image_info[n][3]+0.5)==freq]
        avg_rms_ratio=(sum(rms_ratio)/len(rms_ratio))
        rms_rms_ratio=math.sqrt((sum(n*n-(avg_rms_ratio*avg_rms_ratio) for n in rms_ratio))/len(rms_ratio))
        plotfig(image_info2, 2, 6, 'Observation Time (hours)', 'RMS/Theoretical', 'theoretical_'+str(int(freq+0.5)),avg_rms_ratio,rms_rms_ratio,'Frequency: '+str(int(freq+0.5)))
        plotfig4(image_info2, 13, 6, 'Ellipticity (Bmaj/Bmin)', 'RMS/Theoretical', 'theoretical_ellipticity_'+str(int(freq+0.5)),avg_rms_ratio,rms_rms_ratio,'Frequency: '+str(int(freq+0.5)))
        rms_ratio2=[image_info[n][8] for n in range(len(image_info)) if int(image_info[n][3]+0.5)==freq]
        avg_rms_ratio2=(sum(rms_ratio2)/len(rms_ratio2))
        rms_rms_ratio2=math.sqrt((sum(n*n-(avg_rms_ratio2*avg_rms_ratio2) for n in rms_ratio2))/len(rms_ratio2))
        plotfig(image_info2, 2, 8, 'Observation Time (hours)', 'RMS/Confusion', 'confusion_'+str(int(freq+0.5)),avg_rms_ratio2,rms_rms_ratio2,'Frequency: '+str(int(freq+0.5)))
        plotfig4(image_info2, 13, 8, 'Ellipticity (Bmaj/Bmin)', 'RMS/Confusion', 'confusion_ellipticity_'+str(int(freq+0.5)),avg_rms_ratio2,rms_rms_ratio2,'Frequency: '+str(int(freq+0.5)))
        rms2=[image_info[n][13] for n in range(len(image_info)) if int(image_info[n][3]+0.5)==freq]
        avg_rms2=(sum(rms2)/len(rms2))
        rms_rms2=math.sqrt((sum(n*n-(avg_rms2*avg_rms2) for n in rms2))/len(rms2))
        for ateam in ['CasA', 'CygA', 'VirA']:
            if ateam == 'CasA':
                a=9
            elif ateam == 'CygA':
                a=10
            elif ateam == 'VirA':
                a=11
            plotfig2(image_info2, a, 4, 'Separation (degrees)', 'RMS (Jy/beam)', ateam+'_'+str(int(freq+0.5)),avg_rms,rms_rms,ateam+' - Frequency: '+str(int(freq+0.5)),min_sep)
            plotfig2(image_info2, a, 13, 'Separation (degrees)', 'Ellipticity (Bmaj/Bmin)', ateam+'_ellipticity_'+str(int(freq+0.5)),avg_rms2,rms_rms2,ateam+' - Frequency: '+str(int(freq+0.5)),min_sep)
            
    print 'Clipped image properties'
    print 'noise high bound: '+str(clip)
    print 'ellipticity clip: '+str(round(ellipticity_threshold,1))
    clipped_image_info2=[image_info[n] for n in range(len(image_info)) if image_info[n][6] < clip if image_info[n][13] < ellipticity_threshold]
    rms=[clipped_image_info2[n][4] for n in range(len(clipped_image_info2))]
    avg_rms=(sum(rms)/len(rms))
    rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
    rms2=[clipped_image_info2[n][13] for n in range(len(clipped_image_info2))]
    avg_rms2=(sum(rms2)/len(rms2))
    rms_rms2=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms2))/len(rms2))
    for ateam in ['CasA', 'CygA', 'VirA']:
        if ateam == 'CasA':
            a=9
        elif ateam == 'CygA':
            a=10
        elif ateam == 'VirA':
            a=11
        min_sep = plotfig2(clipped_image_info2, a, 4, 'Separation (degrees)', 'RMS (Jy/beam)', ateam+'_all_clipped',avg_rms,rms_rms,ateam+' - Frequency: all',min_sep)
        plotfig2(clipped_image_info2, a, 13, 'Separation (degrees)', 'Ellipticity (Bmaj/Bmin)', ateam+'_ellipticity_all_clipped',avg_rms2,rms_rms2,ateam+' - Frequency: all',min_sep)

    print 'separation from A-Team: '+str(min_sep)
    clipped_image_info=[image_info[n] for n in range(len(image_info)) if image_info[n][6] < clip if image_info[n][13] < ellipticity_threshold if image_info[n][9] > min_sep if image_info[n][10] > min_sep if image_info[n][11] > min_sep]
    print 'Number of images remaining: '+str(len(clipped_image_info))
    freq='all'
    rms=[clipped_image_info[n][4] for n in range(len(clipped_image_info))]
    avg_rms=(sum(rms)/len(rms))
    rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
    plotfig(clipped_image_info, 2, 4, 'Observation Time (hours)', 'RMS (Jy/beam)', 'rms_clipped',avg_rms,rms_rms,'Frequency: '+str(freq))
    plotfig4(clipped_image_info, 13, 4, 'Ellipticity (Bmaj/Bmin)', 'RMS (Jy/beam)', 'rms_ellipticity_clipped',avg_rms,rms_rms,'Frequency: '+str(freq))    
    rms_ratio=[clipped_image_info[n][6] for n in range(len(clipped_image_info))]
    avg_rms_ratio=(sum(rms_ratio)/len(rms_ratio))
    rms_rms_ratio=math.sqrt((sum(n*n-(avg_rms_ratio*avg_rms_ratio) for n in rms_ratio))/len(rms_ratio))
    plotfig(clipped_image_info, 2, 6, 'Observation Time (hours)', 'RMS/Theoretical', 'theoretical_clipped',avg_rms_ratio,rms_rms_ratio,'Frequency: '+str(freq))
    plotfig4(clipped_image_info, 13, 6, 'Ellipticity (Bmaj/Bmin)', 'RMS/Theoretical', 'theoretical_ellipticity_clipped',avg_rms_ratio,rms_rms_ratio,'Frequency: '+str(freq))
    rms_ratio_threshold=avg_rms_ratio+rms_rms_ratio
    rms_ratio2=[clipped_image_info[n][8] for n in range(len(clipped_image_info))]
    avg_rms_ratio2=(sum(rms_ratio2)/len(rms_ratio2))
    rms_rms_ratio2=math.sqrt((sum(n*n-(avg_rms_ratio2*avg_rms_ratio2) for n in rms_ratio2))/len(rms_ratio2))
    plotfig(clipped_image_info, 2, 8, 'Observation Time (hours)', 'RMS/Confusion', 'confusion_clipped',avg_rms_ratio2,rms_rms_ratio2,'Frequency: '+str(freq))
    plotfig4(clipped_image_info, 13, 8, 'Ellipticity (Bmaj/Bmin)', 'RMS/Confusion', 'confusion_ellipticity_clipped',avg_rms_ratio2,rms_rms_ratio2,'Frequency: '+str(freq))
    if plt_frq:
      for freq in frequencies:
        image_info2=[clipped_image_info[n] for n in range(len(clipped_image_info)) if int(clipped_image_info[n][3]+0.5)==freq]
        rms=[clipped_image_info[n][4] for n in range(len(clipped_image_info)) if int(clipped_image_info[n][3]+0.5)==freq]
        avg_rms=(sum(rms)/len(rms))
        rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
        plotfig(image_info2, 2, 4, 'Observation Time (hours)', 'RMS (Jy/beam)', 'rms_'+str(int(freq+0.5)),avg_rms,rms_rms,'Frequency: '+str(int(freq+0.5)))
        plotfig4(image_info2, 13, 4, 'Ellipticity (Bmaj/Bmin)', 'RMS (Jy/beam)', 'rms_ellipticity_'+str(int(freq+0.5)),avg_rms,rms_rms,'Frequency: '+str(int(freq+0.5)))
        rms_ratio=[image_info2[n][6] for n in range(len(image_info2)) if int(image_info2[n][3]+0.5)==freq]
        avg_rms_ratio=(sum(rms_ratio)/len(rms_ratio))
        rms_rms_ratio=math.sqrt((sum(n*n-(avg_rms_ratio*avg_rms_ratio) for n in rms_ratio))/len(rms_ratio))
        plotfig(image_info2, 2, 6, 'Observation Time (hours)', 'RMS/Theoretical', 'theoretical_'+str(int(freq+0.5)),avg_rms_ratio,rms_rms_ratio,'Frequency: '+str(int(freq+0.5)))
        plotfig4(image_info2, 13, 6, 'Ellipticity (Bmaj/Bmin)', 'RMS/Theoretical', 'theoretical_ellipticity_'+str(int(freq+0.5)),avg_rms_ratio,rms_rms_ratio,'Frequency: '+str(int(freq+0.5)))
        rms_ratio2=[image_info[n][8] for n in range(len(image_info)) if int(image_info[n][3]+0.5)==freq]
        avg_rms_ratio2=(sum(rms_ratio2)/len(rms_ratio2))
        rms_rms_ratio2=math.sqrt((sum(n*n-(avg_rms_ratio2*avg_rms_ratio2) for n in rms_ratio2))/len(rms_ratio2))
        plotfig(image_info2, 2, 8, 'Observation Time (hours)', 'RMS/Confusion', 'confusion_'+str(int(freq+0.5)),avg_rms_ratio2,rms_rms_ratio2,'Frequency: '+str(int(freq+0.5)))
        plotfig4(image_info2, 13, 8, 'Ellipticity (Bmaj/Bmin)', 'RMS/Confusion', 'confusion_ellipticity_'+str(int(freq+0.5)),avg_rms_ratio2,rms_rms_ratio2,'Frequency: '+str(int(freq+0.5)))
        rms2=[image_info2[n][13] for n in range(len(image_info2)) if int(image_info2[n][3]+0.5)==freq]
        avg_rms2=(sum(rms2)/len(rms2))
        rms_rms2=math.sqrt((sum(n*n-(avg_rms2*avg_rms2) for n in rms2))/len(rms2))
        for ateam in ['CasA', 'CygA', 'VirA']:
            if ateam == 'CasA':
                a=9
            elif ateam == 'CygA':
                a=10
            elif ateam == 'VirA':
                a=11
            plotfig2(image_info2, a, 4, 'Separation (degrees)', 'RMS (Jy/beam)', ateam+'_'+str(int(freq+0.5)),avg_rms,rms_rms,ateam+' - Frequency: '+str(int(freq+0.5)),min_sep)
            plotfig2(image_info2, a, 13, 'Separation (degrees)', 'Ellipticity (Bmaj/Bmin)', ateam+'_ellipticity_'+str(int(freq+0.5)),avg_rms2,rms_rms2,ateam+' - Frequency: '+str(int(freq+0.5)),min_sep)
    # Flux plots

    fitsfiles=glob.glob("*.fits")
    frequencies=[]
    avg_int_flx_rat=[]
    avg_int_flx_rat_clipped=[]
    for fits in fitsfiles:
        print 'Analysing image: '+fits
        hdulist = pyfits.open(fits)
        ra = hdulist[0].header['CRVAL1']
        dec = hdulist[0].header['CRVAL2']
        bmaj = hdulist[0].header['BMAJ']
        bmin = hdulist[0].header['BMIN']
        restfrq = int((hdulist[0].header['RESTFRQ']/1e6)+0.5)
        if restfrq not in frequencies:
            frequencies.append(restfrq)
        date = hdulist[0].header['DATE-OBS']
        info1 = hdulist[0].header['HISTORY*']
        info1_new = str(info1).split("cellx='")
        cellsize = str(info1_new[1]).split("arcsec")
        skymodel = fits+'.sky'
#        os.system('gsm.py '+skymodel+' '+str(ra)+' '+str(dec)+' '+str(search_radius)+' '+str(flux_limit))
#        os.system('pyse.py --detection='+str(detection)+' --analysis='+str(analysis)+' --grid='+str(grid)+' --radius='+str(radius)+' --deblend --deblend-thresholds='+str(deblend_nthresh)+' --force-beam --csv '+fits)
        date=datetime.strptime(date.strip()[:19],'%Y-%m-%dT%H:%M:%S')
        for lines in image_info:
            if fits == lines[12]:
                rms2=lines[4]
                ellipticity2=lines[13]
                num_lines = sum(1 for line in open(fits.split('.fits')[0]+'.csv'))
                if num_lines > 1:
                    flx, flxrms=find_avg_int_flx_rat(fits+'.sky',flux_limit,restfrq,fits.split('.fits')[0]+'.csv')
                    if flx<max_flx_rat_cutoff:
                        avg_int_flx_rat.append([date, restfrq, flx,rms2,ellipticity2,flxrms])
        for lines in clipped_image_info:
            if fits == lines[12]:
                rms2=lines[4]
                ellipticity2=lines[13]
                num_lines = sum(1 for line in open(fits.split('.fits')[0]+'.csv'))
                if num_lines > 1:
                    flx, flxrms =find_avg_int_flx_rat(fits+'.sky',flux_limit,restfrq,fits.split('.fits')[0]+'.csv')
                    if flx<max_flx_rat_cutoff:
                        avg_int_flx_rat_clipped.append([date, restfrq, flx,rms2,ellipticity2,flxrms])
    for freq in frequencies:
        avg_int_flx_rat2=[avg_int_flx_rat[n] for n in range(len(avg_int_flx_rat)) if avg_int_flx_rat[n][1]==freq]
        rms=[avg_int_flx_rat[n][2] for n in range(len(avg_int_flx_rat)) if avg_int_flx_rat[n][1]==freq]
        avg_rms=(sum(rms)/len(rms))
        rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
        rms2=[avg_int_flx_rat[n][3] for n in range(len(avg_int_flx_rat)) if avg_int_flx_rat[n][1]==freq]
        avg_rms2=(sum(rms2)/len(rms2))
        rms_rms2=math.sqrt((sum(n*n-(avg_rms2*avg_rms2) for n in rms2))/len(rms2))
        ellipticity2=[avg_int_flx_rat[n][4] for n in range(len(avg_int_flx_rat)) if avg_int_flx_rat[n][1]==freq]
        avg_ellipticity2=(sum(ellipticity2)/len(ellipticity2))
        rms_ellipticity2= math.sqrt((sum(n*n-(avg_ellipticity2*avg_ellipticity2) for n in ellipticity2))/len(ellipticity2))
        if plt_all:
          plotfig3(avg_int_flx_rat2, 'Observation Time (hours)', 'Average Flux Ratio (Observed/Correct_sky)', 'flxrat_'+str(int(freq)),avg_rms,rms_rms,'Frequency: '+str(int(freq)), freq,avg_rms2,rms_rms2)
          plotfig5(avg_int_flx_rat2, 'Ellipticity (Bmaj/Bmin)', 'Average Flux Ratio (Observed/Correct_sky)', 'flxrat_'+str(int(freq)),avg_rms,rms_rms,'Frequency: '+str(int(freq)), freq,avg_ellipticity2,rms_ellipticity2)
        avg_int_flx_rat2_clipped=[avg_int_flx_rat_clipped[n] for n in range(len(avg_int_flx_rat_clipped)) if avg_int_flx_rat_clipped[n][1]==freq]
        rms=[avg_int_flx_rat_clipped[n][2] for n in range(len(avg_int_flx_rat_clipped)) if avg_int_flx_rat_clipped[n][1]==freq]
        if len(rms)==0:
            avg_rms=0.
        else:
            avg_rms=(sum(rms)/len(rms))
        rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
        rms2=[avg_int_flx_rat_clipped[n][3] for n in range(len(avg_int_flx_rat_clipped)) if avg_int_flx_rat_clipped[n][1]==freq]
        avg_rms2=(sum(rms2)/len(rms2))
        rms_rms2=math.sqrt((sum(n*n-(avg_rms2*avg_rms2) for n in rms2))/len(rms2))
        ellipticity2=[avg_int_flx_rat_clipped[n][4] for n in range(len(avg_int_flx_rat_clipped)) if avg_int_flx_rat_clipped[n][1]==freq]
        avg_ellipticity2=(sum(ellipticity2)/len(ellipticity2))
        rms_ellipticity2= math.sqrt((sum(n*n-(avg_ellipticity2*avg_ellipticity2) for n in ellipticity2))/len(ellipticity2))
        plotfig3(avg_int_flx_rat2_clipped, 'Observation Time (hours)', 'Average Flux Ratio (Observed/Correct_sky)', 'flxrat_'+str(int(freq))+'_clipped',avg_rms,rms_rms,'Frequency: '+str(int(freq)), freq,avg_rms2,rms_rms2)
        plotfig5(avg_int_flx_rat2_clipped, 'Ellipticity (Bmaj/Bmin)', 'Average Flux Ratio (Observed/Correct_sky)', 'flxrat_'+str(int(freq))+'_clipped',avg_rms,rms_rms,'Frequency: '+str(int(freq)), freq,avg_ellipticity2,rms_ellipticity2)

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
    dt_array=[]
    start_time = min(trans_data[x][a] for x in range(len(trans_data)))
    for x in range(len(trans_data)):
        tmp=abs(trans_data[x][a]-start_time)
        dt=str(abs(trans_data[x][a]-start_time)).split(':')
        if "day" in dt[0]:
            dt[0]=tmp.days*24.
        dt=float(dt[0])+float(dt[1])/60+float(dt[2])/3600
        dt_array.append(dt)
        plt.plot(dt, [trans_data[x][b]],'r.')
    ymin=min(trans_data[x][b] for x in range(len(trans_data)))*0.7
    ymax=max(trans_data[x][b] for x in range(len(trans_data)))*1.1
    plt.axhline(y=avg, linewidth=1, color='b')
    plt.axhline(y=avg+rms, linewidth=1, color='b', linestyle='--')
    plt.axhline(y=avg-rms, linewidth=1, color='b', linestyle='--')
    plt.xlabel(xlabel)
    plt.annotate('Mean: '+str(round(avg,3)), xy=(24.3, avg*1.1),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms,3)), xy=(24.3, (rms+avg)*1.1),  xycoords='data', color='b')
    plt.axis([-1,max(dt_array),ymin,ymax])
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(plotname+'.png')
    plt.close()

def plotfig4(trans_data, a, b, xlabel, ylabel, plotname,avg,rms,title):
    print('plotting figure: '+plotname)
    plt.figure()
    x1=[]
    x2=[]
    y1=[]
    y2=[]
    n1=0
    n2=0
    x=0
    dt_array=[]
    start_time = min([trans_data[x][a] for x in range(len(trans_data))])
    for x in range(len(trans_data)):
        dt=trans_data[x][a]
        dt_array.append(dt)
        plt.plot(dt, [trans_data[x][b]],'r.')
    rms=[trans_data[x][b] for x in range(len(trans_data))]
    avg_rms=(sum(rms)/len(rms))
    rms_rms=math.sqrt((sum(n*n-(avg_rms*avg_rms) for n in rms))/len(rms))
    rms2=[trans_data[x][a] for x in range(len(trans_data))]
    avg_rms2=(sum(rms2)/len(rms2))
    rms_rms2=math.sqrt((sum(n*n-(avg_rms2*avg_rms2) for n in rms2))/len(rms2))

    ymin=min(trans_data[x][b] for x in range(len(trans_data)))*0.7
    ymax=max(trans_data[x][b] for x in range(len(trans_data)))*1.1
    plt.axhline(y=avg_rms, linewidth=1, color='b')
    plt.axhline(y=avg_rms+rms_rms, linewidth=1, color='b', linestyle='--')
    plt.axhline(y=avg_rms-rms_rms, linewidth=1, color='b', linestyle='--')
    plt.axvline(x=avg_rms2, linewidth=1, color='b')
    plt.axvline(x=avg_rms2+rms_rms2, linewidth=1, color='b', linestyle='--')
    plt.axvline(x=avg_rms2-rms_rms2, linewidth=1, color='b', linestyle='--')
    plt.xlabel(xlabel)
    plt.annotate('Mean: '+str(round(avg_rms,3)), xy=(max(dt_array)*0.8, avg_rms*1.1),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms_rms,3)), xy=(max(dt_array)*0.8, (avg_rms+rms_rms)*1.1),  xycoords='data', color='b')
    plt.annotate('Mean: '+str(round(avg_rms2,3)), xy=(avg_rms2*1.1,ymax*0.8),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms_rms2,3)), xy=(avg_rms2*1.1,ymax*0.85),  xycoords='data', color='b')
    plt.axis([1.,max(dt_array)+0.1,ymin,ymax])
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(plotname+'.png')
    plt.close()

def plotfig2(trans_data, a, b, xlabel, ylabel, plotname,avg,rms,title,min_sep):
    print('plotting figure: '+plotname)
    plt.figure()
    x1=[]
    x2=[]
    y1=[]
    y2=[]
    n1=0
    n2=0
    x=0
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
#            if np.mean(ydata) > avg:
#                print 'Value above mean: '+str(xbin)
        else:
            xbins_to_pop.append(xbin)
    new_bins = [bins[x] for x in range(len(bins)) if x not in xbins_to_pop]
    bins=[b2+(bin_size/2.) for b2 in new_bins]
    nums=5
    for k in range(len(new_bins)):
        if yavg[k]<avg:
            if k>nums:
                min_sep=int(new_bins[k]+1.)
            break
    plt.axhline(y=avg, linewidth=1, color='b')
    plt.axhline(y=avg+rms, linewidth=1, color='b', linestyle='--')
    plt.axhline(y=avg-rms, linewidth=1, color='b', linestyle='--')
    plt.xlabel(xlabel)
    plt.annotate('Mean: '+str(round(avg,3)), xy=(xmax*0.8, avg*1.1),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms,3)), xy=(xmax*0.8, (rms+avg)*1.1),  xycoords='data', color='b')
    plt.errorbar(bins,yavg,fmt='.',color='k',linestyle='-',zorder=1e5)
    plt.axis([xmin,xmax,ymin,ymax])
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(plotname+'.png')
    plt.close()
    return min_sep


def extract_sky(vlss,min_flux,restfrq):
    vlss_sources=[]
    vlss_data=open(vlss, 'r')
    lines = iter(vlss_data)
    line1=vlss_data.readline()
    frq=float(line1.split("'")[1])/1e6
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
    if len(srcs_pyse) > 0:
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
    if len(intflxrat)==0:
        return 0.0, 0.0
    else:
        avgintflxrat = sum(intflxrat)/float(len(intflxrat))
        rms = math.sqrt((sum(n*n - (avgintflxrat*avgintflxrat) for n in intflxrat))/len(intflxrat))
        return avgintflxrat, rms

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
    dt_array=[]
    start_time = min([trans_data[x][0] for x in range(len(trans_data))])
    dt2=[]
    flxs=[]
    flxerrs=[]
    for x in range(len(trans_data)):
        if trans_data[x][1] == freq:
            tmp=abs(trans_data[x][0]-start_time)
            dt=str(abs(trans_data[x][0]-start_time)).split(':')
            if "day" in dt[0]:
                dt[0]=tmp.days*24.
            dt=float(dt[0])+float(dt[1])/60+float(dt[2])/3600
            dt_array.append(dt)
            dt2.append(dt)
            flxs.append(trans_data[x][2])
            flxerrs.append(trans_data[x][5])
    plt.errorbar(dt2, flxs,fmt='r.',yerr=flxerrs)
    ymin=min(trans_data[x][2] for x in range(len(trans_data)))*0.7
    ymax=max(trans_data[x][2] for x in range(len(trans_data)))*1.1
    plt.axhline(y=avg, linewidth=1, color='b')
    plt.axhline(y=avg+rms, linewidth=1, color='b', linestyle='--')
    plt.axhline(y=avg-rms, linewidth=1, color='b', linestyle='--')
    plt.xlabel(xlabel)
    plt.annotate('Mean: '+str(round(avg,3)), xy=(24.3, avg*1.1),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms,3)), xy=(24.3, (rms+avg)*1.1),  xycoords='data', color='b')
    plt.axis([-1,max(dt_array)+1,0.0,ymax])
    plt.ylabel(ylabel)
    plt.yscale('linear')
    plt.title(title)
    plt.savefig(plotname+'.png')
    plt.close()
    plt.figure()
    xmin=min(trans_data[x][3] for x in range(len(trans_data)))*0.7
    xmax=max(trans_data[x][3] for x in range(len(trans_data)))*1.1
    for x in range(len(trans_data)):
#        plt.plot(trans_data[x][3],trans_data[x][2],'r.')
        plt.errorbar(trans_data[x][3], [trans_data[x][2]],fmt='r.',yerr=trans_data[x][5])
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
    plt.axis([xmin,xmax,0.0,ymax])
    plt.ylabel(ylabel)
    plt.yscale('linear')
    plt.title(title)
    plt.savefig(plotname+'_rms.png')
    plt.close()

def plotfig5(trans_data, xlabel, ylabel, plotname,avg,rms,title,freq,avg2,rms2):
    print('plotting figure: '+plotname)
    plt.figure()
    x1=[]
    x2=[]
    y1=[]
    y2=[]
    n1=0
    n2=0
    x=0
    plt.figure()
    ymin=min(trans_data[x][2] for x in range(len(trans_data)))*0.7
    ymax=max(trans_data[x][2] for x in range(len(trans_data)))*1.1
    xmin=1.
    xmax=max(trans_data[x][4] for x in range(len(trans_data)))+0.1
    for x in range(len(trans_data)):
#        plt.plot(trans_data[x][4],trans_data[x][2],'r.')
        plt.errorbar(trans_data[x][4], [trans_data[x][2]],fmt='r.',yerr=trans_data[x][5])
    plt.axhline(y=avg, linewidth=1, color='b')
    plt.axhline(y=avg+rms, linewidth=1, color='b', linestyle='--')
    plt.axhline(y=avg-rms, linewidth=1, color='b', linestyle='--')
    plt.axvline(x=avg2, linewidth=1, color='b')
    plt.axvline(x=avg2+rms2, linewidth=1, color='b', linestyle='--')
    plt.xlabel('Ellipticity (Bmaj/Bmin)')
    plt.annotate('Mean: '+str(round(avg,3)), xy=(xmax*0.8, avg*1.1),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms,3)), xy=(xmax*0.8, (rms+avg)*1.1),  xycoords='data', color='b')
    plt.annotate('Mean: '+str(round(avg2,3)), xy=(avg2*1.1, ymax*0.8),  xycoords='data', color='b')
    plt.annotate('RMS: '+str(round(rms2,3)), xy=((avg2)*1.1, ymax*0.85),  xycoords='data', color='b')
    plt.axis([1.,xmax,0.0,ymax])
    plt.ylabel(ylabel)
    plt.yscale('linear')
    plt.title(title)
    plt.savefig(plotname+'_ellipticity_rms.png')
    plt.close()

def res(p, y, x):
  m1, sd1, a = p
  y_fit = a*norm2(x, m1, sd1) #+ 0.0*norm2(x, m2, sd2)
  err = y - y_fit
  return err

def norm2(x, mean, sd):
  normdist = []
  for i in range(len(x)):
    normdist += [1.0/(sd*np.sqrt(2*np.pi))*np.exp(-(x[i] - mean)**2/(2*sd**2))]
  return np.array(normdist)

def guess_p(x):
  median = np.median(x)
  temp=[n*n-(median*median) for n in x]
  rms = math.sqrt((abs(sum(temp))/len(x)))
  return [median, rms, math.sqrt(len(x))]

def plothist(x, name,filename,sigma,freq,p):
    hist_x=np.histogram(x,bins=500)
    range_x=[hist_x[1][n]+(hist_x[1][n+1]-hist_x[1][n])/2. for n in range(len(hist_x[1])-1)]
    plt.hist(x,bins=500,histtype='stepfilled')
    plsq = leastsq(res, p, args = (hist_x[0], range_x))
    fit2 = plsq[0][2]*norm2(range_x, plsq[0][0], plsq[0][1])# + plsq[0][5]*norm2(range_x, plsq[0][1], plsq[0][3])
    plt.plot(range_x,fit2, 'r-')
    sigcut=plsq[0][0]+plsq[0][1]*sigma
    plt.axvline(x=sigcut, linewidth=2, color='k',linestyle='--')
    plt.text(sigcut*1.3, plsq[0][2]*3., r'%.1f $\sigma$ cut off = %.3f' % (sigma, 10.**sigcut))
    plt.xlabel(name)
    plt.ylabel('Number of images')
    ticks = np.arange(int(min(range_x)), int(max(range_x)+1.), 1)
    ticks = [int(n) for n in ticks]
    labels = [10.**x for x in ticks]
    plt.xticks(ticks, labels)
    plt.title(r'Mean = %.3f RMS = %.3f' %(10.**plsq[0][0], (10.**(plsq[0][0]+plsq[0][1])-10.**(plsq[0][0]))))
    plt.savefig('hist_'+filename+'_1gauss_'+str(freq)+'MHz.png')
    plt.close()
    return 10.**sigcut

def plothist2(x, name,filename,freq):
    print 'plotting: '+filename
    hist_x=np.histogram(x,bins=200)
    range_x=[hist_x[1][n]+(hist_x[1][n+1]-hist_x[1][n])/2. for n in range(len(hist_x[1])-1)]
    plt.hist(x,bins=200,histtype='stepfilled')
    plt.xlabel(name)
    plt.xlim(1.,2.)
#    plt.semilogy()
    plt.ylabel('Number of images')
#    ticks = np.arange(int(min(range_x)), int(max(range_x)+1.), 1)
#    ticks = [int(n) for n in ticks]
#    labels = [10.**x for x in ticks]
#    plt.xticks(ticks, labels)
    plt.savefig('hist_'+filename+'_1gauss_'+str(freq)+'MHz.png')
    plt.close()
    return


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
opt.add_option('-m','--max_cut',help='Cut on theoretical noise ratio to remove images where AWImager failed (number of sigma above median value)',default='2',type='float')
opt.add_option('-A','--plt_all',help='Plot all images without the clipping',default=False)
opt.add_option('-F','--plt_frq',help='Plot the different observing frequencies separately',default=False)
opts,args = opt.parse_args()

if len(sys.argv) < 4:
    print 'python TraP_QC_plots.py [arguments] <database> <dataset_id> <version>'
else:
    main(opts,args)
