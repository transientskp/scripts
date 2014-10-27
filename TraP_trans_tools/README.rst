TraP_trans_tools Script Archive
========================

This folder contains the files required to analyse the transient parameters for a large number of sources. The tools developed are not TraP specific, however there are executable scripts demonstrating how to use these scripts with outputs from TraP databases (process_TraP.py and train_TraP.py). The techniques implemented in these scripts and how to interpret the outputs are described in Rowlinson et al. (In Prep).

Contents
--------

`dump_trans_data_v1 <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/dump_trans_data_v1.py>`_
    Tools to extract required data from a TraP database (TraP release 1). Outputs the transient parameters and individual extracted sources.

`format_TraP_data <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/format_TraP_data.py>`_
    Tools to extract required to convert data extracted by dump_trans_data_v1 into the format required for the other scripts.

`generic_tools <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/generic_tools.py>`_
    General tools to help with processing data.

`plotting_tools <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/plotting_tools.py>`_
    Tools to generate the scatter/histogram and diagnostic plots to visualise datasets.

`process_TraP <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/process_TraP.py>`_
    An example executable script that fully processes data from TraP (from reading database to creating plots).

`train_anomaly_detect <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/train_anomaly_detect.py>`_
    Tools to train and use an anomaly detection algorithm (machine learning).

`train_logistic_regression <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/train_logistic_regression.py>`_
    Tools to train and use an logistic regression algorithm (machine learning).

`train_TraP <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/train_TraP.py>`_
    An example executable script that trains and applies machine learning algorithms using the outputs from process_TraP.py.

`examples <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/examples>`_
    A folder containing example training data for train_TraP.py.

Requirements
------------

- tkp (The LOFAR Transients Pipeline, TraP)
- numpy
- scikit-learn
- astroML
- os
- pylab
- csv
- scipy
- math
- matplotlib
- random

dump_trans_data_v1.py
---------------------
*Requirements:* tkp (TraP installed and initiated), csv

- **dump_trans**

  *Inputs:* database name, dataset id, engine (monetdb or postgres),  host, port, username, password

  *Info:* queries the database to extract the transient and extracted source tables. Files saved in working directory as "ds_${dataset id}_transients.csv" and "ds_${dataset id}_sources.csv"

- **dump_list_of_dicts_to_csv**

  *Inputs:* data, output filename

  *Info:* writes the data out to a file in the csv format.

format_TraP_data.py
--------------------
*Requirements:* dump_trans_data_v1, generic_tools, os, numpy

- **get_data**

  *Inputs:* database, dataset_id, release, host, port, user, password

  *Info:* Calls dump_trans_data_v1.py to obtain the data and put it into a CSV file

- **read_src_lc**

  *Inputs:* sources data, lightcurves

  *Info:* sorts the lightcurves for the unique sources in the extracted sources data. lightcurves is a true/false option to output the lightcurves

  *Outputs:* unique frequencies, source lightcurves

- **collate_trans_data**

  *Inputs:* unique source lightcurves, frequencies, transient sources

  *Info:* sorts the data into the required information for later analysis. Each unique source has its transient parameters, maximum flux, ratio between maximum flux and average flux and observing frequency.

  *Outputs:* transient data for each source

- **format_data**

  *Inputs:* database, dataset_id, release, host, port, username, password, lightcurves

  *Info:* uses dump_trans_data to extract data, extracts the transient data for each unique source and saves the output to "ds_${dataset id}_trans_data.csv" for use in later analysis.


generic_tools.py
----------------
*Requirements:* numpy, scipy

- **extract_data**

  *Inputs:* filename

  *Info:* reads the data in a given file into an array.

  *Outputs:* array of data

- **get_frequencies**

  *Inputs:* transient data

  *Info:* finds all the unique values in the "frequency" column. This column typically contains observing frequencies, but is also used to identify different types of transients in the machine learning code.

  *Outputs:* the unique frequencies

- **get_sigcut**

  *Inputs:* data, sigma

  *Info:* fits the 1D data with a Gaussian distribution and finds the threshold associated with a given sigma.

  *Outputs:* sigma threshold, Gaussian fit parameters, range fitted over

- **precision_and_recall**

  *Inputs:* Number of true positive, false positive and false negative identifications

  *Info:* This calculates the precision (probability that a source is correctly identified) and recall (probability that all sources have been identified) for given results. Required for assessing quality of machine learning results.

  *Outputs:* precision, recall

- **label_data**

  *Inputs:* data, label1, label2

  *Info:* Inserts label1 into the frequency column, typically a string which is the type of transient. Appends a new column with either ``1`` or ``0`` to represent ``transient`` and ``stable``.

  *Outputs:* labelled data


plotting_tools.py
-----------------
*Requirements:* numpy, scipy, matplotlib, math, pylab, astroML

- **make_colours**

  *Inputs:* unique frequencies

  *Info:* assigns a colour from a colourmap (jet) to each unique frequency for plotting.

  *Outputs:* colours

