#!/usr/bin/python
#
# This script reads a skymodel and an extracted source list from PySE and/or PyBDSM. The sources are then compared to the skymodel values and graphs are output into a pdf with a page for each sourcefinder used.
#
# Usage: /home/rowlinson/scripts/sourcefinder2.py <skymodel> <arguments>
#
# The arguments can be found by running /home/rowlinson/scripts/sourcefinder.py -h
#
# If the script fails to work, it is usually due to losing the XWindows connection - logout of CEP and log back in again and it should work. If that does not help, please send the screen output to me (e-mail below) and I will have a look. If you identify any bugs in the code, please contact me so I can correct it for everyone.
#
# Version 2 (31st July 2012)
#
# Author: Antonia Rowlinson
# E-mail: b.a.rowlinson@uva.nl

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import coords as C
from scipy import *
from pylab import *
from matplotlib.backends.backend_pdf import PdfPages
import optparse


def main(opts,args):
    vlss = args[0]
    pyse = opts.pyse
    ra_cent = opts.ra_cent
    dec_cent = opts.dec_cent
    min_flux = opts.min_flux
    max_sep_cutoff = opts.max_sep_cutoff
    output = opts.output
    pixel_size = opts.pixel_size
    bmaj = opts.bmaj
    bmin = opts.bmin
    restfrq = opts.freq
    abit = float(opts.abit)
    abit = abit/3600
    flux_ratio = opts.flux_ratio
    
    pc = C.Position((ra_cent, dec_cent))
    vlss_sources=[]
    vlss_data=open(vlss, 'r')
    lines = iter(vlss_data)
    line1=vlss_data.readline()
    frq=float(line1.split("'")[1])
    lines = iter(vlss_data)
    lines.next()
    for line in lines:
        vlss_sources.append(line)
    vlss_data.close()
    ra_vlss=[]
    dec_vlss=[]
    flux_vlss=[]
    posdifcent=[]
    new_flux_vlss=[]
    p1=[]
    for a in vlss_sources:
        nums=a.split(', ')
        if float(nums[4]) > min_flux:
            dec=nums[3]
            dec=dec.replace('.',':', 2)
            position= nums[2] + ' ' + dec
            x=C.Position(position)
            x2=(C.Position(position)).dd()
            ra_vlss.append(x2[0])
            dec_vlss.append(x2[1])
            p1.append((C.Position(position)).dd())
            posdifcent.append(float(str(x.angsep(pc)).split()[0]))
            flux_vlss.append(float(nums[4]))
# The fluxes given in the skymodel are usually at a different frequency to the observation, but we are also given an approximate spectral shape which can be used to calculate a new flux at the observing freequency.
            test=nums[9]
            f=test.split('[')
            A1 = float(f[1].split(']')[0])
            A2 = 0
            if len(nums)>10 and ']' in nums[10]: A2 = float(nums[10].split(']')[0])
            if A2 == 0:
                new=float(nums[4])*(math.pow(restfrq,A1))/(math.pow(frq,A1))
                new_flux_vlss.append(new)
            else:
                new=float(nums[4])*((math.pow(restfrq,A1))+(math.pow((restfrq*restfrq),A2)))/((math.pow(frq,A1))+(math.pow((frq*frq),A2)))
                new_flux_vlss.append(new)


############################################################################################################

