# Dockerfile for Hadoop deploying in Docker containers
# 
# NOTE: In this case, there is no need to use the multi-stage building,
#   because jre can be used for both stages. However, it have been done 
#   to demonstrate such option and provide future extensibility.

# Set global arguments for user home and hadoop dirs
ARG USER_HOME_ARG=/home/bigdata
ARG HADOOP_HOME_ARG=$USER_HOME_ARG/hadoop

# ======================
#
# Builder Stage
#
# ======================

FROM openjdk:8-jdk-slim AS builder

LABEL maintainer="Sergei Usovik <usovik@bmstu.ru>"

ARG USER_HOME_ARG
ARG HADOOP_HOME_ARG
ARG HADOOP_VERSION=3.1.2
ARG HADOOP_URL=https://archive.apache.org/dist/hadoop/common

# Set current dir
WORKDIR $USER_HOME_ARG

RUN apt update && apt install -y wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install hadoop
RUN mkdir hadoop && \
    wget -P sources $HADOOP_URL/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -xvf sources/hadoop-$HADOOP_VERSION.tar.gz --directory hadoop --strip-components 1 && \
    rm sources/hadoop-$HADOOP_VERSION.tar.gz

# Copy hadoop configuration files
COPY ["config/hdfs", "config/yarn", "config/mapreduce", "$HADOOP_HOME_ARG/etc/hadoop/"]

# ======================
#
# Final Stage
#
# ======================

FROM openjdk:8-jre-slim 

ARG USER_HOME_ARG
ARG HADOOP_HOME_ARG

RUN apt update && apt install -y openssh-server sudo tini && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN \
    # Create a user named bigdata
    useradd -m -d $USER_HOME_ARG -s /bin/bash -p "$(openssl passwd -1 12345)" bigdata && \
    # Add sudo permission for hadoop user to start ssh service
    echo "bigdata ALL=NOPASSWD:/usr/sbin/service ssh start" >> /etc/sudoers

# Set Hadoop environment variables
ENV HADOOP_HOME $HADOOP_HOME_ARG
ENV HADOOP_CONF_DIR $HADOOP_HOME/etc/hadoop
ENV PATH $HADOOP_HOME/bin:$HADOOP_HOME:$PATH

# Copy hadoop from the builder stage
COPY --from=builder --chown=bigdata:bigdata $HADOOP_HOME $HADOOP_HOME

# Append a java home directory
RUN echo "\nexport JAVA_HOME=/usr/local/openjdk-8" >> $HADOOP_CONF_DIR/hadoop-env.sh

COPY entrypoint.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/entrypoint.sh

# Set current dir
WORKDIR $USER_HOME_ARG

# change root to the bigdata user
USER bigdata

ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]