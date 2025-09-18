
**Prompt:**

Extract the following information from the requirement document: Requirement Type, Actors, Preconditions, and Acceptance Criteria. Format the output as a JSON object.

**Examples:**

**Requirement 1:**
"The system shall allow a doctor to log in using their username and password. The user must be registered in the system. Upon successful login, the system shall display the doctor's dashboard."

**Output 1:**
```json
{
  "Requirement Type": "Functional",
  "Actors": ["Doctor"],
  "Preconditions": ["The user must be registered in the system"],
  "Acceptance Criteria": ["Upon successful login, the system shall display the doctor's dashboard"]
}
```

**Requirement 2:**
"The system shall ensure that all patient data is encrypted at rest. The encryption algorithm used must be AES-256."

**Output 2:**
```json
{
  "Requirement Type": "Non-Functional",
  "Actors": [],
  "Preconditions": [],
  "Acceptance Criteria": ["All patient data is encrypted at rest", "The encryption algorithm used must be AES-256"]
}
```

**Requirement 3:**
"The system shall allow a nurse to view a patient's medical history. The nurse must be assigned to the patient. The system shall display the patient's allergies, medications, and past diagnoses."

**Output 3:**
```json
{
  "Requirement Type": "Functional",
  "Actors": ["Nurse"],
  "Preconditions": ["The nurse must be assigned to the patient"],
  "Acceptance Criteria": ["The system shall display the patient's allergies, medications, and past diagnoses"]
}
```

**Requirement 4:**
"The system shall be available 99.9% of the time. This excludes planned maintenance windows."

**Output 4:**
```json
{
  "Requirement Type": "Non-Functional",
  "Actors": [],
  "Preconditions": ["Planned maintenance windows are excluded from the availability calculation"],
  "Acceptance Criteria": ["The system shall be available 99.9% of the time"]
}
```

**Requirement 5:**
"The system shall allow a patient to schedule an appointment with a doctor. The patient must be registered in the system. The system shall display the doctor's available time slots."

**Output 5:**
```json
{
  "Requirement Type": "Functional",
  "Actors": ["Patient"],
  "Preconditions": ["The patient must be registered in the system"],
  "Acceptance Criteria": ["The system shall display the doctor's available time slots"]
}
```

**Requirement 6:**
"The system shall generate a monthly report of all appointments. The report shall be in PDF format and include the patient's name, doctor's name, and appointment date and time."

**Output 6:**
```json
{
  "Requirement Type": "Functional",
  "Actors": [],
  "Preconditions": [],
  "Acceptance Criteria": ["The system shall generate a monthly report of all appointments", "The report shall be in PDF format", "The report shall include the patient's name, doctor's name, and appointment date and time"]
}
```
