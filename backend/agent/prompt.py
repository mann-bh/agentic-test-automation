SYSTEM_PROMPT = """
You are an expert Playwright Automation Engineer.

You have access to the following tools:

1. fetch_test_case(test_case_id)
2. generate_script(test_case_id)
3. execute_script(test_case_id)
4. analyze_results(test_case_id)

Workflow:

1. Fetch the manual test case using fetch_test_case().
2. Generate the Playwright script using generate_script().
3. Execute the generated script using execute_script().
4. Analyze the execution results using analyze_results().
5. Return a concise execution summary.

Always use the available tools.
Never generate Playwright code yourself.
Never skip any workflow step.
"""

def build_script_prompt(test_case: dict) -> str:

    steps_text = "\n".join(
        f"Step {step['step']}: {step['action']}\nExpected: {step['expected_result']}"
        for step in test_case["steps"]
    )

    return f"""
Generate Playwright Python code for the following manual test case.

Test Case ID:
{test_case["id"]}

Title:
{test_case["title"]}

Objective:
{test_case["objective"]}

Steps:
{steps_text}

Rules:
1. Return only Playwright Python code.
2. Use the Playwright Python Sync API.
3. Include all required imports.
4. Generate runnable code.
5. Do not include markdown or explanations.
6. Add print() statements for major execution steps.
7. Print "Test execution started" at the beginning.
8. Print the current action before performing it.
9. Print "Test Passed" if the test completes successfully.
10. Wrap the test logic in a try-except-finally block.
11. If an exception occurs:
    - Print "Test Failed".
    - Print the exception message.
    - Re-raise the exception.
12. Close the browser inside the finally block before exiting the sync_playwright() context.
"""