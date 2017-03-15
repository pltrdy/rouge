from unittest import TestCase

import rouge
import json

class BasicTest(TestCase):
  def setUp(self):
    self.hyp_path = './tests/hyp.txt'
    self.ref_path = './tests/ref.txt'

    self.data_path = './tests/data.json' 
    with open(self.data_path) as f:
      self.data = json.load(f)
    
    self.rouge = rouge.Rouge()
    self.files_rouge = rouge.FilesRouge(self.hyp_path, self.ref_path)

  def test_one_sentence(self):
    for d in self.data[:1]:
      hyp = d["hyp"]
      ref = d["ref"]
      score = self.rouge.get_scores(hyp, ref)[0]
      self.assertEqual(score, d["scores"])
  
  def test_multi_sentence(self):
    data = self.data
    hyps, refs = map(list, zip(*[[d['hyp'], d['ref']] for d in data]))
    expected_scores = [d['scores'] for d in data]
    scores = self.rouge.get_scores(hyps, refs)
    self.assertEqual(expected_scores, scores)

  def test_files_scores(self):
    data = self.data
    hyps, refs = map(list, zip(*[[d['hyp'], d['ref']] for d in data]))
    expected_scores = [d['scores'] for d in data]
    scores = self.files_rouge.get_scores()
    self.assertEqual(expected_scores, scores)
