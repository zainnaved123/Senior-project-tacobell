import streamlit as st
from chatbot_logic import parse_user_input, simplify_sentence, remove_context, detect_intent, apply_modifications, get_price, get_description, show_tacos, show_burritos, show_nachos, show_bowls, show_sides, show_drinks, show_sauces, show_dairy, show_gluten_free, show_menu, show_categorized_menu, generate_conversational_response
import logging
from collections import defaultdict
import time

# Set up logging
logging.basicConfig(level=logging.INFO)

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

# Initialize session state if not already done
if 'order' not in st.session_state:
    st.session_state.order = defaultdict(int)  # item name: quantity
if 'total' not in st.session_state:
    st.session_state.total = 0.0  # total $ amount
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # Stores (user_message, bot_response) tuples
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

# Function to display chat history in a chat-like format
def display_chat_history():
    for user_message, bot_response in reversed(st.session_state.chat_history):
        if len(st.session_state.chat_history) > 1:
            st.write("\n\n\n\n")

        # Display the user message
        st.markdown(f"**You:** {user_message}")
        # Display the chatbot response
        st.markdown(f"**Chatbot:** {bot_response}")

# Update order
def update_order(commands):
    responses = []

    for command in commands:
        intent, item, quantity, modifications, size = command.values()

        # Check if the item is recognized
        if not item:
            responses.append("An item in the user's order could not be recognized.")
            continue    # Skip to the next command

        item_name = item["name"]    # Extract item name
        have_or_has = "have" if quantity > 1 else "has"

        # Add size information to the item name if size is provided
        if size:
            item_name = f"{size.capitalize()} {item_name}"

        # Add modifications if needed
        if modifications:
            modification_message = apply_modifications(modifications)
            item_name = item_name + f" ({modification_message})"

        # Handle the 'add_item' intent
        if intent == "add_item":
            st.session_state.order[item_name] += quantity  # Update the order with the added item quantity
            st.session_state.total += item["price"] * quantity  # Update the total price
            # Generate response message about the added items
            responses.append(f"{quantity} {item_name + "s" if quantity > 1 else item_name} {have_or_has} been added to your order.")

        elif intent == "remove_item":
            amount = min(quantity, st.session_state.order[item_name])  # Ensure not removing more than what's in the order
            st.session_state.order[item_name] -= amount  # Update the order after removal
            # If the item count is zero, remove it from the order entirely
            if st.session_state.order[item_name] == 0:
                st.session_state.order.pop(item_name)
            st.session_state.total -= item["price"] * amount  # Update the total price after removal
            # Generate response message about the removed items
            responses.append(f"{amount} {item_name + "s" if quantity > 1 else item_name} {have_or_has} been removed from your order.")
    
    # Return all the responses as a single string, joining them with a space
    return " ".join(responses)

def process_user_input(user_input):
    commands = parse_user_input(user_input)
    response = update_order(commands)
    return response

def print_order():
    order = []

    for item_name, quantity in st.session_state.order.items():
        order.append(f"{quantity} x {item_name}")

    return "\n\n".join(order)


# Chatbot logic
def handle_message(user_input):
    simplified_input = user_input.replace("Let's", "").strip()
    simplified_input = simplify_sentence(simplified_input)
    intent = detect_intent(simplified_input)

    if intent == 'add_item' or intent == 'remove_item':
        context = process_user_input(simplified_input)
        response = remove_context(generate_conversational_response(context))
    
    elif intent == "get_price":
        response = get_price(simplified_input)
    elif intent == "get_description":
        description = get_description(simplified_input)
        if description:
            response = description
        else:
            context = "The chatbot couldn't find what the user was looking for."
            response = remove_context(generate_conversational_response(context))
    elif intent == 'get_tacos':
        response = show_tacos()
    elif intent == 'get_burritos':
        response = show_burritos()
    elif intent == 'get_nachos':
        response = show_nachos()
    elif intent == 'get_bowls':
        response = show_bowls()
    elif intent == 'get_sides':
        response = show_sides()
    elif intent == 'get_drinks':
        response = show_drinks()
    elif intent == 'get_sauces':
        response = show_sauces()
    elif intent == 'get_dairy':
        response = show_dairy()
    elif intent == 'get_gluten_free':
        response = show_gluten_free()
    elif intent == 'get_menu':
        response = show_menu()
    
    elif intent == 'ask_question':
        context = f"The user asked: '{user_input}'"
        response = remove_context(generate_conversational_response(context))

    elif intent == "view_order":
        if st.session_state.order:
            response = f"Your current order is \n\n{print_order()}\n\nand your total is ${st.session_state.total:.2f}."
        else:
            context = "The user asked to see their current order, but the user has not ordered anything."
            response = remove_context(generate_conversational_response(context))
    
    elif intent == 'complete_order':
        context = f"The user has finished their order. The final order is {print_order()}."
        response = remove_context(generate_conversational_response(context))
        st.write("\n\n")
        st.write(f"Final order: {print_order()}")
        logging.info(f"logging Final order: {st.session_state.order}")

    elif intent == 'cancel_order':
        st.session_state.order.clear()
        context = "The user cancelled the entire order."
        response = remove_context(generate_conversational_response(context))

    else:
        context = "The chatbot couldn't understand the user's question."
        response = remove_context(generate_conversational_response(context))

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
    categorized_menu = show_categorized_menu()

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



# Main Streamlit App
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