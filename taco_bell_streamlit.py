import streamlit as st
import spacy
from chatbot_backend import extract_menu_items, get_price, get_description, show_menu, generate_conversational_response
import logging

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
        'view_order': ['my', 'current', 'order'],
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
    st.session_state.order = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # Stores (user_message, bot_response) tuples

# Function to display chat history in a chat-like format
def display_chat_history():
    for user_message, bot_response in reversed(st.session_state.chat_history):
        if len(st.session_state.chat_history) > 1:
            st.write("\n\n\n\n")

        # Display the user message
        st.markdown(f"**You:** {user_message}")
        # Display the chatbot response
        st.markdown(f"**Chatbot:** {bot_response}")

# Main Streamlit App
def main():
    st.title("Taco Bell Chatbot")

    # Display chat history
    st.write("### Chat:")
    # display_chat_history()

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
        
        elif intent == "get_price":
            st.session_state.chat_history.append((user_input, get_price(user_input)))

        elif intent == "get_description":
            description = get_description(user_input)
            if description:
                st.session_state.chat_history.append((user_input, get_description(user_input)))
            else:
                context = "The chatbot couldn't find what the user was looking for."
                response = generate_conversational_response(context)
                st.session_state.chat_history.append((user_input, response))

        elif intent == 'get_menu':
            st.session_state.chat_history.append((user_input, show_menu()))
        
        elif intent == 'ask_question':
            context = f"The user asked: '{user_input}'"
            response = generate_conversational_response(context)
            st.session_state.chat_history.append((user_input, response))

        elif intent == "view_order":
            if st.session_state.order:
                response = f"Your current order is {" ".join(st.session_state.order)}."
            else:
                context = "The user asked to see their current order."
                response = generate_conversational_response(context)
            st.session_state.chat_history.append((user_input, response))
        
        elif intent == 'complete_order':
            context = f"The user has finished their order. The final order is {', '.join(st.session_state.order)}."
            response = generate_conversational_response(context)
            st.session_state.chat_history.append((user_input, response))
            st.write(f"Final order: {st.session_state.order}")
            logging.info(f"logging Final order: {st.session_state.order}")

        elif intent == 'cancel_order':
            st.session_state.order.clear()
            context = "The user cancelled the entire order."
            response = generate_conversational_response(context)
            st.session_state.chat_history.append((user_input, response))
            st.session_state.order.clear()
            # st.write("Order has been cancelled.")

        else:
            context = "The chatbot couldn't understand the user's intent."
            response = generate_conversational_response(context)
            st.session_state.chat_history.append((user_input, response))

        # Display updated chat
        display_chat_history()

if __name__ == "__main__":
    main()