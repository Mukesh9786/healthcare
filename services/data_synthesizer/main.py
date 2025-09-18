import os
import json
from google.cloud import pubsub_v1
import vertexai
from vertexai.generative_models import GenerativeModel
from faker import Faker

# --- Configuration ---
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")
location = "us-central1"
model_name = "gemini-1.5-flash-001"

# --- Initialize Clients ---
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, "data-synthesizer-topic-sub")

publisher = pubsub_v1.PublisherClient()
alm_integrator_topic_path = publisher.topic_path(project_id, "alm-integrator-topic")
results_topic_path = publisher.topic_path(project_id, "results-topic")

vertexai.init(project=project_id, location=location)
model = GenerativeModel(model_name)
fake = Faker()

# --- Load Prompt ---
prompt_file_path = "../../prompts/data_synthesizer_prompt.md"
with open(prompt_file_path, "r") as f:
    prompt = f.read()

def get_data_generation_plan(data):
    """Calls Gemini to get a plan for what data to generate."""
    full_prompt = f"{prompt}\n\n**Input Data:**\n```json\n{json.dumps(data, indent=2)}\n```\n\n**Output:**"
    response = model.generate_content(full_prompt)
    cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_response)

def generate_fake_data(plan):
    """Generates fake data based on the plan from Gemini using the Faker library."""
    synthetic_data = {}
    for entity in plan.get("data_entities", []):
        entity_type = entity.get("type")
        count = entity.get("count", 1)
        attributes = entity.get("attributes", {})
        synthetic_data[entity_type] = [dict((attr_name, str(getattr(fake, faker_method)())) for attr_name, faker_method in attributes.items()) for _ in range(count)]
    return synthetic_data

def callback(message):
    """Processes incoming messages, synthesizes data, and forwards."""
    job_id = None
    try:
        data_str = message.data.decode('utf-8')
        payload = json.loads(data_str)
        job_id = payload.get("job_id")
        
        print(f"Data Synthesizer received data for job: {job_id}")

        data_plan = get_data_generation_plan(payload)
        synthetic_data = generate_fake_data(data_plan)
        print(f"Successfully synthesized data for job {job_id}")

        # 1. Publish result for this agent
        result_payload = {"job_id": job_id, "agent": "Data Synthesizer", "status": "Complete", "data": synthetic_data}
        publisher.publish(results_topic_path, json.dumps(result_payload).encode("utf-8"))

        # 2. Forward the augmented payload to the next agent
        next_payload = {**payload, "synthetic_test_data": synthetic_data}
        publisher.publish(alm_integrator_topic_path, json.dumps(next_payload).encode("utf-8"))
        print(f"Data Synthesizer forwarded message for job {job_id} to {alm_integrator_topic_path}")

    except Exception as e:
        print(f"Error synthesizing data for job {job_id}: {e}")
        if job_id:
            error_payload = {"job_id": job_id, "agent": "Data Synthesizer", "status": "Error", "data": str(e)}
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
