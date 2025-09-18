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
subscription_path = subscriber.subscription_path(project_id, "test-generator-topic-sub")

publisher = pubsub_v1.PublisherClient()
data_synthesizer_topic_path = publisher.topic_path(project_id, "data-synthesizer-topic")

vertexai.init(project=project_id, location=location)
model = GenerativeModel(model_name)

# --- Load Prompt ---
prompt_file_path = "../../prompts/test_case_generator_prompt.md"
with open(prompt_file_path, "r") as f:
    prompt = f.read()

def generate_test_cases(data):
    """Calls the Gemini model to generate test cases."""
    full_prompt = f"{prompt}\n\n**Input Data:**\n```json\n{json.dumps(data, indent=2)}\n```\n\n**Output:**"
    
    response = model.generate_content(full_prompt)
    
    # Clean up the response to get just the JSON
    parsed_json = response.text.strip().replace("```json", "").replace("```", "").strip()
    return parsed_json

def callback(message):
    """Processes incoming Pub/Sub messages."""
    try:
        data_str = message.data.decode('utf-8')
        print(f"Test Case Generator received data: {data_str}")
        augmented_data = json.loads(data_str)

        # Generate test cases using Vertex AI
        test_cases_str = generate_test_cases(augmented_data)
        test_cases = json.loads(test_cases_str)
        print(f"Successfully generated test cases: {test_cases_str}")

        # Augment the data with the new test cases
        final_data = {
            **augmented_data,
            "generated_test_cases": test_cases
        }

        final_data_str = json.dumps(final_data, indent=2)

        # Publish the final data to the data synthesizer topic
        future = publisher.publish(data_synthesizer_topic_path, final_data_str.encode("utf-8"))
        print(f"Test Case Generator published message {future.result()} to {data_synthesizer_topic_path}")

    except Exception as e:
        print(f"Error generating test cases: {e}")

    message.ack()

# --- Start Subscriber ---
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..")

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()