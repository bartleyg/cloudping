resource "google_cloudfunctions_function" "cloud-ping" {
    name                  = "cloud-ping"
    for_each              = toset([
                                    "us-central1",
                                    "us-east1",
                                    "us-east4",
                                    "us-west2",
                                    "us-west3",
                                    "us-west4",
                                    "northamerica-northeast1",
                                    "southamerica-east1",
                                  ])
    region                = each.key

    source_archive_bucket = "gcf-sources-264829074674-us-central1"
    source_archive_object = "cloud-ping-10f9bc9d-5f50-4e93-b0ee-bebaf83421be/version-5/function-source.zip"
    available_memory_mb   = 128
    entry_point           = "cloud_ping"
    ingress_settings      = "ALLOW_ALL"
    max_instances         = 0
    runtime               = "python39"
    timeout               = 60
    trigger_http          = true
}

# IAM entry for all users to invoke the function
resource "google_cloudfunctions_function_iam_member" "cloud-ping-invoker" {
  for_each       = google_cloudfunctions_function.cloud-ping
  project        = google_cloudfunctions_function.cloud-ping[each.key].project
  region         = google_cloudfunctions_function.cloud-ping[each.key].region
  cloud_function = google_cloudfunctions_function.cloud-ping[each.key].name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}
