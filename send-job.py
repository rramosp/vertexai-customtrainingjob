from google.cloud import aiplatform
from datetime import datetime
from datetime import timedelta
import os


from google.cloud import storage
from zipfile import ZipFile, ZipInfo
import io
import pathlib
import zipfile 

def zip_current_directory(zip_filename="archive.zip"):
    """
    Zips all files in the current directory into a single zip file.

    Args:
        zip_filename (str): The name of the output zip file.
    """
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in os.listdir('.'):  # Iterate through items in the current directory
                if os.path.isfile(item):  # Check if it's a file
                    zipf.write(item)
        print(f"Successfully created '{zip_filename}' containing all files in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")



def upload_current_dir_as_zip(bucket_name, destination_blob_name):
    """Uploads the current directory as a zip file to a GCS bucket."""
    
    # The directory to be zipped (current working directory)
    source_dir = pathlib.Path.cwd()
    
    # Create a zip archive in memory
    archive = io.BytesIO()
    with ZipFile(archive, 'w') as zip_archive:
        for file_path in source_dir.rglob("*"): # Recursively get all files
            if file_path.is_file():
                # Determine the relative path for the zip entry name
                relative_path = file_path.relative_to(source_dir)
                with open(file_path, 'rb') as file:
                    zip_info = ZipInfo(str(relative_path))
                    zip_archive.writestr(zip_info, file.read())

    # Seek back to the beginning of the in-memory file
    archive.seek(0)
    
    # Initialize the GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    # Upload the in-memory archive
    # Specify the content type as 'application/zip' for correct handling
    blob.upload_from_file(archive, content_type='application/zip')
    
    print(f"Directory '{source_dir.name}' successfully uploaded as '{destination_blob_name}' to bucket '{bucket_name}'.")


# ---------------------------------------
# ------------- setup vars --------------
use_reservation = False

location = 'us-east1'
project_id = 'genai-dev-454121'

container_image_uri = f'{location}-docker.pkg.dev/genai-dev-454121/deeplearning-us-east1/hftrain:v0'
api_endpoint        = f"{location}-aiplatform.googleapis.com"
api_endpoint        = f"us-central1-aiplatform.googleapis.com"

# next two vars must start with 'gs://'
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

if not base_output_dir.startswith('gs://'):
    raise ValueError('base_output_dir must start with gs://')

if not experiment_metadata_gspath.startswith('gs://'):
    raise ValueError('experiment_metadata_gspath must start with gs://')


if 'HF_TOKEN' in os.environ.keys():
    hf_token = os.environ['HF_TOKEN']
else:
    print ('WARNING!!! no HF_TOKEN found in environment variables')
    hf_token = 'NO_TOKEN_FOUND'

print(f"""

--------------- setup --------------------
LOCATION           {location}
GCLOUD_PROJECT_ID  {project_id}
JOB_ID             {job_id}
EXPERIMENT_ID      {experiment_id}
RUN_ID             {run_id}
BASE_OUTPUT_DIR    {base_output_dir}
EXPERIMENT_METADATA_GSPATH  {experiment_metadata_gspath}

CONTAINER          {container_image_uri}
API_ENDPOINT       {api_endpoint}
CONSUMPTION MODEL  {'reservation' if use_reservation else 'DWS FLEX'}
------------------------------------------
""")
# ---- done setup vars ----

# ---- zip current folder and upload to gcp ----

if not os.path.isfile('run.sh'):
    raise ValueError('you must have a run.sh file in the current dir to launch the job')

experiment_src_gspath = f'{experiment_metadata_gspath}/src.zip'
experiment_bucket = experiment_metadata_gspath[5:].split('/')[0]
experiment_path = '/'.join(experiment_metadata_gspath[5:].split('/')[1:])

print (f'uploading source content to gs://  {experiment_bucket}  /  {experiment_path}/src.zip')
upload_current_dir_as_zip(experiment_bucket, f'{experiment_path}/src.zip')



# ---- build customjob request for vertex ai ----

client_options = {"api_endpoint": api_endpoint}

client = aiplatform.gapic.JobServiceClient(client_options=client_options)


import google.cloud.aiplatform_v1.types as aip_types
from google.cloud.aiplatform_v1.services.job_service.client import JobServiceClient
import google

if use_reservation:
    reservation_affinity = aip_types.ReservationAffinity(
        reservation_affinity_type = aip_types.ReservationAffinity.Type.SPECIFIC_RESERVATION,
        key='compute.googleapis.com/reservation-name',
        values=['projects/genai-dev-454121/zones/us-east4-a/reservations/xx02-reservation-20251127-210211'],
    )
    machine_spec = aip_types.MachineSpec(
        machine_type="n2-standard-4",
        reservation_affinity=reservation_affinity,
    )
else:
    machine_spec = aip_types.MachineSpec(
        machine_type="n2-standard-4",
    )


worker_spec = aip_types.WorkerPoolSpec(
    machine_spec=machine_spec,
    replica_count=1,
    container_spec=aip_types.ContainerSpec(
        image_uri=container_image_uri,
        env =  [
                {'name': 'ZIP_WITH_RUNSCRIPT_GSPATH', 'value': experiment_src_gspath},
                {'name': 'GCLOUD_PROJECT_ID', 'value': project_id},
                {'name': 'LOCATION', 'value': location},
                {'name': 'JOB_ID', 'value': job_id},
                {'name': 'RUN_ID', 'value': run_id},
                {'name': 'EXPERIMENT_ID', 'value': experiment_id},
                {'name': 'EXPERIMENT_METADATA_GSPATH', 'value': experiment_metadata_gspath},
                {'name': 'HF_TOKEN', 'value': hf_token},
                {'name': 'BASE_OUTPUT_DIR', 'value': base_output_dir}
                ]
        
    ),
)

if use_reservation:
    custom_job_spec = aip_types.CustomJobSpec(
        worker_pool_specs=[worker_spec],
        # Add other specs like service_account, base_output_directory if needed
    )
else:

    scheduling = aip_types.Scheduling(
        timeout = google.protobuf.duration_pb2.Duration(seconds=24 * 60 * 5), # 5 mins
        strategy = google.cloud.aiplatform_v1.types.Scheduling.Strategy.FLEX_START,
        max_wait_duration = google.protobuf.duration_pb2.Duration(seconds=24 * 60 * 60) # one hour
    )    
    custom_job_spec = aip_types.CustomJobSpec(
        worker_pool_specs=[worker_spec],
        scheduling = scheduling
        # Add other specs like service_account, base_output_directory if needed
    )

# --- Create the CustomJob resource object ---
custom_job = aip_types.CustomJob(
    display_name=job_id,
    job_spec=custom_job_spec,
)

LOCATION = 'us-east4'
PROJECT_ID = project_id

# --- Instantiate the JobServiceClient and create the job ---
client_options = {"api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"}
job_service_client = JobServiceClient(client_options=client_options)

parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
request = aip_types.CreateCustomJobRequest(
    parent=parent,
    custom_job=custom_job,
)

try:
    response = job_service_client.create_custom_job(request)
    print(f"Created Custom Job: {response.name}")
except Exception as e:
    print(f"An error occurred: {e}")
