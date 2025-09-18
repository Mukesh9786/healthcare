from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
def process_requirement():
    """
    This endpoint receives a new requirement and starts the workflow.
    "
    data = request.get_json()
    if not data or 'requirement' not in data:
        return 'Invalid request', 400

    # For now, we'll just log the requirement.
    # In a real implementation, this would publish a message to the ingestor topic.
    print(f"Received requirement: {data['requirement']}")

    return 'Requirement received', 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
