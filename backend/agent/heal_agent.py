from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from backend.agent.heal_prompt import HEALING_SYSTEM_PROMPT
from google import genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = GoogleModel("gemini-3.5-flash")

healing_agent = Agent(
    model=model,
    system_prompt=HEALING_SYSTEM_PROMPT
)


def strip_markdown_fences(code: str) -> str:
    """
    Remove markdown code fences returned by Gemini.
    """
    code = code.strip()

    if code.startswith("```"):
        code = code.replace("```python", "")
        code = code.replace("```", "")
        code = code.strip()

    return code


@healing_agent.tool_plain
def heal_script(
    test_case: dict,
    script: str,
    error: str,
    log: str,
    script_path: str
) -> dict:
    """
    Repair a failed Playwright script and overwrite the existing script.
    """

    prompt = f"""
Original Manual Test Case:
{test_case}

Current Playwright Script:
{script}

Execution Error:
{error}

Execution Log:
{log}

Your task:

1. Identify the root cause of the failure.
2. Modify ONLY the failing part.
3. Preserve the original test logic.
4. Keep existing print() statements whenever possible.
5. Use the Playwright Python Sync API.
6. Return ONLY valid runnable Python code.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    healed_code = strip_markdown_fences(response.text)

    # Overwrite the existing script with the healed version
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(healed_code)

    return {
        "status": "success",
        "message": "Script healed successfully.",
        "script_path": script_path
    }