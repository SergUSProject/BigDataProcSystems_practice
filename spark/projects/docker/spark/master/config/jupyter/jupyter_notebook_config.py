# Notebook root directory
c.NotebookApp.notebook_dir="/home/bigdata/notebooks"

# Set ip for the public server
c.NotebookApp.ip = "master"

# Password "bigdata" encrypted as follows
c.NotebookApp.password = "sha1:40c51150b803:86574df18da0ab73751cd957dda0f74c9f5013f8"
c.NotebookApp.open_browser = False

# It is a good idea to set a known, fixed port for server access
c.NotebookApp.port = 9999