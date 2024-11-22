import streamlit as st
import spacy
import time
from chatbot_backend import extract_menu_items, get_price, get_description, show_menu
import logging
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Set page layout and theme
st.set_page_config(page_title="Taco Bell Chatbot", layout="wide")

# Custom CSS for styling
def add_custom_styles():
    st.markdown(
        """
        <style>
        /* Import Montserrat Font */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

        /* Global Styling */
        * {
            font-family: 'Montserrat', sans-serif;
        }

        /* Background and Text Colors */
        [data-testid="stAppViewContainer"] {
            background-color: #FFF8E1; /* Soft cream background */
        }
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #5C2D91; /* Purple background */
            width: 160px !important; /* Force sidebar width */
            min-width: 160px !important; /* Set minimum width */
            max-width: 160px !important; /* Set maximum width */
        }

        /* Adjust Sidebar Content Alignment */
        [data-testid="stSidebar"] .block-container {
            padding: 0; /* Remove default padding */
            text-align: center; /* Center content */
        }

        /* Adjust Sidebar Button Styles */
        [data-testid="stSidebar"] button {
            font-size: 12px; /* Adjust font size for narrow layout */
            padding: 5px 10px; /* Adjust button padding */
        }
        [data-testid="stSidebar"]::-webkit-scrollbar {
            display: none; /* Hide scrollbar */
        }

        h1, h2, h3, h4, h5, h6 {
            color: #5C2D91; /* Purple headings */
        }
        p, li {
            color: black; /* Black text for general content */
        }

        /* Navbar Arrow Highlight */
        [data-testid="stSidebarNav"]::before {
            content: '❮'; /* Arrow icon */
            color: #5C2D91; /* Purple color for visibility */
            font-size: 18px;
            position: absolute;
            top: 10px;
            left: 10px;
        }
        [data-testid="stSidebarNav"]:hover::before {
            color: #7A42D1; /* Highlight color on hover */
        }

        /* Updated Title Sizes */
        h1 {
            font-weight: 400; /* Remove bold */
            font-size: 50px; /* Bigger size for main titles */
        }
        h2 {
            font-weight: 400;
            font-size: 35px; /* Large size for page titles (e.g., "Menu") */
        }
        h3 {
            font-weight: 600;
            font-size: 24px; /* Smaller size for category titles */
        }

        /* Navbar Button Styling */
        .stButton > button {
            background-color: #F1EFFF; /* Light contrasting purple */
            color: #5C2D91; /* Purple text */
            border: 1px solid #5C2D91;
            border-radius: 5px;
            padding: 8px 12px;
            font-size: 14px;
            cursor: pointer;
        }
        .stButton > button:hover {
            background-color: #7A42D1; /* Darker purple on hover */
            color: white; /* White text for contrast */
        }

        /* Menu Items Styling */
        .menu-item {
            background-color: #FFFFFF;
            color: black;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border: 2px solid #5C2D91;
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .menu-item h4 {
            font-size: 20px;
            color: #5C2D91;
        }
        .menu-item p {
            font-size: 16px;
        }

        /* Sticky Navbar */
        .navbar-container {
            position: sticky;
            top: 0;
            z-index: 1000;
            background-color: #FFF8E1;
        }
        .navbar {
            display: flex;
            justify-content: space-evenly;
            background-color: #5C2D91;
            padding: 10px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .navbar a {
            color: white;
            text-decoration: none;
            font-size: 16px;
            padding: 10px 15px;
            font-weight: 600;
        }
        .navbar a:hover {
            background-color: #7A42D1;
            border-radius: 5px;
        }

        /* Parent Container */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-height: 400px;
            width: 300px;
            overflow-y: auto;
            padding: 10px;
            background-color: #FFFFFF;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
            margin: 0 auto; /* Center the chat container */
        }

        /* Chat Bubbles */
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 14px;
            line-height: 1.4;
            display: inline-block;
            max-width: 85%;
            word-wrap: break-word;
            margin: 5px 0;
        }
        .user-message {
            background-color: #DCF8C6; /* Light green */
            align-self: flex-end;
            text-align: left; /* Left-align text inside bubble */
            margin-left: 25%;
            color: black;
        }
        .bot-message {
            background-color: #F1F1F1; /* Light gray */
            align-self: flex-start;
            text-align: left;
            margin-right: 50%;
            color: black;
        }

        /* Dynamic Input Field Styling */
        .stTextInput > div {
            position: fixed;
            bottom: 10px;
            width: calc(100% - 40px); /* Dynamically fit input field */
            max-width: 300px;
            margin: 0 auto;
            display: flex;
            gap: 10px;
            z-index: 1000;
        }
        [data-testid="stSidebar"][aria-expanded="true"] + div .stTextInput > div {
            max-width: calc(100% - 360px); /* Adjust input width if sidebar is expanded */
        }
        .stTextInput input {
            flex-grow: 1;
            padding: 10px;
            border: 2px solid #5C2D91;
            border-radius: 25px;
            font-size: 14px;
            background-color: white;
            outline: none;
        }
        .custom-send-button {
            background-color: #5C2D91;
            color: white;
            border: none;
            border-radius: 25px;
            padding: 10px 15px;
            font-size: 14px;
            cursor: pointer;
        }
        .custom-send-button:hover {
            background-color: #7A42D1;
        }

        /* Always Visible Scrollbar */
        html, body, [data-testid="stAppViewContainer"] {
            overflow: auto !important;
            scrollbar-width: thin;
            scrollbar-color: #5C2D91 #F1F1F1; /* Purple thumb with light gray track */
        }
        [data-testid="stAppViewContainer"]::-webkit-scrollbar {
            width: 10px; /* Set scrollbar width */
        }
        [data-testid="stAppViewContainer"]::-webkit-scrollbar-thumb {
            background-color: #5C2D91; /* Purple scrollbar thumb */
            border-radius: 10px;
        }
        [data-testid="stAppViewContainer"]::-webkit-scrollbar-track {
            background-color: #F1F1F1; /* Light gray scrollbar track */
        }

        /* Hide Streamlit Black Toolbar */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Initialize session state
if "order" not in st.session_state:
    st.session_state.order = []  # Stores items in the order
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Chat history
if "current_page" not in st.session_state:
    st.session_state.current_page = "order"  # Default page

# Navbar for navigation
def navbar():
    with st.sidebar:
        st.markdown("<h3>Navigate</h3>", unsafe_allow_html=True)
        if st.button("Menu"):
            st.session_state.current_page = "menu"
        if st.button("Order"):
            st.session_state.current_page = "order"
        if st.button("Help"):
            st.session_state.current_page = "help"

# Intent detection
def detect_intent(user_input):
    doc = nlp(user_input.lower())
    intents = {
        "place_order": ["want", "get", "add", "have"],
        "remove_item": ["remove", "take out", "delete"],
        "get_price": ["price", "cost"],
        "get_description": ["describe", "description"],
        "get_menu": ["menu", "items"],
        "ask_question": ["hours", "open", "deals"],
        "view_order": ["my", "current", "order", "cart"],
        "complete_order": ["checkout", "complete", "finish"],
        "cancel_order": ["cancel", "clear", "reset"],
    }
    for token in doc:
        for intent, keywords in intents.items():
            if token.lemma_ in keywords:
                return intent
    return "unknown_intent"

# Chatbot logic
def handle_message(user_input):
    intent = detect_intent(user_input)
    response = ""

    if intent == "place_order":
        extracted_items = extract_menu_items(user_input)
        if extracted_items:
            for item in extracted_items:
                st.session_state.order.append(item["name"])
            response = f"Added {', '.join([item['name'] for item in extracted_items])} to your order."
        else:
            response = "Couldn't find the item in the menu."
    elif intent == "view_order":
        response = f"Your current order: {', '.join(st.session_state.order) if st.session_state.order else 'Your order is empty.'}"
    elif intent == "cancel_order":
        st.session_state.order.clear()
        response = "Your order has been canceled."
    else:
        response = "Sorry, I didn't understand that."

    return response

# Pages
def show_menu_page():
    st.title("Menu")
    # Navbar for Categories
    st.markdown(
        """
        <div class="navbar-container">
            <div class="navbar">
                <a href="#tacos">Tacos</a>
                <a href="#burritos">Burritos</a>
                <a href="#quesadillas">Quesadillas</a>
                <a href="#specialties">Specialties</a>
                <a href="#bowls-salads">Bowls & Salads</a>
                <a href="#sides-snacks">Sides & Snacks</a>
                <a href="#desserts">Desserts</a>
                <a href="#sauces-extras">Sauces & Extras</a>
                <a href="#drinks">Drinks</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Fetch categorized menu items
    categorized_menu = show_menu()

    # Render Menu Items Dynamically
    for category, items in categorized_menu.items():
        # Generate a sanitized id for the category
        sanitized_id = category.lower().replace(" & ", "-").replace(" ", "-")
        st.markdown(f'<h2 id="{sanitized_id}">{category}</h2>', unsafe_allow_html=True)
        
        cols = st.columns(4)  # Create 4 columns for items
        for idx, item in enumerate(items):
            with cols[idx % 4]:
                st.markdown(
                    f"""
                    <div class="menu-item">
                        <h4>{item["name"]}</h4>
                        <p>{item["description"]}</p>
                        <p><strong>Price:</strong> ${item["price"]:.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def show_order_page():
    st.title("Taco Bell Chatbot")

    # Chat Display Container
    for user_message, bot_response in st.session_state.chat_history:
        # User message (right-aligned)
        st.markdown(
            f'<div class="chat-bubble user-message">{user_message}</div>',
            unsafe_allow_html=True,
        )
        time.sleep(0.5)  # Delay for animation effect
        # Bot response (left-aligned)
        st.markdown(
            f'<div class="chat-bubble bot-message">{bot_response}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Define the message submission handler
    def submit_message():
        if "chat_input" in st.session_state and st.session_state.chat_input.strip():  # Ensure there's input
            print("CHAT INPUT: ", st.session_state.chat_input)
            # Append user message and bot response to the chat history
            response = handle_message(st.session_state.chat_input)
            st.session_state.chat_history.append((st.session_state.chat_input, response))
            # Clear the input box
            st.session_state.chat_input = ""  # Reset input field safely

    # Add CSS for styling Streamlit's default input box
    st.markdown(
        """
        <style>
        /* Custom Input Box Styling */
        .stTextInput > div {
            position: fixed;
            bottom: 20px;
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            display: flex;
            gap: 10px;
            z-index: 1000;
        }
        .stTextInput input {
            flex-grow: 1;
            padding: 10px;
            border: 2px solid #5C2D91;
            border-radius: 25px;
            font-size: 16px;
            color: black;
            background-color: white;
            outline: none;
        }
        .custom-send-button {
            background-color: #5C2D91;
            color: white;
            border: none;
            border-radius: 25px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        .custom-send-button:hover {
            background-color: #7A42D1;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Render the input box
    st.text_input(
        "",  # Empty label
        key="chat_input",  # Key for session state
        on_change=submit_message,  # Submit message on Enter
        placeholder="Type your message here...",  # Placeholder text
        label_visibility="collapsed",  # Hide the label
    )

def show_help_page():
    st.title("Help")
    st.write(
        """
        - **How to place an order?** Use the chatbot to type your order.
        - **View the menu:** Use the Menu page for a complete list.
        - **Cancel your order:** Type "cancel my order" in the chatbot.
        """
    )

# Main function to handle page routing
def main():
    add_custom_styles()
    navbar()
    if st.session_state.current_page == "menu":
        show_menu_page()
    elif st.session_state.current_page == "help":
        show_help_page()
    else:
        show_order_page()

if __name__ == "__main__":
    main()
