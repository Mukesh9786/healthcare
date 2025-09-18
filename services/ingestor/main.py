import os
import json
from google.cloud import pubsub_v1

# --- Configuration ---
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")

# --- Clients ---
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "ingestor-topic-sub")

publisher = pubsub_v1.PublisherClient()
parser_topic_path = publisher.topic_path(project_id, "parser-topic")
results_topic_path = publisher.topic_path(project_id, "results-topic")

def callback(message):
    """Processes incoming messages, adds its status, and forwards."""
    try:
        data_str = message.data.decode('utf-8')
        payload = json.loads(data_str)
        job_id = payload.get("job_id")
        
        print(f"Ingestor received message for job: {job_id}")

        # 1. Publish result for this agent
        result_payload = {
            "job_id": job_id,
            "agent": "Ingestor",
            "status": "Complete",
            "data": {"message": "Requirement ingested successfully."}
        }
        publisher.publish(results_topic_path, json.dumps(result_payload).encode("utf-8"))

        # 2. Forward the original payload to the next agent
        publisher.publish(parser_topic_path, message.data)
        print(f"Ingestor forwarded message for job {job_id} to {parser_topic_path}")

    except Exception as e:
        print(f"Error in Ingestor: {e}")
    
    message.ack()

# --- Start Subscriber ---
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()