from google.cloud import aiplatform
from google.oauth2 import service_account
import os
import numpy as np
from datetime import datetime

if not 'HF_TOKEN' in os.environ.keys():
    raise ValueError('set your HF_TOKEN environment variable before running')

if not 'GCLOUD_PROJECT_ID' in os.environ.keys():
    raise ValueError(
"""
set your GCLOUD_PROJECT_ID env var before running by running

> export GCLOUD_PROJECT_ID=`gcloud config get project`

"""
)

# ---------------------------------------
# ------------- setup vars --------------

location = 'us-east4'
project_id = os.environ['GCLOUD_PROJECT_ID']

# next three vars must start with 'gs://'
staging_bucket      = 'gs://genai-dev-tmp'
base_output_dir     = 'gs://genai-dev-tmp-useast4'
experiments_metadata_gspath  = 'gs://genai-dev-tmp/experiments_metadata'

# timestamp for experiment and runid
now = datetime.now()
timestamp = f'{now.year}{now.month:02d}{now.day:02d}-{now.hour:02d}{now.minute:02d}{now.second:02d}'

# experiment folder in GCP
experiment_id = f'experiment-{timestamp}'
run_id = f"run-{timestamp}"
job_id = f"job-{timestamp}"
experiment_metadata_gspath = f'{experiments_metadata_gspath}/{location}--{experiment_id}--{run_id}'

print(f"""
--------------- setup --------------------
LOCATION           {location}
GCLOUD_PROJECT_ID  {project_id}
JOB_ID             {job_id}
EXPERIMENT_ID      {experiment_id}
RUN_ID             {run_id}
STAGING_BUCKET     {staging_bucket}
BASE_OUTPUT_DIR    {base_output_dir}
EXPERIMENT_METADATA_GSPATH  {experiment_metadata_gspath}
------------------------------------------
""")
# ---- done setup vars ----


aiplatform.init(staging_bucket=staging_bucket, 
                location=location,
                experiment = experiment_id)
aiplatform.autolog()
aiplatform.start_run(run_id)

hyperparams = {}
hyperparams["epochs"] = 100
hyperparams["batch_size"] = 32
hyperparams["learning_rate"] = 0.01
aiplatform.log_params(hyperparams)

# define job
job = aiplatform.CustomJob.from_local_script(
            display_name      = job_id,
            # script_path       = 'finetune-gemma.py',
            script_path       = 'finetune-gemma.py',
            args              = ['--epochs', '2', '--max_steps', '2'],
            container_uri     = 'us-east4-docker.pkg.dev/genai-dev-454121/deeplearning/hftrain:v0',
            machine_type      = 'g2-standard-12',
            accelerator_type  = 'NVIDIA_L4',
            accelerator_count = 1,
            labels            = {'key1': 'val1', 'key2': 'val2'},
            base_output_dir   = base_output_dir,
            environment_variables = {'HF_TOKEN':           os.environ['HF_TOKEN'],
                                     'GCLOUD_PROJECT_ID':  os.environ['GCLOUD_PROJECT_ID'],
                                     'LOCATION':           location,
                                     'STAGING_BUCKET':     staging_bucket, 
                                     'EXPERIMENT_METADATA_GSPATH':  experiment_metadata_gspath,
                                     'RUN_ID':             run_id, 
                                     'EXPERIMENT_ID':      experiment_id,
                                     'JOB_ID':             job_id},   
)

# runjob
job.run(
        #service_account = '615780545876-compute@developer.gserviceaccount.com',
       )
