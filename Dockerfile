# Specifies base image and tag
FROM us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-4.py310:latest

WORKDIR /root
RUN ln -s /usr/bin/python3 /usr/bin/python

# Installs additional packages
RUN pip install trl bitsandbytes peft
RUN /usr/lib/google-cloud-sdk/platform/bundledpythonunix/bin/pip install python-json-logger

# copy script
COPY dockerfiles/run_from_gspath.sh .

# Any script will be renamed as task.py
ENTRYPOINT ["bash", "run_from_gspath.sh"]

