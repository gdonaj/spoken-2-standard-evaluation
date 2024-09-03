# spoken-2-standard-evaluation

A simple tool for evaluation systems for the translation of non-standard (most often spoken) form of language to the standard form. If you are using this tool in your research, please cite as:

``` bibtex
@article{todo,
  title = {...},
  author = {...},
  journal = {...},
}
```

## Function

This tools compares text segments from all 3 files and checks wheater the conversion is done correctly. If not, it counts errors that are categorized into the following categories:
- Missing conversion -- the literal and standard forms of a word are different, but the normalization algorithm did not convert the word, i.e., the word remained in literal form.
- Wrong conversions -- the literal and standard forms of a word are different, but the normalization algorithm made a conversion to another word form.
- Unwarranted conversions -- the literal and standard forms of a word are the same, but the normalization algorithm made a conversion, although none was needed.
- Inserted words -- the normalization algorithm produced more words on its output than there were given on the input.
- Deleted words -- the normalization algorithm produced fewer words on its output than there were given on the input.

Additionaly, it also shows the percentage of words that did not need conversion (non-standard form is identical to standard form) and can perform 2 statistical tests if several testfiles are provided.

## Requirements

The requirements are: python3 with the following packages: numpy, python_Levenshtein. Use `requirements.txt`.

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

To perform statistical test, use the corresponding flags for one or both tests: `--ar` for approximate randomization and `--br` for bootstrap resampling. The number of trials/bootstraps for each test can be specified with the flags `--ar-n` and `--br-n`. Default values are 1000.
``` bash
python spk2std-evaluation --ar --br --ar-n 10000 --br-n 10000 \
                          input-form.txt standard-form.txt \
                          system-1-output.txt system-2-output.txt system-3-output.txt ...
```

To get results in the form of a latex table, use the --latex flag with a filename. To get the visualization of errors in an HTML file, use the --html flag with a filename. For exmaple:
``` bash
python spk2std-evaluation --ar --br --ar-n 10000 --br-n 10000 \
                          --latex output.tex --html output.html \
                          input-form.txt standard-form.txt \
                          system-1-output.txt system-2-output.txt system-3-output.txt ...
```


