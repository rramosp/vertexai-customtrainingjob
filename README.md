# Custom training jobs on Vertex AI

This repo shows how to configure and run a training job in VertexAI by creating a custom Docker container and a custom training script within.

This is a very abridged version of [this tutorial](https://cloud.google.com/vertex-ai/docs/training/create-custom-container)

## Files

- `Dockerfile`: container definition
- `send-job.py`: the script that creates and sends the training job to GCP
- `template-job.py`: a basic dummy job gather env vars, etc.
- `finetune-gemma.py`: a job to finetunegemma


## Prepare stuff 

Set default credentials:

      gcloud auth application-default login 

Make sure you have:

Create first an artifact repository in your project. Here we use an artifact repository named`deeplearning`, whicn you can create under GCP Console $\to$ Artifact Registry (_you might look for it on the search bar_) $\to$ Create Repository. See [example here](https://cloud.google.com/artifact-registry/docs/docker/store-docker-container-images#before-you-begin).


## build container

        export PROJECT_ID=$(gcloud config list project --format "value(core.project)")
        export REPO_NAME=deeplearning
        export IMAGE_NAME=hftrain
        export IMAGE_TAG=v0
        export IMAGE_URI=us-east4-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}
        
        docker build -f Dockerfile -t ${IMAGE_URI} ./

## check by running locally 

        zip template-job.zip run.sh template-job.py
        gsutil cp template-job.zip gs://mytmpbucket/scripts
        export ZIP_WITH_RUNSCRIPT_GSPATH=gs://mytmpbucket/scripts/template-job.zip
        docker run --rm -e ZIP_WITH_RUNSCRIPT_GSPATH=${ZIP_WITH_RUNSCRIPT_GSPATH} ${IMAGE_URI}

## upload image to registry

        gcloud auth configure-docker us-east4-docker.pkg.dev
        docker push ${IMAGE_URI}

And check it appears under the repository you created

## run training job

    python send-job.py

## check progress

Under GCP console $\to$ Vertex AI $\to$ Training $\to$ Custom jobs, and the corresponding logs under Cloud Logging

## experiments

see [this video](https://www.youtube.com/watch?v=a_YXZ5UltkU) for an introduction on how to track experiments.

## comments

- you can pass on parameters to your training job, see [`aiplatform.CustomJob.from_local_script`](https://cloud.google.com/python/docs/reference/aiplatform/latest/google.cloud.aiplatform.CustomJob#google_cloud_aiplatform_CustomJob_from_local_script) using the `args` parameter.
- you can use what you want in your training script .. for instance, you can configure it to log to wandb.
