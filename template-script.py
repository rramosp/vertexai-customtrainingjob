import os


def upload_blob_from_json(bucket_name, json_content, destination_blob_name):
    """Uploads a string to the bucket."""

    from google.cloud import storage
    import json
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    text_content = json.dumps(json_content)
    blob.upload_from_string(text_content)
    
job_id         = os.environ['JOB_ID']
experiment_id  = os.environ['EXPERIMENT_ID']
run_id         = os.environ['RUN_ID']
location       = os.environ['LOCATION']
experiment_metadata_gspath = os.environ['EXPERIMENT_METADATA_GSPATH']
project_id     = os.environ['GCLOUD_PROJECT_ID']

if staging_bucket.startswith('gs://'):
    staging_bucket = staging_bucket[5:]

if experiment_gspath.startswith('gs://'):
    experiment_gspath = experiment_gspath[5:]

experiment_metadata_bucket = experiment_metadata_gspath.split('/')[0]
experiment_metadata_path   = '/'.join(experiment_metadata_gspath.split('/')[1:])
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


upload_blob_from_json(experiment_metadata_bucket, {'testing':'hola'}, metrics_file_name)

print('uploaded metrics to bucket')
