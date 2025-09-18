from flask import Flask, request
import os
from google.cloud import pubsub_v1

app = Flask(__name__)

# Configure Pub/Sub
project_id = os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id")
publisher = pubsub_v1.PublisherClient()
ingestor_topic_path = publisher.topic_path(project_id, "ingestor-topic")

@app.route('/', methods=['POST'])
def process_requirement():
    """
    This endpoint receives a new requirement and starts the workflow by publishing
    it to the ingestor topic.
    """
    data = request.get_json()
    if not data or 'requirement' not in data:
        return 'Invalid request', 400

    requirement = data['requirement']

    # Publish the requirement to the ingestor topic
    future = publisher.publish(ingestor_topic_path, requirement.encode("utf-8"))
    print(f"Published message {future.result()} to {ingestor_topic_path}")

    return 'Requirement received and sent for processing.', 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))