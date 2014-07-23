import format_TraP_data
import plotting_tools
import generic_tools
import numpy as np
import sys

# Obtain input parameters from the command line
if len(sys.argv) != 8:
    print 'python process_TraP.py <database> <dataset_id> <release> <host> <port> <sigma1> <sigma2>'
    exit()
database = sys.argv[1]
dataset_id = str(sys.argv[2])
release = str(sys.argv[3])
host = str(sys.argv[4])
port = int(sys.argv[5])
sigma1 = float(sys.argv[6])
sigma2 = float(sys.argv[7])

# get TraP data from the database and sort it into the required array which is then loaded
format_TraP_data.format_data(database,dataset_id,release,host,port)
trans_data=generic_tools.extract_data('ds'+str(dataset_id)+'_trans_data.txt')

# make first array for the scatter_hist plot: [log10(eta_nu), log10(V_nu), nu]
data=[[np.log10(float(trans_data[n][1])),np.log10(float(trans_data[n][3])),trans_data[n][6]] for n in range(len(trans_data)) if float(trans_data[n][1]) > 0 if float(trans_data[n][3]) > 0]

# Find the thresholds for a given sigma (in log space)
sigcutx,paramx,range_x = generic_tools.get_sigcut([a[0] for a in data],sigma1)
sigcuty,paramy,range_y = generic_tools.get_sigcut([a[1] for a in data],sigma2)

# Get the different frequencies in the dataset
frequencies = generic_tools.get_frequencies(data)

# Create the scatter_hist plot
plotting_tools.create_scatter_hist(data,sigcutx,sigcuty,paramx,paramy,range_x,range_y,dataset_id,frequencies)

# make second array for the diagnostic plot: [eta_nu, V_nu, maxflx_nu, flxrat_nu, nu, trans_type]
data2=[[float(trans_data[n][1]),float(trans_data[n][3]),float(trans_data[n][4]),float(trans_data[n][5]),trans_data[n][6], trans_data[n][-1]] for n in range(len(trans_data)) if float(trans_data[n][1]) > 0 if float(trans_data[n][3]) > 0] 

# Create the diagnostic plot
plotting_tools.create_diagnostic(data2,sigcutx,sigcuty,frequencies,dataset_id)
