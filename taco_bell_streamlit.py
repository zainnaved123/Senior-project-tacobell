import streamlit as st
import spacy
from chatbot_backend import extract_menu_items, generate_conversational_response
import logging

# Load spaCy model
nlp = spacy.load("en_core_web_medium")

def detect_intent(user_input):
    doc = nlp(user_input)
    user_input = user_input.lower()

    intents = {
        'place_order': ['order', 'want', 'get', 'add', 'have'],
        'remove_item': ['remove', 'take out', 'delete'],
        'ask_question': ['hours', 'open', 'menu', 'deals'],
        'complete_order': ['checkout', 'complete', 'finish'],
        'cancel_order': ['cancel', 'clear', 'reset']
    }
    
    for token in doc:
        for intent, keywords in intents.items():
            if token.text.lower() in keywords:
                return intent

    return 'unknown_intent'

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize session state if not already done
if 'order' not in st.session_state:
    st.session_state.order = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # Stores (user_message, bot_response) tuples

# Function to display chat history in a chat-like format
def display_chat_history():
    for user_message, bot_response in st.session_state.chat_history:
        # Display the user message
        st.markdown(f"**You:** {user_message}")
        # Display the chatbot response
        st.markdown(f"**Chatbot:** {bot_response}")

# Main Streamlit App
def main():
    st.title("Taco Bell Ordering Chatbot")

    # Display chat history
    st.write("### Chat:")
    display_chat_history()

    # User input for order
    user_input = st.text_input("Type your message:")

    if st.button("Send"):
        intent = detect_intent(user_input)
        print("INTENT: ", intent)

        if intent == 'place_order':
            extracted_items = extract_menu_items(user_input)
            if extracted_items:
                st.session_state.order.extend(extracted_items)
                context = f"The user added {', '.join(extracted_items)} to their order. The current order is {', '.join(st.session_state.order)}."
                response = generate_conversational_response(context)
                st.session_state.chat_history.append((user_input, response))
            else:
                context = "The user tried to order something that is not on the menu."
                response = generate_conversational_response(context)
                st.session_state.chat_history.append((user_input, response))

        elif intent == 'remove_item':
            removed_items = extract_menu_items(user_input)
            if removed_items:
                for item in removed_items:
                    if item in st.session_state.order:
                        st.session_state.order.remove(item)
                context = f"The user removed {', '.join(removed_items)} from their order. The current order is {', '.join(st.session_state.order)}."
                response = generate_conversational_response(context)
                st.session_state.chat_history.append((user_input, response))
            else:
                context = "The user tried to remove something that is not in the order."
                response = generate_conversational_response(context)
                st.session_state.chat_history.append((user_input, response))

        elif intent == 'ask_question':
            context = f"The user asked: '{user_input}'"
            response = generate_conversational_response(context)
            st.session_state.chat_history.append((user_input, response))

        elif intent == 'complete_order':
            context = f"The user has finished their order. The final order is {', '.join(st.session_state.order)}."
            response = generate_conversational_response(context)
            st.session_state.chat_history.append((user_input, response))
            st.write(f"Final order: {st.session_state.order}")

        elif intent == 'cancel_order':
            st.session_state.order.clear()
            context = "The user cancelled the entire order."
            response = generate_conversational_response(context)
            st.session_state.chat_history.append((user_input, response))
            st.write("Order has been cancelled.")

        else:
            context = "The chatbot couldn't understand the user's intent."
            response = generate_conversational_response(context)
            st.session_state.chat_history.append((user_input, response))

    # Display updated chat and order after input
    display_chat_history()
    st.write(f"Current order: {st.session_state.order}")

if __name__ == "__main__":
    main()

"""        
        if user_input.lower() == 'done':
            # Finalize the order and show the array
            context = f"The user has finished their order. The final order is {', '.join(st.session_state.order)}."
            response = generate_conversational_response(context)
            st.session_state.chat_history.append((user_input, response))  # Append user input and bot response
            st.write(f"Order array: {st.session_state.order}")  # Display the order as an array for testing
            logging.info(f"Final order: {st.session_state.order}")
        else:
            # Extract menu items based on the user's input
            extracted_items = extract_menu_items(user_input)

            if extracted_items:
                st.session_state.order.extend(extracted_items)
                context = f"The user added {', '.join(extracted_items)} to their order. The current order is {', '.join(st.session_state.order)}."
                response = generate_conversational_response(context)
                st.session_state.chat_history.append((user_input, response))  # Append user input and bot response
                logging.info(f"User added: {extracted_items}")
            else:
                context = "The user tried to order something that is not on the menu."
                response = generate_conversational_response(context)
                st.session_state.chat_history.append((user_input, response))  # Append user input and bot response
                logging.warning("User tried to order an unavailable item.")
"""