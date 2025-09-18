import os
from google.cloud import pubsub_v1

# Configure Pub/Sub
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")

# Subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "data-synthesizer-topic-sub")

# Publisher
publisher = pubsub_v1.PublisherClient()
alm_integrator_topic_path = publisher.topic_path(project_id, "alm-integrator-topic")

def callback(message):
    print(f"Data Synthesizer Agent received message: {message.data.decode('utf-8')}")
    message.ack()

    # In a real implementation, this agent would create synthetic data.

    # Pass the message to the ALM integrator agent
    future = publisher.publish(alm_integrator_topic_path, b"Synthetic data created")
    print(f"Data Synthesizer Agent published message {future.result()} to {alm_integrator_topic_path}")


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
