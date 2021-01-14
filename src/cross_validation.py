#!/usr/bin/env python3
# This will run k-fold tests on the results generated by analyzer.py
# Provide a .csv file with test data

import os
import sys
import logging
import csv
import time
import multiprocessing
import math
import statistics
import random

#
#   LOGGER
#

log_format = "%(asctime)s %(name)s [%(levelname)s] %(message)s" # From exitmap by Philipp Winter
logging.basicConfig(format=log_format, level=logging.DEBUG)
log = logging.getLogger("analyzer")

#
#   LOAD FROM CSV
#

def read_csv(path):
    data = []
    with open(path, mode='r') as csv_file:
        for line in csv.DictReader(csv_file):
            data.append(line)
    return data

def write_data(data, filename):
    with open(str(filename + ".csv"), mode='w') as F:
        csv_writer = csv.DictWriter(F, fieldnames=[
            'method',
            'C',
            'TPR',
            'FPR',
            'TNR',
            'PPV',
            'NPV',
            'FNR',
            'FDR',
            'FOR',
            'PT',
            'TS',
            'ACC',
            'BA',
            'F1',
            'MCC',
            'FM',
            'BM',
            'MK'
            ])
        csv_writer.writeheader()
        csv_writer = csv.writer(F)
        for row in data:
            csv_writer.writerow([
                row['method'],
                row['C'],
                row['TPR'],
                row['FPR'],
                row['TNR'],
                row['PPV'],
                row['NPV'],
                row['FNR'],
                row['FDR'],
                row['FOR'],
                row['PT'],
                row['TS'],
                row['ACC'],
                row['BA'],
                row['F1'],
                row['MCC'],
                row['FM'],
                row['BM'],
                row['MK'],
                ])

#
#   RESULT LIST OPERATIOSN
#

def get_directories(data):
    return set([x["directory"] for x in data])

def get_data_by_directories(data, directories=list()):
    t = time.time()
    if len(directories) == 0:
        directories = get_directories(data)
    output = []
    # N^2 TODO improve
    for directory in directories:
        output.append([x for x in data if x["directory"] == directory])
        if time.time() - t > 10:
            t = time.time()
            log.debug("Divide data by directories. " + str(len(directories) - len(output)) + " left.")
    return output

def get_fingerprints(data):
    return set([x["fingerprint"] for x in data])

def get_data_by_fingerprints(data, fingerprints=list()):
    t = time.time()
    if len(fingerprints) == 0:
        fingerprints = get_fingerprints(data)
    output = []
    # N^2 TODO improve
    for fingerprint in fingerprints:
        output.append([x for x in data if x["fingerprint"] == fingerprint])
        if time.time() - t > 10:
            t = time.time()
            log.debug("Divide data by fingerprints. " + str(len(fingerprints) - len(output)) + " left.")
    return output

def get_methods(data):
    return set([x["method"] for x in data])

def get_data_by_method(data, methods=list()):
    t = time.time()
    if len(methods) == 0:
        methods = get_methods(data)
    output = []
    # N^2 TODO improve
    for method in methods:
        output.append([x for x in data if x["method"] == method])
        if time.time() - t > 10:
            t = time.time()
            log.debug("Divide data by method. " + str(len(methods) - len(output)) + " left.")
    return output

#
#   STATISTICS
#   Sensitivity and specificity calculations
#   https://en.wikipedia.org/wiki/Sensitivity_and_specificity
#

# sensitivity, recall, hit rate, or true positive rate (TPR)
def S_TPR(TP, P):
    return float(TP / P)

# specificity, selectivity or true negative rate (TNR)
def S_TNR(TN, N):
    if N == 0:
        return -1
    return float(TN / N)

# precision or positive predictive value (PPV)
def S_PPV(TP, FP):
    if (TP + FP) == 0:
        return -1
    return float(TP / (TP + FP))

# negative predictive value (NPV)
def S_NPV(TN, FN):
    if (TN + FN) == 0:
        return -1
    return float(TN / (TN + FN))

# miss rate or false negative rate (FNR)
def S_FNR(FN, P):
    if P == 0:
        return -1
    return float(FN / P)

# fall-out or false positive rate (FPR)
def S_FPR(FP, N):
    return float(FP / N)

# false discovery rate (FDR)
def S_FDR(FP, TP):
    if (FP + TP) == 0:
        return -1
    return float(FP / (FP + TP))

