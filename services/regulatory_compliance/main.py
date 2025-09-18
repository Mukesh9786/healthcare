import os
from google.cloud import pubsub_v1

# Configure Pub/Sub
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")

# Subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "compliance-topic-sub")

# Publisher
publisher = pubsub_v1.PublisherClient()
test_generator_topic_path = publisher.topic_path(project_id, "test-generator-topic")

def callback(message):
    print(f"Regulatory Compliance Agent received message: {message.data.decode('utf-8')}")
    message.ack()

    # In a real implementation, this agent would map requirements to regulations.

    # Pass the message to the test case generator agent
    future = publisher.publish(test_generator_topic_path, b"Compliance checked data")
    print(f"Regulatory Compliance Agent published message {future.result()} to {test_generator_topic_path}")


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
