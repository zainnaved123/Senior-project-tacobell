import streamlit as st
import spacy
from chatbot_backend import extract_menu_items, get_price, get_description, show_menu, generate_conversational_response
import logging
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

def detect_intent(user_input):
    doc = nlp(user_input.lower())

    intents = {
        'place_order': ['want', 'get', 'add', 'have'],
        'remove_item': ['remove', 'take out', 'delete'],
        'get_price': ['price', 'cost'],
        'get_description': ['describe', 'description'],
        'get_menu': ['menu', 'items'],
        'ask_question': ['hours', 'open', 'deals'],
        'view_order': ['my', 'current', 'order', 'cart'],
        'complete_order': ['checkout', 'complete', 'finish'],
        'cancel_order': ['cancel', 'clear', 'reset']
    }
    
    for token in doc:
        for intent, keywords in intents.items():
            if token.lemma_ in keywords:
                return intent

    return 'unknown_intent'

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize session state if not already done
if 'order' not in st.session_state:
    st.session_state.order = []  # Stores items in the order
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # Stores (user_message, bot_response, order_snapshot) tuples

# Function to get prices for each item in the current order from MongoDB
def get_order_with_prices(order):
    order_with_prices = []
    for item in order:
        price = get_price(item)  # Assuming get_price queries MongoDB by item name and returns the price
        if price is not None:
            order_with_prices.append((item, price))
        else:
            order_with_prices.append((item, "Price not found"))  # Fallback if item price is not available
    return order_with_prices

# Function to clean up any unwanted HTML/Markdown tags from bot response
def sanitize_text(text):
    # Remove any HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove any remaining Markdown special characters
    text = re.sub(r"[*_`~^]", "", text)
    # Fix spacing issues or artifacts left by removed elements
    text = re.sub(r"\s+", " ", text).strip()
    return text

# Function to display chat history in styled bubbles
def display_chat_history():
    st.markdown(
        """
        <style>
        .chat-bubble {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 10px;
            margin: 10px 0;
            line-height: 1.4;
        }
        .user-message {
            background-color: #DCF8C6;
            color: black;
            align-self: flex-end;
            margin-left: auto;
            border-radius: 10px 10px 0 10px;
        }
        .bot-message {
            background-color: #E8E8E8;
            color: black;
            align-self: flex-start;
            margin-right: auto;
            border-radius: 10px 10px 10px 0;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            overflow-y: auto;
            max-height: 400px;
        }
        </style>
        <div class="chat-container">
        """, unsafe_allow_html=True
    )

    # Generate each message bubble
    for user_message, bot_response, order_snapshot in st.session_state.chat_history:
        # User message bubble
        st.markdown(
            f"""
            <div class="chat-bubble user-message"><strong>You:</strong> {sanitize_text(user_message)}</div>
            """, unsafe_allow_html=True
        )
        
        # Bot message bubble, including the order snapshot with item prices and additional spacing
        bot_text = (
            f"<strong>Chatbot:</strong> {sanitize_text(bot_response['text'])}"
            f"<br><br><em>Intent Detected:</em> {bot_response['intent']}"
            f"<br><br><br><strong>Order at the Time:</strong><br>"
        )
        for item, price in order_snapshot:
            price_text = f"${price:.2f}" if isinstance(price, (int, float)) else price
            bot_text += f"- {sanitize_text(item)}: {price_text}<br>"
        
        st.markdown(
            f"""
            <div class="chat-bubble bot-message">{sanitize_text(bot_text)}</div>
            """, unsafe_allow_html=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

def replace_context(response):
    system_prompt = "You are a chatbot for a Taco Bell restaurant. Your job is to assist customers in answering questions about the menu and placing their orders. Only respond to questions or commands related to ordering food. Do not generate any other kind of response."
    new_response = response.replace(system_prompt, "")
    new_response = new_response.replace("\n", "", 2)
    return new_response

def handle_message():
    user_input = st.session_state.user_input
    intent = detect_intent(user_input)
    response = ""

    if intent == 'place_order':
        extracted_items = extract_menu_items(user_input)
        if extracted_items:
            # Update the order by adding items with quantities
            for item in extracted_items:
                for _ in range(item["quantity"]):  # Add the item multiple times based on quantity
                    st.session_state.order.append(item["name"])
                    
            added_items = ", ".join([f"{item['quantity']} x {item['name']}" for item in extracted_items])
            context = f"The user added {added_items} to their order. The current order is {', '.join(st.session_state.order)}."
            response = replace_context(generate_conversational_response(context))
        else:
            context = "The user tried to order something that is not on the menu."
            response = replace_context(generate_conversational_response(context))
    
    elif intent == 'remove_item':
        removed_items = extract_menu_items(user_input)
        if removed_items:
            for item in removed_items:
                item_name = item["name"]
                quantity_to_remove = item["quantity"]
                # Remove the specified quantity of the item from the order
                for _ in range(quantity_to_remove):
                    if item_name in st.session_state.order:
                        st.session_state.order.remove(item_name)
            # Format the removed items for display
            removed_items_str = ", ".join([f"{item['quantity']} x {item['name']}" for item in removed_items])
            context = f"The user removed {removed_items_str} from their order. The current order is {', '.join(st.session_state.order)}."
            response = replace_context(generate_conversational_response(context))
        else:
            context = "The user tried to remove something that is not in the order."
            response = replace_context(generate_conversational_response(context))
            
    elif intent == "get_price":
        response = get_price(user_input)

    elif intent == "get_description":
        description = get_description(user_input)
        if description:
            response = description
        else:
            context = "The chatbot couldn't find what the user was looking for."
            response = replace_context(generate_conversational_response(context))

    elif intent == 'get_menu':
        response = show_menu()
    
    elif intent == 'ask_question':
        context = f"The user asked: '{user_input}'"
        response = replace_context(generate_conversational_response(context))

    elif intent == "view_order":
        if st.session_state.order:
            order_with_prices = get_order_with_prices(st.session_state.order)
            total_price = sum(price for _, price in order_with_prices if isinstance(price, (int, float)))
            order_details = "\n".join([f"- {item}: ${price:.2f}" for item, price in order_with_prices if isinstance(price, (int, float))])
            response = f"Your current order:\n{order_details}\n\nTotal Price: ${total_price:.2f}"
        else:
            response = "Your order is currently empty."

    elif intent == 'complete_order':
        context = f"The user has finished their order. The final order is {', '.join(st.session_state.order)}."
        response = replace_context(generate_conversational_response(context))
        st.write(f"Final order: {st.session_state.order}")
        logging.info(f"logging Final order: {st.session_state.order}")

    elif intent == 'cancel_order':
        st.session_state.order.clear()
        context = "The user cancelled the entire order."
        response = replace_context(generate_conversational_response(context))
        st.session_state.order.clear()

    else:
        context = "The chatbot couldn't understand the user's question."
        response = replace_context(generate_conversational_response(context))

    # Append the user message, response, and a snapshot of the order (with prices) to the chat history
    order_snapshot = get_order_with_prices(st.session_state.order)
    st.session_state.chat_history.append((user_input, {"text": response, "intent": intent}, order_snapshot))

    # Clear the user input after sending the message
    st.session_state.user_input = ""

# Main Streamlit App
def main():
    st.title("Taco Bell Chatbot")

    # Display the chat history in styled bubbles
    display_chat_history()

    # User input for order with an on_change event to trigger handle_message
    st.text_input("Type your message:", key="user_input", on_change=handle_message)

if __name__ == "__main__":
    main()
