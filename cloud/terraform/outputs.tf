output "bucket_name" {
  description = "Name of the GCS bucket"
  value       = google_storage_bucket.videos.name
}

output "service_account_email" {
  description = "Service account email for the downloader"
  value       = google_service_account.downloader.email
}

output "service_account_key_path" {
  description = "Path to the service account key file"
  value       = local_file.service_account_key.filename
  sensitive   = true
}

output "cloud_run_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_service.downloader.status[0].url
}

output "vm_external_ip" {
  description = "External IP of the Compute Engine VM"
  value       = google_compute_instance.downloader_vm.network_interface[0].access_config[0].nat_ip
}

output "vm_ssh_command" {
  description = "Command to SSH into the VM"
  value       = "gcloud compute ssh ${google_compute_instance.downloader_vm.name} --zone=${google_compute_instance.downloader_vm.zone}"
}
