# streamlit_app/chatbot.py

import streamlit as st
import google.generativeai as genai
# import google.generativeai as genai



def park_chatbot(detection_context=None):
    st.markdown("## 🤖 AI Security Assistant")
    
    # API Key Handling (Sidebar or Session)
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        st.warning("Please enter your Gemini API Key in the settings sidebar to enable the AI Chatbot.")
        return

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return

    # System Prompt & Context
    system_instruction = (
        "You are a specialized AI Security Assistant for a Park Monitoring System. "
        "You analyze security alerts, explain authorized vs unauthorized activities, "
        "and advise on safety protocols. "
    )
    if detection_context:
        system_instruction += f"\n\nCurrent Detection Context: {detection_context}"

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # User Input
    if prompt := st.chat_input("Ask about security status, rules, or detections..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            try:
                # Prepare history for Gemini
                gemini_history = []
                for m in st.session_state.messages[:-1]:
                    if m["role"] == "system":
                        # For gemini-pro, we can prepend system context to the first user message or handle it this way
                        continue 
                    role = "user" if m["role"] == "user" else "model"
                    gemini_history.append({"role": role, "parts": [m["content"]]})
                
                # Prepend system instruction to the chat if needed, or rely on the prompt context
                if not gemini_history and system_instruction:
                     gemini_history.append({"role": "user", "parts": [system_instruction]})
                elif gemini_history and system_instruction:
                     gemini_history[0]["parts"].insert(0, system_instruction + "\n\n")

                # Dynamic Model Selection with UI Debugging
                model_name = "gemini-2.5-flash" # Fallback
                try:
                    all_models = list(genai.list_models())
                    # Filter for generateContent support
                    valid_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
                    
                    if valid_models:
                        # Prefer 1.5-flash, then pro, then first available
                        if any("gemini-2.5-flash" in m for m in valid_models):
                            model_name = "gemini-2.5-flash"
                        elif any("gemini-2.0-flash-exp" in m for m in valid_models):
                            model_name = "gemini-2.0-flash-exp"
                        else:
                            model_name = valid_models[0] # Use full name e.g. models/gemini-2.0-flash-exp
                            
                        # Clean name if needed by SDK, but usually full name is fine or short name. 
                        # SDK often wants "gemini-pro", but "models/gemini-pro" might also work or fail depending on version.
                        # Let's try to strip "models/" if it's there, as SDK usually reconstructs it.
                        if model_name.startswith("models/"):
                            short_name = model_name.replace("models/", "")
                            # Only use short name if it's a known standard, otherwise keep full?
                            # Actually, safely is to use what worked for others. 
                            # If the list returns 'models/gemini-pro', we usually pass 'gemini-pro'.
                            model_name = short_name

                    # Debug Info in UI (Temporary)
                    with st.expander("Debug: Available Models"):
                         st.write(f"Selected: {model_name}")
                         st.write("Valid Models:", valid_models)

                except Exception as e:
                    st.error(f"Failed to list models: {e}")

                model = genai.GenerativeModel(model_name)
                chat = model.start_chat(history=gemini_history)
                
                response_stream = chat.send_message(prompt, stream=True)
                
                def stream_generator():
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                            
                response = st.write_stream(stream_generator)
                
            except Exception as e:
                st.warning(f"⚠️ Gemini API Error: {e}. Switching to offline mode.")
                response = get_fallback_response(prompt)
                st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

def get_fallback_response(prompt):
    prompt_lower = prompt.lower()
    knowledge_base = {
        "authorized": "Authorized activities include: Walking, Jogging, Running, Sitting, and Playing in designated areas.",
        "unauthorized": "Unauthorized activities include: Fighting, Violence, Stealing, Vandalism, and Carrying weapons.",
        "weapon": "Weapons like knives and guns are strictly prohibited and classified as critical threats.",
        "safe": "The system marks normal public movement as SAFE (Green).",
        "alert": "The system triggers ALERTS (Red) for any violent or suspicious behavior.",
        "help": "I can assist you with understanding park rules and analyzing security feeds.",
        "hello": "Hello! I am your Offline Security Assistant. My cloud connection is down, but I can still help with basic rules."
    }
    
    for key, val in knowledge_base.items():
        if key in prompt_lower:
            return val
            
    return "I am currently in offline mode and couldn't process that specific query. Please ask about 'authorized' or 'unauthorized' activities."
