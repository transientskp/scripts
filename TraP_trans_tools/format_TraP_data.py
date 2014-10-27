from dump_trans_data_v1 import dump_trans
import generic_tools
import os
import numpy as np

def get_data(database, dataset_id, release, host, port, user, pword):
#
# Calls a function to dump the source data from the TraP database into a CSV file
#
    if release == 'm':
        dump_trans(database,dataset_id, 'monetdb', host, port, user, pword)
        return
    elif release == 'p':
        dump_trans(database,dataset_id, 'postgresql', host, port, user, pword)
        return
    else:
        print 'This script is for either MonetDB (m) or Postgres (p) databases, please specify m or p.'
        exit()

def read_src_lc(sources, lightcurves):
#
# Reads all the extracted source data and sorts them into unique sources with their lightcurves
#
    runcat=[] # A list comprising all the unique runcat source ids.
    new_source={} # A dictionary containing all the lightcurves, etc, for each unique source
    frequencies=[] # The frequencies in the dataset
    for a in range(len(sources)):
        new_runcat=sources[a][8]
        new_freq=int((float(sources[a][7])/1e6)+0.5) # observing frequency in MHz
        # check if it's a new runcat source and then either create a new entry or append
        if new_runcat not in runcat:
            runcat.append(new_runcat)
            new_source[new_runcat]=[sources[a]]
        else:
            new_source[new_runcat]=new_source[new_runcat]+[sources[a]]
        # If the observing frequency is new, append to the list
        if new_freq not in frequencies: 
            frequencies.append(new_freq)
    # If required, can output a single light curve file for each unique source in the dataset
    if lightcurves=='T' or lightcurves=='True' or lightcurves=='t' or lightcurves=='true':
        for key in new_source.keys():
            output = open(str(key)+'_lc.txt','w')
            output.write('#ExtrSrcId,Time,IntegrationTime,IntFlux,IntFluxErr,Freq,Eta,V,extrType\n')
            for a in range(len(new_source[key])):
                x = new_source[key][a]
                string='%s' % ','.join(str(val) for val in [x[14], x[10], x[9], x[5], x[6], float(x[7])/1e6, x[2], x[11], x[3]])
                output.write(string+'\n')
            output.close()
    # return the list of observing frequencies and the full dictionary of source information
    return frequencies, new_source

def collate_trans_data(new_source,frequencies,transients):
#
# Using the data stored in the new_source dictionary and the transients list, store the transient and variability
# parameters for each unique source in the dataset.
#    
    trans_data=[]
    bands={}
    # sort the information in the transients list into a dictionary
    # transient id:[transient type, flux/max_rms, flux/min_rms, detection_thresh]
    transRuncat={x[5]:[x[2],float(x[1])/float(x[3]), float(x[1])/float(x[4]), x[0]] for x in transients}
    for freq in frequencies:
        for keys in new_source.keys():
            flux=[]
            flux_err=[]
            date=[]
            band=[]
            tmp=0.
            # Extract the different parameters for the source
            for b in range(len(new_source[keys])):
                if int((float(new_source[keys][b][7])/1e6)+0.5)==freq:
                    band.append(new_source[keys][b][0])
                    flux.append(float(new_source[keys][b][5]))
                    flux_err.append(float(new_source[keys][b][6]))
                    if tmp<int(new_source[keys][b][14]):
                        eta=float(new_source[keys][b][2])
                        V=float(new_source[keys][b][11])
                        N=float(new_source[keys][b][4])
                        tmp=int(new_source[keys][b][14])
                    ra=new_source[keys][b][-2]
                    dec=new_source[keys][b][-3]
            # if the source has been observed in the given observing frequency, extract the variability parameters
            # from the final observation at that frequency.
            if len(flux)!=0:
                bands[freq]=band
                ### Calculate the ratios...
                avg_flux_ratio = [x/(sum(flux)/len(flux)) for x in flux]
                ### Collate and store the transient parameters (these are across all the pipeline runs for the final figures)
                if keys in transRuncat.keys():
                # identify if this source is in the new source transient list and extract parameters
                    transType=transRuncat[keys][0]
                    min_sig=transRuncat[keys][1]
                    max_sig=transRuncat[keys][2]
                    detect_thresh=transRuncat[keys][3]
                else:
                # if not in the transient list, then insert standard parameters for non-transients
                    transType=2
                    min_sig=0
                    max_sig=0
                    detect_thresh=0
                # write out the key parameters for each source at each observing frequency
                trans_data.append([keys, eta, V, max(flux), max(avg_flux_ratio), freq, len(flux), ra, dec, transType, min_sig, max_sig, detect_thresh])
    print 'Number of transients in sample: '+str(len(trans_data))
    # Return the array of key parameters for each source
    return trans_data

def format_data(database, dataset_id, release,host,port, user, pword, lightcurves):
#
# Extract the required data from the TraP database and put it into the required format for later analysis
#    
    if not os.path.isfile('ds_'+str(dataset_id)+'_sources.csv'):
    # grab the data if it has not been previously extracted from the database
        get_data(database, dataset_id, release,host,port, user, pword)
    if not os.path.isfile('ds_'+str(dataset_id)+'_transients.csv'):
    # if no new sources were detected, create an empty list
        transients=[]
    else:
        transients = generic_tools.extract_data('ds_'+str(dataset_id)+'_transients.csv')
    sources = generic_tools.extract_data('ds_'+str(dataset_id)+'_sources.csv')
    frequencies, new_source = read_src_lc(sources, lightcurves)
    trans_data = collate_trans_data(new_source,frequencies,transients)
    output3 = open('ds'+str(dataset_id)+'_trans_data.txt','w')
    output3.write('#Runcat_id, eta_nu, V_nu, flux, fluxrat, freq, dpts, RA, Dec, trans_type, max_rms_sigma, min_rms_sigma, detection_threshold  \n')
    for x in range(len(trans_data)):
        string='%s' % ','.join(str(val) for val in trans_data[x])
        output3.write(string+'\n')
    output3.close()
    print 'Data extracted and saved'
    return
