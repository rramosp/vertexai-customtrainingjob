from google.cloud import aiplatform
from google.oauth2 import service_account
import os
import numpy as np

if not 'HF_TOKEN' in os.environ.keys():
    raise ValueError('set your HF_TOKEN environment variable before running')


# initialize
# EDIT: use your own staging_bucket

experiment_id = np.random.randint(1000)
aiplatform.init(staging_bucket='gs://genai-dev-tmp', 
                location='us-east4',
                experiment = f'experiment-{experiment_id:04d}')

aiplatform.autolog()

# define job
job_id = np.random.randint(100)
job = aiplatform.CustomJob.from_local_script(
            display_name      = f'job-{job_id:03d}',
            script_path       = 'finetune-gemma.py',
            args              = ['--epochs', '2'],
            container_uri     = 'us-east4-docker.pkg.dev/genai-dev-454121/deeplearning/hftrain:v0',
            machine_type      = 'g2-standard-12',
            accelerator_type  = 'NVIDIA_L4',
            accelerator_count = 1,
            labels            = {'key1': 'val1', 'key2': 'val2'},
            base_output_dir   = 'gs://genai-dev-tmp-useast4',
            environment_variables = {'HF_TOKEN': os.environ['HF_TOKEN']},   
)

# runjob
job.run(
        #service_account = '615780545876-compute@developer.gserviceaccount.com',
       )