- **create_scatter_hist**

  *Inputs:* data for plotting, sigma thresholds for x-axis and y-axis, parameters from Gaussian fit for x and y axes, range used for fitting Gaussian distributions, dataset id, unique frequencies

  *Info:* creates a plot showing the two transient parameters  (typically Eta_nu and V_nu) with histograms and fitted Gaussian distributions. If thresholds are not equal to 0, it also plots dashed lines to represent the thresholds used on the transient parameters. Plot saved as "ds${dataset id}_scatter_hist.png". See `example <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/examples/rsm_scatter_hist.png>`_

  *Outputs:* a list of transient id numbers

- **create_diagnostic**

  *Inputs:* data for plotting, thresholds for x-axis and y-axis, unique frequencies, dataset id

  *Info:*  creates a scatter plot showing four transient parameters (typically Eta_nu, V_nu, max flux and ratio between max flux and average flux). If thresholds are not equal to 0, it also plots dashed lines to represent the thresholds used on the transient parameters. Plot saved as "ds${dataset id}_diagnostic_plots.png". See `example <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/examples/rsm_diagnostic_plots.png>`_


process_TraP.py
---------------
*Requirements:* format_TraP_data, plotting_tools, generic_tools, numpy, sys

An example executable script for processing TraP data. Usage:

``python process_TraP.py <database> <username> <password> <dataset_id> <release> <host> <port> <sigma1> <sigma2> <lightcurves>``

<database>: name of TraP database containing data

<username>: your database username

<password>: your database password

<dataset_id>: the dataset id that is to be processed

<release>: TraP release and engine, options p and m (postgres and monetdb respectively)

<host>: The machine hosting the database

<port>: The port number for the machine hosting the database

<sigma1>: sigma threshold for use in determining threshold on Eta_nu

<sigma2>: sigma threshold for use in determining threshold on V_nu

<lightcurves>: "True/False" option to output the lightcurves for each unique source

This script will extract data from the database, identify unique sources and obtain their lightcurves, sort the transient parameters and create the various diagnostic plots.

train_anomaly_detect.py
-----------------------
*Requirements:* generic_tools, numpy, multiprocessing, scipy, operator, matplotlib, pylab

- **trial_data**

  *Inputs:* data, sigma1, sigma2

  *Info:* tries out a given pair of thresholds on the labelled data. It calculates the true positives, false positives, true negatives and false negatives. These are then used to calculate the precision and recall.

  *Outputs:* sigma1, sigma2, precision, recall

- **multiple_trials**

  *Inputs:* data

  *Info:* Runs trial_data using different sigma values. sigma1 and  sigma2 both range from 0 to 4 sigma with 500 bins. This is using a multiprocessing pool with 4 processes. The data are appended to a file, "sigma_data.txt".

- **tests**

  *Inputs:* list containing x sigma data,y sigma data, precisions, recalls, training data, transient x data, transient y data, stable x data, stable y data, required precision, required recall

  *Info:* Using the gridded precision and recall values for different
  combinations of sigma, find the best match to the input required
  precision and recall. Then use observed training data to measure the obtained
  precision and recall values. These should be roughly equal.

  *Outputs:* list containing: required precision, required recall, obtained precision, obtained recall

- **check_method_works**

  *Inputs:*  list containing x sigma data,y sigma data, precisions, recalls, training data, above threshold sigma

  *Info:* Runs the test function multiple times for a wide range of input precisions and recalls. Plots a figure to show the performance.

- **find_best_sigmas**

  *Inputs:* required precision, required recall, sigma data

  *Info:* Creates a 2000x2000 grid using the data in "sigma_data.txt" with a cubic interpolation between the trialed data points. The parameter space that gives the required precision and recall is identified, then use an F-score to identify the optimal balance of precision and recall in this parameter space. A plot illustrating the precision and recall parameter space is output and here is an `example <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/examples/sim_precisions_and_recalls.png>`_ 

  *Outputs:* best sigma threshold for Eta_nu, best sigma threshold for V_nu


train_logistic_regression.py
----------------------------
*Requirements:* generic_tools, numpy, scipy, random, matplotlib, pylab

- **shuffle_datasets**

  *Inputs:* data

  *Info:* Ensures that your data is randomised so that the training, validation and testing datasets do not contain too many of one kind of source.

  *Outputs:* shuffled data

- **create_datasets**

  *Inputs:* data, number of training datapoints, number of validation datapoints

  *Info:* splits the data array into 3, with the required number of datapoints. The number of testing datapoints constitutes the remaining data.

  *Outputs:* training, validation and testing datasets

- **create_X_y_arrays**

  *Inputs:* data

  *Info:* Splits the data into the parameters and labels (as required for the machine learning algorithm).

  *Outputs:* parameters and labels

- **sigmoid**

  *Inputs:* value

  *Info:* calculates the sigmoid of a given value (1/(1+e^(-z)))

  *Outputs:* sigmoid(value)

