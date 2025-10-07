from google.cloud import aiplatform
from google.oauth2 import service_account
import os
import numpy as np

if not 'HF_TOKEN' in os.environ.keys():
    raise ValueError('set your HF_TOKEN environment variable before running')

# Path to your service account key file
service_account_path = 'service-account.json'

# Create credentials from the service account key file
#credentials = service_account.Credentials.from_service_account_file(service_account_path)

# initialize
# EDIT: use your own staging_bucket

experiment_id = np.random.randint(1000):04d
aiplatform.init(staging_bucket='gs://genai-dev-tmp', 
#                credentials=credentials, 
                location='us-east4',
                experiment = f'experiment-{experiment_id}')

aiplatform.autolog()

# define job
job = aiplatform.CustomJob.from_local_script(
            display_name      = f'job-{experiment_id}',
            script_path       = 'finetune-gemma.py',
            container_uri     = 'us-east4-docker.pkg.dev/genai-dev-454121/deeplearning/hftrain:v0',
            machine_type      = 'g2-standard-12',
            accelerator_type  = 'NVIDIA_L4',
            accelerator_count = 1,
            environment_variables = {'HF_TOKEN': os.environ['HF_TOKEN']},   
#            credentials       = credentials
)

# runjob
job.run(
        service_account = '615780545876-compute@developer.gserviceaccount.com',
       )
