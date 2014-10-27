import train_anomaly_detect
import train_logistic_regression
import train_sigma_margin
import plotting_tools
import generic_tools
import glob
import sys
import numpy as np
from scipy import optimize
import os

if len(sys.argv) != 8:
    print 'python train_TraP.py <precision threshold> <recall threshold> <lda> <anomaly> <logistic> <trans> <tests>'
    exit()
precis_thresh = float(sys.argv[1])
recall_thresh = float(sys.argv[2])
lda=float(sys.argv[3])
if sys.argv[4] == 'T':
    anomaly=True
else:
    anomaly=False
if sys.argv[5] == 'T':
    logistic=True
else:
    logistic=False
if sys.argv[6] == 'T':
    transSrc=True
else:
    transSrc=False
if sys.argv[7] == 'T':
    tests=True
else:
    tests=False

# sort the transient/variable datasets and the stable datasets into the format required for training.
trans_data=generic_tools.extract_data('stable_trans_data.txt')
stable_data = generic_tools.label_data(trans_data,'stable',0)
files = glob.glob('sim_*_trans_data.txt')
trans_data=[]
for filename in files:
    sim_name = filename.split('m_')[1].split('_trans_data')[0]
    trans_data_tmp=generic_tools.extract_data('sim_'+sim_name+'_trans_data.txt')
    trans_data = trans_data + generic_tools.label_data(trans_data_tmp,sim_name,1)
full_data=stable_data+trans_data
variables = [x for x in full_data if x[-5]=='2']


# Sort data into transient and non-transient
variable = [[x[0],x[1],float(x[2])/1.6,x[3],x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12]] for x in variables if float(x[-1]) != 0.  if float(x[1]) > 0. if float(x[2]) > 0.]
stable = [x for x in variables if float(x[-1]) == 0. if float(x[1]) > 0. if float(x[2]) > 0.]

