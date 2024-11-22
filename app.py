import streamlit as st
import spacy
from chatbot_logic import parse_user_input, simplify_sentence, remove_context, detect_intent, split_items, apply_modifications, get_price, get_description, show_tacos, show_burritos, show_nachos, show_bowls, show_sides, show_drinks, show_sauces, show_dairy, show_gluten_free, show_menu, generate_conversational_response
import logging
from collections import defaultdict
import re

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize session state if not already done
if 'order' not in st.session_state:
    st.session_state.order = defaultdict(int)
if 'total' not in st.session_state:
    st.session_state.total = 0.0
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
    items_and_modifications = split_items(user_input)
    
    responses = []
    for item_text in items_and_modifications:
        item, quantity, modifications = detect_item_and_modifications(item_text)

        if item:
            if modifications:
                modification_message = apply_modifications(modifications)
                st.session_state.order[f"{item["name"]} ({modification_message})"] += quantity
                responses.append(f"{quantity} {item["name"]}(s) ({modification_message}) have been added to the order.")
            else:
                st.session_state.order[f"{item["name"]}"] += quantity
                responses.append(f"{quantity} {item["name"]}(s) have been added to the order.")
        else:
            responses.append("An item in the user's order could not be recognized.")

    # Combine responses
    return " ".join(responses)

def print_order():
    order = []

    for item_name, quantity in st.session_state.order.items():
        order.append(f"{quantity} x {item_name}")

    return "\n\n".join(order)

# Main Streamlit App
def main():
    st.title("Taco Bell Chatbot")

    # Display chat history
    st.write("### Chat:")

    # User input for order
    user_input = st.text_input("Type your message:")

    if st.button("Send"):
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
            # st.write("Order has been cancelled.")

        else:
            context = "The chatbot couldn't understand the user's question."
            response = remove_context(generate_conversational_response(context))

        st.session_state.chat_history.append((user_input, response))

        # Display updated chat
        display_chat_history()

if __name__ == "__main__":
    main()