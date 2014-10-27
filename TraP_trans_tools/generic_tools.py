from scipy.stats import norm
import numpy as np

def extract_data(filename):
    # extract data in a csv file into a list
    info=[]
    data=open(filename,'r')
    for lines in data:
        if not lines.startswith("#"):
            lines=lines.rstrip().replace(" ", "")
            info.append(lines.split(','))
    data.close()
    return info

def get_frequencies(trans_data):
    # identify all the unique observing frequencies in the dataset
    frequencies=[]
    for lines in trans_data:
        if lines[3] not in frequencies:
            frequencies.append(lines[3])
    return frequencies

def get_sigcut(x,sigma):
    # identify the sigma cut for a given dataset fitted with a Gaussian distribuion
    param=norm.fit(x)
    range_x=np.linspace(min(x),max(x),1000)
    sigcut = param[1]*sigma+param[0]
    return sigcut,param,range_x # return the sigma cut, the Gaussian model and the range fitted over

def precision_and_recall(tp,fp,fn):
    # calculate the precision and recall values
    if tp==0:
        precision=0.
    else:
        precision=float(tp)/float(tp+fp)
    if tp==0:
        recall=0.
    else:
        recall=float(tp)/float(tp+fn)
    return precision, recall

def label_data(data,label1,label2):
    # Label different arrays so that their transient type is known, label1, and they have a transient (1) or non-transient (0), label2
    for x in data:
        x[5]=label1
    data=np.matrix(data)
    data=np.c_[data,[label2]*len(data)]
    return data.tolist()
