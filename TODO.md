- Why fast api, async was not working, and current one works? [HIGH]
- 
gcloud artifacts repositories create kaist-cafeteria-menu \
    --repository-format=docker \
    --location=us-central1 \
    --project=gen-lang-client-0019414025

gcloud auth configure-docker us-central1-docker.pkg.dev

gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  --project=YOUR_PROJECT_ID