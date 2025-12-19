# Cloud Deployment Guide

This guide explains how to deploy the Khan Academy download pipeline to Google Cloud Platform.

## Architecture Options

### Option 1: Cloud Run (Serverless - Recommended for Scheduled Jobs)
- **Pros**: Pay per use, auto-scaling, no server management
- **Cons**: 60-minute timeout limit, may need multiple runs for large downloads
- **Best for**: Scheduled daily/weekly downloads, on-demand runs

### Option 2: Compute Engine VM (Long-running)
- **Pros**: No timeout limits, full control, can run continuously
- **Cons**: Pay for running time, need to manage server
- **Best for**: Large bulk downloads, continuous operation

### Option 3: Cloud Functions (Event-driven)
- **Pros**: Fully serverless, event-triggered
- **Cons**: 9-minute timeout, less flexible
- **Best for**: Small batches, triggered by events

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** installed (for building images)
4. **Terraform** (optional, for infrastructure as code)

## Quick Start: Deploy with Script

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"
export GCS_BUCKET="khan-academy-videos"

# Make deploy script executable
chmod +x cloud/deploy.sh

# Run deployment
./cloud/deploy.sh
```

## Manual Deployment

### Step 1: Enable APIs

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    compute.googleapis.com \
    cloudscheduler.googleapis.com \
    storage-api.googleapis.com
```

### Step 2: Create GCS Bucket

```bash
gsutil mb -p $PROJECT_ID -l us-central1 gs://khan-academy-videos
```

### Step 3: Build and Push Docker Image

```bash
# Build image
gcloud builds submit --tag gcr.io/$PROJECT_ID/khan-academy-downloader:latest .
```

### Step 4: Deploy Cloud Run Service

```bash
gcloud run deploy khan-academy-downloader \
    --image gcr.io/$PROJECT_ID/khan-academy-downloader:latest \
    --platform managed \
    --region us-central1 \
    --memory 4Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars GCS_BUCKET=khan-academy-videos \
    --service-account SERVICE_ACCOUNT_EMAIL
```

## Terraform Deployment (Infrastructure as Code)

### Step 1: Configure Terraform

```bash
cd cloud/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project ID
```

### Step 2: Initialize and Apply

```bash
terraform init
terraform plan -var="project_id=your-project-id"
terraform apply -var="project_id=your-project-id"
```

### Step 3: Get Service Account Key

After Terraform completes, get the service account key:

```bash
# Get service account email from outputs
terraform output service_account_email

# Create key
gcloud iam service-accounts keys create key.json \
    --iam-account=$(terraform output -raw service_account_email)
```

## Compute Engine VM Deployment

### Option A: Using Terraform

The Terraform configuration includes a VM. After applying:

```bash
# Get VM IP
terraform output vm_external_ip

# SSH into VM
gcloud compute ssh khan-downloader-vm --zone=us-central1-a

# Once inside, the startup script should have set everything up
# Start the downloader
systemctl start khan-downloader
```

### Option B: Manual VM Creation

```bash
# Create VM
gcloud compute instances create khan-downloader-vm \
    --zone=us-central1-a \
    --machine-type=e2-standard-4 \
    --boot-disk-size=100GB \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --metadata-from-file startup-script=cloud/compute-engine-startup.sh
```

## Cloud Scheduler Setup

### Create Scheduled Job

```bash
# Get Cloud Run service URL
SERVICE_URL=$(gcloud run services describe khan-academy-downloader \
    --region=us-central1 --format='value(status.url)')

# Create scheduled job (runs daily at 2 AM)
gcloud scheduler jobs create http khan-academy-daily-download \
    --location=us-central1 \
    --schedule="0 2 * * *" \
    --time-zone="America/Los_Angeles" \
    --uri="$SERVICE_URL/run" \
    --http-method=POST \
    --message-body='{"command":"discover_and_download","max_videos":100}' \
    --oidc-service-account-email=SERVICE_ACCOUNT_EMAIL
```

### Test the Job

```bash
# Run job immediately
gcloud scheduler jobs run khan-academy-daily-download --location=us-central1
```

## Running Downloads

