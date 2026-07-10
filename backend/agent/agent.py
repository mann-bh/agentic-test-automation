from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from backend.agent.prompt import SYSTEM_PROMPT
from backend.json_read import get_test_case
from pydantic_ai import RunContext
import os
import subprocess
from google import genai
from backend.agent.prompt import build_script_prompt
import sys

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = GoogleModel("gemini-2.5-flash")

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT
)
@agent.tool
def fetch_test_case(ctx: RunContext, test_case_id: str) -> dict:
    print(f"Tool called with: {test_case_id}") 
    
    result = get_test_case(test_case_id)

    if result is None:
        return {"error": "Test case not found"}

    return result

@agent.tool
def generate_script(ctx: RunContext, test_case_id: str) -> dict:


    test_case = get_test_case(test_case_id)

    if test_case is None:
        return {"error": "Test case not found"}

    prompt = build_script_prompt(test_case)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    generated_code = response.text

    os.makedirs("generated_scripts", exist_ok=True)

    file_path = os.path.join(
        "generated_scripts",
        f"{test_case_id}.py"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(generated_code)

    return {
    "status": "success",
    "test_case_id": test_case_id,
    "script_path": file_path
}


@agent.tool
def execute_script(ctx: RunContext, test_case_id: str) -> dict:
    """
    Execute a generated Playwright script and collect execution results.
    """

    # Path to generated Playwright script
    script_path = os.path.join(
        "generated_scripts",
        f"{test_case_id}.py"
    )

    # Check if script exists
    if not os.path.exists(script_path):
        return {
            "status": "error",
            "test_case_id": test_case_id,
            "message": "Generated script not found.",
            "script_path": script_path
        }

    try:
        # Execute the Playwright script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )

    except Exception as e:
        return {
            "status": "error",
            "test_case_id": test_case_id,
            "message": str(e),
            "script_path": script_path
        }

    # Create logs directory
    os.makedirs("execution_logs", exist_ok=True)

    log_path = os.path.join(
        "execution_logs",
        f"{test_case_id}.log"
    )

    # Save execution log
    with open(log_path, "w", encoding="utf-8") as log:
        log.write("===== STDOUT =====\n")
        log.write(result.stdout)

        log.write("\n\n===== STDERR =====\n")
        log.write(result.stderr)

        log.write("\n\n===== RETURN CODE =====\n")
        log.write(str(result.returncode))

    # Return execution details
    return {
        "status": "success" if result.returncode == 0 else "failed",
        "test_case_id": test_case_id,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "script_path": script_path,
        "log_file": log_path
    }


@agent.tool
def analyze_results(ctx: RunContext, test_case_id: str) -> dict:
    """
    Analyze the execution log using Gemini and generate a human-readable summary.
    """

    log_path = os.path.join(
        "execution_logs",
        f"{test_case_id}.log"
    )

    if not os.path.exists(log_path):
        return {
            "status": "error",
            "message": "Execution log not found."
        }

    with open(log_path, "r", encoding="utf-8") as f:
        execution_log = f.read()

    prompt = f"""
You are an experienced QA Automation Engineer.

Analyze the following Playwright execution log.

Test Case ID:
{test_case_id}

Execution Log:
{execution_log}

Generate a concise report with the following sections:

1. Test Status (Passed / Failed)
2. Execution Summary
3. Failure Reason (if any)
4. Recommendation

Keep the response professional and easy to understand.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {
        "status": "success",
        "test_case_id": test_case_id,
        "analysis": response.text,
        "log_file": log_path
    }