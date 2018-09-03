# NTCIR14-STC3: DQ and ND subtasks

Recently, many reserachers are trying to build an automatic helpdesk system. However, there are very few methods to evaluate such systems. In this competitoin, we aim to explore methods to evaluate task-oriented, multi-round, textual dialogue systems automatically. This dataset have the following features:

- Chinese customer-helpdesk dialogues carwled from [Weibo](weibo.com).
- English dialgoues: manually translated from a subset of the Chinese dialgoues.
- Nugget type annotatoins for each turn: indicate whether the current turn is useful to accomplish the task.
- Quality annotation for each dialogue. 
  - task accomplishment
  - customer satisfcation
  - dialogue effectiveness 

[STC3 Homepage](http://sakailab.com/ntcir14stc3/)

[Slides for DQ and ND subtasks](http://sakailab.com/wp-content/uploads/2018/06/STC3atNTCIR-14.pdf ) .

[Download Dataset](https://codeload.github.com/sakai-lab/stc3-dataset/zip/master)

## News
- Sep 3: **Dataset published:**  This [dataset](https://sakai-lab.github.io/stc3-dataset/) has been available.
- Sep 3: **Registration deadline extended:**  We already have 14 registered teams but we have decided to extend the task registration deadline to Sunday 9th Steptember! Please register! Have fun with our new tasks! To register, please click [HERE](http://research.nii.ac.jp/ntcir/ntcir-14/howto.html).


## Dataset Overview

The Chinese dataset contains 4,090 (3,700 for training + 390 for testing)  customer-helpdesk dialgoues which are crawled from [Weibo](weibo.com). All of these dialogues are annotated by 19 annotators.

The English dataset contains 2062 dialogues (1,672 for training + 390 for testing)  are manually translated from a subset of the Chinese dataset. The English dataset shares the same annotations with the Chinese dataset.

### Training Data

 *[train_data_cn.json](https://github.com/sakai-lab/stc3-dataset/blob/master/train_data_cn.json)* (3,700 dialogues)

 *[train_data_en.json](https://github.com/sakai-lab/stc3-dataset/blob/master/train_data_en.json)* (1,672 dialogues)

### Test Data

*[test_data_cn.json](https://github.com/sakai-lab/stc3-dataset/blob/master/test_data_cn.json)* (390 dialogues)

*[test_data_en.json](https://github.com/sakai-lab/stc3-dataset/blob/master/test_data_en.json)* (390 dialogues)



## Format of the JSON file

---

Each file is in JSON format with UTF-8 encoding. 

Following are the top-level fields:

- `id`
- `turns`: array of turns from the customer and the helpdesk (see details below)
- `annotations`: a list of annotations provided by 19 annotators. Each annotation consists of two fields: `nugget` and `quality`

Each element of the `turns` field contains the following fields:

- `sender`: the speaker of this turn (either customer or helpdesk)
- `utterances`: the utterances (may be multiple) they sent in this turn. Note that some utterances are empty strings since we didn't crawl emoji and photos.

Each element of `annotations` contains the following fields:

- `nugget`: The list of nugget types for each turn (see details below).
- `quality`: A dictonary consists of the subjetive dialogue quality scores: `A`-score, `S`-score, and `E`-score (see details below).



### Nugget Types

---

`CNUG0`: Customer trigger (problem stated)

`CNUG*`: Customer goal (solution confirmed)

`HNUG*`: Helpdesk goal (solution stated)

`CNUG`: Customer regular

`HNUG`: Helpdesk regular

`CNaN`: Customer Not-a-Nugget

`HNaN`: Helpdesk Not-a-Nugget



### Dialogue Quality

---

`A`-score: Task **A**ccomplishment (Has the problem been solved? To what extent?) 

`S`-score: Customer **S**atisfaction of the dialogue (not of the product/service or the company) 

`E`-score: Dialogue **E**ffectiveness (Do the utterers interact effectively to solve the problem efficiently?) 

Scale: 2, 1, 0, -1, -2




## Evaluation

---

To evaluate your model, please submit all prediction distributions and the corresponding IDs in JSON format (please refer to `submission_example.json`). For A-score, E-score and S-score in  `quality`, please calculate the probability distributions over 2, 1, 0, -1, -2 for each dialogue. For `nugget`, please calculate the probility distributions over different nugget types for each turn (**NOT** each utterance).
If you are only interested in one subtask (*nugget detection* or *dialogue quality*), it is okay to  include only `nugget` or `quality`.


## Annotators

We hired 19  Chinese students from the department of Computer Science, Waseda University to annotate this dataset.

## Citation

```bibtex
@inproceedings{zeng17evia, 
Author = {Zhaohao Zeng and Cheng Luo and Lifeng Shang and Hang Li and Tetsuya Sakai},
Title = {Test Collections and Measures for Evaluating Customer-Helpdesk Dialogues},
Booktitle = {Proceedings of EVIA 2017},
	Pages = {1-9},
 Year = {2017}}
```

## Have questions?

Please contact: [zhaohao@fuji.waseda.jp](mailto:zhaohao@fuji.waseda.jp)        