import os
from google.cloud import pubsub_v1

# Configure Pub/Sub
project_id = os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id")

# Subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "parser-topic-sub")

# Publisher
publisher = pubsub_v1.PublisherClient()
compliance_topic_path = publisher.topic_path(project_id, "compliance-topic")

def callback(message):
    print(f"Parser received message: {message.data.decode('utf-8')}")
    # Here you would add the logic to parse the requirement using the Vertex AI prompt
    message.ack()

    # Pass the message to the compliance agent
    future = publisher.publish(compliance_topic_path, b"Parsed requirement data")
    print(f"Parser published message {future.result()} to {compliance_topic_path}")


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
