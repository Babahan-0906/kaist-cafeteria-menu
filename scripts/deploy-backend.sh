PROJECT_ID="gen-lang-client-0019414025"
gcloud config set project $PROJECT_ID

# choose region and name
REGION="us-central1"
SERVICE_NAME="kaist-cafeteria-menu"

# local docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# extract local secrets
export $(grep -v '^#' .env | xargs)

# build local image
IMAGE_URL="us-central1-docker.pkg.dev/$PROJECT_ID/kaist-cafeteria-menu/$SERVICE_NAME:latest"
echo "Building $IMAGE_URL..."
docker build -t "$IMAGE_URL" .

# push to artifact registry
echo "Pushing $IMAGE_URL..."
docker push "$IMAGE_URL"

# deploy to cloud run with env vars
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image "$IMAGE_URL" \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN,TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID,GEMINI_API_KEY=$GEMINI_API_KEY,DEBUG_SCRAPER=True,GIT_ACTIONS_WEBHOOK_SECRET=$GIT_ACTIONS_WEBHOOK_SECRET"