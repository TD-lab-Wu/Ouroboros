#!/usr/bin/python
"""
Set of functions for producing output for the run_analysis script.

@author: Miguel Correa Marrero
"""

import os
import warnings
import numpy as np

from sklearn.metrics import matthews_corrcoef, log_loss

from helpers import round_labels
import plots


def is_inc_monotonic(lst):
    """
    Check whether the the elements in the list increase monotonically.

    Arguments
    ---------
    lst:    list

    Returns
    --------
    Bool, whether the elements of the list increase monotonically (True) or not
    (False)

    """
    return all(x < y for x, y in zip(lst, lst[1:]))


def write_llh_warning(out_path):
    """
    Creates a text file warning the user that the total log-likelihood does
    not increase monotonically
    """

    with open(os.path.join(out_path, 'likelihood_warning.txt'), 'w') as target:
        target.write(
            "Total log-likelihood does not increase monotonically")


def create_output(labels_per_iter, alt_llhs_per_iter, null_llhs_per_iter,
                  alt_int_per_iter, null_nonint_per_iter, mode, out_path, test,
                  true_labels=None, alt_true_per_iter=None,
                  null_true_per_iter=None):
    """
    Create output concerning PPI prediction
    """
    checks_dir = os.path.join(out_path, 'output')
    # Evolution of labels accros iterations
    write_evolution_zs(labels_per_iter, out_path)
    # Compute sums of log-likelihoods
    sum_alt_per_iter = [x.sum() for x in np.array(alt_llhs_per_iter)]
    sum_null_per_iter = [x.sum() for x in np.array(null_llhs_per_iter)]
    sum_alt_int_per_iter = [x.sum() for x in np.array(alt_int_per_iter)]
    sum_null_nonint_per_iter = [x.sum()
                                for x in np.array(null_nonint_per_iter)]
    total_llh_per_iter = np.sum(
        (sum_alt_int_per_iter, sum_null_nonint_per_iter), axis=0)

    if not is_inc_monotonic(total_llh_per_iter):
        warnings.warn(
            """Total log-likelihood does not increase monotonically:
            inspect results""", RuntimeWarning)
        write_llh_warning(out_path)

    if test:
        all_true_int = np.sum(np.asarray(alt_true_per_iter), axis=1)
        all_true_nonint = np.sum(np.asarray(null_true_per_iter), axis=1)
        all_true = np.sum((all_true_int, all_true_nonint), axis=0)

    if test:
        plots.draw_llh_plot(sum_alt_per_iter, sum_null_per_iter,
                            sum_alt_int_per_iter, sum_null_nonint_per_iter,
                            total_llh_per_iter, os.path.join(
                                checks_dir, 'convergence.png'),
                            all_true_int, all_true_nonint, all_true)
    else:
        plots.draw_llh_plot(sum_alt_per_iter, sum_null_per_iter,
                            sum_alt_int_per_iter, sum_null_nonint_per_iter,
                            total_llh_per_iter, os.path.join(
                                checks_dir, 'convergence.png'))

    # Write log-likelihoods per iteration to disk
    if test:
        write_llhs(sum_alt_per_iter, sum_null_per_iter,
                   sum_alt_int_per_iter, sum_null_nonint_per_iter,
                   total_llh_per_iter, out_path, test, all_true_int,
                   all_true_nonint, all_true)
    else:
        write_llhs(sum_alt_per_iter, sum_null_per_iter,
                   sum_alt_int_per_iter, sum_null_nonint_per_iter,
                   total_llh_per_iter, out_path, test)

    if test:
        pred_labels = labels_per_iter[-1]
        draw_confusion_matrices(
            true_labels, pred_labels, mode, checks_dir)
        write_model_report(true_labels, pred_labels, mode, checks_dir)

        plots.draw_performance_per_iter(labels_per_iter, true_labels,
                                        mode, checks_dir)


def write_evolution_zs(labels_per_iter, results_dir):
    """
    Write to disk files concerning the evolution of the hidden variables.

    Arguments
    ---------
    labels_per_iter: array-like, contains the values of the hidden variables in
                     each iteration
    results_dir:     str, base directory

    Returns
    -------
    None

    """

    labels_per_iter = np.asarray(labels_per_iter).T
    labels_path = os.path.join(results_dir, "labels_per_iter.csv")
    np.savetxt(labels_path, labels_per_iter)
    plots.draw_label_heatmap(np.asarray(labels_per_iter), os.path.join(
        results_dir, 'output', "z_over_iters.pdf"))


