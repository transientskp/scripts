#!/usr/bin/python
#
#
# Author: Antonia Rowlinson
# E-mail: b.a.rowlinson@uva.nl
#

import sys
import tools
import coords as C
import numpy as np
import math
import os

###################### INITIAL SETUP STEPS ######################

if len(sys.argv) != 7:
    print 'python TraP_QC_diagnostics.py <database> <dataset_id> <release> <sigma> <plt_freqs> <database_id2>'
    exit()
database = sys.argv[1]
dataset_id = str(sys.argv[2])
release = str(sys.argv[3])
sigma = float(sys.argv[4])
plt_freqs = sys.argv[5]
dataset_id2 = str(sys.argv[6])
# A-Team positions
CasA=C.Position((350.866417,58.811778))
CygA=C.Position((299.868153,40.733916))
VirA=C.Position((187.705930,12.391123))

min_sep=0. # The absolute minimum allowed separation from the A-Team source, set to zero to enable the code to work independently

###################### MAIN SCRIPT ######################

# Extracting data from the TraP database into a text file
tools.get_data(database, dataset_id, dataset_id2, release)

# Extract relevant data from dataset text file
image_info, frequencies = tools.extract_data(dataset_id, CasA, CygA, VirA)

freq='all'
# RMS noise properties
noise_avg_log, noise_scatter_log, noise_threshold_log = tools.fit_hist([np.log10(image_info[n][4]) for n in range(len(image_info))], sigma, r'log$_{10}$(Observed RMS (Jy))', 'ds'+dataset_id+'_rms', freq)
noise_avg=10.**(noise_avg_log)
noise_max=10.**(noise_avg_log+noise_scatter_log)-10.**(noise_avg_log)
noise_min=10.**(noise_avg_log)-10.**(noise_avg_log-noise_scatter_log)
print 'Average RMS Noise in images (1 sigma range, frequency='+str(freq)+' MHz): '+str(round(noise_avg*1e3,1))+' (+'+str(round(noise_max*1e3,1))+',-'+str(round(noise_min*1e3,1))+') mJy'
# RMS/Theoretical limit for TraP
ratio_avg_log, ratio_scatter_log, ratio_threshold_log = tools.fit_hist([np.log10(image_info[n][6]) for n in range(len(image_info))], sigma, r'log$_{10}$(Observed RMS / Theoretical Noise)', 'ds'+dataset_id+'_ratio', freq)
ratio_avg=10.**(ratio_avg_log)
ratio_threshold = round((10.**ratio_threshold_log),1)
print 'Average RMS/Theoretical in images (frequency='+str(freq)+' MHz): '+str(round(ratio_avg,1))
print '######## Recommended TraP high_bound threshold: '+str(ratio_threshold)

tools.plotfig_scatter(image_info, 7, 4, 'Ellipticity (Bmaj/Bmin)', 'RMS (Jy)', 'ds'+dataset_id+'_theoretical_ellipticity_'+str(freq)+'MHz')

if plt_freqs == 'T':
    for freq in frequencies:
        # RMS noise properties
        noise_avg_log_tmp, noise_scatter_log_tmp, noise_threshold_log_tmp = tools.fit_hist([np.log10(image_info[n][4]) for n in range(len(image_info)) if image_info[n][3]==freq], sigma, r'log$_{10}$(Observed RMS (Jy))', 'ds'+dataset_id+'_rms', freq)
        noise_avg_tmp=10.**(noise_avg_log_tmp)
        noise_max_tmp=10.**(noise_avg_log_tmp+noise_scatter_log_tmp)-10.**(noise_avg_log_tmp)
        noise_min_tmp=10.**(noise_avg_log_tmp)-10.**(noise_avg_log_tmp-noise_scatter_log_tmp)
        print 'Average RMS Noise in images (1 sigma range, frequency='+str(freq)+' MHz): '+str(round(noise_avg_tmp*1e3,1))+' (+'+str(round(noise_max_tmp*1e3,1))+',-'+str(round(noise_min_tmp*1e3,1))+') mJy'
        # RMS/Theoretical limit for TraP
        ratio_avg_log_tmp, ratio_scatter_log_tmp, ratio_threshold_log_tmp = tools.fit_hist([np.log10(image_info[n][6]) for n in range(len(image_info)) if image_info[n][3]==freq], sigma, r'log$_{10}$(Observed RMS / Theoretical Noise)', 'ds'+dataset_id+'_ratio', freq)
        ratio_avg_tmp=10.**(ratio_avg_log_tmp)
        print 'Average RMS/Theoretical in images (frequency='+str(freq)+' MHz): '+str(round(ratio_avg_tmp,1))

