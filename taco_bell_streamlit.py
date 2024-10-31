import streamlit as st
from chatbot_backend import extract_menu_items, generate_conversational_response
import logging

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

    # Display updated chat and order after input
    display_chat_history()
    st.write(f"Current order: {st.session_state.order}")

if __name__ == "__main__":
    main()
