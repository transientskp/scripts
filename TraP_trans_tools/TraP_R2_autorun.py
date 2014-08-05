#!/usr/bin/python
import fileinput
import os
import glob
import numpy as np
import math
import format_TraP_data
import tkp.utility.coordinates as coords
import generic_tools

def read_skymodel(sky):
    vlss_data2=open(sky, 'r')
    lines = iter(vlss_data2)
    lines.next()
    lines.next()
    for line in lines:
        vlss_sources.append(line)
    vlss_data2.close()
    for a in range(len(vlss_sources)):
        data=vlss_sources[a].split(', ')
        dec=data[3].replace('.',':', 2)
        position=data[2]+' '+dec
        x=(C.Position(position)).dd()
        vlss_data_tmp.append([x,float(data[4])])
    return vlss_data_tmp

def run_TraP(sky,data,output_folder):
    if not os.path.isdir(sky+'_'+output_folder):
        os.system('cp -r blank '+sky+'_'+output_folder)
        for line in fileinput.input(sky+'_'+output_folder+'/images_to_process.py', inplace=1):
            print line.replace('        os.path.expanduser("/scratch/antoniar/stuff/*.fits")','os.path.expanduser("'+data+'/'+output_folder+'_'+sky+'*.corr")')
        for line in fileinput.input(sky+'_'+output_folder+'/job_params.cfg',inplace=1):
            print line.replace('description = "TRAP dataset"','description = "'+sky+'_'+output_folder+'_thresh"')
        os.system('./manage.py run '+sky+'_'+output_folder+' 2>&1 | tee '+sky+'_'+output_folder+'/traplog')
    f = open(sky+'_'+output_folder+'/traplog', 'r')
    for line in f:
        print line
        if 'for dataset ' in line:
            dataset_id=line.split('INFO:tkp.db.configstore:storing config to database for dataset ')[-1].rstrip()
            print dataset_id
            break
    return dataset_id

###################### INITIAL SETUP STEPS ######################

simulations=['gaussian','fred','single_flare','periodic','slow_fall','slow_rise','turn_on','turn_off']
print simulations
for sims in simulations:
# General parameters...
    print 'Running: '+sims
    database='antoniar'
    data='/scratch/antoniar/heastro-home/simulations/'+sims
#    transient_position=C.Position('09:00:02.173 52:08:39.92')#.dd()
    trans_ra = 135.009054
    trans_decl = 52.144422

    output_folder=sims
    trap='TRUE'
    Cvalue=[1]#[0.01,0.05,0.1,0.5,1,5,10,50,100]
    eta='n' # 1,10,100,1000
    V='n'
    sigma=2.

    skymodels={(x.split('/')[-1]).split('_')[0]: x for x in glob.glob('/scratch/antoniar/heastro-home/simulations/*basic.skymodel')}
    outname=data.split('/')[-1]
    os.system('mkdir '+output_folder)

    vlss_data={}
    trans_params={}
    transient_list={}
    source_list={}
    dataset_id={}
    trans_runcat=[]
    trans_data=[]
    new_steady_data=[]
    output=[]
    for sky in skymodels.keys():
        if os.path.exists(data+'/'+output_folder+'_'+sky+'_0.skymodel.ms.img.restored.corr'):
#            vlss_sources=[]
#            vlss_data_tmp=[]
#            vlss_data[sky]=read_skymodel(skymodels[sky])
            trans_params[sky]=[sky.split('to')[0],sky.split('to')[1]]
            dataset_id[sky]=run_TraP(sky,data,output_folder)
            format_TraP_data.format_data('antoniar',dataset_id[sky],'p','heastrodb','5432','antoniar','antoniar')
            trans_data=generic_tools.extract_data('ds'+str(dataset_id[sky])+'_trans_data.txt')
            for line in trans_data:
                if coords.angsep(float(line[8]),float(line[9]),trans_ra,trans_decl)<10.:
                    output.append(line)
            
    output3 = open('sim_'+sims+'_trans_data.txt','w')
    output3.write('#Runcat_id, eta_nu, signif, V_nu, flux, fluxrat, freq, dpts, RA, Dec, trans_type \n')
    for x in range(len(output)):
        string='%s' % ','.join(str(val) for val in output[x])
        output3.write(string+'\n')
    output3.close()

