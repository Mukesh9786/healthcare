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
        
        synthetic_data[entity_type] = []
        for _ in range(count):
            record = {}
            for attr_name, faker_method in attributes.items():
                try:
                    record[attr_name] = str(getattr(fake, faker_method)()) # Ensure all data is string
                except AttributeError:
                    record[attr_name] = "invalid_method"
            synthetic_data[entity_type].append(record)
            
    return synthetic_data

def callback(message):
    """Processes incoming Pub/Sub messages."""
    try:
        data_str = message.data.decode('utf-8')
        print(f"Data Synthesizer received data: {data_str}")
        augmented_data = json.loads(data_str)

        # Get a data generation plan from Vertex AI
        data_plan = get_data_generation_plan(augmented_data)
        print(f"Received data generation plan: {json.dumps(data_plan, indent=2)}")

        # Generate synthetic data with Faker
        synthetic_data = generate_fake_data(data_plan)
        print(f"Generated synthetic data: {json.dumps(synthetic_data, indent=2)}")

        # Augment the data with the synthetic data
        final_data = {
            **augmented_data,
            "synthetic_test_data": synthetic_data
        }

        final_data_str = json.dumps(final_data, indent=2)

        # Publish to the next topic
        future = publisher.publish(alm_integrator_topic_path, final_data_str.encode("utf-8"))
        print(f"Data Synthesizer published message {future.result()} to {alm_integrator_topic_path}")

    except Exception as e:
        print(f"Error synthesizing data: {e}")

    message.ack()

# --- Start Subscriber ---
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()