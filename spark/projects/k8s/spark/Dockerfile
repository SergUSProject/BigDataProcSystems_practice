FROM spark:latest

LABEL maintainer="Sergei Usovik <usovik@bmstu.ru>"

ENV PATH="$SPARK_HOME/bin:${PATH}"

COPY ["./start-spark.sh", "./stop-spark.sh", "/opt/"]

RUN chmod 755 /opt/start-spark.sh /opt/stop-spark.sh
