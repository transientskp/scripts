#!/bin/python
import os
import math
import random

position='14:20:00.00000000, +52.00.00.00000000'
testtype='single_flare' # single_flare, periodic, fred, random, slow_rise, slow_decay, gaussian
lda=0.5 #fred test lambda

obsids=['L40020', 'L40022', 'L40024', 'L40026', 'L40028', 'L40030', 'L40032', 'L40034', 'L40036', 'L40038', 'L40040', 'L40042', 'L40044', 'L40046', 'L40048', 'L40050', 'L40052', 'L40054', 'L40056', 'L40058']
original_skymodel='/data/scratch/rowlinson/simulate_image/lsc_fake.skymodel'

for peak in range(5,100,5):
    for const in range (0,peak,5):
        testname=testtype+'_'+str(peak)+'Jy_'+str(const)+'Jy'
        print testname
        if os.path.exists('/staging3/rowlinson/simulated_datasets/single_flare/'+testname+'/'+testname+'_L40020.fits'):
            print('Test already exists')
        else:
            print(testname)

            if testtype == 'single_flare':
                transient=[const, const, const, const, const, const, const, peak, const, const, const, const, const, const, const, const, const, const, const, const]
                print(transient)
            elif testtype == 'periodic':
                transient=[const, peak, const, peak, const, peak, const, peak, const, peak, const, peak, const, peak, const, peak, const, peak, const, peak]
                print(transient)
            elif testtype == 'fred':
                peak_old=peak
                peak=peak_old-const
                transient=[const, const, peak+const, peak*math.exp(-1*lda)+const,  peak*math.exp(-2*lda)+const, peak*math.exp(-3*lda)+const, peak*math.exp(-4*lda)+const, peak*math.exp(-5*lda)+const, peak*math.exp(-6*lda)+const, peak*math.exp(-7*lda)+const, peak*math.exp(-8*lda)+const, peak*math.exp(-9*lda)+const, peak*math.exp(-10*lda)+const, peak*math.exp(-11*lda)+const, peak*math.exp(-12*lda)+const, peak*math.exp(-13*lda)+const, peak*math.exp(-14*lda)+const, peak*math.exp(-15*lda)+const, peak*math.exp(-16*lda)+const, peak*math.exp(-17*lda)+const]
                peak=peak_old
                print(transient)
            elif testtype == 'random':
                transient=[random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak), random.uniform(const, peak)]
                print transient
            elif testtype == 'slow_rise':
                peak_old=peak
                peak=peak_old-const
                increment=float(peak)/19
                transient=[const, const+increment, const+increment*2, const+increment*3, const+increment*4, const+increment*5, const+increment*6, const+increment*7, const+increment*8, const+increment*9, const+increment*10, const+increment*11, const+increment*12, const+increment*13, const+increment*14, const+increment*15, const+increment*16, const+increment*17, const+increment*18, const+increment*19]
                print(transient)
            elif testtype == 'slow_decay':
                peak_old=peak
                peak=peak_old-const
                increment=-1*float(peak)/19
                const=peak
                transient=[const, const+increment, const+increment*2, const+increment*3, const+increment*4, const+increment*5, const+increment*6, const+increment*7, const+increment*8, const+increment*9, const+increment*10, const+increment*11, const+increment*12, const+increment*13, const+increment*14, const+increment*15, const+increment*16, const+increment*17, const+increment*18, const+increment*19]
                print(transient)
            elif testtype == 'gaussian':
                transient=[((peak-const)*math.exp(-0.25*(0-8)*(0-8)))+const, (peak-const)*math.exp(-0.25*(1-8)*(1-8))+const, (peak-const)*math.exp(-0.25*(2-8)*(2-8))+const, (peak-const)*math.exp(-0.25*(3-8)*(3-8))+const, (peak-const)*math.exp(-0.25*(4-8)*(4-8))+const, (peak-const)*math.exp(-0.25*(5-8)*(5-8))+const, (peak-const)*math.exp(-0.25*(6-8)*(6-8))+const, (peak-const)*math.exp(-0.25*(7-8)*(7-8))+const, ((peak-const)*math.exp(-0.25*(8-8)*(8-8)))+const, (peak-const)*math.exp(-0.25*(9-8)*(9-8))+const, (peak-const)*math.exp(-0.25*(10-8)*(10-8))+const, (peak-const)*math.exp(-0.25*(11-8)*(11-8))+const, (peak-const)*math.exp(-0.25*(12-8)*(12-8))+const, (peak-const)*math.exp(-0.25*(13-8)*(13-8))+const, (peak-const)*math.exp(-0.25*(14-8)*(14-8))+const, (peak-const)*math.exp(-0.25*(15-8)*(15-8))+const, (peak-const)*math.exp(-0.25*(16-8)*(16-8))+const, (peak-const)*math.exp(-0.25*(17-8)*(17-8))+const, (peak-const)*math.exp(-0.25*(18-8)*(18-8))+const, (peak-const)*math.exp(-0.25*(19-8)*(19-8))+const]
                print(transient)
            else:
                print('not valid test type')
                exit()

            os.mkdir('/data/scratch/rowlinson/simulate_image/'+testname)
            os.system('cp -r /data/scratch/rowlinson/simulate_image/original/* /data/scratch/rowlinson/simulate_image/'+testname+'/.')
                
            n=0
                
            os.chdir('/data/scratch/rowlinson/simulate_image/'+testname)

            for obsid in obsids:
                os.chdir('/data/scratch/rowlinson/simulate_image/'+testname+'/'+obsid)
                msname=obsid+'_band4.MS.flag'
                transient_skymodel='TRANSIENT, POINT, '+position+', '+str(transient[n])+', , , , , [-0.7]'
                skymodel=obsid+'_transient.skymodel'
                os.system('cp '+original_skymodel+' '+skymodel)

                with open(skymodel,'a') as sky:
                    sky.write(transient_skymodel)
                    sky.close()

                os.system('python /data/scratch/rowlinson/simulate_image/injectnoise_edit.py '+msname)
                os.system('calibrate-stand-alone --replace-sourcedb '+msname+' /data/scratch/rowlinson/simulate_image/add.parset '+skymodel)
                os.system('calibrate-stand-alone -f '+msname+' /data/scratch/rowlinson/simulate_image/uv-plane-cal.parset '+skymodel)

                f = open('aw_'+msname+'_'+skymodel+'.parset','w')
                f.write("""
            UseMasks=TRUE
            applyIonosphere=FALSE 
            data=CORRECTED_DATA
            operation=csclean
            threshold=2.00Jy
            verbose=0
            StepApplyElement=2
            applyBeam=TRUE
            cellsize=90arcsec
            mask=%s
            niter=100000
            npix=512
            padding=1.2
            robust=0.0
            select=sumsqr(UVW[:2])<9e6
            stokes=I
            weight=briggs
            wmax=3000
            wprojplanes=150
            ms=%s
            image=%s.img
            """ % (skymodel, msname, obsid) )
                f.close()

                os.system('awimager aw_'+msname+'_'+skymodel+'.parset')
                os.system('addImagingInfo '+obsid+'.img.restored.corr ~/test2.sky 0 3000 '+msname)
                os.system("image2fits 'in'="+obsid+".img.restored.corr 'out'="+testname+"_"+obsid+".fits")
                os.system('cp '+testname+'_'+obsid+'.fits ../.')
                n=n+1
            

