#!/usr/bin/python
import datetime
from datetime import datetime
import time
import os
import sys

###################### INITIAL SETUP STEPS ######################

database='cycle0'
dataset_id='42'
average_image_RMS=0.031
average_image_RMS_scatter=0.010
detection_threshold=8

if len(sys.argv) != 7:
    print 'python TraP_sort_transinets.py <database> <dataset_id> <release> <detection_threshold> <img_RMS> <img_RMS_scatter>'
    exit()
database = sys.argv[1]
dataset_id = str(sys.argv[2])
release = str(sys.argv[3])
detection_threshold = float(sys.argv[4])
average_image_RMS = float(sys.argv[5])
average_image_RMS_scatter = float(sys.argv[6])

if release!='0' and release!='1m' and release!='1p':
    print 'This script is for either Cycle0 (0) or Release 1 MonetDB (1m) or Release 1 Postgres (1p) databases, please specify 0, 1m or 1p.'
    exit()


###################### MAIN CODE ######################

outname=database+'_'+str(dataset_id)+'_'

transient_detection_flux_limit=(average_image_RMS+average_image_RMS_scatter)*detection_threshold
print 'Transient flux detection limit (Jy) = '+str(transient_detection_flux_limit)
trans_data=[]
trans_data2=[]

### Getting the data from the Database
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

### Reading in the data from the output files of above script
transients=[]
data=open('ds_'+dataset_id+'_transients.csv','r')
for lines in data:
    lines=lines.rstrip()
    transients.append(lines.split(','))
data.close()
sources=[]
data=open('ds_'+dataset_id+'_sources.csv','r')
for lines in data:
    lines=lines.rstrip()
    sources.append(lines.split(','))
data.close()
runcat=0

### Reading the lightcurves of each individual source in the dataset
new_source={}
frequencies=[]
for a in range(len(sources)):
    new_runcat=sources[a][6]
    freq= sources[a][5]
    if freq not in frequencies:
        frequencies.append(freq)
    if new_runcat != runcat:
        runcat=new_runcat
        new_source[runcat]=[sources[a]]
    else:
        new_source[runcat]=new_source[runcat]+[sources[a]]
avg_flux={}
count1=0
count2=0
count3=0
keylog2=[]
for freq in frequencies:
    keylog=[]
    for keys in new_source.keys():
        flux=[]
        flux_err=[]
        date=[]
        for b in range(len(new_source[keys])):
            if new_source[keys][b][5] == freq:
                flux.append(float(new_source[keys][b][3]))
                flux_err.append(float(new_source[keys][b][4]))
                date.append(datetime.strptime(new_source[keys][b][8],  '%Y-%m-%d %H:%M:%S'))
                oldest=min(date)
                time_diff=[]
        if len(flux)>0:
            for c in range(len(date)):
                time1=time.mktime(date[c].timetuple())
                time2=time.mktime(oldest.timetuple())
                time3=(time1-time2)
                time_diff.append(time3)
            avg_flux_ratio = [x / (sum(flux)/len(flux)) for x in flux]
            avg_flux = (sum(flux)/len(flux))
            for n in range(len(transients)):
                if keys == transients[n][5]:
                    if keys not in keylog:
                        keylog.append(transients[n][5])
                        count1=count1+1
                        if avg_flux > transient_detection_flux_limit:
                            trans_data.append([keys, int(transients[n][4]), freq, float(transients[n][3]), float(transients[n][6]), float(transients[n][10]), max(flux),  max(avg_flux_ratio), avg_flux])
                            count2=count2+1
                            if keys not in keylog2:
                                keylog2.append(transients[n][5])
                                trans_data2.append([keys, int(transients[n][4]), freq, float(transients[n][3]), float(transients[n][6]), float(transients[n][10]), max(flux),  max(avg_flux_ratio), avg_flux])
                                count3=count3+1
                        

print 'Original number of transients = '+str(count1)
print 'New number of transients = '+str(count2)
print 'Unique number of transients = '+str(count3)


###################### WRITE OUT TRANSIENT DATA TO FILE ######################

trans_data = sorted(trans_data, key=lambda data: float(data[0]))
output2 = open(outname+'sorted_data.txt','w')
output2.write('#Runcat_id,Trans_id,freq,eta_nu,signif,V_nu,pk_flx,flx_rat, avg_flx \n')
for x in range(len(trans_data)):
    string='%s' % ', '.join(str(val) for val in trans_data[x])
    output2.write(string+'\n')
output2.close()
trans_data2 = sorted(trans_data2, key=lambda data: float(data[0]))
output2 = open(outname+'unique_sources.txt','w')
output2.write('#Runcat_id,Trans_id,freq,eta_nu,signif,V_nu,pk_flx,flx_rat, avg_flx \n')
for x in range(len(trans_data2)):
    string='%s' % ', '.join(str(val) for val in trans_data2[x])
    output2.write(string+'\n')
output2.close()

print('Completed successfully :-)')
print('Your new transient list is here: '+outname+'sorted_data.txt')
