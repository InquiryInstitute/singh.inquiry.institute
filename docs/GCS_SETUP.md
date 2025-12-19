# Google Cloud Storage Setup

This guide explains how to configure the Khan Academy download pipeline to store videos and transcripts in Google Cloud Storage.

## Prerequisites

1. **Google Cloud Account** - Sign up at https://cloud.google.com
2. **Create a GCS Bucket** - For storing videos and transcripts
3. **Service Account** - For authentication

## Step 1: Create a GCS Bucket

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Cloud Storage** → **Buckets**
3. Click **Create Bucket**
4. Configure:
   - **Name**: e.g., `khan-academy-videos` (must be globally unique)
   - **Location**: Choose a region close to you or your users
   - **Storage class**: Standard (for frequent access) or Nearline (for cost savings)
   - **Access control**: Uniform (recommended)
5. Click **Create**

## Step 2: Create a Service Account

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Enter details:
   - **Name**: `khan-academy-downloader`
   - **Description**: Service account for Khan Academy video downloads
4. Click **Create and Continue**
5. Grant role: **Storage Admin** (or **Storage Object Admin** for more restricted access)
6. Click **Continue** → **Done**

## Step 3: Create and Download Credentials

1. Click on the service account you just created
2. Go to **Keys** tab
3. Click **Add Key** → **Create new key**
4. Choose **JSON** format
5. Click **Create** - the JSON file will download automatically
6. **Save this file securely** - you'll need it for authentication

## Step 4: Configure Authentication

You have two options for providing credentials:

### Option A: Environment Variable (Recommended)

Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:

```bash
# macOS/Linux
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"

# Windows
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\credentials.json
```

### Option B: Command Line Argument

Pass the credentials path directly to the script:

```bash
python scripts/download_all.py --gcs-bucket your-bucket-name --gcs-credentials /path/to/credentials.json
```

## Step 5: Install Google Cloud Libraries

The required libraries are already in `requirements.txt`. Install them:

```bash
pip install -r requirements.txt
```

Or install just the GCS library:

```bash
pip install google-cloud-storage
```

## Step 6: Run Download with GCS

```bash
# Download to GCS bucket
python scripts/download_all.py \
  --gcs-bucket khan-academy-videos \
  --gcs-credentials /path/to/credentials.json \
  --catalog data/metadata/khan_academy_catalog.json

# Or use environment variable for credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
python scripts/download_all.py --gcs-bucket khan-academy-videos
```

## GCS Bucket Structure

Files will be organized in the bucket as follows:

```
gs://your-bucket-name/
├── videos/
│   ├── {video_id_1}.mp4
│   ├── {video_id_2}.mp4
│   └── ...
├── transcripts/
│   ├── {video_id_1}.vtt
│   ├── {video_id_2}.vtt
│   └── ...
│   └── processed/
│       ├── {video_id_1}_transcript.json
│       ├── {video_id_1}_transcript.txt
│       └── ...
└── metadata/
    ├── download_results.json
    └── khan_academy_catalog.json
```

## Options

### Keep Local Files

By default, local files are deleted after successful GCS upload. To keep them:

```bash
python scripts/download_all.py --gcs-bucket your-bucket --keep-local
```

### Upload Only (Skip Local Storage)

The pipeline downloads to a temporary local directory first, then uploads to GCS. This is necessary because `yt-dlp` requires local file access. However, files are automatically deleted after upload unless `--keep-local` is specified.

## Cost Considerations

### Storage Costs

- **Standard Storage**: ~$0.020 per GB/month (frequent access)
- **Nearline Storage**: ~$0.010 per GB/month (access < 1x/month)
- **Coldline Storage**: ~$0.004 per GB/month (access < 1x/quarter)
- **Archive Storage**: ~$0.0012 per GB/month (access < 1x/year)

### Example Costs

For ~10,000 videos averaging 50MB each = ~500GB:
- Standard: ~$10/month
- Nearline: ~$5/month
- Coldline: ~$2/month

### Network Egress Costs

- First 1GB/month: Free
- Next 9TB/month: $0.12 per GB
- Additional: Varies by region

## Access Control

### Making Files Public (Optional)

If you want to make videos publicly accessible:

```python
from src.storage.gcs_storage import GCSStorage

gcs = GCSStorage("your-bucket-name")
gcs.make_public("videos/video_id.mp4")
```

Or use the GCS console to set bucket-level permissions.

### Private Access

By default, files are private. Access requires:
- Service account credentials
- Signed URLs (for temporary access)
- IAM permissions

## Monitoring

Monitor your GCS usage:

1. **Cloud Console** → **Cloud Storage** → Your bucket
2. View storage usage, operations, and costs
3. Set up billing alerts in **Billing** → **Budgets & alerts**

## Troubleshooting

### Authentication Errors

```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```

**Solution**: Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable or use `--gcs-credentials` flag.

### Permission Denied

```
403 Forbidden: Permission denied
```

**Solution**: Ensure your service account has **Storage Admin** or **Storage Object Admin** role.

### Bucket Not Found

```
404 Not Found: Bucket not found
```

**Solution**: 
- Verify bucket name is correct
- Ensure bucket exists in the project
- Check you're using the correct GCP project

### Large File Uploads

For very large files (>100MB), consider:
- Using resumable uploads (handled automatically by the library)
- Increasing timeout settings
- Using parallel uploads for multiple files

## Best Practices

1. **Use lifecycle policies** to automatically move old files to cheaper storage classes
2. **Enable versioning** if you need to recover deleted files
3. **Set up monitoring** to track costs and usage
4. **Use regional buckets** close to your users for better performance
5. **Enable logging** to track access patterns

## Example: Complete Workflow

```bash
# 1. Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

# 2. Discover all videos
python scripts/discover_all_content.py

# 3. Upload catalog to GCS
python -c "
from src.storage.gcs_storage import GCSStorage
gcs = GCSStorage('your-bucket-name')
gcs.upload_file('data/metadata/khan_academy_catalog.json', 'metadata/khan_academy_catalog.json')
"

# 4. Download videos and upload to GCS
python scripts/download_all.py \
  --gcs-bucket your-bucket-name \
  --catalog data/metadata/khan_academy_catalog.json \
  --max 10  # Test with 10 videos first
```

## Additional Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Python Client Library](https://cloud.google.com/storage/docs/reference/libraries#client-libraries-usage-python)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
