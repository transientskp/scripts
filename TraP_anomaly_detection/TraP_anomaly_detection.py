#!/usr/bin/python
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import math
import sys
from scipy.stats import norm
import pylab
import tools
pylab.rcParams['legend.loc'] = 'best'

###################### INITIAL SETUP STEPS ######################

if len(sys.argv) != 5:
    print 'python TraP_source_overview.py <database> <dataset_id> <release> <sigma>'
    exit()
database = sys.argv[1]
dataset_id = str(sys.argv[2])
release = str(sys.argv[3])
sigma = float(sys.argv[4])

if release!='0' and release!='1m' and release!='1p':
    print 'This script is for either Cycle0 (0) or Release 1 MonetDB (1m) or Release 1 Postgres (1p) databases, please specify 0, 1m or 1p.'
    exit()


###################### DEFINE SUBROUTINES ######################


tools.dump_data(release,database,dataset_id)
transients=[]
data=open('ds_'+dataset_id+'_transients.csv','r')
for lines in data:
    lines=lines.rstrip()
    transients.append(lines.split(','))
data.close()
trans_data=[]
for n in range(len(transients)):
    trans_data.append([transients[n][4], float(transients[n][3]), float(transients[n][10])])
tools.detect_anomaly(trans_data,sigma)
