# Training jobs on Vertex AI

## Files

- `Dockerfile`: container definition
- `finetune-gemma.py`: the training script that gets installed within the container
- `sendjob.py`: the script that creates and sends the training job to GCP


## Prepare stuff 

Set default credentials:

      gcloud auth application-default login 

Make sure you have:

- a service account (see `sendjob.py`)
- IAM role as **Service Account User**


Create first an artifact repository in your project [here](https://cloud.google.com/artifact-registry/docs/docker/store-docker-container-images#before-you-begin). For instance,  a repository named `deeplearning` under GCP Console $\to$ Artifact Registry (_you might look for it on the search bar_) $\to$ Create Repository.


This is a very abridged version of [this tutorial](https://cloud.google.com/vertex-ai/docs/training/create-custom-container)


## build container

        export PROJECT_ID=$(gcloud config list project --format "value(core.project)")
        export REPO_NAME=deeplearning
        export IMAGE_NAME=hftrain
        export IMAGE_TAG=v0
        export IMAGE_URI=us-east4-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}
        
        docker build -f Dockerfile -t ${IMAGE_URI} ./

## check by running locally 

        docker run --rm --gpus all -e HF_TOKEN=${HF_TOKEN} ${IMAGE_URI}

## upload image to registry


        gcloud auth configure-docker us-east4-docker.pkg.dev
        docker push ${IMAGE_URI}

And check it appears under the repository you created

## run training job

    python sendjob.py

## check progress

Under GCP console $\to$ Vertex AI $\to$ Training $\to$ Custom jobs, and the corresponding logs under Cloud Logging

## experiments

see [this video](https://www.youtube.com/watch?v=a_YXZ5UltkU) for an introduction on how to track experiments.

## comments

- you can pass on parameters to your training job, see [`aiplatform.CustomJob.from_local_script`](https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.CustomJob#google_cloud_aiplatform_CustomJob_from_local_script) using the `args` parameter.
- you can use what you want in your training script .. for instance, you can configure it to log to wandb.