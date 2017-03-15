#!/usr/bin/env python3
import argparse
import json
import os
from rouge import Rouge, FilesRouge

def main():
  import argparse
  parser = argparse.ArgumentParser(description='Rouge Metric Calculator')
  parser.add_argument('-f', '--file', help="File mode", action='store_true')
  parser.add_argument('-a', '--avg', help="Average mode", action='store_true')
  parser.add_argument('hypothesis', type=str, help='Text of file path')
  parser.add_argument('reference', type=str, help='Text or file path')

  args = parser.parse_args()
  if args.file:
    hyp, ref = args.hypothesis, args.reference
    assert(os.path.isfile(hyp))
    assert(os.path.isfile(ref))

    files_rouge = FilesRouge(hyp, ref)
    scores = files_rouge.get_scores(avg=args.avg)

    print(json.dumps(scores, indent=2))
  else:
    hyp, ref = args.hypothesis, args.reference
    assert(type(hyp) == str)
    assert(type(ref) == str)
    
    rouge = Rouge()
    scores = rouge.get_scores(hyp, ref, avg=args.avg)

    print(json.dumps(scores, indent=2))

if __name__ == "__main__":
  main()
