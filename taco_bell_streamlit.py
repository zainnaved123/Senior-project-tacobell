import streamlit as st
import spacy
from chatbot_backend import split_items, detect_item_and_modifications, detect_item, detect_modifications, apply_modifications, get_price, get_description, show_tacos, show_burritos, show_nachos, show_sides, show_drinks, show_sauces, show_dairy, show_gluten_free, show_menu, generate_conversational_response
import logging
from collections import defaultdict
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

intents = {
    'add_item': ['want', 'get', 'add', 'have'],
    'remove_item': ['remove', 'take out', 'delete'],
    'get_price': ['price', 'cost', 'much'],
    'get_description': ['describe', 'description'],
    'get_tacos': ['taco'],
    'get_burritos': ['burrito', 'burritos'],
    'get_nachos': ['nachos'],
    'get_sides': ['side'],
    'get_drinks': ['drink', 'beverage', 'soda', 'refreshment'],
    'get_sauces': ['sauce'],
    'get_dairy': ['dairy'],
    'get_gluten_free': ['gluten'],
    'get_menu': ['menu', 'items'],
    'ask_question': ['hours', 'open', 'deals'],
    'view_order': ['my', 'current', 'order', 'cart'],
    'complete_order': ['checkout', 'complete', 'finish'],
    'cancel_order': ['cancel', 'clear', 'reset']
}

text_to_number = {
    'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
    'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10', 'eleven': '11',
    'twelve': '12', 'thirteen': '13', 'fourteen': '14', 'fifteen': '15', 'sixteen': '16',
    'seventeen': '17', 'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'twenty-one': '21',
    'twenty-two': '22', 'twenty-three': '23', 'twenty-four': '24', 'twenty-five': '25',
    'twenty-six': '26', 'twenty-seven': '27', 'twenty-eight': '28', 'twenty-nine': '29',
    'thirty': '30', 'thirty-one': '31', 'thirty-two': '32', 'thirty-three': '33',
    'thirty-four': '34', 'thirty-five': '35', 'thirty-six': '36', 'thirty-seven': '37',
    'thirty-eight': '38', 'thirty-nine': '39', 'forty': '40', 'forty-one': '41',
    'forty-two': '42', 'forty-three': '43', 'forty-four': '44', 'forty-five': '45',
    'forty-six': '46', 'forty-seven': '47', 'forty-eight': '48', 'forty-nine': '49',
    'fifty': '50', 'fifty-one': '51', 'fifty-two': '52', 'fifty-three': '53', 'fifty-four': '54',
    'fifty-five': '55', 'fifty-six': '56', 'fifty-seven': '57', 'fifty-eight': '58', 'fifty-nine': '59',
    'sixty': '60', 'sixty-one': '61', 'sixty-two': '62', 'sixty-three': '63', 'sixty-four': '64',
    'sixty-five': '65', 'sixty-six': '66', 'sixty-seven': '67', 'sixty-eight': '68', 'sixty-nine': '69',
    'seventy': '70', 'seventy-one': '71', 'seventy-two': '72', 'seventy-three': '73', 'seventy-four': '74',
    'seventy-five': '75', 'seventy-six': '76', 'seventy-seven': '77', 'seventy-eight': '78', 'seventy-nine': '79',
    'eighty': '80', 'eighty-one': '81', 'eighty-two': '82', 'eighty-three': '83', 'eighty-four': '84',
    'eighty-five': '85', 'eighty-six': '86', 'eighty-seven': '87', 'eighty-eight': '88', 'eighty-nine': '89',
    'ninety': '90', 'ninety-one': '91', 'ninety-two': '92', 'ninety-three': '93', 'ninety-four': '94',
    'ninety-five': '95', 'ninety-six': '96', 'ninety-seven': '97', 'ninety-eight': '98', 'ninety-nine': '99'
}

def detect_intent(user_input):
    doc = nlp(user_input.lower())

    for token in doc:
        print(token.lemma_)
        for intent, keywords in intents.items():
            if token.lemma_ in keywords:
                return intent

    return 'unknown_intent'

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize session state if not already done
if 'order' not in st.session_state:
    st.session_state.order = defaultdict(int)
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

def replace_context(response):
    system_prompt = "You are a chatbot for a Taco Bell restaurant. Your job is to assist customers in answering questions about the menu and placing their orders. Only respond to questions or commands related to ordering food. Do not generate any other kind of response."
    new_response = response.replace(system_prompt, "")
    new_response = new_response.replace("\n", "", 2)
    return new_response