# false omission rate (FOR)
def S_FOR(FN, TN):
    if (FN + TN) == 0:
        return -1
    return float(FN / (FN + TN))

# Prevalence Threshold (PT)
def S_PT(TN, N, TP, P):
    return -1
    # TODO, implement fully
    #     dt = float(math.sqrt(S_TPR(TP=TP, P=P) * (1 + S_TNR(TN=TN, N=N))) + S_TNR(TN=TN, N=N) - 1)
    # ValueError: math domain error
    dt = float(math.sqrt(S_TPR(TP=TP, P=P) * (1 + S_TNR(TN=TN, N=N))) + S_TNR(TN=TN, N=N) - 1)
    dn = float(S_TPR(TP=TP, P=P) + S_TNR(TN=TN, N=N) - 1)
    if dn == 0:
        return -1
    return float(dt / dn)

# Threat score (TS) or critical success index (CSI)
def S_TS(TP, FN, FP):
    if (TP + FN + FP) == 0:
        return -1
    return float(TP / (TP + FN + FP))

# accuracy (ACC)
def S_ACC(TP, TN, P, N):
    if (P + N) == 0:
        return -1
    return float((TP + TN) / (P + N))

# balanced accuracy (BA)
def S_BA(TP, P, TN, N):
    return float((S_TPR(TP=TP, P=P) + S_TNR(TN=TN, N=N)) / 2)

# F1 score
def S_F1(TP, FP, P):
    dt = float(S_PPV(TP=TP, FP=FP) * S_TPR(TP=TP, P=P))
    dn = float(S_PPV(TP=TP, FP=FP) + S_TPR(TP=TP, P=P))
    if dn == 0:
        return -1
    return float(dt / dn * 2)

# Matthews correlation coefficient (MCC)
# # TODO https://en.wikipedia.org/wiki/Matthews_correlation_coefficient
def S_MCC(TP, TN, FP, FN):
    # dt = float() 
    p0 = float(TP + FP)
    p1 = float(TP + FN)
    p2 = float(TN + FP)
    p3 = float(TN + FN)
    dn = float(math.sqrt(p0 * p1 * p2 * p3))
    # return float(dt / dn)
    return float(-1)

# Fowlkes–Mallows index (FM)
def S_FM(TP, FP, FN):
    if (TP + FP) == 0 or (TP + FN) == 0:
        return -1
    p0 = float(TP / (TP + FP))
    p1 = float(TP / (TP + FN))
    return float(math.sqrt(p0 * p1))

# informedness or bookmaker informedness (BM)
def S_BM(TP, P, TN, N):
    return float(S_TPR(TP=TP, P=P) + S_TNR(TN=TN, N=N) - 1)

# markedness (MK) or deltaP
def S_MK(TP, FP, TN, FN):
    return float(S_PPV(TP=TP, FP=FP) + S_NPV(TN=TN, FN=FN) - 1)

#
#   THRESHOLD METHODS
#

# Using the fastest time ever for a non cached resolve.
# Return threshold time as float
def tm_fastest_non_cached_ever(training_data):
    return float(sorted(set([float(y["time"]) for y in training_data if str(y["cached"]) == "False"]), key=lambda x: x, reverse=False)[0])

# Using the median value of non cached resolves response times.
# Return threshold time as float
def tm_median_non_cached(training_data):
    return float(statistics.median(set([float(x["time"]) for x in training_data if str(x["cached"]) == "False"])))

# Using the mean value of non cached resolves response times.
# Return threshold time as float
def tm_mean_non_cached(training_data):
    return float(statistics.mean(set([float(x["time"]) for x in training_data if str(x["cached"]) == "False"])))

# Using the lower quartile (Q1) value of non cached resolves response times.
# Return threshold time as float
def tm_lower_quartile_non_cached(training_data):
    q2 = tm_median_non_cached(training_data)
    return float(q2 / 2)

# Using the upper quartile (Q3) value of non cached resolves response times.
# Return threshold time as float
def tm_upper_quartile_non_cached(training_data):
    q2 = tm_median_non_cached(training_data)
    return float(q2 / 2 * 3)

# Randomly selects a value from the training data.
# Return threshold time as float
def tm_random_non_cached(training_data):
    return float(random.choice(training_data)["time"])

#
#   CROSS VALIDATION (K-FOLD)
#

# Calculare new threshold from original and C value.
def threshold_c(threshold, C):
    if C == 0:
        return threshold
    else:
        return threshold + (threshold / C )

