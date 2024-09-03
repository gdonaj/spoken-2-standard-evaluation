# spoken-2-standard-evaluation

A simple tool for evaluation systems for the translation of non-standard (most often spoken) form of language to the standard form. If you are using this tool in your research, please cite as:

``` bibtex
@article{todo,
  title = {...},
  author = {...},
  journal = {...},
}
```

## Requrements

## Installation

## Usage

To use the tool the following files are needed: 
- the input file with non-standard text segments, one per line;
- the reference file with the correct standard form of the text segments;
- the output file(s) from the translation system(s); more than one output file can be provided.

To perform the evaluation, run the following command:
``` bash
python spk2std-evaluation input-form.txt standard-form.txt system-output.txt
```

To perform the evaluation of several systems, run the command with all output files:
``` bash
python spk2std-evaluation input-form.txt standard-form.txt system-1-output.txt system-2-output.txt system-3-output.txt ...
```

To perform statistical test, use the corresponding flags for one or both tests: --ar for approximate randomization and --br for bootstrap resampling. The number of trials/bootstraps for each test can be specified with the flags --ar-n and --br-n. Default values are 1000.
``` bash
python spk2std-evaluation --ar --br --ar-n 10000 --br-n 10000 input-form.txt standard-form.txt system-1-output.txt system-2-output.txt system-3-output.txt ...
```