if anomaly:
######### ANOMALY DETECTION ##########

    # train the anomaly detection algorithm by conducting multiple trials.
    if not os.path.exists('sigma_data.txt'):
        filename = open("sigma_data.txt", "w")
        filename.write('')
        filename.close()
        train_anomaly_detect.multiple_trials([[np.log10(float(x[1])), np.log10(float(x[2])), float(x[-1])] for x in variables if float(x[1]) > 0 if float(x[2]) > 0])
    data2=np.genfromtxt('sigma_data.txt', delimiter=' ')
    data=[[np.log10(float(variables[n][1])),np.log10(float(variables[n][2])),variables[n][5],float(variables[n][-1])] for n in range(len(variables)) if float(variables[n][1]) > 0 if float(variables[n][2]) > 0]
    best_sigma1, best_sigma2 = train_anomaly_detect.find_best_sigmas(precis_thresh,recall_thresh,data2,tests,data)
    print 'sigma_(eta_nu)='+str(best_sigma1)+', sigma_(V_nu)='+str(best_sigma2)    
    
    # Find the thresholds for a given sigma (in log space)
    sigcutx,paramx,range_x = generic_tools.get_sigcut([a[0] for a in data if a[3]==0.],best_sigma1)
    sigcuty,paramy,range_y = generic_tools.get_sigcut([a[1] for a in data if a[3]==0.],best_sigma2)
    print(r'Gaussian Fit $\eta$: '+str(round(10.**paramx[0],2))+'(+'+str(round((10.**(paramx[0]+paramx[1])-10.**paramx[0]),2))+' '+str(round((10.**(paramx[0]-paramx[1])-10.**paramx[0]),2))+')')
    print(r'Gaussian Fit $V$: '+str(round(10.**paramy[0],2))+'(+'+str(round((10.**(paramy[0]+paramy[1])-10.**paramy[0]),2))+' '+str(round((10.**(paramy[0]-paramy[1])-10.**paramy[0]),2))+')')
    print 'Eta_nu threshold='+str(10.**sigcutx)+', V_nu threshold='+str(10.**sigcuty)

    data=[[variables[n][0],np.log10(float(variables[n][1])),np.log10(float(variables[n][2])),variables[n][5],float(variables[n][-1])] for n in range(len(variables)) if float(variables[n][1]) > 0 if float(variables[n][2]) > 0]
    
    # Get the different frequencies in the dataset
    frequencies = generic_tools.get_frequencies(data)
    
    # Create the scatter_hist plot
    plotting_tools.create_scatter_hist(data,0,0,paramx,paramy,range_x,range_y,'',frequencies)
    
    # make second array for the diagnostic plot: [eta_nu, V_nu, maxflx_nu, flxrat_nu, nu]
    data2=[[variables[n][0],float(variables[n][1]),float(variables[n][2]),float(variables[n][3]),float(variables[n][4]),variables[n][5]] for n in range(len(variables)) if float(variables[n][1]) > 0 if float(variables[n][2]) > 0] 
    
    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data2,0,0,frequencies,'')

    # Setup data to make TP/FP/TN/FN plots
    # Create arrays containing the data to plot
    fp=[[z[0],np.log10(float(z[1])),np.log10(float(z[2])),'FP'] for z in stable if (float(z[1])>=10.**sigcutx and float(z[2])>=10.**sigcuty)] # False Positive
    tn=[[z[0],np.log10(float(z[1])),np.log10(float(z[2])),'TN'] for z in stable if (float(z[1])<10.**sigcutx or float(z[2])<10.**sigcuty)] # True Negative
    tp=[[z[0],np.log10(float(z[1])),np.log10(float(z[2])),'TP'] for z in variable if (float(z[1])>=10.**sigcutx and float(z[2])>=10.**sigcuty)] # True Positive
    fn=[[z[0],np.log10(float(z[1])),np.log10(float(z[2])),'FN'] for z in variable if (float(z[1])<10.**sigcutx or float(z[2])<10.**sigcuty)] # False Negative
    data3=fp+tn+tp+fn

    # Print out the actual precision and recall using the training data.
    precision, recall =  generic_tools.precision_and_recall(len(tp),len(fp),len(fn))
    print "Precision: "+str(precision)+", Recall: "+str(recall)

    # Get the different frequencies in the dataset
    frequencies = generic_tools.get_frequencies(data3)

    # Create the scatter_hist plot
    plotting_tools.create_scatter_hist(data3,sigcutx,sigcuty,paramx,paramy,range_x,range_y,'_ADresults',frequencies)
    
    # Create arrays containing the data to plot
    fp=[[z[0],float(z[1]),float(z[2]),float(z[3]),float(z[4]),'FP'] for z in stable if (float(z[1])>=10.**sigcutx and float(z[2])>=10.**sigcuty)] # False Positive
    tn=[[z[0],float(z[1]),float(z[2]),float(z[3]),float(z[4]),'TN'] for z in stable if (float(z[1])<10.**sigcutx or float(z[2])<10.**sigcuty)] # True Negative
    tp=[[z[0],float(z[1]),float(z[2]),float(z[3]),float(z[4]),'TP'] for z in variable if (float(z[1])>=10.**sigcutx and float(z[2])>=10.**sigcuty)] # True Positive
    fn=[[z[0],float(z[1]),float(z[2]),float(z[3]),float(z[4]),'FN'] for z in variable if (float(z[1])<10.**sigcutx or float(z[2])<10.**sigcuty)] # False Negative
    data4=fp+tn+tp+fn

    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data4,sigcutx,sigcuty,frequencies,'_ADresults')

    
    # sorting the candidate variables into a tidy format for outputting on screen and in a text file
    fpTMP={}
    for row in fp:
        if row[0] not in fpTMP.keys():
            fpTMP[row[0]]=row
        else:
            if float(fpTMP[row[0]][1])>float(row[1]):
                fpTMP[row[0]]=row
    fp=[fpTMP[x] for x in fpTMP.keys()]

    output = open('AD_candidate_variables.txt','w')
    output.write('#Runcat_id, eta_nu, V_nu \n')
    print "Unique candidate variables:"
    print 'RuncatID, eta, V'
    for line in fp:
        print line[0], line[1], line[2]
        output.write(str(line[0])+','+str(line[1])+','+str(line[2])+'\n')
    output.close()

            