# Performs cross validation with all threshold methods
def cross_validate_all_threshold_methods(training_data, validation_data, k, C):
    training_data_size = len(training_data)
    results = list()

    # Fastest non cached
    threshold = tm_fastest_non_cached_ever(training_data=training_data)
    threshold = threshold_c(threshold, C)
    results.append(cross_validate(
        training_data_size=training_data_size,
        validation_data=validation_data,
        threshold=threshold,
        method_name="fastest non cached",
        k=k,
        C=C))
    # Median non cached
    threshold = tm_median_non_cached(training_data=training_data)
    threshold = threshold_c(threshold, C)
    results.append(cross_validate(
        training_data_size=training_data_size,
        validation_data=validation_data,
        threshold=threshold,
        method_name="median non cached",
        k=k,
        C=C))
    # Mean non cached
    threshold = tm_mean_non_cached(training_data=training_data)
    threshold = threshold_c(threshold, C)
    results.append(cross_validate(
        training_data_size=training_data_size,
        validation_data=validation_data,
        threshold=threshold,
        method_name="mean non cached",
        k=k,
        C=C))
    # Lower quartile non cached
    threshold = tm_lower_quartile_non_cached(training_data=training_data)
    threshold = threshold_c(threshold, C)
    results.append(cross_validate(
        training_data_size=training_data_size,
        validation_data=validation_data,
        threshold=threshold,
        method_name="lower quartile non cached",
        k=k,
        C=C))
    # Upper quartile non cached
    threshold = tm_upper_quartile_non_cached(training_data=training_data)
    threshold = threshold_c(threshold, C)
    results.append(cross_validate(
        training_data_size=training_data_size,
        validation_data=validation_data,
        threshold=threshold,
        method_name="upper quartile non cached",
        k=k,
        C=C))
    # Random non cached
    threshold = tm_random_non_cached(training_data=training_data)
    threshold = threshold_c(threshold, C)
    results.append(cross_validate(
        training_data_size=training_data_size,
        validation_data=validation_data,
        threshold=threshold,
        method_name="random non cached",
        k=k,
        C=C))

    # Cleanup results if some are broken.
    # Broken result datapoints are represented by a fingerprint set to none.
    results = [x for x in results if not x["fingerprint"] == "none"]
    return results

# Format cross validation results
def cross_validate_result_format(fingerprint="none", training_data_size=-1, validation_data_size=-1, k=-1, threshold=-1, P=-1, N=-1, TP=-1, TN=-1, FP=-1, FN=-1, method_name="none", C=-1):
    a = {}
    # Basic
    a["fingerprint"]            = str(fingerprint)
    a["training_data_size"]     = str(training_data_size)
    a["validation_data_size"]   = str(validation_data_size)
    a["k"]                      = str(k)
    a["method"]                 = str(method_name)
    a["C"]                      = str(C)
    a["threshold"]              = str(threshold)
    a["P"]                      = str(P)
    a["N"]                      = str(N)
    # Statistics
    a["TP"]                     = str(TP)
    a["TN"]                     = str(TN)
    a["FP"]                     = str(FP)
    a["FN"]                     = str(FN)
    # Derived statistics
    a["TPR"]                    = str(S_TPR(TP=TP, P=P))
    a["FPR"]                    = str(S_FPR(FP=FP, N=N))
    a["TNR"]                    = str(S_TNR(TN=TN, N=N))
    a["PPV"]                    = str(S_PPV(TP=TP, FP=FP))
    a["NPV"]                    = str(S_NPV(TN=TN, FN=FN))
    a["FNR"]                    = str(S_FNR(FN=FN, P=P))
    a["FDR"]                    = str(S_FDR(FP=FP, TP=TP))
    a["FOR"]                    = str(S_FOR(FN=FN, TN=TN))
    a["PT"]                     = str(S_PT(TN=TN, N=N, TP=TP, P=P))
    a["TS"]                     = str(S_TS(TP=TP, FN=FN, FP=FP))
    a["ACC"]                    = str(S_ACC(TP=TP, TN=TN, P=P, N=N))
    a["BA"]                     = str(S_BA(TP=TP, P=P, TN=TN, N=N))
    a["F1"]                     = str(S_F1(TP=TP, FP=FP, P=P))
    a["MCC"]                    = str(S_MCC(TP=TP, TN=TN, FP=FP, FN=FN))
    a["FM"]                     = str(S_FM(TP=TP, FP=FP, FN=FN))
    a["BM"]                     = str(S_BM(TP=TP, P=P, TN=TN, N=N))
    a["MK"]                     = str(S_MK(TP=TP, FP=FP, TN=TN, FN=FN))
    return a

