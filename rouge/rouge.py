# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six
import rouge.rouge_score as rouge_score
import io
import os


def exclude_ngrams(sequence, n, exclude_ngrams):
    from nltk import ngrams
    sg = ngrams(sequence.split(), n)
    for g in sg:
        if g in exclude_ngrams:
            sequence = sequence.replace(" ".join(g), "").strip()
    return sequence


def exclude_sequences(hyps, refs, excludes, max_n=10, min_n=2):
    assert len(hyps) == len(refs)
    assert len(excludes) == len(hyps)
    assert max_n > min_n

    xhyps = []
    xrefs = []
    for i, (h, r, e) in enumerate(zip(hyps, refs, excludes)):
        for n in range(max_n, min_n, -1):
            eg = list(ngrams(e.split(), n))
            h = exclude_ngrams(h, n, eg)
            r = exclude_ngrams(r, n, eg)
        xhyps.append(h)
        xrefs.append(r)
    return xhyps, xrefs


class FilesRouge:
    def __init__(self, *args, **kwargs):
        """See the `Rouge` class for args
        """
        self.rouge = Rouge(*args, **kwargs)

    def _check_files(self, *paths):
        def line_count(path):
            count = 0
            with open(path, "rb") as f:
                for line in f:
                    count += 1
            return count

        lc = None
        for path in paths:
            if path is None:
                continue

            assert os.path.isfile(path), "AssertionError on " + path
            _lc = line_count(path)
            if lc is None:
                lc = _lc
            else:
                assert lc == _lc, "AssertionError on " + path

    def get_scores(self, hyp_path, ref_path, exclude_path=None, **kwargs):
        """Calculate ROUGE scores between each pair of
        lines (hyp_file[i], ref_file[i]).
        Args:
          * hyp_path: hypothesis file path
          * ref_path: references file path
          * **kwargs: see `Rouge.get_scores` for doc
        """
        self._check_files(hyp_path, ref_path, exclude_path)

        def read(path):
            with io.open(path, encoding="utf-8", mode="r") as f:
                return [line.strip() for line in f]

        hyps = read(hyp_path)
        refs = read(ref_path)
        exclude = read(exclude_path) if exclude_path is not None else None
        return self.rouge.get_scores(hyps, refs, exclude=exclude, **kwargs)


class Rouge:
    DEFAULT_METRICS = ["rouge-1", "rouge-2", "rouge-l"]
    AVAILABLE_METRICS = {
        "rouge-1": lambda hyp, ref, **k: rouge_score.rouge_n(hyp, ref, 1, **k),
        "rouge-2": lambda hyp, ref, **k: rouge_score.rouge_n(hyp, ref, 2, **k),
        "rouge-3": lambda hyp, ref, **k: rouge_score.rouge_n(hyp, ref, 3, **k),
        "rouge-4": lambda hyp, ref, **k: rouge_score.rouge_n(hyp, ref, 4, **k),
        "rouge-5": lambda hyp, ref, **k: rouge_score.rouge_n(hyp, ref, 5, **k),
        "rouge-l": lambda hyp, ref, **k:
            rouge_score.rouge_l_summary_level(hyp, ref, **k),
    }
    DEFAULT_STATS = ["r", "p", "f"]
    AVAILABLE_STATS = ["r", "p", "f"]

    def __init__(self, metrics=None, stats=None, return_lengths=False,
                 raw_results=False, exclusive=True):
        self.return_lengths = return_lengths
        self.raw_results = raw_results
        self.exclusive = exclusive

        if metrics is not None:
            self.metrics = [m.lower() for m in metrics]

            for m in self.metrics:
                if m not in Rouge.AVAILABLE_METRICS:
                    raise ValueError("Unknown metric '%s'" % m)
        else:
            self.metrics = Rouge.DEFAULT_METRICS

        if self.raw_results:
            self.stats = ["hyp", "ref", "overlap"]
        else:
            if stats is not None:
                self.stats = [s.lower() for s in stats]

                for s in self.stats:
                    if s not in Rouge.AVAILABLE_STATS:
                        raise ValueError("Unknown stat '%s'" % s)
            else:
                self.stats = Rouge.DEFAULT_STATS

    def get_scores(self, hyps, refs, avg=False, ignore_empty=False,
                   exclude=None):

        if exclude is not None:
            print("(excluding)")
            hyps, refs = exclude_sequences(hyps, refs, exclude)
            ignore_empty = True
            hyps = [
                h if h.replace(".", "").strip() != ""
                else ""
                for h in hyps
            ]
            refs = [
                r if r.replace(".", "").strip() != ""
                else ""
                for r in refs
            ]
        if isinstance(hyps, six.string_types):
            hyps, refs = [hyps], [refs]

        if ignore_empty:
            # Filter out hyps of 0 length
            hyps_and_refs = zip(hyps, refs)
            hyps_and_refs = [_ for _ in hyps_and_refs
                             if len(_[0]) > 0
                             and len(_[1]) > 0]
            hyps, refs = zip(*hyps_and_refs)

        assert(isinstance(hyps, type(refs)))
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
                sc = fn(
                    hyp,
                    ref,
                    raw_results=self.raw_results,
                    exclusive=self.exclusive)
                sen_score[m] = {s: sc[s] for s in self.stats}

            if self.return_lengths:
                lengths = {
                    "hyp": len(" ".join(hyp).split()),
                    "ref": len(" ".join(ref).split())
                }
                sen_score["lengths"] = lengths
            scores.append(sen_score)
        return scores

    def _get_avg_scores(self, hyps, refs):
        scores = {m: {s: 0 for s in self.stats} for m in self.metrics}
        if self.return_lengths:
            scores["lengths"] = {"hyp": 0, "ref": 0}

        count = 0
        for (hyp, ref) in zip(hyps, refs):
            hyp = [" ".join(_.split()) for _ in hyp.split(".") if len(_) > 0]
            ref = [" ".join(_.split()) for _ in ref.split(".") if len(_) > 0]

            for m in self.metrics:
                fn = Rouge.AVAILABLE_METRICS[m]
                sc = fn(hyp, ref, exclusive=self.exclusive)
                scores[m] = {s: scores[m][s] + sc[s] for s in self.stats}

            if self.return_lengths:
                scores["lengths"]["hyp"] += len(" ".join(hyp).split())
                scores["lengths"]["ref"] += len(" ".join(ref).split())

            count += 1
        avg_scores = {
            m: {s: scores[m][s] / count for s in self.stats}
            for m in self.metrics
        }

        if self.return_lengths:
            avg_scores["lengths"] = {
                k: scores["lengths"][k] / count
                for k in ["hyp", "ref"]
            }

        return avg_scores
