# Rouge
*A full Python librarie for the ROUGE metric [(paper)](http://www.aclweb.org/anthology/W04-1013).*

### Disclaimer
This implementation is independant from the "official" ROUGE script (aka. `ROUGE-155`).   
Results may be *slighlty* different, see [discussions in #2](https://github.com/pltrdy/rouge/issues/2).

## Quickstart
#### Clone & Install
```shell
git clone https://github.com/pltrdy/rouge
cd rouge
python setup.py install
# or
pip install -U .
```
or from pip:
```
pip install rouge
```
#### Use it from the shell (JSON Output)
```
$rouge -h
usage: rouge [-h] [-f] [-a] hypothesis reference

Rouge Metric Calculator

positional arguments:
  hypothesis  Text of file path
  reference   Text or file path

optional arguments:
  -h, --help  show this help message and exit
  -f, --file  File mode
  -a, --avg   Average mode

```

e.g. 


```shell
# Single Sentence
rouge "transcript is a written version of each day 's cnn student" \
      "this page includes the show transcript use the transcript to help students with"

# Scoring using two files (line by line)
rouge -f ./tests/hyp.txt ./ref.txt

# Avg scoring - 2 files
rouge -f ./tests/hyp.txt ./ref.txt --avg
```

#### As a library

###### Score 1 sentence

```python
from rouge import Rouge 

hypothesis = "the #### transcript is a written version of each day 's cnn student news program use this transcript to he    lp students with reading comprehension and vocabulary use the weekly newsquiz to test your knowledge of storie s you     saw on cnn student news"

reference = "this page includes the show transcript use the transcript to help students with reading comprehension and     vocabulary at the bottom of the page , comment for a chance to be mentioned on cnn student news . you must be a teac    her or a student age # # or older to request a mention on the cnn student news roll call . the weekly newsquiz tests     students ' knowledge of even ts in the news"

rouge = Rouge()
scores = rouge.get_scores(hypothesis, reference)
```

*Output:*

```json
[
  {
    "rouge-1": {
      "f": 0.4786324739396596,
      "p": 0.6363636363636364,
      "r": 0.3835616438356164
    },
    "rouge-2": {
      "f": 0.2608695605353498,
      "p": 0.3488372093023256,
      "r": 0.20833333333333334
    },
    "rouge-l": {
      "f": 0.44705881864636676,
      "p": 0.5277777777777778,
      "r": 0.3877551020408163
    }
  }
]
```

*Note: "f" stands for f1_score, "p" stands for precision, "r" stands for recall.*

###### Score multiple sentences
```python
import json
from rouge import Rouge

# Load some sentences
with open('./tests/data.json') as f:
  data = json.load(f)

hyps, refs = map(list, zip(*[[d['hyp'], d['ref']] for d in data]))
rouge = Rouge()
scores = rouge.get_scores(hyps, refs)
# or
scores = rouge.get_scores(hyps, refs, avg=True)
```

*Output (`avg=False`)*: a list of `n` dicts:

```
{"rouge-1": {"f": _, "p": _, "r": _}, "rouge-2" : { .. }, "rouge-l": { ... }}
```


*Output (`avg=True`)*: a single dict with average values:

```
{"rouge-1": {"f": _, "p": _, "r": _}, "rouge-2" : { ..     }, "rouge-l": { ... }}
``` 

###### Score two files (line by line)
Given two files `hyp_path`, `ref_path`, with the same number (`n`) of lines, calculate score for each of this lines, or, the average over the whole file. 

```python
from rouge import FilesRouge

files_rouge = FilesRouge()
scores = files_rouge.get_scores(hyp_path, ref_path)
# or
scores = files_rouge.get_scores(hyp_path, ref_path, avg=True)
```