# PySE sourcefinder results
    pyse_sources=[]
    pyse_data=open(pyse, 'r')
    lines = iter(pyse_data)
    lines.next() 
    for line in lines:
        pyse_sources.append(line)
    pyse_data.close()

    ra_pyse=[]
    ra_err_pyse=[]
    dec_pyse=[]
    dec_err_pyse=[]
    int_flux_pyse=[]
    int_flux_err_pyse=[]
    pk_flux_pyse=[]
    pk_flux_err_pyse=[]
    posdifall_pyse=[]
    posdifall_err_pyse=[]
    int_flux_ratio_pyse=[]
    int_flux_ratio_err_pyse=[]
    pk_flux_ratio_pyse=[]
    pk_flux_ratio_err_pyse=[]
    flux_vlss_pyse=[]
    new_int_flux_ratio_pyse=[]
    new_int_flux_ratio_err_pyse=[]
    new_pk_flux_ratio_pyse=[]
    new_pk_flux_ratio_err_pyse=[]
    new_flux_vlss_pyse=[]
    posdifcent_pyse=[]
    de_ruiter_radius_pyse=[]
    associations=[]
    positions=[]
    fluxes={}

    variable_file = open('variables.txt','a')
    transients_file = open('transients.txt','a')
    multiple_assoc_file = open('multiple_assoc.txt','a')

    text_file = open(output+'_pyse.txt', "w")
    text_file.write('# CatPosition, Position, Distcent, catFlux, new_catFlux, de_Ruiter, separation, separation_err, intflux, intflux_err, pkflux, pkflux_err, intfluxrat, intfluxrat_err, pkfluxrat, pkfluxrat_err, new_intfluxrat, new_intfluxrat_err, new_pkfluxrat, new_pkfluxrat_err \n')
    
    for b in pyse_sources:
        nums2=b.split(', ')
        if float(nums2[10]) > min_flux:
            x2 = C.Position((float(nums2[0]), float(nums2[2])))
            positions.append(x2)
            fluxes[str(x2)] = nums2[10]   
            posdif_old=1000000
            for c in range(len(flux_vlss)):
                posdif=x2.angsep(C.Position(p1[c]))
                if posdif < posdif_old:
                    catpos=p1[c]
                    assoc=x2
                    posdif_err=((((float(nums2[1])**2+float(abit)**2)**(0.5))**2 + ((float(nums2[3])**2+float(abit)**2)**(0.5))**2)**0.5)
                    intfluxrat=float(nums2[10])/flux_vlss[c]
                    intfluxrat_err=((float(nums2[11])+float(nums2[10]))/flux_vlss[c])-intfluxrat
                    pkfluxrat=(float(nums2[12]))/flux_vlss[c]
                    pkfluxrat_err=((float(nums2[13])+float(nums2[12]))/flux_vlss[c])-pkfluxrat
                    new_intfluxrat=float(nums2[10])/new_flux_vlss[c]
                    new_intfluxrat_err=((float(nums2[11])+float(nums2[10]))/new_flux_vlss[c])-intfluxrat
                    new_pkfluxrat=(float(nums2[12]))/new_flux_vlss[c]
                    new_pkfluxrat_err=((float(nums2[13])+float(nums2[12]))/new_flux_vlss[c])-pkfluxrat
                    distcent=posdifcent[c]
                    flux=flux_vlss[c]
                    new_flux=new_flux_vlss[c]
                    posdif_old=posdif
                    pt1 = math.pow(((float(nums2[0])*math.cos(math.radians(float(nums2[2]))))-(float(ra_vlss[c])*math.cos(math.radians(float(dec_vlss[c]))))),2)
                    pt2 = math.pow(((float(nums2[1])**2+float(abit)**2)**(0.5)),2)
                    pt3 = math.pow((float(nums2[2])-float(dec_vlss[c])),2)
                    pt4 = math.pow(((float(nums2[3])**2+float(abit)**2)**(0.5)),2)
                    pt5 = (pt1/pt2)+(pt3/pt4)
                    de_ruiter=math.sqrt(pt5)


            posdif_old=float(str(posdif_old).split()[0])
            if posdif_old < max_sep_cutoff:
                associations.append(assoc)
                de_ruiter_radius_pyse.append(de_ruiter)
                posdifall_pyse.append(posdif_old*3600)
                posdifall_err_pyse.append(posdif_err*3600)
                int_flux_ratio_pyse.append(intfluxrat)
                int_flux_ratio_err_pyse.append(intfluxrat_err)
                pk_flux_ratio_pyse.append(pkfluxrat)
                pk_flux_ratio_err_pyse.append(pkfluxrat_err)
                new_int_flux_ratio_pyse.append(new_intfluxrat)
                new_int_flux_ratio_err_pyse.append(new_intfluxrat_err)
                new_pk_flux_ratio_pyse.append(new_pkfluxrat)
                new_pk_flux_ratio_err_pyse.append(new_pkfluxrat_err)
                posdifcent_pyse.append(distcent)
                flux_vlss_pyse.append(flux)
                new_flux_vlss_pyse.append(new_flux)
                
                text_file.write(str(catpos)+' '+str(x2)+' '+str(distcent)+' '+str(flux)+' '+str(new_flux)+' '+str(de_ruiter)+' '+str((posdif_old*3600))+' '+str((posdif_err*3600))+' '+str(nums2[10])+' '+str(nums2[11])+' '+str(nums2[12])+' '+str((nums2[13]).rstrip('\n'))+' '+str(intfluxrat)+' '+str(intfluxrat_err)+' '+str(pkfluxrat)+' '+str(pkfluxrat_err)+' '+str(new_intfluxrat)+' '+str(new_intfluxrat_err)+' '+str(new_pkfluxrat)+' '+str(new_pkfluxrat_err)+'\n')
                if new_intfluxrat > flux_ratio:
                    print('Possible flaring known source. Flux ratio between observed and skymodel = '+str(new_intfluxrat))
                    print('Position: '+str(catpos))
                    print('Catalogue flux: '+str(new_flux))
                    print('Observed flux: '+str(nums2[10]))
                    print('Image: '+output.split('.pdf')[0])
                    variable_file.write(str(catpos)+' '+str(x2)+' '+str(distcent)+' '+str(flux)+' '+str(new_flux)+' '+str(de_ruiter)+' '+str((posdif_old*3600))+' '+str((posdif_err*3600))+' '+str(nums2[10])+' '+str(nums2[11])+' '+str(nums2[12])+' '+str((nums2[13]).rstrip('\n'))+' '+str(intfluxrat)+' '+str(intfluxrat_err)+' '+str(pkfluxrat)+' '+str(pkfluxrat_err)+' '+str(new_intfluxrat)+' '+str(new_intfluxrat_err)+' '+str(new_pkfluxrat)+' '+str(new_pkfluxrat_err)+' '+output.split('.pdf')[0]+'\n')

    for pos in positions:
        if pos not in associations:
            print('!!!!!!!!!NEW SOURCE!!!!!!!!!')
            print('Position = '+str(pos))
            print('Flux = '+str(fluxes[str(pos)]))
            print('Image = '+output.split('.pdf')[0])
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n \n')
            transients_file.write(str(pos)+' '+str(fluxes[str(pos)])+' '+output.split('.pdf')[0]+'\n')

    for pos1 in associations:
        n=0
        for pos2 in associations:
            if pos1==pos2:
                n=n+1
        if n > 1:
            print('!!!!!!!!MULTIPLE ASSOCIATION!!!!!!!!!!!!')
            print('Possible transient? Check associations.')
            print('Position = '+str(pos1))
            print('Number of associated sources: '+str(n))
            print('Image = '+output.split('pdf')[0])
            multiple_assoc_file.write(str(pos1)+' '+str(n)+' '+output.split('.pdf')[0]+'\n')

