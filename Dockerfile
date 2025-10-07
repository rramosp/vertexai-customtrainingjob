# Specifies base image and tag
FROM us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-4.py310:latest

WORKDIR /root
RUN ln -s /usr/bin/python3 /usr/bin/python

# Installs additional packages
RUN pip install trl bitsandbytes peft

# Copies the trainer code to the docker image.
COPY finetune-gemma.py /root

# Sets up the entry point to invoke the trainer.
ENTRYPOINT ["python", "finetune-gemma.py"]
