
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
}

provider "google" {
  project = "your-gcp-project-id" # Please replace with your GCP project ID
  region  = "us-central1"
}

resource "google_firestore_database" "database" {
  project        = "your-gcp-project-id" # Please replace with your GCP project ID
  name           = "(default)"
  location_id    = "us-central"
  type           = "FIRESTORE_NATIVE"
  delete_protection_state = "DELETE_PROTECTION_DISABLED"
  deletion_policy = "DELETE"
}

resource "google_bigquery_dataset" "regulations" {
  dataset_id                 = "regulations"
  friendly_name              = "Regulations"
  description                = "Dataset for storing regulatory compliance data"
  location                   = "US"
  delete_contents_on_destroy = true
}

resource "google_bigquery_dataset" "traceability" {
  dataset_id                 = "traceability"
  friendly_name              = "Traceability"
  description                = "Dataset for storing traceability information"
  location                   = "US"
  delete_contents_on_destroy = true
}

resource "google_pubsub_topic" "ingestor" {
  name = "ingestor-topic"
}

resource "google_pubsub_topic" "parser" {
  name = "parser-topic"
}

resource "google_pubsub_topic" "compliance" {
  name = "compliance-topic"
}

resource "google_pubsub_topic" "test_generator" {
  name = "test-generator-topic"
}

resource "google_pubsub_topic" "data_synthesizer" {
  name = "data-synthesizer-topic"
}

resource "google_pubsub_topic" "traceability_agent" {
  name = "traceability-agent-topic"
}

resource "google_pubsub_topic" "alm_integrator" {
  name = "alm-integrator-topic"
}

resource "google_pubsub_topic" "orchestrator" {
  name = "orchestrator-topic"
}

resource "google_pubsub_topic" "human_in_the_loop" {
  name = "human-in-the-loop-topic"
}
