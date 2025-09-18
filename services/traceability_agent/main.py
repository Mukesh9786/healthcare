import os
import json
from google.cloud import pubsub_v1

# --- Configuration ---
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")

# --- Initialize Clients ---
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "traceability-agent-topic-sub")

publisher = pubsub_v1.PublisherClient()
results_topic_path = publisher.topic_path(project_id, "results-topic")

def callback(message):
    """Processes incoming messages and marks the end of the workflow."""
    job_id = None
    try:
        data_str = message.data.decode('utf-8')
        payload = json.loads(data_str)
        job_id = payload.get("job_id")
        
        print(f"Traceability Agent received data for job: {job_id}")

        # In a real implementation, this agent would write to a BigQuery traceability matrix.
        final_status = {"message": "Traceability links updated. Workflow complete."}

        # Publish the final result for this agent
        result_payload = {
            "job_id": job_id,
            "agent": "Traceability",
            "status": "Complete",
            "data": final_status
        }
        publisher.publish(results_topic_path, json.dumps(result_payload).encode("utf-8"))
        print(f"Traceability Agent completed job {job_id}")

    except Exception as e:
        print(f"Error in Traceability Agent for job {job_id}: {e}")
        if job_id:
            error_payload = {"job_id": job_id, "agent": "Traceability", "status": "Error", "data": str(e)}
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