# Perform a cross validation of trainig and validation data
# Return cross_validate_result_format(...)
def cross_validate(training_data_size, validation_data, threshold, method_name, k, C):
    # https://en.wikipedia.org/wiki/Sensitivity_and_specificity
    P = len([x for x in validation_data if str(x["cached"]) == "True"]) # Positives
    N = len([x for x in validation_data if str(x["cached"]) == "False"]) # Negatives
    TP = 0 # True positives     (prediction = cached,     validation = cached)        (same)
    FP = 0 # False positives    (prediction = cached,     validation = non cached)    (not same)
    TN = 0 # True negative      (prediction = not cached, validation = non cached)    (same)
    FN = 0 # False negative     (prediction = not cached, validation = cached)        (not same)
    fingerprint = str(validation_data[0]["fingerprint"]) # Fingerprint of exit node
    
    # Does this add up?
    # P or N is zero, results will be discarded.
    if P == 0 or N == 0:
        #log.error("\u001b[31mCross validate, something does not add upp here! P=" + str(P) + " and N=" + str(N) + ". Will abandon and discard this data. Data belongs to fingerprint " + str(get_fingerprints(validation_data)) + " with training data size " + str(training_data_size) + " and validation data size " + str(len(validation_data)) + " from k=" + str(k) + ". Threshold was set at " + str(threshold) + " with C=" + str(C) + " and the method used was " + str(method_name) + ". Discarding data from results!\u001b[0m")
        return cross_validate_result_format() # Return a empty datapoint
    
    # Start cross validation
    for validation_datapoint in validation_data:
        # Is datapoint cached according to training data
        is_cached_predicted = bool(float(validation_datapoint["time"]) < threshold)
        is_cached = validation_datapoint["cached"] == "True"

        # Set TP, FP, TN and FN
        if is_cached_predicted == True:
            # Is either TP or FP
            if is_cached:
                TP += 1
            else:
                FP += 1
        else:
            # Is either TN or FN
            if is_cached:
                FN += 1
            else:
                TN += 1

    return cross_validate_result_format(
        fingerprint=fingerprint,
        training_data_size=training_data_size,
        validation_data_size=len(validation_data),
        k=k,
        threshold=threshold,
        P=P,
        N=N,
        TP=TP,
        TN=TN,
        FP=FP,
        FN=FN,
        method_name=method_name,
        C=C
        )

# Perform cross validation of results using k-fold
# Provide data for one fingerprint only, fingerprint has to be unique
# Provide N times to split data in k-fold operation
# Provide process number for identification
# Provide a dictoionary to return output to main process
# Return True
def mp_k_fold(data, N, cs, procnum, return_dict):
    # Time for stats
    t = time.time()
    # Print stats
    log.info("\u001b[36mK-Fold #" + str(procnum) + " fingerprint=" + str(data[0]["fingerprint"]) + " N=" + str(N) + " c_range=" + str(len(cs)) + " data_size=" + str(len(data)) + "\u001b[0m")
    # If data is insufficient, abort
    if len(data) < N:
        log.error("\u001b[31mData set too small!\u001b[0m")
        exit(-1)

    # Output as list of cross_validate_result_format(...)
    output = list()
    # For N splits in k-fold, perform k-fold where k is validation data and (k)´ is training data
    for k in range(N):
        # List limits
        # validate 0
        v0_lower = int(len(data) / N * k) # t0 upper
        v0_upper = int(len(data) / N * (k + 1)) # t1 lower
        # training 0
        t0_lower = 0 # Bottom of list
        t0_upper = v0_lower
        # validate 1
        t1_lower = v0_upper
        t1_upper = int(len(data) + 1) # Top of list

        # Prepare data sets for traning
        td0 = data[t0_lower:t0_upper]
        td1 = data[t1_lower:t1_upper]
        training_data = []
        training_data.extend(td0)
        training_data.extend(td1)

        # Prepare data sets for validation
        vd0 = data[v0_lower:v0_upper]
        validation_data = []
        validation_data.extend(vd0)

        # Itterate over all C's in cs (list with C)
        for C in cs:
            # Perform cross validation with C
            # Results is a list of data formatted as cross_validate_result_format(...)
            cv_results = cross_validate_all_threshold_methods(training_data=training_data, validation_data=validation_data, k=k, C=C)
            output.extend(cv_results)
        
    return_dict[procnum] = output
    log.info("\u001b[32mK-Fold #" + str(procnum) + " done in " + str(float(time.time() - t))[0:5] + " seconds.\u001b[0m")
    return True

