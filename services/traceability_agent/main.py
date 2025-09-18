import os
from google.cloud import pubsub_v1

# Configure Pub/Sub
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")

# Subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "traceability-agent-topic-sub")

def callback(message):
    print(f"Traceability Agent received message: {message.data.decode('utf-8')}")
    message.ack()

    # In a real implementation, this agent would update the traceability matrix.
    print("End of workflow.")


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
