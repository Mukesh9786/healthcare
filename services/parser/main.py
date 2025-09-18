import os
from google.cloud import pubsub_v1
import vertexai
from vertexai.generative_models import GenerativeModel

# --- Configuration ---
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")
location = "us-central1"
model_name = "gemini-1.5-flash-001"

# --- Initialize Clients ---
# Pub/Sub Subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "parser-topic-sub")

# Pub/Sub Publisher
publisher = pubsub_v1.PublisherClient()
compliance_topic_path = publisher.topic_path(project_id, "compliance-topic")

# Vertex AI
vertexai.init(project=project_id, location=location)
model = GenerativeModel(model_name)

# --- Load Prompt ---
prompt_file_path = "../../prompts/semantic_parser_prompt.md"

with open(prompt_file_path, "r") as f:
    prompt = f.read()

def parse_requirement(requirement_text):
    """Calls the Gemini model to parse the requirement."""
    full_prompt = f"{prompt}\n\n**Requirement:**\n\"{requirement_text}\"\n\n**Output:**"
    
    response = model.generate_content(full_prompt)
    
    # Clean up the response to get just the JSON
    parsed_json = response.text.strip().replace("```json", "").replace("```", "").strip()
    return parsed_json

def callback(message):
    """Processes incoming Pub/Sub messages."""
    requirement_text = message.data.decode('utf-8')
    print(f"Parser received requirement: {requirement_text}")
    
    try:
        # Parse the requirement using Vertex AI
        parsed_data = parse_requirement(requirement_text)
        print(f"Successfully parsed requirement: {parsed_data}")
        
        # Publish the parsed data to the compliance topic
        future = publisher.publish(compliance_topic_path, parsed_data.encode("utf-8"))
        print(f"Parser published message {future.result()} to {compliance_topic_path}")
        
    except Exception as e:
        print(f"Error parsing requirement: {e}")
        # Optionally, publish to an error topic or a human-in-the-loop topic

    message.ack()

# --- Start Subscriber ---
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()