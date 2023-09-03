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

FROM openjdk:8-alpine AS builder

LABEL maintainer="Sergei Usovik <usovik@bmstu.ru>"

ARG USER_HOME_ARG
ARG HADOOP_HOME_ARG
ARG HADOOP_VERSION=3.1.2
ARG HADOOP_URL=https://archive.apache.org/dist/hadoop/common

# Set current dir
WORKDIR $USER_HOME_ARG

RUN apk upgrade --no-cache && \
    apk add --no-cache bash wget && \
    rm /bin/sh && ln -sv /bin/bash /bin/sh

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

FROM openjdk:8-alpine 

ARG USER_HOME_ARG
ARG HADOOP_HOME_ARG

RUN apk upgrade --no-cache && \
    apk add --no-cache bash wget sudo tini openssh && \
    rm /bin/sh && ln -sv /bin/bash /bin/sh

# Set Hadoop environment variables
ENV HADOOP_HOME $HADOOP_HOME_ARG
ENV HADOOP_CONF_DIR $HADOOP_HOME/etc/hadoop
ENV PATH $HADOOP_HOME/bin:$HADOOP_HOME:$PATH

RUN \
    # Create user
    addgroup bigdata && \
    adduser --ingroup bigdata -h $USER_HOME_ARG --shell /bin/bash --disabled-password bigdata && \
    echo "bigdata:12345" | chpasswd && \
    # Append sudo permission for hadoop user to start ssh service
    echo "bigdata ALL=NOPASSWD:/usr/sbin/sshd -D" >> /etc/sudoers \
    # Replace a comment line with the actual path of the host private key in sshd_config
    sed -ir 's/#HostKey \/etc\/ssh\/ssh_host_rsa_key/HostKey \/etc\/ssh\/id_rsa/g' /etc/ssh/sshd_config

# Replace a java home directory in hadoop-env.sh
#RUN sed -ir 's/JAVA_HOME=\/usr\/lib\/jvm\/java-8-openjdk-amd64/JAVA_HOME=\/usr\/lib\/jvm\/java-1.8-openjdk/g' $HADOOP_CONF_DIR/hadoop-env.sh

# Copy hadoop from the builder stage
COPY --from=builder --chown=bigdata:bigdata $HADOOP_HOME $HADOOP_HOME

# Append a java home directory
RUN echo "export JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk" >> $HADOOP_CONF_DIR/hadoop-env.sh

# Set current dir
WORKDIR $USER_HOME_ARG

# Copy the starting script
COPY entrypoint.sh /usr/local/bin/
RUN chmod 755 /usr/local/bin/entrypoint.sh

# Change root to the bigdata user
USER bigdata

ENTRYPOINT ["tini", "--", "/usr/local/bin/entrypoint.sh"]
CMD ["alpine"]