# Generate list of C values
def cross_validate_get_cs(c_min, c_max):
    log.debug("C range from " + str(c_min) + " to " + str(c_max) + ".")
    nums = [x for x in range(c_min, c_max)]
    return nums

# Perform cross validation as k-fold using multiple processes.
# Provide raw results data from aggregator.py.
# Provide N peices to devide data into.
# Provide number of cpus to use, 0 for all.
# Return result in list where each element is formatted according to cross_validate_result_format(...)
def mp_cross_validation_boostrap(raw_result_data, N=10, cpu_limit=0, c_min=0, c_max=1):
    # Set allocated cpus
    if cpu_limit < 1:
        log.debug("No CPU limit was specified, will use all avaliable.")
        cpu_limit = int(multiprocessing.cpu_count())
    log.info("Using " + str(cpu_limit) + " CPUs.")

    # Multi processing return dictionary
    return_dict = multiprocessing.Manager().dict()
    output = list()
    processes_waiting_list = list()

    # Devide data by fingerprint
    log.info("Dividing data by fingerprints, please wait...")
    t = time.time()
    data_by_fingerprint = get_data_by_fingerprints(raw_result_data)
    log.info("Dividing data by fingerprints done. Took " + str(float(time.time() - t)) + " seconds.")
    log.debug("Cross validation boostrapper will start " + str(len(data_by_fingerprint)) + " processes.")
    t0 = time.time()
    # Prepare cs (List of C)
    cs = cross_validate_get_cs(c_min, c_max)
    # Prepare processes, one for each fingerprint
    for dbf in sorted(data_by_fingerprint, key=lambda x: len(x), reverse=False):
        processes_waiting_list.append(multiprocessing.Process(target=mp_k_fold, args=(list(dbf), N, cs, len(processes_waiting_list), return_dict, )))
    log.debug("Process waiting list of size " + str(len(processes_waiting_list)) + ".")
    # Start and run k-fold processes
    processes_running_list = list()
    # If either list is not empty
    t = time.time()
    while len(processes_waiting_list) > 0 or len(processes_running_list) > 0:
        while len(processes_running_list) < cpu_limit and len(processes_waiting_list) > 0:
            # Running list is not full and waiting list is not empty.
            # Add more process.
            p = processes_waiting_list.pop()
            processes_running_list.append(p)
            processes_running_list[len(processes_running_list) - 1].start() # Start last process in list
            #log.debug("Add and start process " + str(p))

        while len(processes_running_list) > 0:
            # Running list is full or waiting list is empty
            # Runnign list cannot be empty
            # Wait for processes to join.
            try:
                p = processes_running_list.pop()
                #log.debug("Join process " + str(p))
                p.join()
            except Exception as ex:
                log.error("\u001b[31mCould not join process, error " + str(ex) + "\u001b[0m")
        
        # Stats printout
        if time.time() - t > 10:
            t = time.time()
            log.info("Cross validation running, " + str(len(processes_running_list) + len(processes_waiting_list)) + " processes left.")
    # Handle output
    output = []
    [output.extend(value) for value in return_dict.values()]
    log.debug("Multiprocessing cross validation bootstrap, returning " + str(len(output)) + " rows of data. Took " + str(float(time.time() - t0)) + " seconds.")
    return output

#
#   EVALUATE RESULTS
#

