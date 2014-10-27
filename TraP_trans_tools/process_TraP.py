import format_TraP_data
import plotting_tools
import generic_tools
import numpy as np
import sys
import os

# Obtain input parameters from the command line
if len(sys.argv) != 11:
    print 'python process_TraP.py <database> <username> <password> <dataset_id> <release> <host> <port> <sigma1> <sigma2> <lightcurves>'
    exit()
database = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
dataset_id = str(sys.argv[4])
release = str(sys.argv[5])
host = str(sys.argv[6])
port = int(sys.argv[7])
sigma1 = float(sys.argv[8])
sigma2 = float(sys.argv[9])
lightcurves = sys.argv[10]

# get TraP data from the database and sort it into the required array which is then loaded
if not os.path.isfile('ds'+str(dataset_id)+'_trans_data.txt'):
    format_TraP_data.format_data(database,dataset_id,release,host,port,username,password,lightcurves)
trans_data=generic_tools.extract_data('ds'+str(dataset_id)+'_trans_data.txt')
# make first array for the scatter_hist plot: [log10(eta_nu), log10(V_nu), nu]
data=[[trans_data[n][0],np.log10(float(trans_data[n][1])),np.log10(float(trans_data[n][2])),trans_data[n][5], trans_data[n][-1]] for n in range(len(trans_data)) if float(trans_data[n][1]) > 0 if float(trans_data[n][2]) > 0 if trans_data[n][-4]=='2']

# print out the transients that TraP automatically found
print 'Identified Transient Candidates (no margin)'
print np.sort(list(set([int(x[0]) for x in trans_data if x[-4]!='2' if float(x[-2])>=float(x[-1]) if float(x[-3])<float(x[-1])])))
print 'Identified Transients (no margin)'
print np.sort(list(set([int(x[0]) for x in trans_data if x[-4]!='2' if float(x[-3])>=float(x[-1])])))

# Find the thresholds for a given sigma (in log space)
sigcutx,paramx,range_x = generic_tools.get_sigcut([a[1] for a in data],sigma1)
sigcuty,paramy,range_y = generic_tools.get_sigcut([a[2] for a in data],sigma2)
if sigma1 == 0:
    sigcutx=0
if sigma2 == 0:
    sigcuty=0
print(r'Gaussian Fit $\eta$: '+str(round(10.**paramx[0],2))+'(+'+str(round((10.**(paramx[0]+paramx[1])-10.**paramx[0]),2))+' '+str(round((10.**(paramx[0]-paramx[1])-10.**paramx[0]),2))+')')
print(r'Gaussian Fit $V$: '+str(round(10.**paramy[0],2))+'(+'+str(round((10.**(paramy[0]+paramy[1])-10.**paramy[0]),2))+' '+str(round((10.**(paramy[0]-paramy[1])-10.**paramy[0]),2))+')')
print 'Eta_nu threshold='+str(10.**sigcutx)+', V_nu threshold='+str(10.**sigcuty)

# Get the different frequencies in the dataset
frequencies = generic_tools.get_frequencies(data)

# Create the scatter_hist plot
IdTrans = plotting_tools.create_scatter_hist(data,sigcutx,sigcuty,paramx,paramy,range_x,range_y,dataset_id,frequencies)

print 'Identified variables:'
print np.sort(list(set(IdTrans)))

# make second array for the diagnostic plot: [eta_nu, V_nu, maxflx_nu, flxrat_nu, nu, trans_type]
data2=[[trans_data[n][0],float(trans_data[n][1]),float(trans_data[n][2]),float(trans_data[n][3]),float(trans_data[n][4]),trans_data[n][5], trans_data[n][-1]] for n in range(len(trans_data)) if float(trans_data[n][1]) > 0 if float(trans_data[n][2]) > 0 if trans_data[n][-4]=='2'] 

# Create the diagnostic plot
plotting_tools.create_diagnostic(data2,sigcutx,sigcuty,frequencies,dataset_id)
