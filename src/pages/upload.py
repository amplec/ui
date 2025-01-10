import streamlit as st
import requests
import time
from streamlit_extras.switch_page_button import switch_page
st.set_page_config(layout="wide",page_title="Amplec - Karton Submission", initial_sidebar_state="collapsed", page_icon="amplec.ico")

def main():
    st.title("Amplec - Karton Submission")
    org = st.selectbox(
        label="Organization (org) *",
        options=["cert", "cti", "irs", "soc", "other"],
        help="Required. Currently does not affect anything, but will be used for default analysis profiles in the future."
    )

    sample = st.file_uploader(
        label="Sample file *",
        type=None,
        help="Required. Upload the sample file you want to submit."
    )

    priority = st.selectbox(
        label="Priority",
        options=["normal", "low", "high"],
        help="Priority of the sample. Default is normal."
    )

    origin = st.text_input(
        label="Origin (optional)",
        help="If specified, adds the 'external-origin' attribute to the created payload."
    )

    tags_input = st.text_area(
        label="Tags (optional)",
        help="Enter one tag per line in the format key=value. key must not contain '='. Value can contain '='."
    )

    tags_list = [
        line.strip()
        for line in tags_input.split("\n")
        if line.strip()
    ]

    profile = st.text_input(
        label="Profile (optional)",
        help="Not yet supported. Name of the analysis profile if used in the future."
    )

    create_sandbox_job = st.checkbox(
        label="Create Sandbox Job?",
        help="If checked, sets create_sandbox_job=true. If not checked, sets it to false."
    )

    sandbox_cmdline = st.text_input(
        label="Sandbox Command Line (optional)",
        help="Used in conjunction with create_sandbox_job to specify how the sample is executed in a sandbox."
    )

    family = st.text_input(
        label="Malware Family (optional)",
        help="If specified, used for routing to the correct sandbox or for classification."
    )

    if st.button("Submit"):

        if not sample:
            st.warning("Please upload a sample file before submitting.")
            return
        
        data = {"org": org}
        
        if priority: data["priority"] = priority
        if origin: data["origin"] = origin
        if tags_list: data["tags"] = tags_list
        if profile: data["profile"] = profile
        if create_sandbox_job: data["create_sandbox_job"] = "true"
        if sandbox_cmdline: data["sandbox_cmdline"] = sandbox_cmdline
        if family: data["family"] = family

        files = {"sample": (sample.name, sample, sample.type)}

        endpoint_url = "http://cti-karton.cert.local:5160/submit-sample"

        with st.spinner("Submitting your sample. Please wait..."):
            try:
                response = requests.post(
                    url=endpoint_url,
                    data=data,
                    files=files
                )
            except Exception as e:
                st.error(f"Exception occurred while submitting the sample: {e}")
                return

        if response.status_code in (200, 201):
            submission_id = ""
            try:
                resp_json = response.json()
                submission_id = resp_json.get("analysis_id", "")
                st.json(resp_json)
            except Exception:
                st.write(response.text)

            st.success("Sample submitted successfully!")

            if submission_id:
                st.session_state["submission_id"] = submission_id

            time.sleep(5)
            switch_page("Chat")

        else:
            st.error(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    main()