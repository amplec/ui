import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import requests, uuid, re
from typing import Optional

st.set_page_config(layout="wide",page_title="Amplec - Chat", initial_sidebar_state="collapsed", page_icon="amplec.ico")

def show_settings_dialog():
    """
    This will display a dialog for settings
    """

    st.write("## Amplec Settings")

    # Function Calling checkbox OUTSIDE the form
    st.session_state["function_calling"] = st.checkbox(
        "Function Calling",
        value=st.session_state["function_calling"],
        help="If checked, the llm will be doing function calling on its own, so the regex and search will be obsolete."
    )

    # Trigger re-run immediately when function_calling changes
    if "function_calling_changed" not in st.session_state:
        st.session_state["function_calling_changed"] = False

    if st.session_state["function_calling_changed"] != st.session_state["function_calling"]:
        st.session_state["function_calling_changed"] = st.session_state["function_calling"]
        st.rerun()

    with st.form("settings_form"):
        model_options = ["llama3.2:3b", "llama3.1:8b", "gpt-4o", "gpt-4o-mini"]
        st.session_state["model"] = st.selectbox(
            label="Select Model",
            options=model_options,
            index=model_options.index(st.session_state["model"]),
            help="Choose a model for processing. 'gpt-4o' and 'gpt-4o-mini' require an API key."
        )
        st.session_state["api_key"] = st.text_input(
            "Enter API Key",
            value=st.session_state["api_key"],
            type="password"
        )
        st.session_state["regex"] = st.text_input(
            "Enter Regex or Search String",
            value=st.session_state["regex"],
            disabled=st.session_state["function_calling"]
        )
        st.session_state["submission_id"] = st.text_input(
            "Enter Submission ID",
            value=st.session_state["submission_id"]
        )
        st.session_state["regex_or_search"] = st.checkbox(
            "Use as RegEx",
            value=st.session_state["regex_or_search"],
            help="If not checked, it will be used as a search string",
            disabled=st.session_state["function_calling"]
        )
        st.session_state["force_rerun"] = st.checkbox(
            "Force Rerun",
            value=st.session_state["force_rerun"],
            help="If checked, the karton data will be reloaded and reprocessed, rather than using the cached data"
        )

        st.session_state["system_prompt"] = st.text_area(
            "System Prompt",
            value=st.session_state["system_prompt"],
            disabled=st.session_state["function_calling"]
        )
        
        st.session_state["tool_system_prompt"] = st.text_area(
            "System Prompt, when tool-calling is enabled",
            value=st.session_state["tool_system_prompt"],
            disabled=not st.session_state["function_calling"]
        )

        if st.form_submit_button("Save"):
            # TODO: Build validation here
            st.session_state["error"] = False  # You don't have an error variable defined, so I'm assuming you meant this

            if not st.session_state["error"]:
                st.session_state["show_dialog"] = False
                st.toast("Settings Saved!", icon="✅") # Optional: Show a success message
            
            st.rerun()
    