# TODO: write docstring
def write_llhs(alt_llhs_per_iter, null_llhs_per_iter, alt_int_per_iter,
               null_nonint_per_iter, total_llhs_per_iter, results_dir, test,
               all_true_int, all_true_nonint, all_true):
    """
    Write the different log-likelihoods to disk.

    Arguments
    ---------
    alt_llhs_per_iter:
    null_llhs_per_iter:
    alt_int_per_iter:
    null_nonint_per_iter:
    total_llhs_per_iter:
    results_dir:
    test:
    all_true_int:
    all_true_nonint:
    all_true:

    Returns
    -------
    None
    """
    alt_llhs_path = os.path.join(results_dir, "all_alt_llhs.csv")
    np.savetxt(alt_llhs_path, alt_llhs_per_iter)
    null_llhs_path = os.path.join(results_dir, "all_null_llhs.csv")
    np.savetxt(null_llhs_path, null_llhs_per_iter)
    int_llhs_path = os.path.join(results_dir, "all_int_llhs.csv")
    np.savetxt(int_llhs_path, alt_int_per_iter)
    nonint_llhs_path = os.path.join(results_dir, "all_nonint_llhs.csv")
    np.savetxt(nonint_llhs_path, null_nonint_per_iter)
    total_llhs_path = os.path.join(results_dir, "all_total_llhs.csv")
    np.savetxt(total_llhs_path, total_llhs_per_iter)

    if test:
        true_int_path = os.path.join(results_dir, "true_int_llhs.csv")
        np.savetxt(true_int_path, all_true_int)
        true_nonint_path = os.path.join(results_dir, "true_nonint_llhs.csv")
        np.savetxt(true_nonint_path, all_true_nonint)
        true_total_path = os.path.join(results_dir, "true_total_llhs.csv")
        np.savetxt(true_total_path, all_true)


def draw_confusion_matrices(true_labels, pred_labels, mode, checks_dir):
    """
    Make confusion matrices plots and save them to disk.

    Arguments
    ---------
    true_labels:    array-like, contains ground truth labels
    pred_labels:    array-like, contains final values of the hiddden variables
    mode:           str, whether we are doing 'soft' or 'hard' EM
    checks_dir:     str, path to save the file to

    Returns
    -------
    None
    """
    if mode == 'hard':
        plots.make_confusion_matrices(true_labels, pred_labels, checks_dir)
    elif mode == 'soft':
        plots.make_confusion_matrices(
            true_labels, round_labels(pred_labels), checks_dir)


def write_model_report(true_labels, pred_labels, mode, checks_dir):
    """
    Write a text file containing performance metrics.

    Arguments
    ---------
    true_labels:    array-like, contains ground truth labels
    pred_labels:    array-like, contains final values of the hiddden variables
    mode:           str, whether we are doing 'soft' or 'hard' EM
    checks_dir:     str, path to save the file to
    Returns
    -------
    None
    """
    # Calculate performance metrics
    if mode == 'hard':  # Matthews Correlation Coefficient
        # TODO: is MCC defined for only one class?
        mcc = matthews_corrcoef(true_labels, pred_labels)
        perf_str = ":".join(["Matthews Correlation Coefficient", str(mcc)])
    elif mode == 'soft':  # Cross-entropy loss & MCC
        if len(set(true_labels)) > 1:
            cross = log_loss(true_labels, pred_labels)
            mcc = matthews_corrcoef(
                true_labels, round_labels(pred_labels))
        else:
            # For test cases with only one class
            # Metrics not defined for only one class
            cross = "NA"
            mcc = "NA"
        perf_str = "".join(['Cross-entropy loss:', str(cross), '\n',
                            'Matthews Correlation Coefficient:', str(mcc)])

    report = os.path.join(checks_dir, "model_report.txt")
    with open(report, "w") as target:
        target.write("".join([perf_str, "\n"]))