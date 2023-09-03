FROM ubuntu:14.04

LABEL maintainer="Sergei Usovik <usovik@bmstu.ru>"


# ======================
#
# Install packages 
#
# ======================

RUN apt-get update && apt-get install -y openssh-server software-properties-common nano tini && \
    add-apt-repository ppa:openjdk-r/ppa && \
    apt update && apt -y install openjdk-8-jdk \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# ======================
#
# Create user
#
# ======================

# User home directory
ENV BASE_USER_DIR /home/bigdata

# Create user
RUN useradd -m -d $BASE_USER_DIR -s /bin/bash -p "$(openssl passwd -1 12345)" bigdata 

# Set current dir
WORKDIR /home/bigdata

# Add sudo permission for hadoop user to start ssh service
RUN echo "bigdata ALL=NOPASSWD:/usr/sbin/service ssh start" >> /etc/sudoers

# Copy the entrypoint script
COPY entrypoint.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/entrypoint.sh

# ======================
#
# Install Hadoop
#
# ======================

# TODO: try it out instead of wget
#ADD http://example.com/big.tar.xz /usr/src/things/

# Change root to the bigdata user
USER bigdata

# Install Hadoop
RUN mkdir hadoop && \
    wget -P /home/bigdata/sources https://archive.apache.org/dist/hadoop/common/hadoop-3.1.2/hadoop-3.1.2.tar.gz && \
    tar -xvf sources/hadoop-3.1.2.tar.gz --directory hadoop --strip-components 1 && \
    rm sources/hadoop-3.1.2.tar.gz

# Set Hadoop environment variables
ENV HADOOP_HOME $BASE_USER_DIR/hadoop
ENV HADOOP_CONF_DIR $HADOOP_HOME/etc/hadoop
ENV PATH $HADOOP_HOME/bin:$HADOOP_HOME:$PATH

# Copy hadoop configuration files
COPY --chown=bigdata:bigdata ["config/hdfs", "config/yarn", "config/mapreduce", "$HADOOP_CONF_DIR/"]

ENTRYPOINT ["sh", "/usr/local/bin/entrypoint.sh"]