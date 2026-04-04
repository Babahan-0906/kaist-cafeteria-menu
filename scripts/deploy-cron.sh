#!/bin/bash

# Configuration
PROJECT_ID="gen-lang-client-0019414025"
REGION="us-central1"
SERVICE_NAME="kaist-cafeteria-menu"

# Set project
gcloud config set project $PROJECT_ID

# Load environment variables from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found. Please ensure it exists with CLOUD_SCHEDULER_SECRET."
    exit 1
fi

if [ -z "$CLOUD_SCHEDULER_SECRET" ]; then
    echo "CLOUD_SCHEDULER_SECRET is not set in .env."
    exit 1
fi

# Get the Service URL
echo "Fetching Service URL for $SERVICE_NAME..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format='value(status.url)')

if [ -z "$SERVICE_URL" ]; then
    echo "Could not find Service URL for $SERVICE_NAME in $REGION."
    exit 1
fi

TRIGGER_URL="${SERVICE_URL}/api/menu/trigger/"

echo "Creating/Updating Cloud Scheduler jobs for $SERVICE_NAME..."

# 1. Lunch Broadcast (10:45 AM KST)
# Using 'create or update' logic: delete if exists, then create
gcloud scheduler jobs delete kaist-lunch-trigger --location=$REGION --quiet 2>/dev/null
gcloud scheduler jobs create http kaist-lunch-trigger \
    --schedule="45 10 * * *" \
    --uri="$TRIGGER_URL" \
    --http-method=POST \
    --headers="x-cloud-scheduler-auth=$CLOUD_SCHEDULER_SECRET" \
    --location="$REGION" \
    --time-zone="Asia/Seoul" \
    --description="Triggers GitHub Action for KAIST Lunch Menu"

# 2. Dinner Broadcast (4:45 PM KST)
gcloud scheduler jobs delete kaist-dinner-trigger --location=$REGION --quiet 2>/dev/null
gcloud scheduler jobs create http kaist-dinner-trigger \
    --schedule="45 16 * * *" \
    --uri="$TRIGGER_URL" \
    --http-method=POST \
    --headers="x-cloud-scheduler-auth=$CLOUD_SCHEDULER_SECRET" \
    --location="$REGION" \
    --time-zone="Asia/Seoul" \
    --description="Triggers GitHub Action for KAIST Dinner Menu"

echo "Done! Cloud Scheduler jobs have been deployed."
echo "Lunch: 10:45 AM KST"
echo "Dinner: 16:45 PM KST"
