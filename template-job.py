import os
from google.cloud import storage
import json

def upload_blob_from_json(bucket_name, json_content, destination_blob_name):
    """Uploads a string to the bucket."""

    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    text_content = json.dumps(json_content)
    blob.upload_from_string(text_content)


print ('-----------------------------------------------')
print ('   all environment variables')
print ('-----------------------------------------------')
for k,v in os.environ.items():

   print (f'{k:40s} {v}')


print ('-----------------------------------------------')
print ('   job variables')
print ('-----------------------------------------------')


job_id         = os.environ['JOB_ID'] if 'JOB_ID' in os.environ.keys() else "NO JOB_ID"
experiment_id  = os.environ['EXPERIMENT_ID'] if 'EXPERIMENT_ID' in os.environ.keys() else "NO EXPERIMENT_ID"
run_id         = os.environ['RUN_ID'] if 'RUN_ID' in os.environ.keys() else "NO RUN_ID"
location       = os.environ['LOCATION'] if 'LOCATION' in os.environ.keys() else "NO LOCATION"
experiment_metadata_gspath = os.environ['EXPERIMENT_METADATA_GSPATH'] if 'EXPERIMENT_METADATA_GSPATH' in os.environ.keys() else "NO EXPERIMENT_METADATA_GSPATH"
project_id     = os.environ['GCLOUD_PROJECT_ID'] if 'GCLOUD_PROJECT_ID' in os.environ.keys() else "NO GCLOUD_PROJECT_ID"

experiment_metadata_bucket = experiment_metadata_gspath.split('/')[0]
experiment_metadata_path   = '/'.join(experiment_metadata_gspath.split('/')[1:])
metrics_file_name    = f'{experiment_metadata_path}/metrics.json'

metrics_file_name    = f'{experiment_metadata_path}/metrics.json'


print(f"""
--------------- env vars --------------------
LOCATION           {location}
GCLOUD_PROJECT_ID  {project_id}
EXPERIMENT_ID      {experiment_id}
RUN_ID             {run_id}
JOB_ID             {job_id}
EXPERIMENT_METADATA_BUCKET  {experiment_metadata_bucket}
EXPERIMENT_METADATA_GSPATH  {experiment_metadata_gspath}

-------------- experiment data --------------
metrics_file_name      {metrics_file_name}
""")


if 'experiment_metadata_gspath' in os.environ.keys():
   upload_blob_from_json(experiment_metadata_bucket, {'testing':'hola'}, metrics_file_name)
   print('uploaded metrics to bucket')
else:
   print ('no destination in GCP Storage for metadata')
