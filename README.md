# Rouge
*A full Python librarie for the ROUGE metric [(paper)](http://www.aclweb.org/anthology/W04-1013).*

### Disclaimer
This is an experimental project.   
The results are known to be quite different from official ROUGE scoring script. 

see [isssue #2](https://github.com/pltrdy/rouge/issues/2)

## Quickstart
#### Clone & Install
```shell
git clone https://github.com/pltrdy/pyrouge
cd pyrouge
sudo python3 setup.py install
```
or from pip:
```
sudo pip3 install rouge
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
scores = rouge.get_scores(reference, hypothesis)
```

*Output:*

```json
{
  "rouge-1": {
      "f": 0.5238095189484127,
      "p": 0.6285714285714286,
      "r": 0.4489795918367347
    },  
    "rouge-2": {
      "f": 0.27027026566025497,
      "p": 0.375,
      "r": 0.2112676056338028
    },  
    "rouge-l": {
      "f": 0.28711800978275975,
      "p": 0.4418604651162791,
      "r": 0.25675675675675674
    }
}  
```

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
{"rouge-1": {"f": _, "p": _, "r": _}, "rouge-2" : { .. }, "rouge-3": { ... }}
```


*Output (`avg=True`)*: a single dict with average values:

```
{"rouge-1": {"f": _, "p": _, "r": _}, "rouge-2" : { ..     }, "rouge-3": { ... }}
``` 

###### Score two files (line by line)
Given two files `hyp_path`, `ref_path`, with the same number (`n`) of lines, calculate score for each of this lines, or, the average over the whole file. 

```python
from rouge import FilesRouge

files_rouge = FilesRouge(hyp_path, ref_path)
scores = files_rouge.get_scores()
# or
scores = files_rouge.get_scores(avg=True)
```

**Note** that you can avoid consuming too much memory by using `batch_line=l`. This way, the script will read only `l` lines at a time. (otherwise it loads the whole files). 
