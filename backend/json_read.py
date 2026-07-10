import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "test_cases.json"


def load_test_cases():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
    
def get_test_case(test_case_id):
    data = load_test_cases()

    for tc in data["test_cases"]:
        if tc["id"] == test_case_id:
            return tc

    return None
