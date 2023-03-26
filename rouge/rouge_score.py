# -*- coding: utf-8 -*-
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""ROUGE Metric Implementation

This is a very slightly version of:
https://github.com/pltrdy/seq2seq/blob/master/seq2seq/metrics/rouge.py

---

ROUGe metric implementation.

This is a modified and slightly extended verison of
https://github.com/miso-belica/sumy/blob/dev/sumy/evaluation/rouge.py.
"""
from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
import itertools

from copy import deepcopy


class Ngrams(object):
    """
        Ngrams datastructure based on `set` or `list`
        depending in `exclusive`
    """

    def __init__(self, ngrams={}, exclusive=True):
        if exclusive:
            self._ngrams = set(ngrams)
        else:
            self._ngrams = list(ngrams)
        self.exclusive = exclusive

    def add(self, o):
        if self.exclusive:
            self._ngrams.add(o)
        else:
            self._ngrams.append(o)

    def __len__(self):
        return len(self._ngrams)

    def intersection(self, o):
        if self.exclusive:
            inter_set = self._ngrams.intersection(o._ngrams)
            return Ngrams(inter_set, exclusive=True)
        else:
            other_list = deepcopy(o._ngrams)
            inter_list = []

            for e in self._ngrams:
                try:
                    i = other_list.index(e)
                except ValueError:
                    continue
                other_list.pop(i)
                inter_list.append(e)
            return Ngrams(inter_list, exclusive=False)

    def union(self, *ngrams):
        if self.exclusive:
            union_set = self._ngrams
            for o in ngrams:
                union_set = union_set.union(o._ngrams)
            return Ngrams(union_set, exclusive=True)
        else:
            union_list = deepcopy(self._ngrams)
            for o in ngrams:
                union_list.extend(o._ngrams)
            return Ngrams(union_list, exclusive=False)


def _get_ngrams(n, text, exclusive=True):
    """Calcualtes n-grams.

    Args:
      n: which n-grams to calculate
      text: An array of tokens

    Returns:
      A set of n-grams
    """
    ngram_set = Ngrams(exclusive=exclusive)
    text_length = len(text)
    max_index_ngram_start = text_length - n
    for i in range(max_index_ngram_start + 1):
        ngram_set.add(tuple(text[i:i + n]))
    return ngram_set


def _split_into_words(sentences):
    """Splits multiple sentences into words and flattens the result"""
    return list(itertools.chain(*[_.split(" ") for _ in sentences]))


def _get_word_ngrams(n, sentences, exclusive=True):
    """Calculates word n-grams for multiple sentences.
    """
    assert len(sentences) > 0
    assert n > 0

    words = _split_into_words(sentences)
    return _get_ngrams(n, words, exclusive=exclusive)


def _len_lcs(x, y):
    """
    Returns the length of the Longest Common Subsequence between sequences x
    and y.
    Source: http://www.algorithmist.com/index.php/Longest_Common_Subsequence

    Args:
      x: sequence of words
      y: sequence of words

    Returns
      integer: Length of LCS between x and y
    """
    table = _lcs(x, y)
    n, m = len(x), len(y)
    return table[n, m]


def _lcs(x, y):
    """
    Computes the length of the longest common subsequence (lcs) between two
    strings. The implementation below uses a DP programming algorithm and runs
    in O(nm) time where n = len(x) and m = len(y).
    Source: http://www.algorithmist.com/index.php/Longest_Common_Subsequence

    Args:
      x: collection of words
      y: collection of words

    Returns:
      Table of dictionary of coord and len lcs
    """
    n, m = len(x), len(y)
    table = dict()
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 or j == 0:
                table[i, j] = 0
            elif x[i - 1] == y[j - 1]:
                table[i, j] = table[i - 1, j - 1] + 1
            else:
                table[i, j] = max(table[i - 1, j], table[i, j - 1])
    return table


def _recon_lcs(x, y, exclusive=True):
    """
    Returns the Longest Subsequence between x and y.
    Source: http://www.algorithmist.com/index.php/Longest_Common_Subsequence

    Args:
      x: sequence of words
      y: sequence of words

    Returns:
      sequence: LCS of x and y
    """
    table = _lcs(x, y)
    res = []
    i, j = len(x), len(y)
    while i > 0 and j > 0:
        if x[i-1] == y[j-1]:
            res.append(x[i-1])
            i -= 1
            j -= 1
        elif table[i - 1, j] > table[i, j - 1]:
            i -= 1
        else:
            j -= 1

    return Ngrams(res[::-1], exclusive=exclusive)

def multi_rouge_n(sequences, scores_ids, n=2, exclusive=True):
    """
    Efficient way to compute highly repetitive scoring
    i.e. sequences are involved multiple time

    Args:
        sequences(list[str]): list of sequences (either hyp or ref)
        scores_ids(list[tuple(int)]): list of pairs (hyp_id, ref_id)
            ie. scores[i] = rouge_n(scores_ids[i][0],
                                    scores_ids[i][1])

    Returns:
        scores: list of length `len(scores_ids)` containing rouge `n`
                scores as a dict with 'f', 'r', 'p'
    Raises:
        KeyError: if there's a value of i in scores_ids that is not in
                  [0, len(sequences)[
    """
    ngrams = [_get_word_ngrams(n, sequence, exclusive=exclusive)
              for sequence in sequences]
    counts = [len(ngram) for ngram in ngrams]

    scores = []
    for hyp_id, ref_id in scores_ids:
        evaluated_ngrams = ngrams[hyp_id]
        evaluated_count = counts[hyp_id]

        reference_ngrams = ngrams[ref_id]
        reference_count = counts[ref_id]

        overlapping_ngrams = evaluated_ngrams.intersection(reference_ngrams)
        overlapping_count = len(overlapping_ngrams)

        scores += [f_r_p_rouge_n(evaluated_count,
                                 reference_count, overlapping_count)]
    return scores


def rouge_n(evaluated_sentences, reference_sentences,
            n=2, raw_results=False, exclusive=True):
    """
    Computes ROUGE-N of two text collections of sentences.
    Sourece: http://research.microsoft.com/en-us/um/people/cyl/download/
    papers/rouge-working-note-v1.3.1.pdf

    Args:
      evaluated_sentences: The sentences that have been picked by the
                           summarizer
      reference_sentences: The sentences from the referene set
      n: Size of ngram.  Defaults to 2.

    Returns:
      A tuple (f1, precision, recall) for ROUGE-N

    Raises:
      ValueError: raises exception if a param has len <= 0
    """
    if len(evaluated_sentences) <= 0:
        raise ValueError("Hypothesis is empty.")
    if len(reference_sentences) <= 0:
        raise ValueError("Reference is empty.")

    evaluated_ngrams = _get_word_ngrams(
        n, evaluated_sentences, exclusive=exclusive)
    reference_ngrams = _get_word_ngrams(
        n, reference_sentences, exclusive=exclusive)
    reference_count = len(reference_ngrams)
    evaluated_count = len(evaluated_ngrams)

    # Gets the overlapping ngrams between evaluated and reference
    overlapping_ngrams = evaluated_ngrams.intersection(reference_ngrams)
    overlapping_count = len(overlapping_ngrams)

    if raw_results:
        o = {
            "hyp": evaluated_count,
            "ref": reference_count,
            "overlap": overlapping_count
        }
        return o
    else:
        return f_r_p_rouge_n(
            evaluated_count, reference_count, overlapping_count)


def f_r_p_rouge_n(evaluated_count, reference_count, overlapping_count):
    # Handle edge case. This isn't mathematically correct, but it's good enough
    if evaluated_count == 0:
        precision = 0.0
    else:
        precision = overlapping_count / evaluated_count

    if reference_count == 0:
        recall = 0.0
    else:
        recall = overlapping_count / reference_count

    f1_score = 2.0 * ((precision * recall) / (precision + recall + 1e-8))

    return {"f": f1_score, "p": precision, "r": recall}


def _union_lcs(evaluated_sentences, reference_sentence,
               prev_union=None, exclusive=True):
    """
    Returns LCS_u(r_i, C) which is the LCS score of the union longest common
    subsequence between reference sentence ri and candidate summary C.
    For example:
    if r_i= w1 w2 w3 w4 w5, and C contains two sentences: c1 = w1 w2 w6 w7 w8
    and c2 = w1 w3 w8 w9 w5, then the longest common subsequence of r_i and c1
    is "w1 w2" and the longest common subsequence of r_i and c2 is "w1 w3 w5".
    The union longest common subsequence of r_i, c1, and c2 is "w1 w2 w3 w5"
    and LCS_u(r_i, C) = 4/5.

    Args:
      evaluated_sentences: The sentences that have been picked by the
                           summarizer
      reference_sentence: One of the sentences in the reference summaries

    Returns:
      float: LCS_u(r_i, C)

    ValueError:
      Raises exception if a param has len <= 0
    """
    if prev_union is None:
        prev_union = Ngrams(exclusive=exclusive)

    if len(evaluated_sentences) <= 0:
        raise ValueError("Collections must contain at least 1 sentence.")

    lcs_union = prev_union
    prev_count = len(prev_union)
    reference_words = _split_into_words([reference_sentence])

    combined_lcs_length = 0
    for eval_s in evaluated_sentences:
        evaluated_words = _split_into_words([eval_s])
        lcs = _recon_lcs(reference_words, evaluated_words, exclusive=exclusive)
        combined_lcs_length += len(lcs)
        lcs_union = lcs_union.union(lcs)

    new_lcs_count = len(lcs_union) - prev_count
    return new_lcs_count, lcs_union


def rouge_l_summary_level(
        evaluated_sentences, reference_sentences, raw_results=False, exclusive=True, **_):
    """
    Computes ROUGE-L (summary level) of two text collections of sentences.
    http://research.microsoft.com/en-us/um/people/cyl/download/papers/rouge-working-note-v1.3.1.pdf

    Calculated according to:
    R_lcs = SUM(1, u)[LCS<union>(r_i,C)]/m
    P_lcs = SUM(1, u)[LCS<union>(r_i,C)]/n
    F_lcs = (2*R_lcs*P_lcs) / (R_lcs * P_lcs)

    where:
    SUM(i,u) = SUM from i through u
    u = number of sentences in reference summary
    C = Candidate summary made up of v sentences
    m = number of words in reference summary
    n = number of words in candidate summary

    Args:
      evaluated_sentences: The sentences that have been picked by the
                           summarizer
      reference_sentence: One of the sentences in the reference summaries

    Returns:
      A float: F_lcs

    Raises:
      ValueError: raises exception if a param has len <= 0
    """
    if len(evaluated_sentences) <= 0 or len(reference_sentences) <= 0:
        raise ValueError("Collections must contain at least 1 sentence.")

    # total number of words in reference sentences
    m = len(
        Ngrams(
            _split_into_words(reference_sentences),
            exclusive=exclusive))

    # total number of words in evaluated sentences
    n = len(
        Ngrams(
            _split_into_words(evaluated_sentences),
            exclusive=exclusive))

    # print("m,n %d %d" % (m, n))
    union_lcs_sum_across_all_references = 0
    union = Ngrams(exclusive=exclusive)
    for ref_s in reference_sentences:
        lcs_count, union = _union_lcs(evaluated_sentences,
                                      ref_s,
                                      prev_union=union,
                                      exclusive=exclusive)
        union_lcs_sum_across_all_references += lcs_count

    llcs = union_lcs_sum_across_all_references
    r_lcs = llcs / m
    p_lcs = llcs / n

    f_lcs = 2.0 * ((p_lcs * r_lcs) / (p_lcs + r_lcs + 1e-8))

    if raw_results:
        o = {
            "hyp": n,
            "ref": m,
            "overlap": llcs
        }
        return o
    else:
        return {"f": f_lcs, "p": p_lcs, "r": r_lcs}
