# RNSum-Dataset

A release note is a technical document that describes the latest changes to a software product and is crucial in open source software development. However, it still remains challenging to generate release notes automatically. In this paper, we present a new dataset called RNSum, which contains approximately 82,000 English release notes and the associated commit messages derived from the online repositories in GitHub. Then, we propose classwise extractive-then-abstractive/abstractive summarization approaches to this task, which can employ a modern transformer-based seq2seq network like BART and can be applied to various repositories without specific constraints. The experimental results on the RNSum dataset show that the proposed methods can generate less noisy release notes at higher coverage than the baselines. We also observe that there is a significant gap in the coverage of essential information when compared to human references. Our dataset and the code are publicly available.

## Dataset preparation

```bash
$ export GITHUB_TOKEN=<YOUR_GITHUB_TOKEN>
$ python script.py
```

### Requirement
  
* Python 3.10.4
* pandas 1.4.2
* tqdm 4.64.0

## License

[Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/legalcode)

## Citation

```
@inproceedings{kamezawa-etal-2022-rnsum,
    title = "{RNS}um: A Large-Scale Dataset for Automatic Release Note Generation via Commit Logs Summarization",
    author = "Kamezawa, Hisashi  and
      Nishida, Noriki  and
      Shimizu, Nobuyuki  and
      Miyazaki, Takashi  and
      Nakayama, Hideki",
    booktitle = "Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = may,
    year = "2022",
    address = "Dublin, Ireland",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2022.acl-long.597",
    pages = "8718--8735"
}
```