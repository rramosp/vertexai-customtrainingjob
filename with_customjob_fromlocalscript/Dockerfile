# Specifies base image and tag
FROM us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-4.py310:latest

WORKDIR /root
RUN ln -s /usr/bin/python3 /usr/bin/python

# Installs additional packages
RUN pip install trl bitsandbytes peft

# Any script will be renamed as task.py
ENTRYPOINT ["python", "task.py"]

