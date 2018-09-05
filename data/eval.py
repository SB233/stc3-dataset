#!/usr/bin/env python3
"""
Evaluation script for ND and DQ subtasks, STC-3 Task, NTCIR-14
https://sakai-lab.github.io/stc3-dataset

Usage: https://sakai-lab.github.io/stc3-dataset/#evaluation
Math details: https://waseda.app.box.com/v/SIGIR2018preprint

Author: Zhaohao Zeng <zhaohao@fuji.waseda.jp>
"""

from __future__ import division
from __future__ import print_function

import json
import sys
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy

import numpy as np
from scipy import stats

parser = ArgumentParser()
parser.add_argument("--alpha", type=float, default=.5)

C_NUGGET_TYPES = ('CNUG0', 'CNUG', 'CNUG*', 'CNaN')
H_NUGGET_TYPES = ('HNUG', 'HNUG*', 'HNaN')
QUALITY_SCALES = ('2', '1', '0', '-1', '-2')


def normalize(pred, truth):
    """ convert inputs to np.array and make sure 
    inputs are normalized probability distributions
    """
    if len(pred) != len(truth):
        raise ValueError("pred and truth have different lengths")
    if len(pred) == 0 or len(truth) == 0:
        raise ValueError("pred or truth are empty")

    pred, truth = np.asarray(pred), np.asarray(truth)
    if not ((pred >= 0).all() and (truth >= 0).all()):
        raise ValueError("probability distribution should not be negative")
    pred, truth = pred / pred.sum(), truth / truth.sum()
    return pred, truth


def normalized_match_dist(pred, truth):
    """NMD: Normalized Match Distance"""
    pred, truth = normalize(pred, truth)
    cum_p, cum_q = np.cumsum(pred), np.cumsum(truth)
    return (np.abs(cum_p - cum_q)).sum() / (len(pred) - 1.)


def distance_weighted(pred, truth, i):
    return np.sum([np.abs(i - j) * ((pred[j] - truth[j]) ** 2) for j in range(len(pred))])


def order_aware_div(pred, truth):
    return np.mean([distance_weighted(pred, truth, i) for i in range(len(truth))])


def rsnod(pred, truth):
    """ RSNOD: Root Symmetric Normalised Order-Aware Divergence
    """

    pred, truth = normalize(pred, truth)
    sod = (order_aware_div(pred, truth) + order_aware_div(truth, pred)) / 2.
    return np.sqrt((sod / (len(pred) - 1)))


def root_normalized_squared_error(pred, truth):
    """ RNSS: Root Normalised Sum of Squares
    """

    def squared_error(pred, truth):
        return ((pred - truth) ** 2).sum()

    pred, truth = normalize(pred, truth)
    return np.sqrt(squared_error(pred, truth) / 2)


def jensen_shannon_div(pred, truth, base=2):
    ''' JSD: Jensen-Shannon Divergence
    '''
    pred, truth = normalize(pred, truth)
    m = 1. / 2 * (pred + truth)
    return (stats.entropy(pred, m, base=base)
            + stats.entropy(truth, m, base=base)) / 2.


def evaluate_nugget(id2pred, id2truth, alpha=.5):
    def _evaluate_nugget(measure):
        def _truth2prob(labels, nugget_types):
            c = Counter(labels)
            prob = []
            for nugget_type in nugget_types:
                prob.append(c.get(nugget_type, 0))
            prob = np.array(prob, dtype=np.float64)
            prob /= prob.sum()
            return prob

        def _pred_2_prob(score_dict, nugget_types):
            score_dict = deepcopy(score_dict)
            prob = np.array([score_dict.pop(nugget_type, 0)
                             for nugget_type in nugget_types])
            if score_dict: raise ValueError("contain illegal nugget type in prediction")
            return prob

        dialog_scores = []
        for idx, prediction in id2pred.items():
            if idx not in id2truth:
                print("prediction id %s is not in the ground truth json, skipped"
                      % idx)
                continue
            truth = id2truth[idx]
            prediction = prediction["nugget"]
            is_customer = [t["sender"] == "customer" for t in truth["turns"]]
            if len(is_customer) != len(prediction):
                raise ValueError("#turns != #nugget_predictions")
            c_turn_scores = []
            h_turn_scores = []
            for i, turn_pred in enumerate(prediction):
                nugget_types = C_NUGGET_TYPES if is_customer[i] else H_NUGGET_TYPES
                truth_labels = (anno["nugget"][i]
                                for anno in truth["annotations"])

                truth_prob = _truth2prob(truth_labels, nugget_types)
                score = measure(
                    _pred_2_prob(turn_pred, nugget_types),
                    truth_prob)
                if is_customer[i]:
                    c_turn_scores.append(score)
                else:
                    h_turn_scores.append(score)
            dialog_scores.append(np.mean(c_turn_scores) * alpha + np.mean(h_turn_scores) * (1 - alpha))
        return np.mean(dialog_scores)

    return {
        "jsd": _evaluate_nugget(jensen_shannon_div),
        "rnss": _evaluate_nugget(root_normalized_squared_error)}


def evaluate_quality(id2pred, id2truth):
    def _evaluate_quality(measure):
        def _truth2prob(labels):
            c = Counter(labels)
            prob = []
            for scale in QUALITY_SCALES:
                score = c.pop(scale, 0)
                prob.append(score)
            prob = np.array(prob, dtype=np.float64)
            prob /= prob.sum()
            return prob

        def _pred_2_prob(score_dict):
            score_dict = deepcopy(score_dict)
            prob = np.array(
                [score_dict.pop(scale, 0) for scale in QUALITY_SCALES])
            if score_dict: raise ValueError("contain illegal quality scale in prediction")
            return prob

        result = {}
        for idx, prediction in id2pred.items():
            if idx not in id2truth:
                print("prediction id %s is not in the ground truth json, skipped" % idx)
                continue
            truth = id2truth[idx]
            prediction = prediction["quality"]
            for score_key in prediction:
                truth_labels = (str(anno["quality"][score_key])
                                for anno in truth["annotations"])
                result.setdefault(score_key, [])
                score = measure(
                    _pred_2_prob(prediction[score_key]),
                    _truth2prob(truth_labels))
                result[score_key].append(score)

        for key, value in result.items():
            result[key] = np.mean(value)
        return result

    return {
        "rsnod": _evaluate_quality(rsnod),
        "nmd": _evaluate_quality(normalized_match_dist)}


def evaluate(pred, truth, alpha=.5):
    if not pred:
        raise ValueError("Prediction JSON is empty")
    if not truth:
        raise ValueError("Ground truth JSON is empty")

    id2pred = {d["id"]: d for d in pred}
    id2truth = {d["id"]: d for d in truth}
    results = {"quality": None, "nugget": None}

    if pred[0].get("nugget", None) is not None:
        nugget_result = evaluate_nugget(id2pred, id2truth, alpha=alpha)
        results["nugget"] = nugget_result

    if pred[0].get("quality", None) is not None:
        quality_result = evaluate_quality(id2pred, id2truth)
        results["quality"] = quality_result

    return results


def main():
    FLAGS, _ = parser.parse_known_args()

    if len(sys.argv) != 3:
        raise ValueError(
            "Expected two arguments  <submission.json>  <ground_truth.json> , received %d"
            % (len(sys.argv) - 1))

    _, pred_path, truth_path = sys.argv
    pred = json.load(open(pred_path, encoding="utf-8"))
    truth = json.load(open(truth_path, encoding="utf-8"))
    result = evaluate(pred, truth, alpha=FLAGS.alpha)

    print(result)
    return result


if __name__ == "__main__":
    main()