# Calculate restoring beam threshold using a simple clipping using the average and rms scatter
rms2=[image_info[x][7] for x in range(len(image_info))]
avg_rms2=(sum(rms2)/len(rms2))
rms_rms2=math.sqrt((sum(n*n-(avg_rms2*avg_rms2) for n in rms2))/len(rms2))
ellipticity_threshold=round(avg_rms2+rms_rms2,2)
print '######## Recommended TraP ellipticity threshold: '+str(ellipticity_threshold)

image_info_clip1 = [image_info[n] for n in range(len(image_info)) if image_info[n][6] < ratio_threshold if image_info[n][7] < ellipticity_threshold]

for ateam in ['CasA', 'CygA', 'VirA']:
    if ateam == 'CasA':
        a=8
    elif ateam == 'CygA':
        a=9
    elif ateam == 'VirA':
        a=10
    min_sep = tools.plotfig_ATeam(image_info_clip1, a, 4, 'Separation (degrees)', 'RMS (Jy/beam)', 'ds'+dataset_id+'_'+ateam+'_clipped',min_sep,noise_avg)
print '######## Recommended TraP min seperation from A-Team sources (degrees): '+str(min_sep)

image_info_clip2 = [image_info_clip1[n] for n in range(len(image_info_clip1)) if image_info_clip1[n][8] > min_sep if image_info_clip1[n][9] > min_sep if image_info_clip1[n][10] > min_sep]
tools.plotfig_scatter(image_info_clip2, 7, 4, 'Ellipticity (Bmaj/Bmin)', 'RMS (Jy)', 'ds'+dataset_id+'_theoretical_ellipticity_'+str(freq)+'MHz_Final')

print 'Total images: '+str(len(image_info))+' After first clip: '+str(len(image_info_clip1))+' ('+str(int(round(100.*(float(len(image_info_clip1))/float(len(image_info))),0)))+'%) After second clip: '+str(len(image_info_clip2))+' ('+str(int(round(100.*(float(len(image_info_clip2))/float(len(image_info))),0)))+'%)'

###################### IMAGES AVAILABLE? ######################

if dataset_id2=='N':
    print 'No sources available'
    exit()

avg_flxrat=[]
sources = tools.extr_src_data(dataset_id2)
sky_data={}
for img in [x for x in image_info_clip2]:
    srcs=[x for x in sources if x[0] == img[11]]
    skymodel=str(int(round(float(img[1]),0)))+'_'+str(int(round(float(img[0]),0)))+'.sky'
    skymodel_key=str(int(round(float(img[1]),0)))+str(int(round(float(img[0]))))
    search_radius=5.
    flux_limit=0.
    if not os.path.isfile(skymodel):
        os.system('gsm.py '+skymodel+' '+str(img[1])+' '+str(img[0])+' '+str(search_radius)+' '+str(flux_limit))
    if skymodel_key not in sky_data.keys():
        vlss_sources=[]
        vlss_data=open(skymodel, 'r')
        lines = iter(vlss_data)
        line1=vlss_data.readline()
        frq=float(line1.split("'")[1])/1e6
        lines = iter(vlss_data)
        lines.next()
        lines.next()
        for line in lines:
            vlss_sources.append(line)
        vlss_data.close()
        sky_data[skymodel_key]=vlss_sources
    vlss=tools.extract_sky(sky_data[skymodel_key],img[3],frq)
    flx, flxrms = tools.find_avg_int_flx_rat(vlss,srcs)
    avg_flxrat.append([img[4],flx,img[3]])
freq='all'
flx_avg_log_tmp, flx_scatter_log_tmp, flx_threshold_log_tmp = tools.fit_hist([x[1] for x in avg_flxrat if x[1]!=0.], 0.0, r'Average (Flux / Corrected Skymodel Flux)', 'ds'+dataset_id+'_flux', freq)
print 'Average Flux Ratio: '+str(flx_avg_log_tmp)+' +/-'+str(flx_scatter_log_tmp)
tools.plotfig_scatter([x for x in avg_flxrat if x[1] != 0.], 0, 1, 'RMS (Jy)', 'Average(Flux / Corrected Skymodel Flux)', 'ds'+dataset_id+'_flux_'+str(freq)+'MHz_Final')
if plt_freqs == 'T':
    for freq in frequencies:
        tools.plotfig_scatter([x for x in avg_flxrat if x[2] == freq if x[1]!=0.], 0, 1, 'RMS (Jy)', 'Average(Flux / Corrected Skymodel Flux)', 'ds'+dataset_id+'_flux_'+str(freq)+'MHz_Final')
        flx_avg_log_tmp, flx_scatter_log_tmp, flx_threshold_log_tmp = tools.fit_hist([x[1] for x in avg_flxrat if x[1]!=0. if x[2]==freq], 0.0, r'Average (Flux / Corrected Skymodel Flux)', 'ds'+dataset_id+'_flux', freq)
        print 'Average Flux Ratio ('+str(freq)+' MHz): '+str(flx_avg_log_tmp)+' +/-'+str(flx_scatter_log_tmp)
