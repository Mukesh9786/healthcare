import os
import json
from google.cloud import pubsub_v1
from google.cloud import bigquery

# --- Configuration ---
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")
bigquery_dataset = "regulations"
bigquery_table = "regulations_table"

# --- Initialize Clients ---
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "compliance-topic-sub")

publisher = pubsub_v1.PublisherClient()
test_generator_topic_path = publisher.topic_path(project_id, "test-generator-topic")
results_topic_path = publisher.topic_path(project_id, "results-topic")

bigquery_client = bigquery.Client(project=project_id)

def search_regulations(keywords):
    """Searches the BigQuery regulations table for matching keywords."""
    if not keywords:
        return []
    query_parts = [f"LOWER(description) LIKE '%{keyword.lower()}%'" for keyword in keywords if keyword]
    where_clause = " OR ".join(query_parts)
    query = f'''
        SELECT regulation_id, regulation_name, description
        FROM `{project_id}.{bigquery_dataset}.{bigquery_table}`
        WHERE {where_clause}
    '''
    print(f"Executing BigQuery query: {query}")
    return [dict(row) for row in bigquery_client.query(query).result()]

def callback(message):
    """Processes incoming messages, checks compliance, and forwards."""
    job_id = None
    try:
        data_str = message.data.decode('utf-8')
        payload = json.loads(data_str)
        job_id = payload.get("job_id")
        parsed_requirement = payload.get("requirement")
        
        print(f"Compliance agent received data for job: {job_id}")

        keywords = parsed_requirement.get("Actors", []) + [parsed_requirement.get("Requirement Type")]
        found_regulations = search_regulations(keywords)

        # 1. Publish result for this agent
        result_payload = {
            "job_id": job_id,
            "agent": "Regulatory Compliance",
            "status": "Complete",
            "data": found_regulations
        }
        publisher.publish(results_topic_path, json.dumps(result_payload).encode("utf-8"))

        # 2. Forward the augmented payload to the next agent
        next_payload = {
            "job_id": job_id,
            "requirement": parsed_requirement,
            "relevant_regulations": found_regulations
        }
        publisher.publish(test_generator_topic_path, json.dumps(next_payload).encode("utf-8"))
        print(f"Compliance agent forwarded message for job {job_id} to {test_generator_topic_path}")

    except Exception as e:
        print(f"Error in compliance agent for job {job_id}: {e}")
        if job_id:
            error_payload = {"job_id": job_id, "agent": "Regulatory Compliance", "status": "Error", "data": str(e)}
            publisher.publish(results_topic_path, json.dumps(error_payload).encode("utf-8"))

    message.ack()

# --- Start Subscriber ---
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
