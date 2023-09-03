FROM spark-ubuntu-base

LABEL maintainer="Sergei Usovik <usovik@bmstu.ru>"

# Create a directory for Spark logs and Jupyter notebooks
RUN mkdir notebooks

# Change the current user to root
USER root

# Install the Jupyter Notebook Server
RUN python3 -m pip install --no-cache-dir notebook

# Copy a Jupyter configuration file
COPY --chown=bigdata:bigdata ./config/jupyter/jupyter_notebook_config.py .jupyter/
# Copy a kernel specification to enable PySpark functionality in Jupyter notebooks
COPY --chown=bigdata:bigdata ./config/jupyter/pyspark-kernel.json .local/share/jupyter/kernels/pyspark/kernel.json

RUN chmod 500 .jupyter/jupyter_notebook_config.py

# Change the current user to bigdata
USER bigdata

# Run an entrypoint script on startup
ENTRYPOINT ["/bin/bash", "/usr/local/bin/entrypoint.sh"]