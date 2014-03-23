import train_anomaly_detect
#import train_logistic_regression
import plotting_tools
import generic_tools
import glob
import sys
import numpy as np

if len(sys.argv) != 3:
    print 'python process_LOFAR.py <precision threshold> <recall threshold>'
    exit()
precis_thresh = float(sys.argv[1])
recall_thresh = float(sys.argv[2])

trans_data=generic_tools.extract_data('stable_trans_data.txt')
trans_data=[[x[1],x[3],x[4],x[5],x[7],x[6]] for x in trans_data]
stable_data = train_anomaly_detect.label_data(trans_data,'stable',0)
files = glob.glob('sim_*_trans_data.txt')
trans_data=[]
for filename in files:
    sim_name = filename.split('_')[1]
    trans_data_tmp=generic_tools.extract_data('sim_'+sim_name+'_trans_data.txt')
    trans_runcat=np.genfromtxt('sim_'+sim_name+'_trans_runcat.txt', delimiter=', ')
    trans_data_tmp=[x for x in trans_data_tmp if float(x[0]) in trans_runcat]
    trans_data_tmp=[[x[1],x[3],x[4],x[6],x[8],x[7]] for x in trans_data_tmp]
    trans_data = trans_data + train_anomaly_detect.label_data(trans_data_tmp,sim_name,1)
#
num_obs=max([float(x[4]) for x in trans_data])
#
trans_data=[x for x in trans_data if float(x[4]) == num_obs]
full_data=stable_data+trans_data


#train_anomaly_detect.multiple_trials(full_data)
data=np.genfromtxt('sigma_data.txt', delimiter=' ')
best_sigma1, best_sigma2 = train_anomaly_detect.find_best_sigmas(precis_thresh,recall_thresh,data)
print best_sigma1, best_sigma2

data=[[np.log10(float(full_data[n][0])),np.log10(float(full_data[n][1])),full_data[n][5]] for n in range(len(full_data)) if float(full_data[n][1]) > 0 if float(full_data[n][3]) > 0]

# Find the thresholds for a given sigma (in log space)
sigcutx,paramx,range_x = generic_tools.get_sigcut([a[0] for a in data],best_sigma1)
sigcuty,paramy,range_y = generic_tools.get_sigcut([a[1] for a in data],best_sigma2)

# Get the different frequencies in the dataset
frequencies = generic_tools.get_frequencies(data)

# Create the scatter_hist plot
plotting_tools.create_scatter_hist(data,sigcutx,sigcuty,paramx,paramy,range_x,range_y,'',frequencies)

# make second array for the diagnostic plot: [eta_nu, V_nu, maxflx_nu, flxrat_nu, nu]
data2=[[float(full_data[n][0]),float(full_data[n][1]),float(full_data[n][2]),float(full_data[n][3]),full_data[n][5]] for n in range(len(full_data)) if float(full_data[n][1]) > 0 if float(full_data[n][3]) > 0] 

# Create the diagnostic plot
plotting_tools.create_diagnostic(data2,sigcutx,sigcuty,frequencies,'')
