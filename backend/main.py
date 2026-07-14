from fastapi import FastAPI
from pydantic import BaseModel

from backend.json_read import get_test_case
from backend.agent.agent import agent

app = FastAPI()


class TestRequest(BaseModel):
    test_case_id: str


@app.get("/")
def home():
    return {
        "message": "testing poc"
    }


@app.get("/test_cases/{test_case_id}")
def test_id(test_case_id: str):
    result = get_test_case(test_case_id)

    if result is None:
        return {
            "error": "Test case not found"
        }

    return result


@app.post("/run-test")
def run_test(request: TestRequest):
    try:
        result = agent.run_sync(
            f"Execute the complete workflow for test case {request.test_case_id}."
        )

        return {
            "status": "success",
            "test_case_id": request.test_case_id,
            "result": result.output
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }