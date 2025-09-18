
**Prompt:**

You are a data architect. Your task is to define the schema for synthetic data required to execute a given set of test cases for a medical software application. The data must be GDPR compliant.

Based on the input, which includes the requirement, regulations, and test cases, generate a JSON object. This object should contain a list of data entities to be created. Each entity should have a `type` (e.g., "user_account", "patient_record") and a `attributes` object defining the fields for that entity (e.g., {"name": "full_name", "email": "email_address"}).

**Input Data:**

The input will be a JSON object containing the requirement, regulations, and generated test cases.

**Example Input:**
```json
{
  "requirement": {
    "Requirement Type": "Functional",
    "Actors": ["Doctor"],
    "Acceptance Criteria": ["Upon successful login, the system shall display the doctor's dashboard"]
  },
  "relevant_regulations": [
    {
      "regulation_id": "ISO-27001",
      "description": "Specifies the requirements for an information security management system..."
    }
  ],
  "generated_test_cases": [
    {
      "test_case_id": "TC-LOGIN-001",
      "description": "Verify that a registered doctor can successfully log in with valid credentials.",
      "test_data": "A pre-registered doctor user with a known username and password."
    }
  ]
}
```

**Example Output:**
```json
{
  "data_entities": [
    {
      "type": "doctor_account",
      "count": 2,
      "attributes": {
        "full_name": "name",
        "username": "user_name",
        "password": "password",
        "role": "job",
        "is_active": "boolean"
      }
    }
  ]
}
```
