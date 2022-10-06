# Configuring Spark on YARN
Sergei Yu. Papulin (papulin_bmstu@mail.ru)

## Contents

- Prerequisites
- Configuration files
- Starting cluster
- Running application
- Spark and Jupyter

## Prerequisites

To get started, you need to have done the following:

- Install Ubuntu 14+
- Install Java 8
- Download Hadoop 3+
- Download Spark 2+
- [Optional] Anaconda Python 3.7
- Install Jupyter (for Scala and Python)
- Install Toree (for Scala kernel)

## Configuration files

#### Spark directories:

- `spark/bin/` - spark commands (`spark-submit`, `spark-shell`, `pyspark` etc.)
- `spark/sbin/` - scripts to start/stop Spark daemons
- `spark/conf/` - configuration
- `spark/logs/` - spark logs


#### Spark configuration

Spark specific configuration files:

- `spark/conf/spark-env.sh` - the file contains environment variables used by Spark commands and daemons
- `spark/conf/spark-defaults.conf` ([default values](https://spark.apache.org/docs/2.3.0/configuration.html)) - cluster configuration file
- `spark/conf/slaves` - a list of Spark workers

Modify the aforementioned configuration files in the following way:

`.profile`
```
# Spark configuration
export SPARK_HOME=$HOME/BigData/spark
export SPARK_CONF_DIR=$SPARK_HOME/conf
PATH=$SPARK_HOME/bin:$PATH
```

`spark-env.sh`

```
export SPARK_MASTER_HOST=localhost
export SPARK_EXECUTOR_MEMORY=1G # will be overriden by spark-defaults.conf
export PYSPARK_DRIVER_PYTHON=/home/ubuntu/ML/anaconda3/bin/python
export PYSPARK_PYTHON=/home/ubuntu/ML/anaconda3/bin/python

```

`spark-defaults.conf`

```
spark.master		yarn
spark.driver.cores	2
spark.driver.memory	1g

spark.executor.cores	1
spark.executor.memory	512m

spark.eventLog.enabled	true
spark.eventLog.dir file:///home/ubuntu/BigData/tmp/spark

spark.history.fs.logDirectory file:///home/ubuntu/BigData/tmp/spark
```

`slaves` (for the standalone mode)

```
localhost
```

Environment variables (e.g. `SPARK_HOME`) can specify in:

- `$HOME/.profile` or `$HOME/.bashrc`
- `$SPARK_HOME/conf/spark-env.sh`
- `$SPARK_HOME/sbin/spark-config.sh` (for scripts)

Or load configurations dynamically:
- Using command line flags (e.g. `--master`, `--conf` etc.) for `spark-submit`, `spark-shell`, `pyspark`
- Inside application code by setting context configurations  

## Starting Spark on YARN cluster

Run `HDFS` and `YARN`

`$HADOOP_HOME/sbin/start-dfs.sh && $HADOOP_HOME/sbin/start-yarn.sh`

Run `History Server`

`$SPARK_HOME/sbin/start-history-server.sh`

Check whether all daemons are running

`jps`


Web UI:
- YARN Resource Manager port: `8088`
- Spark History Server port: `18080`
- Spark Cluster port: `8080` (for standalone cluster mode)

## Running sample application

#### Running Spark application

`spark-submit --master yarn --class org.apache.spark.examples.JavaWordCount /usr/lib/spark/examples/jars/spark-examples_2.11-2.3.3.jar /data/yarn/reviews_Electronics_5_2.json /data/yarn/output`

#### Python interactive mode

Enter in terminal the following command:

`pyspark`

```
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version 2.3.3
      /_/

Using Python version 3.7.3 (default, Mar 27 2019 22:11:17)
SparkSession available as 'spark'.
>>> rdd_data = spark.sparkContext.parallelize(range(100))
>>> rdd_data.reduce(lambda x,y: x + y)
4950   
```


#### Scala interactive mode

Enter in terminal the following command:

`spark-shell`

```
Spark context Web UI available at http://bigdata-VirtualBox:4040
Spark context available as 'sc' (master = yarn, app id = application_1571764860395_0015).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 2.3.3
      /_/
         
Using Scala version 2.11.8 (OpenJDK 64-Bit Server VM, Java 1.8.0_222)
Type in expressions to have them evaluated.
Type :help for more information.

scala> val rdd_data = sc.parallelize(0 to 99)
rdd_data: org.apache.spark.rdd.RDD[Int] = ParallelCollectionRDD[1] at parallelize at <console>:24

scala> rdd_data.reduce(_+_)
res1: Int = 4950
```

## Spark and Jupyter

### Python

#### Option 1

Create a new Python notebook and run a cell with the following code:

```python
import os
import sys

os.environ["SPARK_HOME"]="/home/ubuntu/BigData/spark"
os.environ["PYSPARK_PYTHON"]="/home/ubuntu/ML/anaconda3/bin/python"
os.environ["PYSPARK_DRIVER_PYTHON"]="/home/ubuntu/ML/anaconda3/bin/python"

spark_home = os.environ.get("SPARK_HOME")
sys.path.insert(0, os.path.join(spark_home, "python"))
sys.path.insert(0, os.path.join(spark_home, "python/lib/py4j-0.10.7-src.zip"))
```

#### Option 2

Create the file with the content shown below to connect a `python` kernel to `Jupyter`.

```json
{
    "display_name": "spark-python",
    "language_info": { "name": "python" },
    "codemirror_mode": "spark-python",
    "argv": ["/home/ubuntu/ML/anaconda3/bin/python", "-m", "ipykernel", "-f", "{connection_file}"],
    "env": {
        "SPARK_HOME": "/home/ubuntu/BigData/spark",
        "PYSPARK_PYTHON": "/home/ubuntu/ML/anaconda3/bin/python",
        "PYSPARK_DRIVER_PYTHON": "/home/ubuntu/ML/anaconda3/bin/python",
        "PYTHONPATH": "/home/ubuntu/BigData/spark/python:/home/ubuntu/BigData/spark/python/lib/py4j-0.10.7-src.zip"
     }
}
```

The directory where the file should be located:

`$HOME/.local/share/jupyter/kernels/spark-python/kernel.json`

Run `Jupyter` and select the `spark-python` kernel



## References 

- [Running Spark on YARN](https://spark.apache.org/docs/2.3.0/running-on-yarn.html)
