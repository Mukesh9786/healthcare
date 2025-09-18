import os
from google.cloud import pubsub_v1

# Configure Pub/Sub
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")

# Subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "test-generator-topic-sub")

# Publisher
publisher = pubsub_v1.PublisherClient()
data_synthesizer_topic_path = publisher.topic_path(project_id, "data-synthesizer-topic")

def callback(message):
    print(f"Test Case Generator Agent received message: {message.data.decode('utf-8')}")
    message.ack()

    # In a real implementation, this agent would generate test cases.

    # Pass the message to the data synthesizer agent
    future = publisher.publish(data_synthesizer_topic_path, b"Test cases generated")
    print(f"Test Case Generator Agent published message {future.result()} to {data_synthesizer_topic_path}")


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
