from scipy.stats import norm
import numpy as np

def extract_data(filename):
    info=[]
    data=open(filename,'r')
    for lines in data:
        if not lines.startswith("#"):
            lines=lines.rstrip()
            info.append(lines.split(','))
    data.close()
    return info

def get_frequencies(trans_data):
    frequencies=[]
    for lines in trans_data:
        if lines[2] not in frequencies:
            frequencies.append(lines[2])
    return frequencies

def get_sigcut(x,sigma):
    x=[float(i) for i in x]
    param=norm.fit(x)
    range_x=np.linspace(min(x),max(x),1000)
    if sigma != 0:
        sigcut = param[1]*sigma+param[0]
    else:
        sigcut = 0
    return sigcut,param,range_x

def precision_and_recall(tp,fp,fn):
    if (tp+fp)==0:
        precision=1.
    else:
        precision=float(tp)/float(tp+fp)
    recall=float(tp)/float(tp+fn)
    return precision, recall

def label_data(data,label1,label2):
    # Label different arrays so that their transient type is known and they have a transient (1) or non-transient (0) label
    for x in data:
        x[5]=label1
    data=np.matrix(data)
    data=np.c_[data,[label2]*len(data)]
    return data.tolist()
