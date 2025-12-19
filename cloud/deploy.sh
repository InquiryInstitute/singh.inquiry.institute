#!/bin/bash
# Deployment script for Khan Academy downloader to Google Cloud

set -e

PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
BUCKET_NAME="${GCS_BUCKET:-khan-academy-videos}"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID environment variable not set"
    echo "Usage: GCP_PROJECT_ID=your-project-id ./cloud/deploy.sh"
    exit 1
fi

echo "Deploying to GCP Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Bucket: $BUCKET_NAME"

# Authenticate (if not already)
echo "Checking authentication..."
gcloud auth list > /dev/null 2>&1 || gcloud auth login

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    compute.googleapis.com \
    cloudscheduler.googleapis.com \
    storage-api.googleapis.com

# Build and push Docker image (transcript-only, lighter)
echo "Building Docker image (transcript-only)..."
gcloud builds submit -f Dockerfile.transcripts --tag gcr.io/$PROJECT_ID/khan-academy-transcripts:latest .

# Deploy with Terraform (if available)
if command -v terraform &> /dev/null; then
    echo "Deploying infrastructure with Terraform..."
    cd cloud/terraform
    terraform init
    terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="bucket_name=$BUCKET_NAME"
    read -p "Apply these changes? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="bucket_name=$BUCKET_NAME"
    fi
    cd ../..
else
    echo "Terraform not found. Deploying manually..."
    
    # Create GCS bucket
    echo "Creating GCS bucket..."
    gsutil mb -p $PROJECT_ID -l $REGION gs://$BUCKET_NAME || echo "Bucket may already exist"
    
    # Deploy Cloud Run service (optimized for transcripts)
    echo "Deploying Cloud Run service..."
    gcloud run deploy khan-academy-transcripts \
        --image gcr.io/$PROJECT_ID/khan-academy-transcripts:latest \
        --platform managed \
        --region $REGION \
        --memory 2Gi \
        --cpu 1 \
        --timeout 3600 \
        --max-instances 20 \
        --set-env-vars GCS_BUCKET=$BUCKET_NAME \
        --allow-unauthenticated
fi

echo "Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Get service account key: gcloud iam service-accounts keys create key.json --iam-account=SERVICE_ACCOUNT_EMAIL"
echo "2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable"
echo "3. Run: python scripts/download_all.py --gcs-bucket $BUCKET_NAME"
