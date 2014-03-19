#!/usr/bin/python
import numpy as np

def dump_data(release,database,dataset_id):
    ### Getting the data from the Database - Thanks Tim!
    if release == '0':
        import dump_transient_runcat_v0
        from dump_transient_runcat_v0 import dump_trans
        dump_trans(database,dataset_id)
    elif release == '1m':
        import dump_transient_runcat_v1
        from dump_transient_runcat_v1 import dump_trans
        dump_trans(database,dataset_id)
    elif release == '1p':
        import dump_transient_runcat_v1_postgres
        from dump_transient_runcat_v1_postgres import dump_trans
        dump_trans(database,dataset_id)
    else:
        print 'ERROR in release number'
        exit()

def get_lcs(sources):
    runcat=0
    ### Reading the lightcurves of each individual source in the dataset
    new_source={}
    frequencies=[]
    for a in range(len(sources)):
        new_runcat=sources[a][6]
        new_freq=int((float(sources[a][5])/1e6)+0.5)
        if new_runcat != runcat:
            runcat=new_runcat
            new_source[runcat]=[sources[a]]
        else:
            new_source[runcat]=new_source[runcat]+[sources[a]]
        if new_freq not in frequencies:
            frequencies.append(new_freq)
    return new_source, frequencies

def get_fluxes(data, freq):
    flux=[]
    band=[]
    for b in range(len(data)):
        if int((float(data[b][5])/1e6)+0.5)==freq:
            flux.append(float(data[b][3]))
            band.append(data[b][11])
    return flux, band

def collate_data(transients, keys, flux, avg_flux_ratio, dataset_id, num_data_pts, trans_data,band):
    ### Collate and store the transient parameters (these are across all the pipeline runs for the final figures)
    for n in range(len(transients)):
        if keys == transients[n][5] and transients[n][9] in band:
            trans_data.append([transients[n][4], float(transients[n][3]), float(transients[n][10]), max(flux), max(avg_flux_ratio), num_data_pts])
    return trans_data

def sigmoid(z):
    g = 1/(1+np.exp(-z))
    return g

def classify_data(trans_data,theta):
    trans_data=np.array(trans_data)
    theta=np.matrix(theta)
    X=np.matrix([[float(trans_data[a,1]),float(trans_data[a,2]),float(trans_data[a,3]), float(trans_data[a,4])] for a in range(len(trans_data))])
    print X
    X=np.log10(X)
    m=len(X)
    X = np.c_[np.ones(m), X]
    predictions=sigmoid(X * theta.T)
    transient=[]
    non_transient=[]
    for a in range(len(predictions)):
        if predictions[a] > 0.5:
            transient.append(trans_data[a][0])
        else:
            non_transient.append(trans_data[a][0])
    return transient, non_transient