# Perform using multiple processes.
# Results per fingerprint
# Return list of results
def mp_eval_results_fingerprint_boostrap(results, cpu_limit=0):
    # Set allocated cpus
    if cpu_limit < 1:
        log.debug("No CPU limit was specified, will use all avaliable.")
        cpu_limit = int(multiprocessing.cpu_count())
    log.info("Using " + str(cpu_limit) + " CPUs.")

    # Multi processing return dictionary
    return_dict = multiprocessing.Manager().dict()
    output = list()
    processes_waiting_list = list()

    t0 = time.time()
    # Prepare processes, one for each fingerprint
    for dbf in get_data_by_fingerprints(results):
        processes_waiting_list.append(multiprocessing.Process(target=mp_eval_results_fingerprint, args=(list(dbf), len(processes_waiting_list), return_dict, )))
    log.debug("Process waiting list of size " + str(len(processes_waiting_list)) + ".")
    
    processes_running_list = list()
    # If either list is not empty
    t = time.time()
    while len(processes_waiting_list) > 0 or len(processes_running_list) > 0:
        while len(processes_running_list) < cpu_limit and len(processes_waiting_list) > 0:
            # Running list is not full and waiting list is not empty.
            # Add more process.
            p = processes_waiting_list.pop()
            processes_running_list.append(p)
            processes_running_list[len(processes_running_list) - 1].start() # Start last process in list
            #log.debug("Add and start process " + str(p))
        
        while len(processes_running_list) > 0:
            # Running list is full or waiting list is empty
            # Runnign list cannot be empty
            # Wait for processes to join.
            try:
                p = processes_running_list.pop()
                #log.debug("Join process " + str(p))
                p.join()
            except Exception as ex:
                log.error("\u001b[31mCould not join process, error " + str(ex) + "\u001b[0m")
        
        # Stats printout
        if time.time() - t > 10:
            t = time.time()
            log.info("Evaluation per C, Method and Fingerprint running, " + str(len(processes_running_list) + len(processes_waiting_list)) + " processes left.")
    # Handle output
    output = []
    [output.extend(value) for value in return_dict.values()]
    log.debug("Evaluation per C, Method and Fingerprint bootstrap, returning " + str(len(output)) + " rows of data. Took " + str(float(time.time() - t0)) + " seconds.")
    return output

# Evaluates results per fingerpint, C and method
# Effectively removes K from data
# Return list
def mp_eval_results_fingerprint(results_by_fingerprint, procnum, return_dict):
    t = time.time()
    fingerprint = get_fingerprints(results_by_fingerprint).pop()
    log.info("\u001b[36mEvaluation #" + str(procnum) + ".\u001b[0m")
    output = list()
    for results_by_method in get_data_by_method(results_by_fingerprint):
        method = get_methods(results_by_method).pop()
        for C in set([x["C"] for x in results_by_method]):
            data = [x for x in results if str(x["fingerprint"]) == str(fingerprint) and str(x["method"]) == str(method) and str(x["C"]) == str(C)]
            a = {}
            a["fingerprint"]            = str(fingerprint)
            a["method"]                 = str(method)
            a["C"]                      = str(C)
            a["TPR"]                    = str(statistics.mean([float(x["TPR"]) for x in data]))
            a["FPR"]                    = str(statistics.mean([float(x["FPR"]) for x in data]))
            a["TNR"]                    = str(statistics.mean([float(x["TNR"]) for x in data]))
            a["PPV"]                    = str(statistics.mean([float(x["PPV"]) for x in data]))
            a["NPV"]                    = str(statistics.mean([float(x["NPV"]) for x in data]))
            a["FNR"]                    = str(statistics.mean([float(x["FNR"]) for x in data]))
            a["FDR"]                    = str(statistics.mean([float(x["FDR"]) for x in data]))
            a["FOR"]                    = str(statistics.mean([float(x["FOR"]) for x in data]))
            a["PT"]                     = str(statistics.mean([float(x["PT"]) for x in data]))
            a["TS"]                     = str(statistics.mean([float(x["TS"]) for x in data]))
            a["ACC"]                    = str(statistics.mean([float(x["ACC"]) for x in data]))
            a["BA"]                     = str(statistics.mean([float(x["BA"]) for x in data]))
            a["F1"]                     = str(statistics.mean([float(x["F1"]) for x in data]))
            a["MCC"]                    = str(statistics.mean([float(x["MCC"]) for x in data]))
            a["FM"]                     = str(statistics.mean([float(x["FM"]) for x in data]))
            a["BM"]                     = str(statistics.mean([float(x["BM"]) for x in data]))
            a["MK"]                     = str(statistics.mean([float(x["MK"]) for x in data]))
            output.append(a)
    return_dict[procnum] = output
    log.info("\u001b[32mEvaluation #" + str(procnum) + " done in " + str(float(time.time() - t))[0:5] + " seconds.\u001b[0m")
    return True

