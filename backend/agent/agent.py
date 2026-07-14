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
from backend.agent.heal_agent import healing_agent

MAX_HEAL_ATTEMPTS = 2

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = GoogleModel("gemini-3.5-flash")

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

    file_path = os.path.join(
        "generated_scripts",
        f"{test_case_id}.py"
    )

    # Use existing script if present
    if os.path.exists(file_path):
        return {
            "status": "success",
            "message": "Using existing generated script.",
            "test_case_id": test_case_id,
            "script_path": file_path
        }

    test_case = get_test_case(test_case_id)

    if test_case is None:
        return {"error": "Test case not found"}

    prompt = build_script_prompt(test_case)

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    generated_code = response.text

    os.makedirs("generated_scripts", exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(generated_code)

    return {
        "status": "success",
        "message": "New script generated.",
        "test_case_id": test_case_id,
        "script_path": file_path
    }

@agent.tool
def execute_script(ctx: RunContext, test_case_id: str) -> dict:
    """
    Execute a generated Playwright script and self-heal if it fails.
    """

    script_path = os.path.join(
        "generated_scripts",
        f"{test_case_id}.py"
    )

    if not os.path.exists(script_path):
        return {
            "status": "error",
            "test_case_id": test_case_id,
            "message": "Generated script not found.",
            "script_path": script_path
        }

    os.makedirs("execution_logs", exist_ok=True)

    log_path = os.path.join(
        "execution_logs",
        f"{test_case_id}.log"
    )

    heal_attempts = 0
    healing_used = False
    healing_summary = "No self-healing was required."

    while heal_attempts <= MAX_HEAL_ATTEMPTS:

        try:
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

        # Save execution log
        with open(log_path, "w", encoding="utf-8") as log:
            log.write("===== STDOUT =====\n")
            log.write(result.stdout)

            log.write("\n\n===== STDERR =====\n")
            log.write(result.stderr)

            log.write("\n\n===== RETURN CODE =====\n")
            log.write(str(result.returncode))

        
        if result.returncode == 0:
            break

      
        with open(script_path, "r", encoding="utf-8") as f:
            script = f.read()

        with open(log_path, "r", encoding="utf-8") as f:
            execution_log = f.read()

        # Fetch test case
        test_case = get_test_case(test_case_id)

        healing_used = True
        healing_summary = "Script execution failed. Self-healing was triggered."
        print("\n===== SELF HEALING STARTED =====")

        # Call healing agent
        healing_agent.run_sync(
            f"""
Repair the failed Playwright script using the available tool.

Test Case:
{test_case}

Script:
{script}

Execution Error:
{result.stderr}

Execution Log:
{execution_log}

Script Path:
{script_path}
"""
        )
        print("===== SELF HEALING COMPLETED =====\n")
        # Verify script changed
        with open(script_path, "r", encoding="utf-8") as f:
            updated_script = f.read()

        if updated_script.strip() != script.strip():
             healing_summary = "Script was successfully repaired and updated."
        else:
            healing_summary = "Self-healing was attempted but no changes were made."
            break

        heal_attempts += 1

    return {
        "status": "success" if result.returncode == 0 else "failed",
        "test_case_id": test_case_id,
        "return_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "script_path": script_path,
        "log_file": log_path,
        "healing_used": healing_used,
        "healing_summary": healing_summary,
        "heal_attempts": heal_attempts
    }


@agent.tool
def analyze_results(
    ctx: RunContext,
    test_case_id: str,
    healing_used: bool = False,
    heal_attempts: int = 0,
    healing_summary: str = ""
) -> dict:
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

Self-Healing Information:
Used: {"Yes" if healing_used else "No"}
Attempts: {heal_attempts}
Summary:
{healing_summary}

Generate a professional execution report using the following format.

1. Test Status
   - Passed / Failed

2. Execution Summary
   - Briefly describe what happened during execution.

3. Self-Healing
   - Mention whether self-healing was triggered.
   - If yes, summarize what was repaired.
   - Mention the number of healing attempts.

4. Failure Reason
   - If the test ultimately failed, explain why.
   - If the test passed after healing, clearly mention that.

5. Recommendation
   - Suggest any improvements if required.

Keep the report concise, professional and suitable for QA engineers.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return {
        "status": "success",
        "test_case_id": test_case_id,
        "analysis": response.text,
        "healing_used": healing_used,
        "heal_attempts": heal_attempts,
        "healing_summary": healing_summary,
        "log_file": log_path
    }