#!/usr/bin/python
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
import tools
import time
if len(sys.argv) != 5:
    print 'python TraP_source_overview.py <database> <dataset_id> <release> <model>'
    exit()
database = sys.argv[1]
dataset_id = str(sys.argv[2])
release = str(sys.argv[3])
model = sys.argv[4]

if release!='0' and release!='1m' and release!='1p':
    print 'This script is for either Release 0 (0) or Release 1 MonetDB (1m) or Release 1 Postgres (1p) databases, please specify 0, 1m or 1p.'
    exit()

theta=np.genfromtxt(model,delimiter=',')
theta=[i for i in theta]

tools.dump_data(release,database,dataset_id)
transients=[]
sources=[]
trans_data=[]

data=open('ds_'+dataset_id+'_transients.csv','r')
for lines in data:
    lines=lines.rstrip()
    transients.append(lines.split(','))
data.close()
data=open('ds_'+dataset_id+'_sources.csv','r')
for lines in data:
    lines=lines.rstrip()
    sources.append(lines.split(','))
data.close()

print time.time()
source_lcs, frequencies =tools.get_lcs(sources)
print len(source_lcs)
bands={}

for freq in frequencies:
    for keys in source_lcs:
        flux,band=tools.get_fluxes(source_lcs[keys],freq)
        bands[freq]=band
        num_datapoints=len(flux)
        avg_flux_ratio = [x / (float(sum(flux))/float(len(flux))) for x in flux]
        trans_data = tools.collate_data(transients, keys, flux, avg_flux_ratio, dataset_id, num_datapoints, trans_data,bands[freq])

print len(trans_data)
classified_trans, classified_nontrans = tools.classify_data(trans_data, theta)
print time.time()
print 'Transients:'
print classified_trans
