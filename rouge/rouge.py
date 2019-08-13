# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six
import rouge.rouge_score as rouge_score
import io
import os
import copy


class FilesRouge:
    def __init__(self, hyp_path, ref_path, metrics=None, stats=None,
                 batch_lines=None):
        assert(os.path.isfile(hyp_path))
        assert(os.path.isfile(ref_path))

        self.rouge = Rouge(metrics=metrics, stats=stats)

        def line_count(path):
            count = 0
            with open(path, "rb") as f:
                for line in f:
                    count += 1
            return count

        hyp_lc = line_count(hyp_path)
        ref_lc = line_count(ref_path)
        assert(hyp_lc == ref_lc)

        assert(batch_lines is None or type(batch_lines) == int)

        self.hyp_path = hyp_path
        self.ref_path = ref_path
        self.batch_lines = batch_lines

    def get_scores(self, avg=False, ignore_empty=False):
        """Calculate ROUGE scores between each pair of
        lines (hyp_file[i], ref_file[i]).
        Args:
          * hyp_path: hypothesis file path
          * ref_path: references file path
          * avg (False): whether to get an average scores or a list
        """
        hyp_path, ref_path = self.hyp_path, self.ref_path

        with io.open(hyp_path, encoding="utf-8", mode="r") as hyp_file:
            hyps = [line[:-1] for line in hyp_file]
        with io.open(ref_path, encoding="utf-8", mode="r") as ref_file:
            refs = [line[:-1] for line in ref_file]

        return self.rouge.get_scores(hyps, refs, avg=avg,
                                     ignore_empty=ignore_empty)


class Rouge:
    DEFAULT_METRICS = ["rouge-1", "rouge-2", "rouge-l"]
    AVAILABLE_METRICS = {
        "rouge-1": lambda hyp, ref: rouge_score.rouge_n(hyp, ref, 1),
        "rouge-2": lambda hyp, ref: rouge_score.rouge_n(hyp, ref, 2),
        "rouge-l": lambda hyp, ref:
            rouge_score.rouge_l_summary_level(hyp, ref),
    }
    DEFAULT_STATS = ["f", "p", "r"]
    AVAILABLE_STATS = ["f", "p", "r"]

    def __init__(self, metrics=None, stats=None):
        if metrics is not None:
            self.metrics = [m.lower() for m in metrics]

            for m in self.metrics:
                if m not in Rouge.AVAILABLE_METRICS:
                    raise ValueError("Unknown metric '%s'" % m)
        else:
            self.metrics = Rouge.DEFAULT_METRICS

        if stats is not None:
            self.stats = [s.lower() for s in stats]

            for s in self.stats:
                if s not in Rouge.AVAILABLE_STATS:
                    raise ValueError("Unknown stat '%s'" % s)
        else:
            self.stats = Rouge.DEFAULT_STATS

    def get_scores(self, hyps, refs, avg=False, ignore_empty=False):
        if isinstance(hyps, six.string_types):
            hyps, refs = [hyps], [refs]

        if ignore_empty:
            # Filter out hyps of 0 length
            hyps_and_refs = zip(hyps, refs)
            hyps_and_refs = [_ for _ in hyps_and_refs if len(_[0]) > 0]
            hyps, refs = zip(*hyps_and_refs)

        assert(type(hyps) == type(refs))
        assert(len(hyps) == len(refs))

        if not avg:
            return self._get_scores(hyps, refs)
        return self._get_avg_scores(hyps, refs)

    def _get_scores(self, hyps, refs):
        scores = []
        for hyp, ref in zip(hyps, refs):
            sen_score = {}
            hyp = [" ".join(_.split()) for _ in hyp.split(".") if len(_) > 0]
            ref = [" ".join(_.split()) for _ in ref.split(".") if len(_) > 0]

            for m in self.metrics:
                fn = Rouge.AVAILABLE_METRICS[m]
                sc = fn(hyp, ref)
                sen_score[m] = {s: sc[s] for s in self.stats}
            scores.append(sen_score)
        return scores

    def _get_avg_scores(self, hyps, refs):
        scores = {m: {s: 0 for s in self.stats} for m in self.metrics}

        count = 0
        for (hyp, ref) in zip(hyps, refs):
            original_hyp = copy.deepcopy(hyp)
            hyp = [" ".join(_.split()) for _ in hyp.split(".") if len(_) > 0]
            ref = [" ".join(_.split()) for _ in ref.split(".") if len(_) > 0]
            # fix the bug when hypothesis is simply a period.
            if len(hyp) == 0 and original_hyp == ["."]:
                hyp = ["."]

            for m in self.metrics:
                fn = Rouge.AVAILABLE_METRICS[m]
                sc = fn(hyp, ref)
                scores[m] = {s: scores[m][s] + sc[s] for s in self.stats}
            count += 1
        scores = {m: {s: scores[m][s] / count for s in scores[m]}
                  for m in scores}
        return scores
