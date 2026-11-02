from unittest import TestCase
import os
import tempfile

from rouge import FilesRouge, Rouge


class WhitespaceTest(TestCase):
    def test_padding_does_not_change_scores(self):
        for exclusive in (True, False):
            for avg in (True, False):
                scorer = Rouge(exclusive=exclusive, return_lengths=True)
                for hyp, ref in [('cat', 'dog'),
                                 ('the cat sat. the dog ran',
                                  'the cat sat. the dog ran')]:
                    expected = scorer.get_scores(hyp, ref, avg=avg)
                    for suffix in ('. ', '.\t.\n', '.\u00a0'):
                        self.assertEqual(
                            scorer.get_scores(hyp + suffix, ref, avg=avg), expected)
                        self.assertEqual(
                            scorer.get_scores(hyp + suffix, ref + suffix, avg=avg), expected)

    def test_normalized_empty_inputs_raise(self):
        for metric in Rouge.DEFAULT_METRICS:
            scorer = Rouge(metrics=[metric])
            for avg in (True, False):
                for empty in (' ', '\t\n', ' . . ', '.\u00a0.'):
                    with self.assertRaises(ValueError):
                        scorer.get_scores(empty, 'cat', avg=avg)
                    with self.assertRaises(ValueError):
                        scorer.get_scores('cat', empty, avg=avg)

    def test_ignore_empty_skips_normalized_empty_pairs(self):
        scorer = Rouge()
        for avg in (True, False):
            self.assertEqual(
                scorer.get_scores([' . . ', 'cat', 'cat dog'],
                                  ['dog', '\t', 'cat dog'],
                                  avg=avg, ignore_empty=True),
                scorer.get_scores('cat dog', 'cat dog', avg=avg))

    def test_ignore_empty_without_remaining_pairs(self):
        scorer = Rouge()
        self.assertEqual(scorer.get_scores(' . . ', ' ', ignore_empty=True), [])
        with self.assertRaises(ValueError):
            scorer.get_scores(' . . ', ' ', avg=True, ignore_empty=True)

    def test_raw_overlap_has_no_empty_token(self):
        scores = Rouge(raw_results=True).get_scores('cat. ', 'dog. ')[0]
        for metric in Rouge.DEFAULT_METRICS:
            self.assertEqual(scores[metric]['overlap'], 0)
        self.assertEqual(scores['rouge-1']['hyp'], 1)
        self.assertEqual(scores['rouge-1']['ref'], 1)

    def test_files_with_trailing_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            hyp_path = os.path.join(directory, 'hyp.txt')
            ref_path = os.path.join(directory, 'ref.txt')
            with open(hyp_path, 'w') as stream:
                stream.write('cat. \n')
            with open(ref_path, 'w') as stream:
                stream.write('dog. \t\n')
            for avg in (True, False):
                self.assertEqual(
                    FilesRouge().get_scores(hyp_path, ref_path, avg=avg),
                    Rouge().get_scores('cat', 'dog', avg=avg))