if logistic:
###### LOGISTIC REGRESSION #######

    # make data array for the algorithm: [eta_nu, V_nu, maxflx_nu, flxrat_nu, label]
    # Note you can add in multiple parameters before the "label" column and the code should still work fine.
    data=np.matrix([[float(variables[n][0]),np.log10(float(variables[n][1])),np.log10(float(variables[n][2])),np.log10(float(variables[n][3])),float(variables[n][4]),float(variables[n][-1])] for n in range(len(variables)) if float(variables[n][1]) > 0 if float(variables[n][2]) > 0])

    # setting the options for the scipy optimise function
    options = {'full_output': True, 'maxiter': 5000, 'ftol': 1e-4, 'maxfun': 5000, 'disp': True}

    # shuffle up the transient and stable data
    shuffled = np.matrix(train_logistic_regression.shuffle_datasets(data))
    shuffledTMP=shuffled[:,1:]

    # sort the data into a training, validation and testing dataset. This is hardcoded to be 60%, 30% and 10% (respectively) of the total dataset
    train, valid, test = train_logistic_regression.create_datasets(shuffledTMP, len(shuffledTMP)*0.6, len(shuffledTMP)*0.9)

    # separate arrays into data and labels (as required for tools)
    Xtrain, ytrain = train_logistic_regression.create_X_y_arrays(train)
    Xvalid, yvalid = train_logistic_regression.create_X_y_arrays(valid)
    Xtest, ytest = train_logistic_regression.create_X_y_arrays(test)

    # Conduct tests to ensure that the machine learning algorithm is working effectively
    if tests:
        # plot the learning curve to check that it is converging to a solution as you increase the size of the training dataset (Optional but recommended). Basically, it repeatedly trains using 1 datapoint, 2, 3, 4, ... upto the full training dataset size. If the training and validation errors converge, then all is well.
        print "Creating learning curve"
        error_train, error_valid, theta = train_logistic_regression.learning_curve(Xtrain, ytrain.T, Xvalid, yvalid.T, lda, options)
        train_logistic_regression.plotLC(range(len(error_train)),error_train, error_valid, "learning", True, True, "Number")

        # check that the lambda (lda) parameter chosen is appropriate for your dataset (Optional but recommended). This parameter controls the 'weighting' given to the different parameters in the model. If the learning curve converges quickly and the validation curve is relatively flat, you are ok having a small lambda value such as 1e-4.
        print "Creating validation curve"
        error_train, error_valid, lambda_vec, lda = train_logistic_regression.validation_curve(Xtrain, ytrain.T, Xvalid, yvalid.T, options)
        train_logistic_regression.plotLC(lambda_vec, error_train, error_valid, "validation", True, True, r"$\lambda$")

        # check that the results are not dependent upon the subsample of the dataset chosen to train the algorithm by repeating the training a large number of times and checking that the training and validation errors are roughly constant (Optional but recommended).
        print "Creating repeat curve"
        error_train=[]
        error_valid=[]
        for counter in range(1000):
            # shuffle up the transient and stable data
            shuffled = np.matrix(train_logistic_regression.shuffle_datasets(data))
            shuffledTMP=shuffled[:,1:]
            # sort the data into a training, validation and testing dataset. This is hardcoded to be 60%, 30% and 10% (respectively) of the total dataset
            train, valid, test = train_logistic_regression.create_datasets(shuffledTMP, len(shuffledTMP)*0.6, len(shuffledTMP)*0.9)
            Xtrain, ytrain = train_logistic_regression.create_X_y_arrays(train)
            Xvalid, yvalid = train_logistic_regression.create_X_y_arrays(valid)
            initial_theta=np.zeros((Xtrain.shape[1]))
            theta, cost, _, _, _ = optimize.fmin(lambda t: train_logistic_regression.reg_cost_func(t,Xtrain,ytrain.T,lda), initial_theta, **options)
            error_train.append(train_logistic_regression.check_error(Xtrain,ytrain.T,theta))
            error_valid.append(train_logistic_regression.check_error(Xvalid,yvalid.T,theta))
        train_logistic_regression.plotLC(range(len(error_train)), error_train, error_valid, "repeat", False, True, "Trial number")

    # classify the full dataset and check results
    print "Classifying full dataset"
    shuffled = np.matrix(train_logistic_regression.shuffle_datasets(data))
    shuffledTMP=shuffled[:,1:]
    ids=shuffled[:,0]
    X, y = train_logistic_regression.create_X_y_arrays(np.matrix(np.array(shuffledTMP)))
    initial_theta=np.zeros((X.shape[1]))
    theta, cost, _, _, _ = optimize.fmin(lambda t: train_logistic_regression.reg_cost_func(t,X,y.T,lda), initial_theta, **options)
    tp, fp, fn, tn, classified = train_logistic_regression.classify_data(X,y.T,theta)
    classified=np.array(np.c_[ids,classified])
    precision, recall = generic_tools.precision_and_recall(tp,fp,fn)
    print "Logistic Regression Model: "+str(theta)
    print "Precision: "+str(precision)+", Recall: "+str(recall)

    # sorting the candidate variables into a tidy format for outputting on screen and in a text file
    output = open('LR_candidate_variables.txt','w')
    output.write('#Runcat_id, eta_nu, V_nu \n')
    print "candidate variables:"
    print 'RuncatID, eta, V'
    for line in classified:
        if line[5]==2:
            print int(line[0]), 10.**(float(line[1])), 10.**(float(line[2]))
            output.write(str(int(line[0]))+','+str(10.**(float(line[1])))+','+str(10.**(float(line[2])))+'\n')
    output.close()

    fp=[[z[0],float(z[1]),float(z[2]),'FP'] for z in classified if z[5]==2] # False Positive
    tp=[[z[0],float(z[1]),float(z[2]),'TP'] for z in classified if z[5]==1] # True Positive
    fn=[[z[0],float(z[1]),float(z[2]),'FN'] for z in classified if z[5]==3] # False Negative
    tn=[[z[0],float(z[1]),float(z[2]),'TN'] for z in classified if z[5]==4] # True Negative
    data5=fp+tn+tp+fn
    fp=[[z[0],10.**float(z[1]),10.**float(z[2]),10.**float(z[3]),float(z[4]),'FP'] for z in classified if z[5]==2] # False Positive
    tp=[[z[0],10.**float(z[1]),10.**float(z[2]),10.**float(z[3]),float(z[4]),'TP'] for z in classified if z[5]==1] # True Positive
    fn=[[z[0],10.**float(z[1]),10.**float(z[2]),10.**float(z[3]),float(z[4]),'FN'] for z in classified if z[5]==3] # False Negative
    tn=[[z[0],10.**float(z[1]),10.**float(z[2]),10.**float(z[3]),float(z[4]),'TN'] for z in classified if z[5]==4] # True Negative
    data6=fp+tn+tp+fn

    # Get the different frequencies in the dataset
    frequencies = generic_tools.get_frequencies(data5)

    sigcutx,paramx,range_x = generic_tools.get_sigcut([a[1] for a in data5 if (a[3]=='FP' or a[3]=='TN')],0)
    sigcuty,paramy,range_y = generic_tools.get_sigcut([a[2] for a in data5 if (a[3]=='FP' or a[3]=='TN')],0)
    
    # Create the scatter_hist plot
    plotting_tools.create_scatter_hist(data5,0,0,paramx,paramy,range_x,range_y,'_LRresults',frequencies)
    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data6,0,0,frequencies,'_LRresults')

