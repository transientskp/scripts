import train_anomaly_detect
import train_logistic_regression
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

trans_data=generic_tools.extract_data('stable_trans_data.txt')
stable_data = generic_tools.label_data(trans_data,'stable',0)
files = glob.glob('sim_*_trans_data.txt')
trans_data=[]
for filename in files:
    sim_name = filename.split('m_')[1].split('_trans_data')[0]
    trans_data_tmp=generic_tools.extract_data('sim_'+sim_name+'_trans_data.txt')
    trans_data = trans_data + generic_tools.label_data(trans_data_tmp,sim_name,1)
full_data=stable_data+trans_data
variables = [x for x in full_data if x[10]=='2']

# Sort data into transient and non-transient
variable = [x for x in variables if float(x[-1]) != 0.  if float(x[1]) > 0. if float(x[3]) > 0.]
stable = [x for x in variables if float(x[-1]) == 0. if float(x[1]) > 0. if float(x[3]) > 0.]

if anomaly:
######### ANOMALY DETECTION ##########

    # train the anomaly detection algorithm by conducting multiple trials.
    if not os.path.exists('sigma_data.txt'):
        filename = open("sigma_data.txt", "w")
        filename.write('')
        filename.close()
        train_anomaly_detect.multiple_trials([[float(x[1]), float(x[3]), float(x[-1])]for x in variables])
    data2=np.genfromtxt('sigma_data.txt', delimiter=' ')
    data=[[np.log10(float(variables[n][1])),np.log10(float(variables[n][3])),variables[n][6],float(variables[n][-1])] for n in range(len(variables)) if float(variables[n][1]) > 0 if float(variables[n][3]) > 0]
    best_sigma1, best_sigma2 = train_anomaly_detect.find_best_sigmas(precis_thresh,recall_thresh,data2,tests,data)
    print 'sigma_(eta_nu)='+str(best_sigma1)+', sigma_(V_nu)='+str(best_sigma2)    
    
    # Find the thresholds for a given sigma (in log space)
    sigcutx,paramx,range_x = generic_tools.get_sigcut([a[0] for a in data if a[3]==0.],best_sigma1)
    sigcuty,paramy,range_y = generic_tools.get_sigcut([a[1] for a in data if a[3]==0.],best_sigma2)
    print 'Eta_nu threshold='+str(10.**sigcutx)+', V_nu threshold='+str(10.**sigcuty)

    # Get the different frequencies in the dataset
    frequencies = generic_tools.get_frequencies(data)
    
    # Create the scatter_hist plot
    plotting_tools.create_scatter_hist(data,sigcutx,sigcuty,paramx,paramy,range_x,range_y,'',frequencies)
    
    # make second array for the diagnostic plot: [eta_nu, V_nu, maxflx_nu, flxrat_nu, nu]
    data2=[[float(variables[n][1]),float(variables[n][3]),float(variables[n][4]),float(variables[n][5]),variables[n][6]] for n in range(len(variables)) if float(variables[n][1]) > 0 if float(variables[n][3]) > 0] 
    
    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data2,sigcutx,sigcuty,frequencies,'')

    # Setup data to make TP/FP/TN/FN plots
    # Create arrays containing the data to plot
    fp=[[np.log10(float(z[1])),np.log10(float(z[3])),'FP'] for z in stable if (float(z[1])>=10.**sigcutx and float(z[3])>=10.**sigcuty)] # False Positive
    tn=[[np.log10(float(z[1])),np.log10(float(z[3])),'TN'] for z in stable if (float(z[1])<10.**sigcutx or float(z[3])<10.**sigcuty)] # True Negative
    tp=[[np.log10(float(z[1])),np.log10(float(z[3])),'TP'] for z in variable if (float(z[1])>=10.**sigcutx and float(z[3])>=10.**sigcuty)] # True Positive
    fn=[[np.log10(float(z[1])),np.log10(float(z[3])),'FN'] for z in variable if (float(z[1])<10.**sigcutx or float(z[3])<10.**sigcuty)] # False Negative
    data3=fp+tn+tp+fn

    # Print out the actual precision and recall using the training data.
    precision, recall =  generic_tools.precision_and_recall(len(tp),len(fp),len(fn))
    print "Precision: "+str(precision)+", Recall: "+str(recall)

    # Get the different frequencies in the dataset
    frequencies = generic_tools.get_frequencies(data3)

    # Create the scatter_hist plot
    plotting_tools.create_scatter_hist(data3,sigcutx,sigcuty,paramx,paramy,range_x,range_y,'_ADresults',frequencies)
    
    # Create arrays containing the data to plot
    fp=[[float(z[1]),float(z[3]),float(z[4]),float(z[5]),'FP'] for z in stable if (float(z[1])>=10.**sigcutx and float(z[3])>=10.**sigcuty)] # False Positive
    tn=[[float(z[1]),float(z[3]),float(z[4]),float(z[5]),'TN'] for z in stable if (float(z[1])<10.**sigcutx or float(z[3])<10.**sigcuty)] # True Negative
    tp=[[float(z[1]),float(z[3]),float(z[4]),float(z[5]),'TP'] for z in variable if (float(z[1])>=10.**sigcutx and float(z[3])>=10.**sigcuty)] # True Positive
    fn=[[float(z[1]),float(z[3]),float(z[4]),float(z[5]),'FN'] for z in variable if (float(z[1])<10.**sigcutx or float(z[3])<10.**sigcuty)] # False Negative
    data4=fp+tn+tp+fn

    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data4,sigcutx,sigcuty,frequencies,'_ADresults')

    print "candidate transients:"
    for line in fp:
        print line
    
