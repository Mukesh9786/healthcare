import os
from google.cloud import pubsub_v1

# Configure Pub/Sub
project_id = os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id")

# Subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "ingestor-topic-sub")

# Publisher
publisher = pubsub_v1.PublisherClient()
parser_topic_path = publisher.topic_path(project_id, "parser-topic")

def callback(message):
    print(f"Ingestor received message: {message.data.decode('utf-8')}")
    message.ack()

    # Pass the message to the parser agent
    future = publisher.publish(parser_topic_path, message.data)
    print(f"Ingestor published message {future.result()} to {parser_topic_path}")


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
