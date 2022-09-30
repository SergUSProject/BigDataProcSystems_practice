# MapReduce and Python


#### [Version 2018](https://github.com/BigDataProcSystems/Hadoop/blob/2018/mapreduce_basics.ipynb)

## Contents

- Prerequisites
- Configuration
- Installing `Python` plugin for `IntelliJ`
- Creating `Python` project
- Sample source code
- Running MapReduce with local files
- Running MapReduce `python` app on YARN cluster
- References

## Prerequisites

To get started, you need to have done the following:

- Install Ubuntu 14+ (with Python 3.x)
- Install Java 8
- Download Hadoop 3+
- (Optional) Install IntelliJ 2019+ (for Python code)
- (Optional) Install PyCharm 2019+ (for Python code)
- (Optional) Install Jupyter Notebook

## Installing `Python` plugin for `IntelliJ`

`File` -> `Settings` -> `Plugins` -> Find the `Python Community Edition` plugin from `JetBrains` -> Click on `Install` -> Restart IDE

## Creating `Python` project

`File` -> `New` -> `Project...` -> `Python` -> Next ->  Name: `wordcountapp` - > Finish

## Sample `source code`

Mapper

[tokenizer_mapper.py](../projects/py/wordcountapp/tokenizer_mapper.py)

Combiner/Reducer

[intsum_reducer.py](../projects/py/wordcountapp/intsum_reducer.py)

## Running MapReduce with local files

Run the mapper over a small sample text file and look at the output:

`cat /PATH/data/samples.json | python tokenizer_mapper.py`

Input of the reducer must be sorted. So `hadoop-streaming` sorts out tuples from map tasks by key.

`cat /PATH/data/samples.json | python tokenizer_mapper.py | sort`

Run the full map-reduce pipeline:

`cat /PATH/data/samples.json | python tokenizer_mapper.py | sort | python intsum_reducer.py`

## Running MapReduce `python` app on YARN cluster

```
yarn jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.1.2.jar \
    -D mapreduce.job.reduces=2 \
    -mapper "python /PATH/py/wordcountapp/tokenizer_mapper.py/tokenizer_mapper.py" \
    -reducer "python /PATH/py/wordcountapp/intsum_reducer.py" \
    -input "/data/yarn/reviews_Electronics_5_2.json" \
    -output "/data/yarn/output"
```
