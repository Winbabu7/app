import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validate API Key
if not GOOGLE_API_KEY:
    st.error("API Key is missing! Please check your .env file.")
    st.stop()

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-1.5-flash"

# Function to interact with AI
def chat_with_ai(prompt):
    try:
        if any(word in prompt.lower() for word in ["exit", "quit", "bye"]):
            return "Thank you for using TalentScout Hiring Assistant. Goodbye!"

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text if hasattr(response, "text") else "No response generated."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Streamlit UI
st.set_page_config(page_title="TalentScout Hiring Assistant", layout="centered")
st.title("TalentScout Hiring Assistant 🤖")
st.subheader("AI-Powered Candidate Screening & Interview Assistant")

# Initialize session state
if "candidate_details" not in st.session_state:
    st.session_state.candidate_details = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Candidate Information Form (Only if details are not submitted)
if not st.session_state.candidate_details:
    with st.form("candidate_form"):
        st.subheader("Candidate Information")
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        experience = st.number_input("Years of Experience", min_value=0)
        position = st.text_input("Position Applied For")
        location = st.text_input("Current Location")
        tech_stack = st.text_input("Candidate's Tech Stack (comma-separated)")
        submit_button = st.form_submit_button("Start Chatbot")

    if submit_button:
        if name and email and phone and position and tech_stack:
            st.session_state.candidate_details = {
                "name": name,
                "email": email,
                "phone": phone,
                "experience": experience,
                "position": position,
                "location": location,
                "tech_stack": tech_stack,
            }
            st.success(f"Candidate {name} is applying for {position}. Chatbot is now active!")
            st.rerun()
        else:
            st.warning("Please fill in all required fields.")
else:
    candidate = st.session_state.candidate_details
    st.info(f"Chatbot for {candidate['name']} (Applying for {candidate['position']})")

    # Generate initial AI-powered interview questions
    if "generated_questions" not in st.session_state:
        prompt = (
            f"Generate 5 technical interview questions for a candidate applying for {candidate['position']}. "
            f"The candidate is skilled in {candidate['tech_stack']} and has {candidate['experience']} years of experience."
        )
        st.session_state.generated_questions = chat_with_ai(prompt)

    st.subheader("Generated Interview Questions:")
    st.write(st.session_state.generated_questions)

    # Display chat history
    for msg in st.session_state.messages:
        role = msg["role"]
        st.chat_message(role).write(msg["content"])

    # User input for chatbot
    prompt = st.chat_input("Ask anything about the hiring process or interview questions...")

    if prompt:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Get AI response
        response = chat_with_ai(prompt)

        # Add AI response to history and display
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

    # Exit button to restart chatbot
    if st.button("Exit Chat"):
        st.session_state.candidate_details = None
        st.session_state.messages = []
        st.session_state.generated_questions = None
        st.rerun()