if logistic:
###### LOGISTIC REGRESSION #######

    # make data array for the algorithm: [eta_nu, V_nu, maxflx_nu, flxrat_nu, label]
    # Note you can add in multiple parameters before the "label" column and the code should still work fine. (log of flxrat removed...)
    data=np.matrix([[np.log10(float(variables[n][1])),np.log10(float(variables[n][3])),np.log10(float(variables[n][4])),float(variables[n][5]),float(variables[n][-1])] for n in range(len(variables)) if float(variables[n][1]) > 0 if float(variables[n][3]) > 0])

    # setting the options for the scipy optimise function
    options = {'full_output': True, 'maxiter': 5000, 'ftol': 1e-4, 'maxfun': 5000, 'disp': True}

    # shuffle up the transient and stable data
    shuffled = np.matrix(train_logistic_regression.shuffle_datasets(data))
    # sort the data into a training, validation and testing dataset. This is hardcoded to be 60%, 30% and 10% (respectively) of the total dataset
    train, valid, test = train_logistic_regression.create_datasets(shuffled, len(shuffled)*0.6, len(shuffled)*0.9)

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
            shuffled = np.matrix(train_logistic_regression.shuffle_datasets(data))
            train, valid, test = train_logistic_regression.create_datasets(shuffled, len(shuffled)*0.6, len(shuffled)*0.9)
            Xtrain, ytrain = train_logistic_regression.create_X_y_arrays(train)
            Xvalid, yvalid = train_logistic_regression.create_X_y_arrays(valid)
            initial_theta=np.zeros((Xtrain.shape[1]))
            theta, cost, _, _, _ = optimize.fmin(lambda t: train_logistic_regression.reg_cost_func(t,Xtrain,ytrain.T,lda), initial_theta, **options)
            error_train.append(train_logistic_regression.check_error(Xtrain,ytrain,theta))
            error_valid.append(train_logistic_regression.check_error(Xvalid,yvalid,theta))
        train_logistic_regression.plotLC(range(len(error_train)), error_train, error_valid, "repeat", False, True, "Trial number")

    # classify the full dataset and check results
    print "Classifying full dataset"
    X, y = train_logistic_regression.create_X_y_arrays(shuffled)
    initial_theta=np.zeros((X.shape[1]))
    theta, cost, _, _, _ = optimize.fmin(lambda t: train_logistic_regression.reg_cost_func(t,X,y.T,lda), initial_theta, **options)
    tp, fp, fn, tn, classified = train_logistic_regression.classify_data(X,y.T,theta)
    precision, recall = generic_tools.precision_and_recall(tp,fp,fn)
    print "Logistic Regression Model: "+str(theta)
    print "Precision: "+str(precision)+", Recall: "+str(recall)
    print "candidate transients:"
    for line in classified:
        if line[4]=="FP":
            print 10.**line[0], 10.**line[1], 10.**line[2], line[3], line[4]

    fp=[[float(z[0]),float(z[1]),'FP'] for z in classified if z[4]=="FP"] # False Positive
    tp=[[float(z[0]),float(z[1]),'TP'] for z in classified if z[4]=="TP"] # True Positive
    fn=[[float(z[0]),float(z[1]),'FN'] for z in classified if z[4]=="FN"] # False Negative
    tn=[[float(z[0]),float(z[1]),'TN'] for z in classified if z[4]=="TN"] # True Negative
    data5=fp+tn+tp+fn
    fp=[[10.**float(z[0]),10.**float(z[1]),10.**float(z[2]),float(z[3]),'FP'] for z in classified if z[4]=="FP"] # False Positive
    tp=[[10.**float(z[0]),10.**float(z[1]),10.**float(z[2]),float(z[3]),'TP'] for z in classified if z[4]=="TP"] # True Positive
    fn=[[10.**float(z[0]),10.**float(z[1]),10.**float(z[2]),float(z[3]),'FN'] for z in classified if z[4]=="FN"] # False Negative
    tn=[[10.**float(z[0]),10.**float(z[1]),10.**float(z[2]),float(z[3]),'TN'] for z in classified if z[4]=="TN"] # True Negative
    data6=fp+tn+tp+fn
    
    # Create the scatter_hist plot
    plotting_tools.create_scatter_hist(data5,0,0,paramx,paramy,range_x,range_y,'_LRresults',frequencies)
    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data6,0,0,frequencies,'_LRresults')