- **reg_cost_func**

  *Inputs:* theta, X, y, lda

  *Info:* Calculates the regularised cost function for a given model (theta) and dataset. The lda (lambda) parameter regularises it, i.e. controls the weighting given to multiple parameters.

  *Outputs:* cost of the model

- **quadratic_features**

  *Inputs:* data

  *Info:* can double the number of parameters in the model by squaring them. i.e. [x1, x2] becomes [x1, x2, x1^2, x2^2].

  *Outputs:* quadratic data

- **learning_curve**

  *Inputs:* Xtrain, ytrain, Xvalid, yvalid, lda, options for scipy.optimise

  *Info:* finds the optimal model for a given training set and calculates the training and validation errors for that model. The training set starts with 1 datapoint and is incremented by 1 until the full training set is used. This test can check that the model is converging.

  *Outputs:* training and validation errors, theta

- **check_error**

  *Inputs:* X, y, theta

  *Info:* measures the classification error for a given dataset and model.

  *Outputs:* error

- **validation_curve**

  *Inputs:* Xtrain, ytrain, Xvalid, yvalid, options for scipy.optimise

  *Info:* Uses a range of lambda values (1e-5 to 1e5) input into the training algorithm to check that the data is not being overfitted by the model and can be used to chose the optimal lambda value.

  *Outputs:* training and validation errors, lambda values, optimal lambda

- **plotLC**

  *Inputs:* error_train, error_val, fname, xlog (True/False), ylog (True/False), xlabel

  *Info:* A plotting algorthm used to create figures showing the
  training and validation errors. Here are example `learning
  <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/examples/LR_learning_curve.png>`_
  ,  `repeat
  <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/examples/LR_repeat_curve.png>`_
   and  `validation
   <https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/examples/LR_validation_curve.png>`_  curves

- **classify_data**

  *Inputs:* X, y, theta

  *Info:* Classifies a given dataset and then compares to the predictions to identify the true positives, false postives, true negatives and false negatives

  *Outputs:* tp, fp, fn, tn, classified data

- **predict**

  *Inputs:* X, theta

  *Info:* Predicts the classification of new, unknown data.

  *Outputs:* predicted classifications


train_sigma_margin.py
-------------
*Requirements:* numpy, matplotlib, pylab, generic_tools

- **sort_data**

  *Inputs:* The dataset to be used

  *Info:* find the best and worst expected detection significances for each of the sources and extract the detection threshold

  *Outputs:* The best and worst thresholds and the detection threshold

- **find_sigma_margin**

  *Inputs:* best significance observed data, worst significance observed data, best significances simulated data, worst significances simulated data, detection threshold

  *Info:* Find the precision, recall and F-score for a range of different margins applied to the best and worst significances

  *Outputs:* best plot data, worst plot data

- **plot_hist**

  *Inputs:* Observed data, simulated data, detection threshold, label for figure name

  *Info:* Creates histograms of the input data

- **plot_diagnostic**

  *Inputs:* best plot data, worst plot data

  *Info:* Create a diagnostic plot illustrating the precision, recall and F-score as a function of the sigma margin. Identify the optimal margins.

  *Outputs:* Optimal best sigma margin, Optimal worst sigma margin


train_TraP.py
-------------
*Requirements:* train_anomaly_detect, train_logistic_regression, plotting_tools, generic_tools, glob, sys, numpy

An example executable script for processing TraP data. Usage:

``python train_TraP.py <precision threshold> <recall threshold> <lda>
<anomaly> <logistic> <trans> <tests>``

<precision threshold>: required precision of transient identification (1 - False Detection Rate). A probability in the range 0-1 

<recall threshold>: required recall, i.e. the probability that all transients are found (0-1)

<lda>: the lambda value to be used in the logistic regression algorithm

<anomaly>: train anomaly detection algorithm? T/F (if F give 0 for both the precision and recall thresholds)

<logistic>: train logistic regression algorithm? T/F (if F give 0 for lda)

<trans>: train the transient detection algorithm? T/F

<tests>: run the test scripts for anomaly detection and logistic regressions

This script uses pre-processed datasets, in the format output by
``format_trap_data.format_data``. The stable sources are in a file
named "stable_trans_data.txt". Transient sources are in files
"sim_${transient type}_trans_data.txt" where transient type is a short
string describing the type of transient source (used for labelling
sources in diagnostic plots instead of the frequency parameter). The
script trains both the anomaly detection algorithm and logistic
regression algorithm, outputting diagnostic plots. The anomaly
detection algorithm outputs the best transient search thresholds for
use in e.g. TraP, while the logistic regression algorithm outputs an
equation that can classify sources. Each method reports its precision
and recall. Additionally they output text files with the candidate
transient and variable sources identified. Example training files and 
output plots are given `here
<https://github.com/transientskp/scripts/tree/master/TraP_trans_tools/examples>`_ 

