terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "GCS Bucket name for storing videos"
  type        = string
  default     = "khan-academy-videos"
}

variable "service_account_email" {
  description = "Service account email (will be created if not provided)"
  type        = string
  default     = ""
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# GCS Bucket for videos
resource "google_storage_bucket" "videos" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 365  # Move to Nearline after 1 year
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  versioning {
    enabled = true
  }
}

# Service Account for the downloader
resource "google_service_account" "downloader" {
  account_id   = "khan-downloader"
  display_name = "Khan Academy Downloader Service Account"
  description  = "Service account for Khan Academy video download pipeline"
}

# Grant Storage Admin role to service account
resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.downloader.email}"
}

# Grant Cloud Run Admin (if using Cloud Run)
resource "google_project_iam_member" "cloud_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.downloader.email}"
}

# Service Account Key (for local/VM use)
resource "google_service_account_key" "downloader_key" {
  service_account_id = google_service_account.downloader.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Save key to local file (be careful with this in production!)
resource "local_file" "service_account_key" {
  content  = base64decode(google_service_account_key.downloader_key.private_key)
  filename = "${path.module}/../credentials/service-account-key.json"
  
  depends_on = [google_service_account_key.downloader_key]
}

# Cloud Run Service (optional - for serverless execution)
resource "google_cloud_run_service" "downloader" {
  name     = "khan-academy-downloader"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.downloader.email
      
      containers {
        image = "gcr.io/${var.project_id}/khan-academy-downloader:latest"
        
        resources {
          limits = {
            cpu    = "2"
            memory = "4Gi"
          }
        }

        env {
          name  = "GCS_BUCKET"
          value = google_storage_bucket.videos.name
        }
      }

      timeout_seconds = 3600
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }
  }

  traffic {
    percent = 100
    latest_revision = true
  }
}

# Compute Engine Instance (for long-running downloads)
resource "google_compute_instance" "downloader_vm" {
  name         = "khan-downloader-vm"
  machine_type = "e2-standard-4"  # 4 vCPU, 16GB RAM
  zone         = "${var.region}-a"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 100  # 100GB disk
      type  = "pd-standard"
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral public IP
    }
  }

  service_account {
    email  = google_service_account.downloader.email
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = file("${path.module}/../compute-engine-startup.sh")

  labels = {
    purpose = "khan-academy-downloader"
  }
}

# Cloud Scheduler Job (for scheduled runs)
resource "google_cloud_scheduler_job" "daily_download" {
  name        = "khan-academy-daily-download"
  description = "Daily job to download new Khan Academy videos"
  schedule    = "0 2 * * *"  # 2 AM daily
  time_zone   = "America/Los_Angeles"
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.downloader.status[0].url}/run"
    
    oidc_token {
      service_account_email = google_service_account.downloader.email
    }

    body = base64encode(jsonencode({
      command = "discover_and_download"
      max_videos = 100
    }))
  }
}

# Outputs
output "bucket_name" {
  value = google_storage_bucket.videos.name
}

output "service_account_email" {
  value = google_service_account.downloader.email
}

output "service_account_key_path" {
  value     = local_file.service_account_key.filename
  sensitive = true
}

output "cloud_run_url" {
  value = google_cloud_run_service.downloader.status[0].url
}

output "vm_external_ip" {
  value = google_compute_instance.downloader_vm.network_interface[0].access_config[0].nat_ip
}
