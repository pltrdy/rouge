# -*- coding: utf-8 -*-
from __future__ import absolute_import
import rouge.rouge_score as rouge_score
import os
import numpy as np

class FilesRouge:
  def __init__(self, hyp_path, ref_path, metrics=None, stats=None, batch_lines=None):
    assert(os.path.isfile(hyp_path))
    assert(os.path.isfile(ref_path))

    self.rouge = Rouge(metrics=metrics, stats=stats)

    def line_count(path):
      count = 0
      for line in open(path):
        count += 1
      return count

    hyp_lc = line_count(hyp_path)
    ref_lc = line_count(ref_path)
    assert(hyp_lc == ref_lc)

    assert(batch_lines is None or type(batch_lines) == int)

    self.hyp_path = hyp_path
    self.ref_path = ref_path
    self.batch_lines = batch_lines
  
  def get_scores(self, avg=False):
    """Calculate ROUGE scores between each pair of 
    lines (hyp_file[i], ref_file[i]).
    Args:
      * hyp_path: hypothesis file path
      * ref_path: references file path
      * avg (False): whether to get an average scores or a list
      * batch_line(None): set it to an integer value to work with
        subsets of `batch_line` lines (uses less memory)
    """
    batch_lines = self.batch_lines
    hyp_path, ref_path = self.hyp_path, self.ref_path

    if batch_lines is None:
      hyps = [line[:-1] for line in open(hyp_path).readlines()]
      refs = [line[:-1] for line in open(ref_path).readlines()]
     
      
      return self.rouge.get_scores(hyps, refs, avg=avg)

    else:
      if batch_lines > hyp_lc:
        batch_lines = hyp_lc
      
      if avg:
        sc = [0, 0, 0]
        update_scores = lambda s, h, r: [sum(x) for x in zip(s, self.rouge.get_scores(h, r, avg=True))]
      else:
        sc = []
        update_scores = lambda s, h, r: s + self.rouge.get_scores(batch_hyp, batch_ref)

      hyp_file = open(hyp_path)
      ref_file = open(ref_path)
      
      batch_hyp = []
      batch_ref = []

      for count in range(hyp_lc):
        batch_hyp.append(hyp_file.readline()[:-1])
        batch_ref.append(ref_file.readline()[:-1])

        count += 1
        if count == batch_lines:
          sc = update_scores(sc, batch_hyp, batch_ref)
          count = 0
          batch_hyp = []
          batch_ref = []

      if avg:
        return [s/hyp_lc for s in sc]
      return sc


class Rouge:
  DEFAULT_METRICS = ["rouge-1", "rouge-2", "rouge-l"]
  AVAILABLE_METRICS = {"rouge-1": lambda hyp, ref: rouge_score.rouge_n([hyp], [ref], 1), 
                       "rouge-2": lambda hyp, ref: rouge_score.rouge_n([hyp], [ref], 2),
                       "rouge-l": lambda hyp, ref: rouge_score.rouge_l_sentence_level([hyp], [ref]),
                      }

  DEFAULT_STATS = ["f", "p", "r"]
  AVAILABLE_STATS = {"f": 0, "p": 1, "r": 2
  }
  def __init__(self, metrics=None, stats=None):
    self.metrics = metrics if metrics is not None else Rouge.DEFAULT_METRICS
    self.stats = stats if stats is not None else Rouge.DEFAULT_STATS
    
    for m in self.metrics:
      if m not in Rouge.AVAILABLE_METRICS:
        raise ValueError("Unknown metric '%s'" % m)

    for s in self.stats:
      if s not in Rouge.AVAILABLE_STATS:
        raise ValueError("Unknown stat '%s'" % s)
  
  def get_scores(self, hyps, refs, avg=False):
    if type(hyps) == str:
      hyps, refs = [hyps], [refs]

    assert(type(hyps) == type(refs))
    assert(len(hyps) == len(refs))
    
    if not avg:
      return self._get_scores(hyps, refs)
    return self._get_avg_scores(hyps, refs)

  def _get_scores(self, hyps, refs):
    scores = []
    for hyp, ref in zip(hyps, refs):
      sen_score = {}
      for m in self.metrics:
        fn = Rouge.AVAILABLE_METRICS[m] 
        sc = fn(hyp, ref)
        sen_score[m] = {s: sc[Rouge.AVAILABLE_STATS[s]] for s in self.stats}
      scores.append(sen_score)
    return scores

  def _get_avg_scores(self, hyps, refs):
    scores = {}
    for m in self.metrics:
      fn = Rouge.AVAILABLE_METRICS[m]
      sc = [fn(hyp, ref) for hyp, ref in zip(hyps, refs)]
      sc = [[sen_sc[Rouge.AVAILABLE_STATS[s]] for s in self.stats] for sen_sc in sc]
      scores[m] = {s: st for s, st in zip(self.stats, tuple(map(np.mean, zip(*sc))))}
    return scores


