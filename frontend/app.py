import time
import requests
import streamlit as st

st.set_page_config(
    page_title="Agentic Test Automation",
    layout="wide"
)

st.title("Agentic Test Automation")

st.markdown("""
This application demonstrates an **Agentic AI-Powered Test Automation Framework** for the **Swag Labs** application.

**Application Under Test:** [https://www.saucedemo.com/](https://www.saucedemo.com/)

Five manual test cases are already available in the system.

Enter a valid **Test Case ID** (**TC-001** to **TC-005**) and click **Run Test**.

The framework automatically:

- Fetches the manual test case.
- Generates a Playwright automation script using AI.
- Executes the generated script.
- Performs self-healing if execution fails.
- Analyzes the execution results.
- Displays the final execution report.
""")

st.divider()

with st.sidebar:

    st.header("Project Information")

    st.write("**Application**")
    st.write("Swag Labs")

    st.write("**Automation Framework**")
    st.write("Playwright")

    st.write("**Backend**")
    st.write("FastAPI")

    st.write("**AI Framework**")
    st.write("PydanticAI")

    st.write("**Language Model**")
    st.write("Gemini 3.5 Flash")

    st.write("**Available Test Cases**")
    st.code(
        """TC-001
TC-002
TC-003
TC-004
TC-005"""
    )
#input
st.subheader("Execute Test Case")

col1, col2 = st.columns([4, 1])

with col1:
    test_case_id = st.text_input(
        "Test Case ID",
        value="TC-001",
        placeholder="Enter Test Case ID"
    )

with col2:
    st.write("")
    st.write("")
    run = st.button("Run Test", use_container_width=True)

st.divider()
#workflow
if run:

    if not test_case_id.strip():
        st.warning("Please enter a valid Test Case ID.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()

    try:

        status.info("Fetching test case...")
        progress.progress(20)
        time.sleep(0.5)

        status.info("Generating Playwright script...")
        progress.progress(40)
        time.sleep(0.5)

        status.info("Executing test script...")
        progress.progress(70)
        time.sleep(0.5)

        status.info("Analyzing execution results...")
        progress.progress(90)

        response = requests.post(
            "http://127.0.0.1:8000/run-test",
            json={
                "test_case_id": test_case_id
            },
            timeout=300
        )

        data = response.json()

        progress.progress(100)
        status.empty()

    except requests.exceptions.ConnectionError:

        st.error("Unable to connect to the FastAPI backend.")
        st.info(
            "Start the backend server using:\n\n"
            "uvicorn backend.main:app --reload"
        )
        st.stop()

    except Exception as e:

        st.error(f"Unexpected Error: {e}")
        st.stop()

    #Response
    if data.get("status") == "success":

        st.success("Test execution completed successfully.")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Test Case", test_case_id)

        with col2:
            st.metric("Status", "Success")

        st.divider()

        st.subheader("Execution Summary")

        st.text_area(
            label="",
            value=data.get("result", ""),
            height=300
        )
    else:

        st.error("Test execution failed.")

        st.subheader("Error Details")

        st.text_area(
            label="",
            value=data.get("message", "Unknown Error"),
            height=250
        )

st.divider()
