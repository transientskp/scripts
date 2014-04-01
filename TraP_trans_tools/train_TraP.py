import train_anomaly_detect
import train_logistic_regression
import plotting_tools
import generic_tools
import glob
import sys
import numpy as np
from scipy import optimize

if len(sys.argv) != 7:
    print 'python train_TraP.py <precision threshold> <recall threshold> <lda> <anomaly> <logistic> <tests>'
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
    tests=True
else:
    tests=False

trans_data=generic_tools.extract_data('stable_trans_data.txt')
trans_data=[[x[1],x[3],x[4],x[5],x[7],x[6]] for x in trans_data]
stable_data = generic_tools.label_data(trans_data,'stable',0)
files = glob.glob('sim_*_trans_data.txt')
trans_data=[]
for filename in files:
    sim_name = filename.split('_')[1]
    trans_data_tmp=generic_tools.extract_data('sim_'+sim_name+'_trans_data.txt')
    trans_runcat=np.genfromtxt('sim_'+sim_name+'_trans_runcat.txt', delimiter=', ')
    trans_data_tmp=[x for x in trans_data_tmp if float(x[0]) in trans_runcat]
    trans_data_tmp=[[x[1],x[3],x[4],x[6],x[8],x[7]] for x in trans_data_tmp]
    trans_data = trans_data + generic_tools.label_data(trans_data_tmp,sim_name,1)

# Remove all the "new sources" for training
num_obs=max([float(x[4]) for x in trans_data])
trans_data=[x for x in trans_data if float(x[4]) == num_obs]
full_data=stable_data+trans_data

if anomaly:
######### ANOMALY DETECTION ##########

    # train the anomaly detection algorithm by conducting multiple trials.
    filename = open("sigma_data.txt", "w")
    filename.write('')
    filename.close()
    train_anomaly_detect.multiple_trials(full_data)
    data2=np.genfromtxt('sigma_data.txt', delimiter=' ')

    best_sigma1, best_sigma2 = train_anomaly_detect.find_best_sigmas(precis_thresh,recall_thresh,data2,tests)
    print 'sigma_(eta_nu)='+str(best_sigma1)+', sigma_(V_nu)='+str(best_sigma2)
    data=[[np.log10(float(full_data[n][0])),np.log10(float(full_data[n][1])),full_data[n][5]] for n in range(len(full_data)) if float(full_data[n][1]) > 0 if float(full_data[n][3]) > 0]

    # Find the thresholds for a given sigma (in log space)
    sigcutx,paramx,range_x = generic_tools.get_sigcut([a[0] for a in data if a[2]=='stable'],best_sigma1)
    sigcuty,paramy,range_y = generic_tools.get_sigcut([a[1] for a in data if a[2]=='stable'],best_sigma2)
    print 'Eta_nu threshold='+str(10.**sigcutx)+', V_nu threshold='+str(10.**sigcuty)

    # Get the different frequencies in the dataset
    frequencies = generic_tools.get_frequencies(data)

    # Create the scatter_hist plot
    plotting_tools.create_scatter_hist(data,sigcutx,sigcuty,paramx,paramy,range_x,range_y,'',frequencies)
    
    # make second array for the diagnostic plot: [eta_nu, V_nu, maxflx_nu, flxrat_nu, nu]
    data2=[[float(full_data[n][0]),float(full_data[n][1]),float(full_data[n][2]),float(full_data[n][3]),full_data[n][5]] for n in range(len(full_data)) if float(full_data[n][1]) > 0 if float(full_data[n][3]) > 0] 

    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data2,sigcutx,sigcuty,frequencies,'')

    # Setup data to make TP/FP/TN/FN plots
    # Sort data into transient and non-transient
    variables = [x for x in full_data if float(x[6]) != 0.  if float(x[0]) > 0. if float(x[1]) > 0.]
    stable = [x for x in full_data if float(x[6]) == 0. if float(x[0]) > 0. if float(x[1]) > 0.]

    # Create arrays containing the data to plot
    fp=[[np.log10(float(z[0])),np.log10(float(z[1])),'FP'] for z in stable if (float(z[0])>10.**sigcutx and float(z[1])>10.**sigcuty)] # False Positive
    tn=[[np.log10(float(z[0])),np.log10(float(z[1])),'TN'] for z in stable if (float(z[0])<10.**sigcutx or float(z[1])<10.**sigcuty)] # True Negative
    tp=[[np.log10(float(z[0])),np.log10(float(z[1])),'TP'] for z in variables if (float(z[0])>10.**sigcutx and float(z[1])>10.**sigcuty)] # True Positive
    fn=[[np.log10(float(z[0])),np.log10(float(z[1])),'FN'] for z in variables if (float(z[0])<10.**sigcutx or float(z[1])<10.**sigcuty)] # False Negative
    data=fp+tn+tp+fn

    # Print out the actual precision and recall using the training data.
    print 'Precision and recall: '
    print generic_tools.precision_and_recall(len(tp),len(fp),len(fn))

    # Get the different frequencies in the dataset
    frequencies = generic_tools.get_frequencies(data)

    # Create the scatter_hist plot
    plotting_tools.create_scatter_hist(data,sigcutx,sigcuty,paramx,paramy,range_x,range_y,'results',frequencies)
    
    # Create arrays containing the data to plot
    fp=[[float(z[0]),float(z[1]),float(z[2]),float(z[3]),'FP'] for z in stable if (float(z[0])>10.**sigcutx and float(z[1])>10.**sigcuty)] # False Positive
    tn=[[float(z[0]),float(z[1]),float(z[2]),float(z[3]),'TN'] for z in stable if (float(z[0])<10.**sigcutx or float(z[1])<10.**sigcuty)] # True Negative
    tp=[[float(z[0]),float(z[1]),float(z[2]),float(z[3]),'TP'] for z in variables if (float(z[0])>10.**sigcutx and float(z[1])>10.**sigcuty)] # True Positive
    fn=[[float(z[0]),float(z[1]),float(z[2]),float(z[3]),'FN'] for z in variables if (float(z[0])<10.**sigcutx or float(z[1])<10.**sigcuty)] # False Negative
    data2=fp+tn+tp+fn

    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data2,sigcutx,sigcuty,frequencies,'_ADresults')


if logistic:
###### LOGISTIC REGRESSION #######

    # make data array for the algorithm: [eta_nu, V_nu, maxflx_nu, flxrat_nu, label]
    # Note you can add in multiple parameters before the "label" column and the code should still work fine. 
    data=np.matrix([[np.log10(float(full_data[n][0])),np.log10(float(full_data[n][1])),np.log10(float(full_data[n][2])),np.log10(float(full_data[n][3])),float(full_data[n][6])] for n in range(len(full_data)) if float(full_data[n][0]) > 0 if float(full_data[n][1]) > 0])

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
    print theta
    print precision, recall

    # Create the diagnostic plot
    plotting_tools.create_diagnostic(data2,sigcutx,sigcuty,frequencies,'_LRresults')