def parse_user_input(user_input):
    """
    Parses the user's input to extract multiple commands for intents (add_item/remove_item), menu items,
    quantities, and modifications

    Returns:
        list[dict]: A list of dictionaries containing 'intent', 'item', 'quantity', and 'modifications' for each command.
    """
    intent_pattern = r'\b(?:' + '|'.join(intents["add_item"] + intents["remove_item"]) + r')\b'
    quantity_pattern = r'\b(?:' + '|'.join(text_to_number.keys()) + r'|\d+)\b'
    pattern = (
        r'(?:\s+(?P<quantity>' + quantity_pattern + r'))?'  # Match quantity (optional)
        r'\s+(?P<item>.+?)(?:s\b|$)'  # Match item
    )

    # Split the input into potential commands
    delimiters = [',', 'and', ';', '&']
    for delimiter in delimiters:
        user_input = user_input.replace(delimiter, "|")

    # Split the input keeping quantity amounts
    for word, number in text_to_number.items():
        user_input = user_input.replace(word, f"| {word}")
        user_input = user_input.replace(number, f"| {number}")
    
    commands = user_input.split("|") # Split input into individual commands

    results = []
    intent = "add_item"
    for command in commands:
        # Check if intent is specified, otherwise defaults to 'add_item'
        intent_match = re.search(intent_pattern, command.strip(), re.IGNORECASE)
        if intent_match:
            # Extract intent and determine whether it's an add or remove action
            intent_word = intent_match.group(0).lower()
            intent = "add_item" if intent_word in intents["add_item"] else "remove_item"

        match = re.search(pattern, command.strip(), re.IGNORECASE)
        if match:
            # Extract item name
            item_name = match.group("item").strip()
            item = detect_item(item_name)

            if not item and intent_match:
                continue

            # Extract quantity, converting text-based numbers to integers if necessary
            quantity_raw = match.group("quantity")
            if quantity_raw:
                quantity = text_to_number.get(quantity_raw.lower(), int(quantity_raw))  # Handle text or digit
            else:
                quantity = 1  # Default quantity is 1 if none is specified

            # Extract modifications
            modifications = detect_modifications(command, item) if item else []

            results.append({
                "intent": intent,
                "item": item,
                "quantity": quantity,
                "modifications": modifications
            })

    return results

def update_order(commands):
    responses = []

    for command in commands:
        intent, item, quantity, modifications = command.values()

        if not item:
            responses.append("An item in the user's order could not be recognized.")
            continue

        if intent == "add_item":
            if modifications:
                modification_message = apply_modifications(modifications)
                st.session_state.order[f"{item["name"]} ({modification_message})"] += quantity
                responses.append(f"{quantity} {item["name"]}(s) ({modification_message}) have been added to the order.")
            else:
                st.session_state.order[f"{item["name"]}"] += quantity
                responses.append(f"{quantity} {item["name"]}(s) have been added to the order.")
        elif intent == "remove_item":
            st.session_state.order[item["name"]] = max(0, st.session_state.order[item["name"]] - quantity)
            responses.append(f"{quantity} {item["name"]}(s) have been removed from the order.")
    return " ".join(responses)

def process_user_input(user_input):
    commands = parse_user_input(user_input)
    response = update_order(commands)
    return response

def alternate_process_user_input(user_input):
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
    # return ", ".join([f"{quantity} x {item}" for item, quantity in st.session_state.order])
    return "\n\n".join([f"{quantity} x {item}" for item, quantity in st.session_state.order.items()])

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
        print("DETECTED INTENT: ", intent, " FOR ", user_input)

        if intent == 'add_item' or intent == 'remove_item':
            context = process_user_input(user_input)
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
        elif intent == 'get_tacos':
            response = show_tacos()
        elif intent == 'get_burritos':
            response = show_burritos()
        elif intent == 'get_nachos':
            response = show_nachos()
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
            response = replace_context(generate_conversational_response(context))

        elif intent == "view_order":
            if st.session_state.order:
                response = f"Your current order is \n\n{print_order()}."
                #response = f"Your current order is \n\n{print_order()} \n\nand your total is."
            else:
                context = "The user asked to see their current order, but the user has not ordered anything."
                response = replace_context(generate_conversational_response(context))
        
        elif intent == 'complete_order':
            context = f"The user has finished their order. The final order is {print_order()}."
            response = replace_context(generate_conversational_response(context))
            st.write("\n\n")
            st.write(f"Final order: {print_order()}")
            logging.info(f"logging Final order: {st.session_state.order}")

        elif intent == 'cancel_order':
            st.session_state.order.clear()
            context = "The user cancelled the entire order."
            response = replace_context(generate_conversational_response(context))
            # st.write("Order has been cancelled.")

        else:
            context = "The chatbot couldn't understand the user's question."
            response = replace_context(generate_conversational_response(context))

        st.session_state.chat_history.append((user_input, response))

        # Display updated chat
        display_chat_history()

if __name__ == "__main__":
    main()