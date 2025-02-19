import streamlit as st
import requests
import json
import os
import re 
from uuid import uuid4
from dotenv import load_dotenv # For loading environment variables
load_dotenv()
# Configuration
HISTORY_FILE = "chat_history.json"
API_TOKEN = os.getenv("API_TOKEN")
MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# Load chat history
def load_chats():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"chats": {}, "current_chat": None}

# Save chat history
def save_chats(chats):
    with open(HISTORY_FILE, "w") as f:
        json.dump(chats, f)

# Initialize session state
if "chats" not in st.session_state or not isinstance(st.session_state.chats, dict):
    st.session_state.chats = load_chats()

# Ensure structure is correct
if "chats" not in st.session_state.chats:
    st.session_state.chats["chats"] = {}
if "current_chat" not in st.session_state.chats:
    st.session_state.chats["current_chat"] = None

# Create a new chat
def create_new_chat():
    chat_id = str(uuid4())
    st.session_state.chats["chats"][chat_id] = {
        "name": "👻 TeenBuddy 🤖- Your 24/7 Support Pal",
        "messages": []
    }
    st.session_state.chats["current_chat"] = chat_id
    save_chats(st.session_state.chats)

# Delete a chat
def delete_chat(chat_id):
    if chat_id in st.session_state.chats["chats"]:
        del st.session_state.chats["chats"][chat_id]
        if st.session_state.chats["chats"]:
            st.session_state.chats["current_chat"] = list(st.session_state.chats["chats"].keys())[0]
        else:
            create_new_chat()
        save_chats(st.session_state.chats)
        st.rerun()

# Generate AI response
def generate_response(prompt):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    api_url = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
    current_chat_id = st.session_state.chats["current_chat"]
    current_messages = st.session_state.chats["chats"][current_chat_id]["messages"][-4:]

    full_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in current_messages])
    full_prompt += f"\nuser: {prompt}\nassistant:"
    
    payload = {
        "inputs": full_prompt,
        "parameters": {"max_new_tokens": 200, "temperature": 0.7, "repetition_penalty": 1.1}
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        return response.json()[0]['generated_text'].split("assistant:")[-1].strip()
    except:
        return "Let's focus on something fun! 😊 What's a highlight from today?"

# UI Setup
st.set_page_config(page_title="TeenBuddy - Your AI Friend", page_icon="🤝", layout="wide")

# Sidebar: Chat List
with st.sidebar:
    st.header("Chat History")
    if st.button("➕ New Chat"):
        create_new_chat()
        st.rerun()
    
    for chat_id in reversed(list(st.session_state.chats["chats"].keys())):  # Bottoms-up format
        chat = st.session_state.chats["chats"][chat_id]
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"💬 {chat['name']}", key=f"btn_{chat_id}", use_container_width=True):
                st.session_state.chats["current_chat"] = chat_id
                st.rerun()
        with col2:
            if st.button("❌", key=f"del_{chat_id}"):
                delete_chat(chat_id)

# Main Chat Interface
current_chat_id = st.session_state.chats.get("current_chat")
if current_chat_id and current_chat_id in st.session_state.chats["chats"]:
    current_chat = st.session_state.chats["chats"][current_chat_id]
    st.title(f"💬 {current_chat['name']}")
    
    for msg in current_chat["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])
    


    if prompt := st.chat_input("What's on your mind?"):
    # Add user message
        st.chat_message("user").write(prompt)
        current_chat["messages"].append({"role": "user", "content": prompt})

    # Set the chat title if it's the first message
    if len(current_chat["messages"]) == 2:  # First user message
        words = re.findall(r'\b\w+\b', prompt)  # Extract words
        short_title = " ".join(words[:4])  # Take first 4 words
        current_chat["name"] = short_title if short_title else "New Chat"

    # Generate AI response
    with st.spinner("Thinking..."):
        response = generate_response(prompt)

    # Add AI response
    current_chat["messages"].append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

    # Save updated chats
    save_chats(st.session_state.chats)


if not st.session_state.chats["chats"]:
    create_new_chat()
    st.rerun()

# About Section
with st.sidebar:
    st.info("""
    **Features:**
    - Remembers past conversations
    - Context-aware responses
    - Teen-friendly and empathetic
    """)
    
    st.subheader("Need Immediate Help?")
    st.write("""
    🆘 Contact these free helplines:
    - ChildHelp (IN): 1098
    - Helpline Number (IN): 112
    - Depression helpline number India: 1800-599-0019
    """)
    
    st.subheader("Facing Error?")
    st.write("""
    🛠️ If you encounter any issues, please Contact: 
             - [Email](mailto:jeet.github.tm@gmail.com)
    """)
