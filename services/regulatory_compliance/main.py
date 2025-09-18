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

bigquery_client = bigquery.Client(project=project_id)

def search_regulations(keywords):
    """Searches the BigQuery regulations table for matching keywords."""
    if not keywords:
        return []

    query_parts = []
    for keyword in keywords:
        query_parts.append(f"LOWER(description) LIKE '%{keyword.lower()}%'")
    
    where_clause = " OR ".join(query_parts)
    
    query = f"""
        SELECT regulation_id, regulation_name, description
        FROM `{project_id}.{bigquery_dataset}.{bigquery_table}`
        WHERE {where_clause}
    """

    print(f"Executing BigQuery query: {query}")
    query_job = bigquery_client.query(query)
    results = query_job.result()

    return [dict(row) for row in results]

def callback(message):
    """Processes incoming Pub/Sub messages."""
    try:
        data = message.data.decode('utf-8')
        print(f"Regulatory Compliance Agent received message: {data}")
        parsed_requirement = json.loads(data)

        # Extract keywords from the parsed requirement to search for regulations
        # This is a simple example; a real implementation would be more sophisticated.
        keywords = parsed_requirement.get("Actors", []) + [parsed_requirement.get("Requirement Type")]
        
        found_regulations = search_regulations(keywords)

        # Augment the original message with the findings
        augmented_data = {
            "requirement": parsed_requirement,
            "relevant_regulations": found_regulations
        }

        augmented_data_str = json.dumps(augmented_data, indent=2)
        print(f"Augmented data with compliance info: {augmented_data_str}")

        # Publish the augmented data to the test generator topic
        future = publisher.publish(test_generator_topic_path, augmented_data_str.encode("utf-8"))
        print(f"Regulatory Compliance Agent published message {future.result()} to {test_generator_topic_path}")

    except Exception as e:
        print(f"Error processing compliance check: {e}")

    message.ack()

# --- Start Subscriber ---
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()