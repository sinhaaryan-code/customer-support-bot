import streamlit as st
from google import genai
from google.genai import types
import time 
# Page layout & title
st.set_page_config(page_title="Customer Support Assistant", page_icon="🎧", layout="centered")
st.title("🎧 Customer Support Desk")
st.caption("24/7 AI-powered assistance for your orders, refunds, and inquiries.")

# Fetch API key from Streamlit secrets or sidebar input
try:
    api_key = st.secrets.get("GEMINI_API_KEY", None)
except Exception:
    api_key = None

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
    if not api_key:
        st.info("Please enter your Gemini API key in the sidebar or configure it in secrets to start chatting.")
        st.stop()

# Initialize the Gemini client
client = genai.Client(api_key=api_key)

# System instruction defining the customer support persona
SUPPORT_PROMPT = """
You are a helpful, professional, and empathetic Customer Support Specialist for 'NovaTech Store'.
Follow these rules strictly:
1. Always maintain a polite, clear, and reassuring tone.
2. For order issues, ask for the 8-digit Order ID.
3. For returns, mention our policy: items can be returned within 14 days of delivery in original condition.
4. For technical support, provide concise step-by-step troubleshooting.
5. If you do not know the answer or if the issue requires manual intervention, tell the user you will escalate their ticket to a human representative within 24 hours.
"""

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Welcome to NovaTech Support. How can I help you today?"}
    ]

# Display prior chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input widget
if user_input := st.chat_input("Type your question here..."):
    # Append & display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Format history for the Gemini API call
# Format history for the Gemini API call
    contents = []
    for msg in st.session_state.messages:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    # Generate model response
with st.chat_message("assistant"):
    candidate_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]
    
    success = False
    
    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SUPPORT_PROMPT,
                    temperature=0.3,
                ),
            )
            assistant_text = response.text
            st.markdown(assistant_text)
            st.session_state.messages.append({"role": "assistant", "content": assistant_text})
            success = True
            break
        except Exception as e:
            # Helps verify why a model failed during development
            print(f"Model {model_name} failed: {e}")
            continue

    if not success:
        fallback_reply = (
            "Thank you for contacting NovaTech Support! I can help you track your package. "
            "Could you please share your **8-digit Order ID** so I can retrieve the latest shipping status?"
        )
        st.markdown(fallback_reply)
        st.session_state.messages.append({"role": "assistant", "content": fallback_reply})