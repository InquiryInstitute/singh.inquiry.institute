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

variable "machine_type" {
  description = "Compute Engine machine type"
  type        = string
  default     = "e2-standard-4"
}

variable "disk_size" {
  description = "Boot disk size in GB"
  type        = number
  default     = 100
}
