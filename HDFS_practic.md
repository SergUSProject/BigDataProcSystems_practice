# Introduction to HDFS
Sergei Yu. Papulin (papulin_bmstu@mail.ru)

#### [Version 2018](https://github.com/BigDataProcSystems/Hadoop/blob/2018/hdfs_basics.ipynb)

## Contents

- [Prerequisites](#Prerequisites)
- [Objectives](#Objectives)
- [Configuration](#Configuration)
- [HDFS Shell Commands](#HDFS-Shell-Commands)
- [HDFS Java API](#HDFS-Java-API)
- [Running on Docker cluster](#Running-on-Docker-cluster)
- [Running on AWS using Cloudera](#Running-on-Cloudera)
- [HDFS on EMR Cluster](#HDFS-on-EMR-Cluster)

## Prerequisites

To get started, you need to have done the following:

- Install Ubuntu 14+
- Install Java 8
- Download Hadoop 3+
- Install IntelliJ 2019+ (for Java code)

BigData Image for VirtualBox you can find [here](https://disk.yandex.ru/d/0Hd92rzNB0_IHg).

## Objectives

By the end of this guide you will be able to:
- manage HDFS daemons
- change HDFS configuration
- use HDFS CLI
- run JAVA projects for manipulating files in HDFS


## Configuration

#### Hadoop directories:

- `hadoop/bin` - hadoop commands
- `hadoop/sbin` - scripts
- `hadoop/etc/hadoop` - configuration
- `hadoop/logs` - hadoop logs

#### Basic files to configure:

- `hadoop/etc/hadoop/hadoop-env.sh`
- `hadoop/etc/hadoop/core-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-project-dist/hadoop-common/core-default.xml))
- `hadoop/etc/hadoop/hdfs-site.xml` ([default values](https://hadoop.apache.org/docs/r3.1.2/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml))

You can find all configuration files that you should apply by following the link: [configuration files](../config/hdfs).


Or run the following commands to download:

```bash
# .profile
wget -O ~/.profile https://raw.githubusercontent.com/BigDataProcSystems/Practice/master/hadoop/config/hdfs/.profile
# hadoop-env.sh
wget -O ~/BigData/hadoop/etc/hadoop/hadoop-env.sh https://raw.githubusercontent.com/BigDataProcSystems/Practice/master/hadoop/config/hdfs/hadoop-env.sh
# core-site.xml
wget -O ~/BigData/hadoop/etc/hadoop/core-site.xml https://raw.githubusercontent.com/BigDataProcSystems/Practice/master/hadoop/config/hdfs/core-site.xml
# hdfs-site.xml
wget -O ~/BigData/hadoop/etc/hadoop/hdfs-site.xml https://raw.githubusercontent.com/BigDataProcSystems/Practice/master/hadoop/config/hdfs/hdfs-site.xml
```


#### Running HDFS

Preparation:

1) Create access keys and add the public one to `authorized_keys` to enable passwordless communication between `namenode` and `datanode`:

`ssh-keygen -t rsa -P '' -f $HOME/.ssh/id_rsa && cat $HOME/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys`

2) Create the namenode directory:

`mkdir -p $HOME/BigData/tmp/hadoop/namenode`

3) Format HDFS to first start:

`hdfs namenode -format -force`

To start/stop HDFS daemons separately, use the following commands:

`hdfs --daemon start|stop namenode`

`hdfs --daemon start|stop datanode`

`hdfs --daemon start|stop secondarynamenode`

Or you can run the script to start/stop all daemons at once:

`$HADOOP_HOME/sbin/start-dfs.sh`

`$HADOOP_HOME/sbin/stop-dfs.sh`

Run the `jps` command to check whether the daemons are running:

```
7792 Jps
7220 NameNode
7389 DataNode
7663 SecondaryNameNode
```

If something went wrong, look at `hadoop/logs` for more details.

#### HDFS dashboard

`http://localhost:9870`