### Via Cloud Run HTTP Endpoint

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe khan-academy-downloader \
    --region=us-central1 --format='value(status.url)')

# Trigger download
curl -X POST "$SERVICE_URL/run" \
    -H "Content-Type: application/json" \
    -d '{
        "command": "discover_and_download",
        "max_videos": 10,
        "gcs_bucket": "khan-academy-videos"
    }'
```

### Via gcloud

```bash
gcloud run services update khan-academy-downloader \
    --region=us-central1 \
    --update-env-vars COMMAND=discover_and_download,MAX_VIDEOS=10
```

### Via VM

```bash
# SSH into VM
gcloud compute ssh khan-downloader-vm --zone=us-central1-a

# Run downloader
cd /opt/khan-academy-downloader
source venv/bin/activate
python scripts/download_all.py --gcs-bucket khan-academy-videos --max 10
```

## Monitoring

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read khan-academy-downloader --region=us-central1

# VM logs
gcloud compute ssh khan-downloader-vm --zone=us-central1-a --command "journalctl -u khan-downloader -f"
```

### Check GCS Bucket

```bash
# List files
gsutil ls gs://khan-academy-videos/

# Check storage usage
gsutil du -sh gs://khan-academy-videos/
```

### Cloud Monitoring

1. Go to [Cloud Console](https://console.cloud.google.com)
2. Navigate to **Monitoring** → **Dashboards**
3. Create custom dashboard for:
   - Cloud Run request count
   - GCS storage usage
   - VM CPU/Memory usage
   - Download success/failure rates

## Cost Optimization

### Cloud Run
- **Idle time**: $0 (no charges when not running)
- **Active time**: ~$0.00002400 per vCPU-second, ~$0.00000250 per GiB-second
- **Example**: 1 hour run with 2 vCPU, 4GB RAM ≈ $0.20

### Compute Engine
- **e2-standard-4**: ~$0.134/hour (~$97/month if running 24/7)
- **Disk**: ~$0.17/GB/month for 100GB ≈ $17/month
- **Recommendation**: Stop VM when not in use

### GCS Storage
- **Standard**: ~$0.020/GB/month
- **Nearline**: ~$0.010/GB/month (after 30 days)
- **Recommendation**: Use lifecycle policies to move old files

### Cost-Saving Tips

1. **Use Cloud Run** for scheduled jobs (pay per use)
2. **Stop VM** when not downloading
3. **Use Nearline/Coldline** storage for old videos
4. **Set up billing alerts** in Cloud Console
5. **Use preemptible VMs** for non-critical downloads (60% cheaper)

## Troubleshooting

### Cloud Run Timeout

If downloads exceed 60 minutes:
- Break into smaller batches (`max_videos` parameter)
- Use Compute Engine VM instead
- Chain multiple Cloud Run invocations

### Authentication Errors

```bash
# Verify service account has permissions
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:*"

# Grant Storage Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.admin"
```

### VM Startup Issues

```bash
# Check startup script logs
gcloud compute instances get-serial-port-output khan-downloader-vm \
    --zone=us-central1-a

# SSH and check manually
gcloud compute ssh khan-downloader-vm --zone=us-central1-a
```

### GCS Upload Failures

- Check bucket permissions
- Verify service account has Storage Admin role
- Check network connectivity from VM/Cloud Run
- Review GCS quotas and limits

## Security Best Practices

1. **Use Service Accounts** (not user accounts) for automation
2. **Grant minimum permissions** (Storage Object Admin, not Storage Admin)
3. **Store credentials securely** (Secret Manager, not in code)
4. **Enable audit logging** for GCS operations
5. **Use VPC** for VM if accessing private resources
6. **Rotate service account keys** regularly

## Next Steps

After deployment:

1. **Test with small batch**: Run with `max_videos=10` first
2. **Monitor costs**: Set up billing alerts
3. **Schedule regular runs**: Use Cloud Scheduler
4. **Set up alerts**: For failures, high costs, storage limits
5. **Backup catalog**: Keep catalog in version control

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Compute Engine Documentation](https://cloud.google.com/compute/docs)
- [Cloud Scheduler Documentation](https://cloud.google.com/scheduler/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
