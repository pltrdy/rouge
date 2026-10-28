#!/usr/bin/env python3
import argparse
import json
import os
from rouge import Rouge, FilesRouge


METRICS_CHOICES = {k.split('rouge-')[1].upper(): k
                   for k in Rouge.AVAILABLE_METRICS.keys()}
STATS_CHOICES = [s.upper() for s in Rouge.AVAILABLE_STATS]


def main():
    parser = argparse.ArgumentParser(description='Rouge Metric Calculator')
    parser.add_argument('-f', '--file', help="File mode", action='store_true')
    parser.add_argument('-a', '--avg', help="Average mode",
                        action='store_true')
    parser.add_argument('--ignore_empty', action='store_true',
                        help="Ignore empty hypothesis")
    parser.add_argument('hypothesis', type=str, help='Text of file path')
    parser.add_argument('reference', type=str, help='Text or file path')
    parser.add_argument("--metrics", nargs="+", type=str.upper,
                        choices=METRICS_CHOICES.keys(),
                        help="Metrics to use (default=all)")
    parser.add_argument("--stats", nargs="+", type=str.upper,
                        choices=STATS_CHOICES,
                        help="Stats to use (default=all)")

    args = parser.parse_args()

    metrics = args.metrics
    stats = args.stats

    if metrics is not None:
        metrics = [METRICS_CHOICES[m] for m in args.metrics]

    if args.file:
        hyp, ref = args.hypothesis, args.reference
        assert(os.path.isfile(hyp))
        assert(os.path.isfile(ref))

        files_rouge = FilesRouge(metrics, stats)
        scores = files_rouge.get_scores(
            hyp, ref, avg=args.avg, ignore_empty=args.ignore_empty)

        print(json.dumps(scores, indent=2))
    else:
        hyp, ref = args.hypothesis, args.reference
        assert(isinstance(hyp, str))
        assert(isinstance(ref, str))

        rouge = Rouge(metrics, stats)
        scores = rouge.get_scores(hyp, ref, avg=args.avg)

        print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