def main():
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""
    if "model" not in st.session_state:
        st.session_state["model"] = "llama3.2:3b"
    if "regex" not in st.session_state:
        st.session_state["regex"] = ""
    if "submission_id" not in st.session_state:
        st.session_state["submission_id"] = ""
    if "regex_or_search" not in st.session_state:
        st.session_state["regex_or_search"] = False
    if "force_rerun" not in st.session_state:
        st.session_state["force_rerun"] = False
    if "function_calling" not in st.session_state:
        st.session_state["function_calling"] = False
    if "system_prompt" not in st.session_state:
        st.session_state["system_prompt"] = "You are an assistant for a malware researcher, you will be provided with information about the malware sample. The user can control what the data you receive will be. Please dont infer or guess information outside the provided data. IF YOU DONT RECEIVE ANY DATA, SAY SO AND DONT HALLUCINATE ANYTHING."
    if "tool_system_prompt" not in st.session_state:
        st.session_state["tool_system_prompt"] = "You are an assistant for a malware researcher, you have tools associated with you, with the tool you can search for information about the malware sample. Please dont infer or guess information outside the provided data. IF YOU DONT RECEIVE ANY DATA, SAY SO AND DONT HALLUCINATE ANYTHING. Keep in mind, that the tool is working best, if you only provide one search term at a time."
    if "error" not in st.session_state:
        st.session_state["error"] = False
    if "show_dialog" not in st.session_state:
        st.session_state["show_dialog"] = False
    
    
    if not st.session_state["show_dialog"]:
        st.session_state["show_dialog"] = ((st.session_state["submission_id"] == "") and not st.session_state["function_calling"]) or st.session_state["error"]
                                       
    if st.session_state["show_dialog"]:
        show_settings_dialog()
    else:
        st.title("Chat with your Malware - Amplec")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message(name="user", avatar=":material/psychology_alt:"):
                    st.write(msg["content"])
            if msg["role"] == "assistant":
                with st.chat_message(name="assistant", avatar=":material/precision_manufacturing:"):
                    st.write(msg["content"])

        user_input = st.chat_input("Type here...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message(name="user", avatar=":material/psychology_alt:"):
                st.write(user_input)
            
            response = _chatbot(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message(name="assistant", avatar=":material/precision_manufacturing:"):
                st.write(response)

        spacer1, col_btn1, spacer2, col_btn2, spacer3 = st.columns([1,1,1,1,1])

        with col_btn1:
            if st.button("ID & Regex Settings"):
                st.session_state["show_dialog"] = True
                st.rerun()

        with col_btn2:
            if st.button("Go to Upload Page"):
                switch_page("Upload")
                
def _chatbot(user_input) -> str:
    """
    This method will implement the actual chatbot logic
    :param user_input: The user input
    :return: The response from the chatbot
    """
    
    submission_id = _find_submission_id(user_input)
    if not submission_id:
        st.warning("No submission ID found in the prompt, using the submission ID from the settings.")
        submission_id = st.session_state["submission_id"]
    if not _check_for_validity_of_uuid(submission_id):
        st.error("Could not answer because neither submission ID was provided in the prompt nor the submission ID from the settings is valid.")
        return "ERROR"
    
    if not st.session_state["function_calling"]:
        form_data = {
            "karton_submission_id": submission_id,
            "regex_or_search": st.session_state["regex"],
            "use_regex": st.session_state["regex_or_search"],
            "reprocess": st.session_state["force_rerun"],
        }
        response = requests.post("http://core:5000/process", data=form_data)
        
        if response.status_code == 200:
            try:
                karton_input_data = response.json().get("data",[])
            except Exception as e:
                return f"Error: {e}"
        else:
            return f"Error: {response.status_code}"
        user_input = f"{user_input} {' '.join(str(input_str) for input_str in karton_input_data)}"
    
    
    system_message = st.session_state["system_prompt"] if not st.session_state["function_calling"] else st.session_state["tool_system_prompt"]
    
    dict_for_request = {"system_message": system_message, "user_message": user_input, "reprocess": st.session_state["force_rerun"], "function_calling": st.session_state["function_calling"], "model": st.session_state["model"], "api_key": st.session_state["api_key"], "submission_id": submission_id}
              
    chat_response = requests.post("http://core:5000/chat", data=dict_for_request)
    if chat_response.status_code == 200:
        try:
            chatbot_response = chat_response.json().get("data","ERROR")
        except Exception as e:
            return f"Error: {e}"
    else:
        return f"Error, something went wrong with the llm chat answer {chat_response.text}"
    
    return chatbot_response
    
    
def _find_submission_id(user_input:str) -> Optional[str]:
    """
    This method will find the submission ID in the user input
    :param user_input: The user input
    :return: The submission ID
    """
    
    uuid_pattern = r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b'

    matches = re.findall(uuid_pattern, user_input)
    
    if len(matches) == 1:
        return matches[0]
    else:
        return None

def _check_for_validity_of_uuid(uuid_to_check:str) -> bool:
    """
    This method will check if the provided string is a valid UUID
    
    :param uuid_to_check: This is the string to check if it is a valid UUID
    :type uuid_to_check: str
    :return: True if the provided string is a valid UUID, False otherwise
    :rtype: bool
    """
    
    try:
        uuid_obj = uuid.UUID(uuid_to_check, version=4)
        return str(uuid_obj) == uuid_to_check
    except ValueError:
        return False


if __name__ == "__main__":
    main()