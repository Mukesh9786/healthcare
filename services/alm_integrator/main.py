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

def push_to_alm(data):
    """Mocks pushing data to an Application Lifecycle Management (ALM) tool."""
    print("\n--- MOCK ALM INTEGRATION ---")
    print(f"Pushing generated test cases and data to: {MOCK_ALM_API_ENDPOINT}")
    # In a real implementation, this would be an HTTP POST request.
    print("Data sent:")
    print(json.dumps(data, indent=2))
    print("--- END MOCK ALM INTEGRATION ---\n")
    return {"status": "success", "alm_tool": "Jira (Mock)"}

def callback(message):
    """Processes incoming Pub/Sub messages."""
    try:
        data_str = message.data.decode('utf-8')
        print(f"ALM Integrator received data.")
        full_data = json.loads(data_str)

        # Mock pushing the data to the ALM tool
        push_result = push_to_alm(full_data)

        # Augment the data with the push result
        final_data = {
            **full_data,
            "alm_integration_result": push_result
        }
        final_data_str = json.dumps(final_data, indent=2)

        # Publish to the next topic
        future = publisher.publish(traceability_agent_topic_path, final_data_str.encode("utf-8"))
        print(f"ALM Integrator published message {future.result()} to {traceability_agent_topic_path}")

    except Exception as e:
        print(f"Error in ALM Integrator: {e}")

    message.ack()

# --- Start Subscriber ---
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()