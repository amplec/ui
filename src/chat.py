import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import requests

st.set_page_config(layout="wide",page_title="Amplec - Chat", initial_sidebar_state="collapsed", page_icon="amplec.ico")

def show_settings_dialog():
    """
    This will display a dialog for Regex & Submission ID settings
    """
    
    st.write("## ID & Regex Settings")
    with st.form("regex_and_id_form"):
        st.session_state["regex"] = st.text_input(
            "Enter Regex or Search String", 
            value=st.session_state.get("regex", "")
        )
        st.session_state["submission_id"] = st.text_input(
            "Enter Submission ID", 
            value=st.session_state.get("submission_id", "")
        )
        st.session_state["regex_or_search"] = st.checkbox("Use as RegEx",value=st.session_state.get("regex_or_search", False), help="If not checked, it will be used as a search string")
        
        if st.form_submit_button("Save"):
            # TODO: Build validation here
            st.session_state["error"] = False
            
            if not st.session_state["error"]:
                st.session_state["show_dialog"] = False

            st.rerun()
    
def main():
    if "regex" not in st.session_state:
        st.session_state["regex"] = ""
    if "submission_id" not in st.session_state:
        st.session_state["submission_id"] = ""
    if "regex_or_search" not in st.session_state:
        st.session_state["regex_or_search"] = False    
    if "error" not in st.session_state:
        st.session_state["error"] = False
    if "show_dialog" not in st.session_state:
        st.session_state["show_dialog"] = False
    
    if not st.session_state["show_dialog"]:
        st.session_state["show_dialog"] = st.session_state["submission_id"] == "" or st.session_state["error"]
                                       
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
    
    form_data = {
        "karton_submission_id": st.session_state["submission_id"],
        "regex_or_search": st.session_state["regex"],
        "use_regex": st.session_state["regex_or_search"],
    }
    response = requests.post("http://core:5000/process", data=form_data)
    
    if response.status_code == 200:
        try:
            karton_input_data = response.json().get("data",[])
        except Exception as e:
            return f"Error: {e}"
    else:
        return f"Error: {response.status_code}"
    
    system_message = "You are an assistant for a malware researcher, you will be provided with information about the malware sample. The user can control what the data you receive will be. Please dont infer or guess informatin outside the provided data."
    user_input = f"{user_input} {' '.join(str(input_str) for input_str in karton_input_data)}"
    
    chat_response = requests.post("http://core:5000/chat", data={"system_message": system_message, "user_message": user_input})
    if chat_response.status_code == 200:
        try:
            chatbot_response = chat_response.json().get("data","ERROR")
        except Exception as e:
            return f"Error: {e}"
    else:
        return f"Error, something went wrong with the llm chat answer {chat_response.text}"
    
    return chatbot_response
    

if __name__ == "__main__":
    main()