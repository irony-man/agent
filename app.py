import streamlit as st
from agent import get_cricket_agent
from db import MongoManager
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler

st.set_page_config(page_title="Crickbot", layout="wide")
db = MongoManager()

# Sidebar Setup
st.sidebar.title("Settings")
session_id = st.sidebar.text_input("User Session ID", "user_123")

if "messages" not in st.session_state:
    st.session_state.messages = db.get_session_history(session_id)

# Main UI
st.title("Crickbot")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 1. Check Cache First (Save Quota)
    cached_data = db.check_cache(prompt)
    
    with st.chat_message("assistant"):
        if cached_data:
            st.info("Loaded from Cache")
            data = cached_data["data"]
            st.write(data["summary"])
            st.table(data["stats_table"])
            final_content = data["summary"]
        else:
            try:
                agent = get_cricket_agent()
                st_cb = StreamlitCallbackHandler(st.container())
                
                response = agent.invoke(
                    {"messages": st.session_state.messages},
                    {"callbacks": [st_cb]}
                )
                
                # FIXED: Access structured_response key
                res_obj = response["structured_response"]
                
                st.write(res_obj.summary)
                st.table([p.model_dump() for p in res_obj.stats_table])
                
                # Update Cache & History
                db.set_cache(prompt, res_obj.model_dump())
                final_content = res_obj.summary
                
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")
                final_content = "Analysis failed."

        st.session_state.messages.append({"role": "assistant", "content": final_content})
        db.save_session_history(session_id, st.session_state.messages)