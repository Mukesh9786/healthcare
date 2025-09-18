from flask import Flask
from flask_sockets import Sockets
import os
import json
import uuid
import threading
from google.cloud import pubsub_v1

# --- Configuration ---
project_id = os.environ.get("GCP_PROJECT_ID", "mukesh-444504")

# --- Flask & WebSocket Setup ---
app = Flask(__name__)
sockets = Sockets(app)

# Dictionary to hold WebSocket clients, keyed by a unique job_id
clients = {}

# --- Pub/Sub Clients ---
publisher = pubsub_v1.PublisherClient()
ingestor_topic_path = publisher.topic_path(project_id, "ingestor-topic")

subscriber = pubsub_v1.SubscriberClient()
results_subscription_path = subscriber.subscription_path(project_id, "results-topic-sub")

# --- WebSocket Handler ---
@sockets.route('/ws')
def socket_server(ws):
    job_id = str(uuid.uuid4())
    clients[job_id] = ws
    print(f"New client connected with job_id: {job_id}")

    while not ws.closed:
        try:
            message = ws.receive()
            if message:
                print(f"Received requirement for job {job_id}: {message}")
                data = json.loads(message)
                
                # Prepare the initial payload for the agent pipeline
                initial_payload = {
                    "job_id": job_id,
                    "requirement": data['requirement']
                }
                
                # Publish the initial message to start the pipeline
                future = publisher.publish(ingestor_topic_path, json.dumps(initial_payload).encode("utf-8"))
                print(f"Published initial message to {ingestor_topic_path} for job {job_id}")

        except Exception as e:
            print(f"Error in WebSocket handler for job {job_id}: {e}")
            break

    # Once the connection is closed, remove the client
    del clients[job_id]
    print(f"Client disconnected for job_id: {job_id}")

# --- Background Pub/Sub Listener ---
def results_listener():
    """Listens to the results topic and forwards messages to the correct client."""
    def callback(message):
        try:
            data_str = message.data.decode('utf-8')
            data = json.loads(data_str)
            job_id = data.get("job_id")
            
            if job_id and job_id in clients:
                ws = clients[job_id]
                if not ws.closed:
                    print(f"Forwarding result to client for job {job_id}")
                    ws.send(json.dumps(data)) # Send the full data packet
                else:
                    print(f"Client for job {job_id} is closed. Cannot forward result.")
            else:
                print(f"No client found for job_id: {job_id}")

            message.ack()
        except Exception as e:
            print(f"Error in results_listener callback: {e}")
            message.nack()

    streaming_pull_future = subscriber.subscribe(results_subscription_path, callback=callback)
    print(f"Listening for results on {results_subscription_path}...")
    try:
        streaming_pull_future.result() # This blocks until the subscription is cancelled
    except Exception as e:
        print(f"Results listener background thread failed: {e}")
        streaming_pull_future.cancel()

# --- Main Execution ---
if __name__ == "__main__":
    # Start the results listener in a background thread
    listener_thread = threading.Thread(target=results_listener, daemon=True)
    listener_thread.start()

    # Start the WebSocket server
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    port = int(os.environ.get('PORT', 8080))
    server = pywsgi.WSGIServer(('', port), app, handler_class=WebSocketHandler)
    print(f"Orchestrator WebSocket server starting on port {port}...")
    server.serve_forever()
