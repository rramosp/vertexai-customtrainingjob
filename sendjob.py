from google.cloud import aiplatform
from google.oauth2 import service_account
import os
import numpy as np

if not 'HF_TOKEN' in os.environ.keys():
    raise ValueError('set your HF_TOKEN environment variable before running')

if not 'GCLOUD_PROJECT_ID' in os.environ.keys():
    raise ValueError(
"""
set your GCLOUD_PROJECT_ID env var before running by running

> export GCLOUD_PROJECT_ID=`gcloud config get project`

"""
)

# initialize
location = 'us-east4'
staging_bucket = 'gs://genai-dev-tmp'

experiment_id = np.random.randint(1000)
experiment_id = f'experiment-{experiment_id:04d}'
aiplatform.init(staging_bucket=staging_bucket, 
                location=location,
                experiment = experiment_id)

aiplatform.autolog()

run_id = np.random.randint(100)
run_id = f"run-{run_id}"
aiplatform.start_run(run_id)

hyperparams = {}
hyperparams["epochs"] = 100
hyperparams["batch_size"] = 32
hyperparams["learning_rate"] = 0.01
aiplatform.log_params(hyperparams)

# define job
job_id = np.random.randint(100)
job = aiplatform.CustomJob.from_local_script(
            display_name      = f'job-{job_id:03d}',
            # script_path       = 'finetune-gemma.py',
            script_path       = 'aa.py',
            args              = ['--epochs', '2'],
            container_uri     = 'us-east4-docker.pkg.dev/genai-dev-454121/deeplearning/hftrain:v0',
            machine_type      = 'g2-standard-12',
            accelerator_type  = 'NVIDIA_L4',
            accelerator_count = 1,
            labels            = {'key1': 'val1', 'key2': 'val2'},
            base_output_dir   = 'gs://genai-dev-tmp-useast4',
            environment_variables = {'HF_TOKEN': os.environ['HF_TOKEN'],
                                     'GCLOUD_PROJECT_ID': os.environ['GCLOUD_PROJECT_ID'],
                                     'location': location,
                                     'staging_bucket': staging_bucket, 
                                     'run_id':  run_id, 
                                     'experiment_id': experiment_id },   
)

# runjob
job.run(
        #service_account = '615780545876-compute@developer.gserviceaccount.com',
       )
