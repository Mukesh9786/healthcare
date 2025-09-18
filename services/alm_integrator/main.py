import os
import json
from google.cloud import pubsub_v1

# --- Configuration ---
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")
MOCK_ALM_API_ENDPOINT = "https://jira.example.com/api/v2/testcases"

# --- Initialize Clients ---
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "alm-integrator-topic-sub")

publisher = pubsub_v1.PublisherClient()
traceability_agent_topic_path = publisher.topic_path(project_id, "traceability-agent-topic")
results_topic_path = publisher.topic_path(project_id, "results-topic")

def push_to_alm(data):
    """Mocks pushing data to an Application Lifecycle Management (ALM) tool."""
    print(f"--- MOCK ALM INTEGRATION: Pushing to {MOCK_ALM_API_ENDPOINT} ---")
    # In a real implementation, this would be an HTTP POST request.
    # For this mock, we just return a success status and the data that would be sent.
    return {"status": "success", "alm_tool": "Jira (Mock)", "submitted_data": data}

def callback(message):
    """Processes incoming messages, mocks ALM push, and forwards."""
    job_id = None
    try:
        data_str = message.data.decode('utf-8')
        payload = json.loads(data_str)
        job_id = payload.get("job_id")
        
        print(f"ALM Integrator received data for job: {job_id}")

        push_result = push_to_alm(payload)

        # 1. Publish result for this agent
        result_payload = {"job_id": job_id, "agent": "ALM Integrator", "status": "Complete", "data": push_result}
        publisher.publish(results_topic_path, json.dumps(result_payload).encode("utf-8"))

        # 2. Forward the augmented payload to the next agent
        next_payload = {**payload, "alm_integration_result": push_result}
        publisher.publish(traceability_agent_topic_path, json.dumps(next_payload).encode("utf-8"))
        print(f"ALM Integrator forwarded message for job {job_id} to {traceability_agent_topic_path}")

    except Exception as e:
        print(f"Error in ALM Integrator for job {job_id}: {e}")
        if job_id:
            error_payload = {"job_id": job_id, "agent": "ALM Integrator", "status": "Error", "data": str(e)}
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
