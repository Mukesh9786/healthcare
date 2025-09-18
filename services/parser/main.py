import os
import json
from google.cloud import pubsub_v1
import vertexai
from vertexai.generative_models import GenerativeModel

# --- Configuration ---
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")
location = "us-central1"
model_name = "gemini-1.5-flash-001"

# --- Initialize Clients ---
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "parser-topic-sub")

publisher = pubsub_v1.PublisherClient()
compliance_topic_path = publisher.topic_path(project_id, "compliance-topic")
results_topic_path = publisher.topic_path(project_id, "results-topic")

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
    parsed_json = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(parsed_json)

def callback(message):
    """Processes incoming messages, parses the requirement, and forwards."""
    job_id = None
    try:
        data_str = message.data.decode('utf-8')
        payload = json.loads(data_str)
        job_id = payload.get("job_id")
        requirement_text = payload.get("requirement")
        
        print(f"Parser received requirement for job: {job_id}")

        # Parse the requirement using Vertex AI
        parsed_data = parse_requirement(requirement_text)
        print(f"Successfully parsed requirement for job {job_id}")

        # 1. Publish result for this agent
        result_payload = {
            "job_id": job_id,
            "agent": "Parser",
            "status": "Complete",
            "data": parsed_data
        }
        publisher.publish(results_topic_path, json.dumps(result_payload).encode("utf-8"))

        # 2. Forward the new payload to the next agent
        next_payload = {
            "job_id": job_id,
            "requirement": parsed_data
        }
        publisher.publish(compliance_topic_path, json.dumps(next_payload).encode("utf-8"))
        print(f"Parser forwarded message for job {job_id} to {compliance_topic_path}")

    except Exception as e:
        print(f"Error parsing requirement for job {job_id}: {e}")
        if job_id:
            error_payload = {"job_id": job_id, "agent": "Parser", "status": "Error", "data": str(e)}
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