if transSrc:
    print('Transient Search Tests')
    possTrans = [x for x in full_data if x[10]=='0']
    candTrans = [x for x in full_data if x[10]=='1']
    frequencies = ["TN","TP","FN","FP"]
    fp=0
    tp=0
    fn=0
    for a in range(len(possTrans)):
        if possTrans[a][-1] == "0":
            possTrans[a].append('FP')
            fp=fp+1
        elif possTrans[a][-1] != "0":
            possTrans[a].append('TP')
            tp=tp+1
    precision, recall = generic_tools.precision_and_recall(tp,fp,fn)
    print "Possible Transients - Precision: "+str(precision)+", Recall: "+str(recall)
    data=[[np.log10(float(possTrans[n][1])),np.log10(float(possTrans[n][3])),possTrans[n][-1],float(possTrans[n][-2])] for n in range(len(possTrans)) if float(possTrans[n][1])>0. if float(possTrans[n][3])>0.]
    data2=[[float(possTrans[n][1]),float(possTrans[n][3]),float(possTrans[n][4]),float(possTrans[n][5]),possTrans[n][-1]] for n in range(len(possTrans))]
    sigcutx,paramx,range_x = generic_tools.get_sigcut([a[0] for a in data],0)
    sigcuty,paramy,range_y = generic_tools.get_sigcut([a[1] for a in data],0)
    # Create the scatter_hist plot
    plotting_tools.create_scatter_hist(data,0,0,paramx,paramy,range_x,range_y,'_possTransResults',frequencies)
    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data2,0,0,frequencies,'_possTransResults')

    fp=0
    tp=0
    fn=0
    for a in range(len(candTrans)):
        if candTrans[a][-1] == "0":
            candTrans[a].append('FP')
            fp=fp+1
        elif candTrans[a][-1] != "0":
            candTrans[a].append('TP')
            tp=tp+1
    for row in possTrans:
        if row[-1]=='TP':
            row[-1]='FN'
            fn=fn+1
            candTrans.append(row)
        if row[-1]=='FP':
            row[-1]='TN'
            candTrans.append(row)
    precision, recall = generic_tools.precision_and_recall(tp,fp,fn)
    print "Candidate Transients - Precision: "+str(precision)+", Recall: "+str(recall)
    data3=[[np.log10(float(candTrans[n][1])),np.log10(float(candTrans[n][3])),candTrans[n][-1],float(candTrans[n][-2])] for n in range(len(candTrans)) if float(candTrans[n][1])>0. if float(candTrans[n][3])>0.]
    data4=[[float(candTrans[n][1]),float(candTrans[n][3]),float(candTrans[n][4]),float(candTrans[n][5]),candTrans[n][-1]] for n in range(len(candTrans))]
    sigcutx,paramx,range_x = generic_tools.get_sigcut([a[0] for a in data3],0)
    sigcuty,paramy,range_y = generic_tools.get_sigcut([a[1] for a in data3],0)
    # Create the scatter_hist plot
    plotting_tools.create_scatter_hist(data3,0,0,paramx,paramy,range_x,range_y,'_candTransResults',frequencies)
    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data4,0,0,frequencies,'_candTransResults')

    print "Candidate Transients:"
    for row in candTrans:
        if row[-1]=="FP":
            print row