############################################################################################################

# Plot figures to pdf


    pdf = PdfPages(output)

    if len(posdifall_pyse) != 0:
        fig, axs = plt.subplots(nrows=6, ncols=2)
        ax1 = axs[0,0]
        ax2 = axs[0,1]
        ax3 = axs[1,0]
        ax4 = axs[1,1]
        ax5 = axs[2,0]
        ax6 = axs[2,1]
        ax7 = axs[3,0]
        ax8 = axs[3,1]
        ax9 = axs[4,0]
        ax10 = axs[4,1]
        ax11 = axs[5,0]
        ax12 = axs[5,1]
        
        avg_offset=sum(posdifall_pyse)/len(posdifall_pyse)
        avg_flux_ratio=sum(int_flux_ratio_pyse)/len(int_flux_ratio_pyse)
        new_avg_flux_ratio=sum(new_int_flux_ratio_pyse)/len(new_int_flux_ratio_pyse)
        avg_pkflux_ratio=sum(pk_flux_ratio_pyse)/len(pk_flux_ratio_pyse)
        new_avg_pkflux_ratio=sum(new_pk_flux_ratio_pyse)/len(new_pk_flux_ratio_pyse)
        
        rms_flux_ratio = sqrt((sum(n*n-(avg_flux_ratio*avg_flux_ratio) for n in int_flux_ratio_pyse))/len(int_flux_ratio_pyse))
        new_rms_flux_ratio = sqrt((sum(n*n-(new_avg_flux_ratio*new_avg_flux_ratio) for n in new_int_flux_ratio_pyse))/len(new_int_flux_ratio_pyse))
        rms_pkflux_ratio = sqrt((sum(n*n-(avg_pkflux_ratio*avg_pkflux_ratio) for n in pk_flux_ratio_pyse))/len(pk_flux_ratio_pyse))
        new_rms_pkflux_ratio = sqrt((sum(n*n-(new_avg_pkflux_ratio*new_avg_pkflux_ratio) for n in new_pk_flux_ratio_pyse))/len(new_pk_flux_ratio_pyse))

        subplots_adjust(hspace=0.001,wspace=0.001)
        ax1.set_xlim((min(posdifcent_pyse)-1),(max(posdifcent_pyse)+1))
        ax1.set_ylim(-10,(max(posdifall_pyse)+max(posdifall_err_pyse)+10))
        ax1.locator_params(nbins=8)
        ax1.axhline(y=pixel_size,color='red')
        ax1.axhline(y=0,color='black')
        ax1.axhline(y=(sum(posdifall_pyse)/len(posdifall_pyse)), color='blue')
        ax1.text((min(posdifcent_pyse)-0.9), (sum(posdifall_pyse)/len(posdifall_pyse))+2 , str(round((sum(posdifall_pyse)/len(posdifall_pyse)),1)), color='blue', fontsize=8)
        ax2.locator_params(nbins=8)
        ax2.set_xlim((min(flux_vlss_pyse)-1),(max(flux_vlss_pyse)+1))
        ax2.set_ylim(-10,(max(posdifall_pyse)+max(posdifall_err_pyse)+10))
        ax2.axhline(y=pixel_size,color='red')
        ax2.axhline(y=0,color='black')
        ax2.axhline(y=(sum(posdifall_pyse)/len(posdifall_pyse)), color='blue')
        ax3.locator_params(nbins=8)
        ax3.set_xlim((min(posdifcent_pyse)-1),(max(posdifcent_pyse)+1))
        ax3.set_ylim((min(de_ruiter_radius_pyse)-0.5),(max(de_ruiter_radius_pyse)+0.5))
        ax3.axhline(y=5.68,color='red')
        ax4.axhline(y=5.68,color='red')
        
        ax4.locator_params(nbins=8)
        ax4.set_xlim((min(flux_vlss_pyse)-1),(max(flux_vlss_pyse)+1))
        ax4.set_ylim((min(de_ruiter_radius_pyse)-0.5),(max(de_ruiter_radius_pyse)+0.5))
        ax5.locator_params(nbins=8)
        ax5.set_xlim((min(posdifcent_pyse)-1),(max(posdifcent_pyse)+1))
        ax5.set_ylim((min(int_flux_ratio_pyse)-max(int_flux_ratio_err_pyse)-1),(max(int_flux_ratio_pyse)+max(int_flux_ratio_err_pyse)+1))
        ax5.axhline(y=1,color='red')
        ax5.text((min(posdifcent_pyse)-0.9), (sum(int_flux_ratio_pyse)/len(int_flux_ratio_pyse))*1.2 , str(round(avg_flux_ratio,2)), color='blue', fontsize=8)
        
        ax6.locator_params(nbins=8)
        ax6.set_xlim((min(flux_vlss_pyse)-1),(max(flux_vlss_pyse)+1))
        ax6.set_ylim((min(int_flux_ratio_pyse)-max(int_flux_ratio_err_pyse)-1),(max(int_flux_ratio_pyse)+max(int_flux_ratio_err_pyse)+1))
        ax6.axhline(y=1,color='red')
        ax7.locator_params(nbins=8)
        ax7.set_xlim((min(posdifcent_pyse)-1),(max(posdifcent_pyse)+1))
        ax7.set_ylim((min(pk_flux_ratio_pyse)-max(pk_flux_ratio_err_pyse)),(max(pk_flux_ratio_pyse)+max(pk_flux_ratio_err_pyse)))
        ax7.axhline(y=1,color='red')
        ax7.text((min(posdifcent_pyse)-0.9), (sum(pk_flux_ratio_pyse)/len(pk_flux_ratio_pyse))*1.2 , str(round(avg_pkflux_ratio,2)), color='blue', fontsize=8)
        ax8.locator_params(nbins=8)
        ax8.set_xlim((min(flux_vlss_pyse)-1),(max(flux_vlss_pyse)+1))
        ax8.set_ylim((min(pk_flux_ratio_pyse)-max(pk_flux_ratio_err_pyse)),(max(pk_flux_ratio_pyse)+max(pk_flux_ratio_err_pyse)))
        ax8.axhline(y=1,color='red')
        ax5.axhline(y=avg_flux_ratio,color='blue')
        ax6.axhline(y=avg_flux_ratio,color='blue')
        ax7.axhline(y=avg_pkflux_ratio,color='blue')
        ax8.axhline(y=avg_pkflux_ratio,color='blue')
        ax5.axhline(y=(avg_flux_ratio+rms_flux_ratio),color='blue',linestyle='--')
        ax5.axhline(y=(avg_flux_ratio-rms_flux_ratio),color='blue',linestyle='--')
        ax6.axhline(y=(avg_flux_ratio+rms_flux_ratio),color='blue',linestyle='--')
        ax6.axhline(y=(avg_flux_ratio-rms_flux_ratio),color='blue',linestyle='--')
        ax7.axhline(y=(avg_pkflux_ratio+rms_pkflux_ratio),color='blue',linestyle='--')
        ax7.axhline(y=(avg_pkflux_ratio-rms_pkflux_ratio),color='blue',linestyle='--')
        ax8.axhline(y=(avg_pkflux_ratio+rms_pkflux_ratio),color='blue',linestyle='--')
        ax8.axhline(y=(avg_pkflux_ratio-rms_pkflux_ratio),color='blue',linestyle='--')
    
        ax9.locator_params(nbins=8)
        ax9.set_xlim((min(posdifcent_pyse)-1),(max(posdifcent_pyse)+1))
        ax9.set_ylim((min(new_int_flux_ratio_pyse)-max(new_int_flux_ratio_err_pyse)-1),(max(new_int_flux_ratio_pyse)+max(new_int_flux_ratio_err_pyse)+1))
        ax9.axhline(y=1,color='red')
        ax9.text((min(posdifcent_pyse)-0.9), (sum(new_int_flux_ratio_pyse)/len(new_int_flux_ratio_pyse))*1.2 , str(round(new_avg_flux_ratio,2)), color='blue', fontsize=8)
        ax10.locator_params(nbins=8)
        ax10.set_xlim((min(flux_vlss_pyse)-1),(max(flux_vlss_pyse)+1))
        ax10.set_ylim((min(new_int_flux_ratio_pyse)-max(new_int_flux_ratio_err_pyse)-1),(max(new_int_flux_ratio_pyse)+max(new_int_flux_ratio_err_pyse)+1))
        ax10.axhline(y=1,color='red')
        ax11.locator_params(nbins=8)
        ax11.set_xlim((min(posdifcent_pyse)-1),(max(posdifcent_pyse)+1))
        ax11.set_ylim((min(new_pk_flux_ratio_pyse)-max(new_pk_flux_ratio_err_pyse)),(max(new_pk_flux_ratio_pyse)+max(new_pk_flux_ratio_err_pyse)))
        ax11.axhline(y=1,color='red')
        ax11.text((min(posdifcent_pyse)-0.9), (sum(new_pk_flux_ratio_pyse)/len(new_pk_flux_ratio_pyse))*1.2 , str(round(new_avg_pkflux_ratio,2)), color='blue', fontsize=8)
        ax12.locator_params(nbins=8)
        ax12.set_xlim((min(flux_vlss_pyse)-1),(max(flux_vlss_pyse)+1))
        ax12.set_ylim((min(new_pk_flux_ratio_pyse)-max(new_pk_flux_ratio_err_pyse)),(max(new_pk_flux_ratio_pyse)+max(new_pk_flux_ratio_err_pyse)))
        ax12.axhline(y=1,color='red')
        ax9.axhline(y=new_avg_flux_ratio,color='blue')
        ax10.axhline(y=new_avg_flux_ratio,color='blue')
        ax11.axhline(y=new_avg_pkflux_ratio,color='blue')
        ax12.axhline(y=new_avg_pkflux_ratio,color='blue')
        ax9.axhline(y=(new_avg_flux_ratio+new_rms_flux_ratio),color='blue',linestyle='--')
        ax9.axhline(y=(new_avg_flux_ratio-new_rms_flux_ratio),color='blue',linestyle='--')
        ax10.axhline(y=(new_avg_flux_ratio+rms_flux_ratio),color='blue',linestyle='--')
        ax10.axhline(y=(new_avg_flux_ratio-new_rms_flux_ratio),color='blue',linestyle='--')
        ax11.axhline(y=(new_avg_pkflux_ratio+new_rms_pkflux_ratio),color='blue',linestyle='--')
        ax11.axhline(y=(new_avg_pkflux_ratio-new_rms_pkflux_ratio),color='blue',linestyle='--')
        ax12.axhline(y=(new_avg_pkflux_ratio+new_rms_pkflux_ratio),color='blue',linestyle='--')
        ax12.axhline(y=(new_avg_pkflux_ratio-new_rms_pkflux_ratio),color='blue',linestyle='--')
        
        
        xticklabels = ax1.get_xticklabels()+ax2.get_xticklabels()+ax3.get_xticklabels()+ax4.get_xticklabels()+ax5.get_xticklabels()+ax6.get_xticklabels()+ax7.get_xticklabels()+ax8.get_xticklabels()+ax9.get_xticklabels()+ax10.get_xticklabels()+ax11.get_xticklabels()+ax12.get_xticklabels()
        setp(xticklabels, visible=False)
        yticklabels = ax2.get_yticklabels()+ax4.get_yticklabels()+ax6.get_yticklabels()+ax8.get_yticklabels()+ax10.get_yticklabels()+ax12.get_yticklabels()
        setp(yticklabels, visible=False)
        labelx = -0.15  # axes coords
        ax1.tick_params(labelsize='small')
        ax3.tick_params(labelsize='small')
        ax5.tick_params(labelsize='small')
        ax7.tick_params(labelsize='small')
        ax9.tick_params(labelsize='small')
        ax11.tick_params(labelsize='small')
        ax12.tick_params(labelsize='small')
        ax1.set_ylabel('Separation \n (arcsec)', fontsize=8)
        ax1.yaxis.set_label_coords(labelx, 0.5)
        ax3.set_ylabel('De Ruiter \n Radius', fontsize=8)
        ax3.yaxis.set_label_coords(labelx, 0.5)
        ax5.set_ylabel('Int flux \n ratio (sky)', fontsize=8)
        ax5.yaxis.set_label_coords(labelx, 0.5)
        ax7.set_ylabel('Pk flux \n ratio (sky)', fontsize=8)
        ax7.yaxis.set_label_coords(labelx, 0.5)
        ax9.set_ylabel('Int flux \n ratio (obs)', fontsize=8)
        ax9.yaxis.set_label_coords(labelx, 0.5)
        ax11.set_ylabel('Pk flux \n ratio (obs)', fontsize=8)
        ax11.set_xlabel('Distance from centre of image (degrees)', fontsize=8)
        ax11.yaxis.set_label_coords(labelx, 0.5)
        ax12.set_xlabel('Skymodel flux of source (Jy)', fontsize=8)
        ax1.set_title(pyse+' compared to skymodel ', fontsize=8)
        ax2.set_title(' - pixel size: '+str(pixel_size)+' arcsec (Pyse)', fontsize=8)
        ax1.errorbar(posdifcent_pyse, posdifall_pyse, yerr=posdifall_err_pyse, fmt='o')
        ax2.errorbar(flux_vlss_pyse, posdifall_pyse, yerr=posdifall_err_pyse, fmt='o')
        ax3.errorbar(posdifcent_pyse, de_ruiter_radius_pyse, fmt='o')
        ax4.errorbar(flux_vlss_pyse, de_ruiter_radius_pyse, fmt='o')
        ax5.errorbar(posdifcent_pyse, int_flux_ratio_pyse, yerr=int_flux_ratio_err_pyse, fmt='o')
        ax6.errorbar(flux_vlss_pyse, int_flux_ratio_pyse, yerr=int_flux_ratio_err_pyse, fmt='o')
        ax7.errorbar(posdifcent_pyse, pk_flux_ratio_pyse, yerr=pk_flux_ratio_err_pyse, fmt='o')
        ax8.errorbar(flux_vlss_pyse, pk_flux_ratio_pyse, yerr=pk_flux_ratio_err_pyse, fmt='o')
        ax9.errorbar(posdifcent_pyse, new_int_flux_ratio_pyse, yerr=new_int_flux_ratio_err_pyse, fmt='o')
        ax10.errorbar(flux_vlss_pyse, new_int_flux_ratio_pyse, yerr=new_int_flux_ratio_err_pyse, fmt='o')
        ax11.errorbar(posdifcent_pyse, new_pk_flux_ratio_pyse, yerr=new_pk_flux_ratio_err_pyse, fmt='o')
        ax12.errorbar(flux_vlss_pyse, new_pk_flux_ratio_pyse, yerr=new_pk_flux_ratio_err_pyse, fmt='o')
        savefig(pdf, format='pdf', orientation='portrait')
        matplotlib.pyplot.clf()
        pdf.close()
        