# Perform using multiple processes.
# Results for whole oracle
# Return list of results
def mp_eval_results_overall_bootstrap(results, cpu_limit=0):
    # Set allocated cpus
    if cpu_limit < 1:
        log.debug("No CPU limit was specified, will use all avaliable.")
        cpu_limit = int(multiprocessing.cpu_count())
    log.info("Using " + str(cpu_limit) + " CPUs.")

    # Multi processing return dictionary
    return_dict = multiprocessing.Manager().dict()
    output = list()
    processes_waiting_list = list()

    t0 = time.time()
    # Prepare processes, one for each fingerprint
    for dbm in get_data_by_method(results):
        processes_waiting_list.append(multiprocessing.Process(target=mp_eval_results_overall, args=(list(dbm), len(processes_waiting_list), return_dict, )))
    log.debug("Process waiting list of size " + str(len(processes_waiting_list)) + ".")
    
    processes_running_list = list()
    # If either list is not empty
    t = time.time()
    while len(processes_waiting_list) > 0 or len(processes_running_list) > 0:
        while len(processes_running_list) < cpu_limit and len(processes_waiting_list) > 0:
            # Running list is not full and waiting list is not empty.
            # Add more process.
            p = processes_waiting_list.pop()
            processes_running_list.append(p)
            processes_running_list[len(processes_running_list) - 1].start() # Start last process in list
            #log.debug("Add and start process " + str(p))

        while len(processes_running_list) > 0:
            # Running list is full or waiting list is empty
            # Runnign list cannot be empty
            # Wait for processes to join.
            try:
                p = processes_running_list.pop()
                #log.debug("Join process " + str(p))
                p.join()
            except Exception as ex:
                log.error("\u001b[31mCould not join process, error " + str(ex) + "\u001b[0m")
        
        # Stats printout
        if time.time() - t > 10:
            t = time.time()
            log.info("Evaluation per C, Method running, " + str(len(processes_running_list) + len(processes_waiting_list)) + " processes left.")
    # Handle output
    output = []
    [output.extend(value) for value in return_dict.values()]
    log.debug("Evaluation per C, Method bootstrap, returning " + str(len(output)) + " rows of data. Took " + str(float(time.time() - t0)) + " seconds.")
    return output

# Evaluates results per C and method
# Effectively removes K and fingerprint from data
# Return list
def mp_eval_results_overall(results_by_method, procnum, return_dict):
    method = get_methods(results_by_method).pop()
    #t = time.time()
    log.info("\u001b[36mEvaluation overall (per C and method) #" + str(procnum) + " with " + str(len(results_by_method)) + " rows of data.\u001b[0m")
    output = list()
    for C in set([x["C"] for x in results]):
        data = [x for x in results if str(x["method"]) == str(method) and str(x["C"]) == str(C)]
        #log.debug("Evaluate results for method " + str(method) + " with C = " + str(C) + " found " + str(len(data)) + " datapoints.")
        a = {}
        a["method"]                 = str(method)
        a["C"]                      = str(C)
        a["TPR"]                    = str(statistics.mean([float(x["TPR"]) for x in data]))
        a["FPR"]                    = str(statistics.mean([float(x["FPR"]) for x in data]))
        a["TNR"]                    = str(statistics.mean([float(x["TNR"]) for x in data]))
        a["PPV"]                    = str(statistics.mean([float(x["PPV"]) for x in data]))
        a["NPV"]                    = str(statistics.mean([float(x["NPV"]) for x in data]))
        a["FNR"]                    = str(statistics.mean([float(x["FNR"]) for x in data]))
        a["FDR"]                    = str(statistics.mean([float(x["FDR"]) for x in data]))
        a["FOR"]                    = str(statistics.mean([float(x["FOR"]) for x in data]))
        a["PT"]                     = str(statistics.mean([float(x["PT"]) for x in data]))
        a["TS"]                     = str(statistics.mean([float(x["TS"]) for x in data]))
        a["ACC"]                    = str(statistics.mean([float(x["ACC"]) for x in data]))
        a["BA"]                     = str(statistics.mean([float(x["BA"]) for x in data]))
        a["F1"]                     = str(statistics.mean([float(x["F1"]) for x in data]))
        a["MCC"]                    = str(statistics.mean([float(x["MCC"]) for x in data]))
        a["FM"]                     = str(statistics.mean([float(x["FM"]) for x in data]))
        a["BM"]                     = str(statistics.mean([float(x["BM"]) for x in data]))
        a["MK"]                     = str(statistics.mean([float(x["MK"]) for x in data]))
        output.append(a)
    return_dict[procnum] = output
    log.info("\u001b[32mEvaluation overall (per C and method) #" + str(procnum) + " done in " + str(float(time.time() - t))[0:5] + " seconds.\u001b[0m")
    return True

