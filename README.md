# Smart TB Aftercare System

A Python CLI application for monitoring tuberculosis (TB) treatment adherence, symptom tracking, follow-up case management, and medication refill workflows. Built as a multi-person team project demonstrating OOP design, JSON persistence, role-based authentication, and service-layer architecture.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Setup & Installation](#setup--installation)
6. [Running the Application](#running-the-application)
7. [Test Accounts](#test-accounts)
8. [User Roles & Menu Options](#user-roles--menu-options)
9. [Running Tests](#running-tests)
10. [Known Limitations](#known-limitations)
11. [Team Responsibilities](#team-responsibilities)
12. [License](#license)

---

## Project Overview

The Smart TB Aftercare System supports three user roles through an interactive command-line interface:

- **Patients** — record medication adherence, report symptoms, and request refills.
- **Doctors** — create treatments, prescribe medications, monitor adherence and symptoms, record clinical notes, and complete treatments.
- **Health Workers** — monitor assigned patient adherence, review symptoms, manage follow-up cases, escalate issues to doctors, and process refill requests.

All data is persisted as JSON files in a configurable `data/` directory.

---

## Features

| Feature | Description |
|---|---|
| Role-based authentication | Login / Register with username & password; routes to role-specific menu |
| Treatment management | Create, update, and complete TB treatments with duration and instructions |
| Medication prescription | Doctors prescribe medications linked to treatments |
| Adherence tracking | Record taken/missed doses; calculate adherence percentage per medication |
| Symptom check-ins | Patients report symptoms with severity (mild / moderate / severe) |
| Follow-up cases | Health workers create, update, and escalate follow-up cases |
| Refill management | Request medication refills, track supply levels, and process requests |
| JSON persistence | All data stored as flat JSON files via DataManager |
| CLI interface | Interactive menus with argparse-based entry point |

---

## Project Structure

```
smart-tb-aftercare/
├── main.py                        # Application entry point (argparse + service wiring)
├── cli/
│   ├── __init__.py
│   ├── main_menu.py               # Login / Register / Exit loop
│   ├── patient_menu.py            # 9 patient options
│   ├── doctor_menu.py            # 11 doctor options
│   └── healthworker_menu.py      # 11 health worker options
├── app/
│   ├── __init__.py
│   ├── patient.py                 # Patient domain class
│   ├── doctor.py                  # Doctor domain class
│   ├── healthworker.py            # HealthWorker domain class
│   ├── treatment.py               # Treatment domain class
│   ├── medication.py              # Medication domain class
│   ├── adherence.py              # AdherenceTracker domain class
│   ├── symptoms.py                # SymptomTracker domain class
│   ├── followup.py                # FollowUpTracker domain class
│   ├── refills.py                 # RefillManager domain class
│   └── authentication.py         # AuthenticationService
├── services/
│   ├── __init__.py
│   ├── treatment_service.py       # Treatment CRUD + persistence
│   ├── adherence_service.py       # Dose recording + adherence calc
│   ├── symptom_service.py         # Symptom check-in + history
│   ├── followup_service.py        # Follow-up case management
│   ├── refill_service.py          # Refill request workflow
│   ├── patient_service.py         # Patient registration + lookup
│   └── authentication_service.py # Auth wrapper (loads users from JSON)
├── storage/
│   ├── __init__.py
│   └── data_manager.py            # JSON read/write (save_data / load_data + aliases)
├── data/                          # JSON data files (auto-created / seeded)
│   ├── patients.json
│   ├── doctors.json
│   ├── healthworkers.json
│   ├── treatments.json
│   ├── medications.json
│   ├── adherence.json
│   ├── symptoms.json
│   ├── followups.json
│   ├── refills.json
│   └── clinical_notes.json
└── tests/
    ├── __init__.py
    ├── unit/
    │   ├── __init__.py
    │   ├── test_patient.py
    │   ├── test_doctor.py
    │   ├── test_healthworker.py
    │   ├── test_medication.py
    │   └── test_treatment.py
    └── integration/
        ├── __init__.py
        ├── test_treatment_flow.py
        ├── test_adherence_flow.py
        ├── test_refill_flow.py
        └── test_escalation_flow.py
```

---

## Prerequisites

- **Python 3.8+** (tested with 3.10+)
- **pytest** — for running the test suite
- No external dependencies — the project uses only the Python standard library

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd smart-tb-aftercare
```

### 2. (Recommended) Create a virtual environment

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install test dependencies

```bash
pip install pytest
```

### 4. Seed the data files

The `data/` directory must contain JSON files with initial user and clinical data. Copy the seed files from the `seed_data_and_fix.zip` delivery into your `data/` directory:

```bash
# If data/ is empty, copy the seed files
mkdir -p data
cp path/to/seed_data_and_fix/data/* data/
```

At a minimum, you need these three files for login to work:

- `patients.json`
- `doctors.json`
- `healthworkers.json`

Each file must be a JSON array. Example `patients.json`:

```json
[
  {
    "patient_id": 1,
    "name": "John Kamau",
    "username": "john1",
    "password": "john123",
    "phone": "0711111111",
    "role": "patient",
    "needs_attention": false
  }
]
```

### 5. Apply the DataManager fix

The `storage/data_manager.py` file must include `save()` and `load()` alias methods in addition to `save_data()` and `load_data()`. This is because `TreatmentService` and `AdherenceService` call `save()`/`load()`, while the CLI menus call `save_data()`/`load_data()`. Copy the fixed version from `seed_data_and_fix.zip` if needed.

---

## Running the Application

### Basic usage

```bash
python main.py
```

This starts the interactive CLI, loading data from the default `./data` directory.

### Specify a custom data directory

```bash
python main.py --data-dir /path/to/data
```

### Show help

```bash
python main.py --help
```

### Startup sequence

When you run `main.py`, the system:

1. Parses CLI arguments (`--data-dir`)
2. Initializes `DataManager` with the data directory path
3. Instantiates all service objects and wires them together
4. Launches the `main_menu()` interactive loop

---

## Test Accounts

| Role           | Username         | Password       |
|----------------|------------------|----------------|
| Patient        | `john1`          | `john123`      |
| Patient        | `mary2`          | `mary123`      |
| Doctor         | `doctor1`        | `doctor123`    |
| Health Worker  | `healthworker1`  | `health123`    |

> **Note:** You can also register a new patient account from the main menu (option 2).

---

## User Roles & Menu Options

### Main Menu

```
1. Login
2. Register (new patient)
3. Exit
```

### Patient Menu (9 options)

| # | Option | Description |
|---|--------|-------------|
| 1 | View my treatment | Display all active/completed treatments |
| 2 | View my medications | List prescribed medications with dosage details |
| 3 | Record dose | Mark today's dose as taken or missed |
| 4 | View my adherence | Adherence percentage per medication + overall |
| 5 | Symptom check-in | Report symptoms with severity and notes |
| 6 | View symptom history | Review all past check-ins |
| 7 | Request refill | Submit a medication refill request |
| 8 | View refill status | Check the status of submitted refill requests |
| 9 | Logout | Return to main menu |

### Doctor Menu (11 options)

| # | Option | Description |
|---|--------|-------------|
| 1 | View all patients | List every registered patient |
| 2 | View patient details | See a specific patient's profile and treatments |
| 3 | Create treatment | Start a new treatment for a patient |
| 4 | Prescribe medication | Add a medication to an existing treatment |
| 5 | View patient treatments | List all treatments for a patient |
| 6 | View patient adherence | Adherence percentage + missed dose count |
| 7 | View patient symptoms | Review a patient's symptom history |
| 8 | Record clinical note | Write a clinical note for a patient |
| 9 | Complete treatment | Mark a treatment as completed |
| 10 | Update treatment instructions | Change instructions on an active treatment |
| 11 | Logout | Return to main menu |

### Health Worker Menu (11 options)

| # | Option | Description |
|---|--------|-------------|
| 1 | View assigned patients | List all patients assigned to this worker |
| 2 | View patient details | See a specific assigned patient's profile |
| 3 | Monitor adherence | Adherence percentage + missed doses per medication |
| 4 | Review symptoms | View symptom history for an assigned patient |
| 5 | View refill requests | See refill requests from assigned patients |
| 6 | Create follow-up case | Open a new follow-up case for a patient |
| 7 | View follow-up cases | List all cases created by this worker |
| 8 | Update follow-up case | Record an action and/or change case status |
| 9 | Escalate case | Escalate a case to a doctor with a reason |
| 10 | Patients needing attention | List flagged patients with low adherence |
| 11 | Logout | Return to main menu |

---

## Running Tests

### Run the full test suite

```bash
pytest tests/ -v
```

### Run only unit tests

```bash
pytest tests/unit/ -v
```

### Run only integration tests

```bash
pytest tests/integration/ -v
```

### Run a specific test file

```bash
pytest tests/integration/test_refill_flow.py -v
```

### Test structure

| Category | Files | What they test |
|----------|-------|----------------|
| Unit | `test_patient.py`, `test_doctor.py`, `test_healthworker.py`, `test_medication.py`, `test_treatment.py` | Domain class construction, validation, role assignment, profile methods |
| Integration | `test_treatment_flow.py` | Doctor → Treatment → Medication relationships and lifecycle |
| Integration | `test_adherence_flow.py` | Patient → AdherenceTracker → HealthWorker/Doctor monitoring |
| Integration | `test_refill_flow.py` | RefillManager supply calculation, alerts, request lifecycle, duplicate prevention |
| Integration | `test_escalation_flow.py` | Low adherence + severe symptoms → follow-up creation → escalation to doctor |

---

## Known Limitations

1. **SymptomService and FollowUpService** — These services hydrate from JSON on each call and persist back immediately, but there is a subtle edge: if two health workers are active simultaneously, cross-worker data could be overwritten. In practice, this is a single-user CLI, so the risk is minimal.

2. **RefillService** — Each `RefillManager` is scoped to one patient + one medication. The `main.py` entry point creates a default manager at startup; patient-specific managers are created or hydrated on demand by the service layer.

3. **No password hashing** — Passwords are stored in plain text in JSON. This is acceptable for an academic project but must not be used in production.

4. **No concurrent access protection** — JSON files are read/written as whole files. There is no file locking mechanism.

5. **Clinical notes** — Saved to a separate `clinical_notes.json` file. They are not displayed in any CLI menu currently but are persisted.

6. **AuthenticationService expects flat user dicts** — The `main_menu.py` loads users from all three role files and passes them as a flat list. The `AuthenticationServiceWrapper` in the services layer does the same thing with an additional `_refresh_auth()` call. Both approaches work; the CLI uses the simpler `main_menu.py` version.

---

## Team Responsibilities

| Person | Owned Files | Phase A Deliverable | Phase B Deliverable |
|--------|-----------|--------------------|--------------------|
| Person 1(Kamau) | `app/patient.py`, `app/doctor.py`, `app/healthworker.py`, `services/patient_service.py`, `services/authentication_service.py`, `app/authentication.py`, `cli/`, `main.py`, `storage/data_manager.py` | Domain classes + auth | Auth integration | CLI + integration |
| Person 2 (Praise) | `app/treatment.py`, `app/medication.py`, `app/adherence.py`, `services/treatment_service.py`, `services/adherence_service.py` | Treatment & adherence | Service integration |
| Person 3 (Katelyn) | `app/symptoms.py`, `app/followup.py`, `services/symptom_service.py`, `services/followup_service.py` | Symptoms & follow-up | Symptom/follow-up integration |
| Person 4 (Talise) | `app/refills.py`, `services/refill_service.py`, | Refills | 

> **Cross-owner fix:** Person 1 added `save()`/`load()` alias methods to `DataManager` because Person 2's services call `save()`/`load()` while other code calls `save_data()`/`load_data()`. Both names now work.

---

## License

This project is part of a summative group lab assignment. All rights reserved by the contributing team members.