if transSrc:
    ######### Search for the optimal sigma margin for transients #########
    
    print('Transient Search Tests')

    # Extract out the possible and candidate transient sources
    possTransData = [x for x in full_data if x[-5]!='2' if x[-1]=='0']
    possTransSims = [x for x in full_data if x[-5]!='2' if x[-1]=='1']
    
    # Sort out the sigma data for plotting and training
    best_data,worst_data,detection_threshold = train_sigma_margin.sort_data(possTransData)
    best_sim,worst_sim,detection_threshold = train_sigma_margin.sort_data(possTransSims)
   
    # Plot histograms to illustrate the distributions
    train_sigma_margin.plot_hist(best_data,best_sim,detection_threshold,'minimum')
    train_sigma_margin.plot_hist(worst_data,worst_sim,detection_threshold,'maximum')

    # Search and identify the optimal sigma margin for the best and worst parts of the image
    best_plot_data, worst_plot_data = train_sigma_margin.find_sigma_margin(best_data, worst_data, best_sim, worst_sim, detection_threshold)
    sigWorst, sigBest = train_sigma_margin.plot_diagnostic(best_plot_data,worst_plot_data)

    # Identify the ids of interesting transient candidates
    print 'Candidate transients (using threshold trained from best region of best image):'
    print np.sort(list(set([a[0] for a in possTransData if float(a[-3])>(sigBest+detection_threshold)])))
    print 'Candidate transients (using threshold trained from worst region of best image):'
    print np.sort(list(set([a[0] for a in possTransData if float(a[-4])>(sigWorst+detection_threshold)])))

exit()
