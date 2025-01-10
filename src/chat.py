import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide",page_title="Amplec - Chat", initial_sidebar_state="collapsed", page_icon="amplec.ico")

def show_settings_dialog():
    """
    This will display a dialog for Regex & Submission ID settings
    """
    
    st.write("## ID & Regex Settings")
    with st.form("regex_and_id_form"):
        st.session_state["regex"] = st.text_input(
            "Enter Regex", 
            value=st.session_state.get("regex", "")
        )
        st.session_state["submission_id"] = st.text_input(
            "Enter Submission ID", 
            value=st.session_state.get("submission_id", "")
        )

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

            response = f"Echo: {user_input}"
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

if __name__ == "__main__":
    main()