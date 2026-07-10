from fastapi import FastAPI
from backend.json_read import get_test_case
app = FastAPI()

@app.get("/")
def home():
    return{
"message": "testing poc"
    }

@app.get("/test_cases/{test_case_id}")
def test_id(test_case_id : str):
    result= get_test_case(test_case_id)
    if result is None:
        return "Error: test case not found"
    return result