############################################################################################################

opt = optparse.OptionParser()
opt.add_option('-p','--pyse',help='PySE extracted source list (CSV format)',default='none',type='string')
opt.add_option('-r','--ra_cent',help='RA of image centre (degrees)',default='0',type='float')
opt.add_option('-d','--dec_cent',help='Dec of image centre (degrees)',default='0',type='float')
opt.add_option('-f','--min_flux',help='Minimum flux used in analysis (Jy)',default='2',type='float')
opt.add_option('-s','--max_sep_cutoff',help='The maximum separation allowed for associated sources (degrees)',default='0.05',type='float')
opt.add_option('-o','--output',help='Output filename for pdf graphs',default='graphs.pdf',type='string')
opt.add_option('-x','--pixel_size',help='Pixel size (arcsec)',default='0',type='float')
opt.add_option('-y','--bmaj',help='Beam major axis (arcsec)',default='0',type='float')
opt.add_option('-z','--bmin',help='Beam minor axis (arcsec)',default='0',type='float')
opt.add_option('-q','--freq',help='Observation frequency (Hz)',default='60e6',type='float')
opt.add_option('-a','--abit',help='Systematic position error (arcsec)',default='0.0',type='float')
opt.add_option('-g','--flux_ratio',help='Flux ratio which spots if a source is flaring',default='100',type='float')

opts,args = opt.parse_args()

if len(args) != 1: 
	print 'Need required argument skymodel'
else:
	main(opts,args)
