
**Prompt:**

As a software quality assurance engineer in the medical device industry, your task is to generate a set of test cases based on a given software requirement and its associated regulatory guidelines. 

Generate a JSON array of test cases. Each test case should be an object with the following fields:
- `test_case_id`: A unique identifier for the test case (e.g., "TC-001").
- `description`: A brief, clear description of the test objective.
- `steps`: An array of strings, where each string is a step to be executed.
- `test_data`: A description of the data to be used for the test.
- `expected_outcome`: A clear description of the expected result after executing the test steps.

**Input Data:**

The input will be a JSON object containing the parsed requirement and a list of relevant regulations.

**Example Input:**
```json
{
  "requirement": {
    "Requirement Type": "Functional",
    "Actors": ["Doctor"],
    "Preconditions": ["The user must be registered in the system"],
    "Acceptance Criteria": ["Upon successful login, the system shall display the doctor's dashboard"]
  },
  "relevant_regulations": [
    {
      "regulation_id": "IEC-62304",
      "regulation_name": "Software Lifecycle",
      "description": "Specifies lifecycle requirements for the development of medical software..."
    }
  ]
}
```

**Example Output:**
```json
[
  {
    "test_case_id": "TC-LOGIN-001",
    "description": "Verify that a registered doctor can successfully log in with valid credentials.",
    "steps": [
      "Navigate to the login page.",
      "Enter the username of a registered doctor.",
      "Enter the correct password for that doctor.",
      "Click the 'Login' button."
    ],
    "test_data": "A pre-registered doctor user with a known username and password.",
    "expected_outcome": "The system authenticates the user and redirects to the doctor's dashboard. A 'Welcome' message with the doctor's name is displayed."
  },
  {
    "test_case_id": "TC-LOGIN-002",
    "description": "Verify that a user cannot log in with an invalid password.",
    "steps": [
      "Navigate to the login page.",
      "Enter the username of a registered doctor.",
      "Enter an incorrect password.",
      "Click the 'Login' button."
    ],
    "test_data": "A pre-registered doctor user with a known username and an incorrect password.",
    "expected_outcome": "The system displays an 'Invalid username or password' error message and does not grant access."
  }
]
```
