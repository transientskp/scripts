from scipy.stats import norm
import numpy as np

def extract_data(filename):
    info=[]
    data=open(filename,'r')
    for lines in data:
        if not lines.startswith("#"):
            lines=lines.rstrip().replace(" ", "")
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
    sigcut = param[1]*sigma+param[0]
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

def bayesian_blocks(t):
    """Bayesian Blocks Implementation

    By Jake Vanderplas.  License: BSD
    Based on algorithm outlined in http://adsabs.harvard.edu/abs/2012arXiv1207.5578S

    Parameters
    ----------
    t : ndarray, length N
        data to be histogrammed

    Returns
    -------
    bins : ndarray
        array containing the (N+1) bin edges

    Notes
    -----
    This is an incomplete implementation: it may fail for some
    datasets.  Alternate fitness functions and prior forms can
    be found in the paper listed above.
    """
    # copy and sort the array
    t = np.sort(t)
    N = t.size

    # create length-(N + 1) array of cell edges
    edges = np.concatenate([t[:1],
                            0.5 * (t[1:] + t[:-1]),
                            t[-1:]])
    block_length = t[-1] - edges

    # arrays needed for the iteration
    nn_vec = np.ones(N)
    best = np.zeros(N, dtype=float)
    last = np.zeros(N, dtype=int)

    #-----------------------------------------------------------------
    # Start with first data cell; add one cell at each iteration
    #-----------------------------------------------------------------
    for K in range(N):
        # Compute the width and count of the final bin for all possible
        # locations of the K^th changepoint
        width = block_length[:K + 1] - block_length[K + 1]
        count_vec = np.cumsum(nn_vec[:K + 1][::-1])[::-1]

        # evaluate fitness function for these possibilities
        fit_vec = count_vec * (np.log(count_vec) - np.log(width))
        fit_vec -= 4  # 4 comes from the prior on the number of changepoints
        fit_vec[1:] += best[:K]

        # find the max of the fitness: this is the K^th changepoint
        i_max = np.argmax(fit_vec)
        last[K] = i_max
        best[K] = fit_vec[i_max]

    #-----------------------------------------------------------------
    # Recover changepoints by iteratively peeling off the last block
    #-----------------------------------------------------------------
    change_points =  np.zeros(N, dtype=int)
    i_cp = N
    ind = N
    while True:
        i_cp -= 1
        change_points[i_cp] = ind
        if ind == 0:
            break
        ind = last[ind - 1]
    change_points = change_points[i_cp:]

    return edges[change_points]