#
#   BOOSTRAP ANALYZER
#

if __name__ == "__main__":
    try:
        if os.path.isfile(str(sys.argv[1])):
            t = time.time()
            log.info("Reading data from " + str(sys.argv[1]))
            data = read_csv(str(sys.argv[1]))
            log.info("Read data sucessfully, took " + str(float(time.time() - t))[0:5] + " seconds.")
        else:
            log.error("Provide a CSV file as first command line arguemnt.")
            exit(-1)
    except Exception as ex:
        log.error("\u001b[31mReading CSV file as input failed with error " + str(ex) + "\u001b[0m")
        exit(-1)
    else:
        # GET C MAX VALUE
        try:
            c_min = int(sys.argv[2])
            c_max = int(sys.argv[3])
            if c_max < c_min:
                log.error("C max less than C min!")
                exit(-1)
        except Exception as ex:
            log.error("C value from command line failed with error " + str(ex))
            log.info("Provide a a min and max C value as second and third command line argument.")
            exit(-1)
        else:
            log.info("C max value set to " + str(c_max) + ", will run " + str(len(range(c_max))) + " times with different C value.")

        # PERFORM CROSS VALIDATION
        t = time.time()
        log.debug("Got " + str(len(data)) + " rows of data containg " + str(len(get_fingerprints(data))) + " fingerprints.")
        results = mp_cross_validation_boostrap(data, N=10, cpu_limit=0, c_min=c_min, c_max=c_max)
        log.info("Cross validation resulted in " + str(len(results)) + " rows of data.")
        
        # WRITE RESULTS TO DISK
        # try:
        #     log.info("Sorting and writing data to disk, please wait...")
        #     results = sorted(results, key=lambda x: x["method"], reverse=False)
        #     write_data(results, "theoracle_cross_validation_all_" + str(time.time()))
        # except Exception as ex:
        #     log.error("\u001b[31mSorting and writing failed with error " + str(ex) + "\u001b[0m")
        # else:
        #     log.info("Sorted data and wrote to disk sucessfully.")

        # EVALUATE RESULTS PER FINGERPRINT
        try:
            log.info("Evaluating results per fingerprint, calulating means.")
            # EVALUATING RESULTS PER FINGERPRINT
            results = mp_eval_results_fingerprint_boostrap(results, cpu_limit=0)
            log.debug("Resulting in " + str(len(results)) + " rows of data.")
        except Exception as ex:
            log.error("\u001b[31mEvaluation failed with error " + str(ex) + "\u001b[0m")
        else:
            log.info("Evaluation done.")

        # WRITE RESULTS TO DISK
        # try:
        #     log.info("Sorting and writing data to disk, please wait...")
        #     results = sorted(results, key=lambda x: x["method"], reverse=False)
        #     write_data(results, "theoracle_cross_validation_per_fingerprint_" + str(time.time()))
        # except Exception as ex:
        #     log.error("\u001b[31mSorting and writing failed with error " + str(ex) + "\u001b[0m")
        # else:
        #     log.info("Sorted data and wrote to disk sucessfully.")

        # EVALUATE RESULTS PER METHOD AND C
        try:
            # EVALUATING RESULTS OVERALL (PER METHOD)
            log.info("Evaluating results overall (per method), calulating means.")
            results = mp_eval_results_overall_bootstrap(results, cpu_limit=0)
            log.debug("Resulting in " + str(len(results)) + " rows of data.")
        except Exception as ex:
            log.error("\u001b[31mEvaluation failed with error " + str(ex) + "\u001b[0m")
        else:
            log.info("Evaluation done.")

        # WRITE RESULTS TO DISK
        try:
            log.info("Sorting and writing data to disk, please wait...")
            results = sorted(results, key=lambda x: x["method"], reverse=False)
            write_data(results, "theoracle_cross_validation_final_" + str(time.time()))
        except Exception as ex:
            log.error("\u001b[31mSorting and writing failed with error " + str(ex) + "\u001b[0m")
        else:
            log.info("Sorted data and wrote to disk sucessfully.")
    finally:
        log.info("Cross validation done, exiting.")
        exit(0)