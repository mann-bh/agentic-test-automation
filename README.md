# Agentic Test Automation

An AI-powered test automation framework that converts manual test cases into executable **Playwright (Python)** scripts using **Gemini 3.5 Flash** and **PydanticAI**. The generated scripts are executed automatically, and the execution results are analyzed to provide a concise test summary.

## Workflow
The workflow begins when the user enters a Test Case ID through the Streamlit interface. The request is sent to the FastAPI backend, where the PydanticAI agent orchestrates the entire process. First, the agent retrieves the corresponding manual test case from the JSON repository. It then uses Gemini 3.5 Flash to generate an executable Playwright (Python) automation script, which is saved in the generated_scripts/ directory for future reference. The agent executes the generated script using Playwright, and the execution output, including logs, is stored in the execution_logs/ directory. Finally, the execution logs are analyzed by Gemini 3.5 Flash to determine whether the test passed or failed, identify the probable cause of any failure, and generate a concise, human-readable execution summary that is displayed to the user in the Streamlit application.

## Features

* Generate Playwright scripts from manual test cases
* Execute generated scripts automatically
* AI-based execution result analysis
* FastAPI backend
* Streamlit frontend
* Modular agent architecture
* JSON-based test case repository
* Easy to extend with additional AI tools and workflows

## Tech Stack

* Python
* FastAPI
* Streamlit
* Playwright (Python)
* PydanticAI
* Gemini 3.5 Flash
* python-dotenv

## Workflow

1. Enter a Test Case ID in the Streamlit application.
2. Fetch the corresponding manual test case from the JSON repository.
3. Generate a Playwright automation script using Gemini 3.5 Flash.
4. Save the generated script.
5. Execute the script using Playwright.
6. Store execution logs.
7. Analyze the execution results using AI.
8. Display the final execution summary.

---

## Setup

### 1. Clone the repository


### 2. Create a virtual environment


### 3. Activate the environment

### 4. Install dependencies

```bash
pip install -r requirements.txt
```
---

## Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_api_key
```

---

## Run the Project

### Start the FastAPI backend

```bash
uvicorn backend.main:app
```

FastAPI Docs:

```
http://127.0.0.1:8000/docs
```

### Start the Streamlit frontend

```bash
streamlit run frontend/app.py
```

---

## API Endpoint

| Method | Endpoint                     | Description                 |
| ------ | ---------------------------- | --------------------------- |
| GET    | `/test_cases/{test_case_id}` | Retrieve a manual test case |


## License

This project is intended for learning, experimentation, and demonstration purposes.
