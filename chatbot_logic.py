import pymongo
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from dotenv import load_dotenv
import os
import re
import spacy

# Load GPT-2 or a similar model (replace with your model if needed)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2").to("cuda" if torch.cuda.is_available() else "cpu")

# Set the padding token to eos_token (End of Sequence token) to avoid padding errors
tokenizer.pad_token = tokenizer.eos_token

# Load environment variables from the .env file
load_dotenv()

# Get the MongoDB URI from the environment variables
mongodb_uri = os.getenv('MONGODB_URI')

# Connect to MongoDB
client = pymongo.MongoClient(mongodb_uri)
db = client["taco_bell_menu"]
print("Connected to MongoDB")
menu_items = db["menu_items"]

# Retrieve all menu items
menu_items = list(menu_items.find({}))

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

intents = {
    'add_item': ['want', 'get', 'add', 'have', 'do'],
    'remove_item': ['remove', 'delete'],
    'get_price': ['price', 'cost', 'much'],
    'get_description': ['describe', 'description'],
    'get_tacos': ['taco'],
    'get_burritos': ['burrito', 'burritos'],
    'get_nachos': ['nachos'],
    'get_bowls': ['bowl'],
    'get_sides': ['side'],
    'get_drinks': ['drink', 'beverage', 'soda', 'refreshment'],
    'get_sauces': ['sauce'],
    'get_dairy': ['dairy'],
    'get_gluten_free': ['gluten'],
    'get_menu': ['menu', 'items'],
    'ask_question': ['hours', 'open', 'deals'],
    'view_order': ['my', 'current', 'order', 'cart', 'total'],
    'complete_order': ['checkout', 'complete', 'finish'],
    'cancel_order': ['cancel', 'clear', 'reset']
}

# Define modification patterns
modification_patterns = [
    (r"\b(?:no|without)\b\s*(\w+)", "remove"),  # e.g., "no pickles" or "without pickles" 
    (r"\b(?:extra|additional|more)\b\s*(\w+)", "add"),  # e.g., "extra cheese"
    (r"\b(?:substitute|swap|replace)\b\s*(\w+)\s*with\s*(\w+)", "substitute"),  # e.g., "substitute lettuce with onions"
]

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

def process_user_input(user_input):
    commands = parse_user_input(user_input)
    response = update_order(commands)
    return response

def parse_user_input(user_input):
    """
    Parses the user's input to extract multiple commands for intents (add_item/remove_item), menu items,
    quantities, and modifications

    Returns:
        list[dict]: A list of dictionaries containing 'intent', 'item', 'quantity', and 'modifications' for each command.
    """
    intent_pattern = r'\b(?:' + '|'.join(intents["add_item"] + intents["remove_item"]) + r')\b'
    quantity_pattern = r'\b(?:' + '|'.join(text_to_number.keys()) + r'|\d+)\b'
    size_keywords = ["small", "medium", "large"]
    size_pattern = r'\b(' + '|'.join(size_keywords) + r')\b'    # Find all occurrences of size keywords in the sentence
    pattern = (
        r'(?:\s*+(?P<quantity>' + quantity_pattern + r'))?'  # Match quantity (optional)
        r'\s*+(?P<item>.+?)(?:s\b|$)'  # Match item
    )

    # Split the input into potential commands
    delimiters = [',', 'and', ';', '&']
    for delimiter in delimiters:
        user_input = user_input.replace(delimiter, "|")

    # Split the input keeping quantity amounts
    for word, number in text_to_number.items():
        user_input = user_input.replace(f" {word} ", f"| {word} ")
        user_input = user_input.replace(f" {number} ", f"| {number} ")
    
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
            item = detect_item(item_name.lower())

            # Continue to next command if current command was changing intent
            if not item and intent_match:
                continue

            # Extract quantity, converting text-based numbers to integers if necessary
            quantity_raw = match.group("quantity")
            if quantity_raw:
                quantity = int(text_to_number.get(quantity_raw, quantity_raw))  # Handle text or digit
            else:
                quantity = 1  # Default quantity is 1 if none is specified

            # Extract modifications
            modifications = detect_modifications(command, item) if item else []

            # Extract size
            size = None
            size_match = re.search(size_pattern, command.strip(), re.IGNORECASE)
            if item and is_drink(item):
                size = size_match.group(0) if size_match else "medium"

            results.append({
                "intent": intent,
                "item": item,
                "quantity": quantity,
                "modifications": modifications,
                "size": size
            })

    return results

# Simplify sentence using spaCy
def simplify_sentence(user_input):
    doc = nlp(user_input.lower())
    simplified_sentence = []

    for token in doc:
        simplified_sentence.append(token.lemma_)

    return " ".join(simplified_sentence)

# Remove the context message from the chatbot's output
def remove_context(response):
    system_prompt = "You are a chatbot for a Taco Bell restaurant. Your job is to assist customers in answering questions about the menu and placing their orders. Only respond to questions or commands related to ordering food. Do not generate any other kind of response."
    new_response = response.replace(system_prompt, "")
    new_response = new_response.replace("\n", "", 2)
    return new_response

# Identify intent from keywords
def detect_intent(input):
    for word in input.split():
        for intent, keywords in intents.items():
            if word in keywords:
                return intent

    return 'unknown_intent'

# Split input into items (e.g. "2 tacos and 2 burritos" -> ["2 tacos", "2 burritos"])
def split_items(user_input):
    # This regex splits based on common separators such as 'and' or commas, while also considering numbers.
    return re.split(r'(?<=\d)\s*(?:and|,)\s*', user_input.lower())

# Detect the item in the order (e.g., "Burger", "Pizza")
def detect_item(input_text):
    for item in menu_items:
        if item["name"].lower() in input_text:
            return item
    return None

# Detect if the item is a drink (e.g. Pepsi, MTN DEW)
def is_drink(item):
    return "drink" in item["tags"] or "Drinks" in item["tags"]

# Detect modifications (like "no lettuce", "extra cheese", etc.)
def detect_modifications(input_text, item):
    modifications = []
    for pattern, action in modification_patterns:
        matches = re.findall(pattern, input_text, flags=re.IGNORECASE)
        for match in matches:
            if action == "remove":
                if match.lower() in item["ingredients"]:
                    modifications.append(f"no {match}")
            elif action == "add":
                if match.lower() not in item["ingredients"]:
                    modifications.append(f"add {match}")
            elif action == "substitute":
                parts = match.split(" with ")
                if len(parts) == 2:
                    old, new = parts
                    if old.lower() in item["ingredients"]:
                        modifications.append(f"substitute {old} with {new}")
    return modifications

# Apply modifications to an item and return a summary of the changes
def apply_modifications(modifications):
    if not modifications:
        return "No modifications."
    return ", ".join(modifications)

def get_price(user_input):
    for item in menu_items:
        if item['name'].lower() in user_input.lower():
            return f"The price of {item['name']} is ${item['price']}."
    return "I couldn't find that item in the menu."

def get_description(user_input):
    for item in menu_items:
        if item['name'].lower() in user_input.lower():
            return f"{item['description']}"
    return ""

# Retrieve and display various menu items, categorized by type (tacos, burritos, nachos, bowls, sides, drinks, sauces, dairy, gluten-free)
# and provide formatted output including item names and prices. Each function generates a message tailored to its specific category.
def show_tacos():
    tacos = "\n\n".join([f"{item['name']} - ${item['price']}" for item in menu_items if "taco" in item["tags"]])
    return f"We’ve got a variety of delicious tacos to choose from. Here are some of our options:\n\n{tacos}"

def show_burritos():
    burritos = "\n\n".join([f"{item['name']} - ${item['price']}" for item in menu_items if "taco" in item["tags"]])
    return f"Here’s a list of our delicious burritos at Taco Bell:\n\n{burritos}"

def show_nachos():
    nachos = "\n\n".join([f"{item['name']} - ${item['price']}" for item in menu_items if "nachos" in item["tags"]])
    return f"Great question! We have several delicious nacho options for you:\n\n{nachos}"

def show_bowls():
    bowls = "\n\n".join([f"{item['name']} - ${item['price']}" for item in menu_items if "bowl" in item["tags"]])
    return f"We have a variety of delicious bowls to satisfy your cravings! Our options include:\n\n{bowls}"

def show_sides():
    sides = "\n\n".join([f"{item['name']} - ${item['price']}" for item in menu_items if "side" in item["tags"]])
    return f"Here are the sides we offer at Taco Bell:\n\n{sides}"

def show_drinks():
    drinks = "\n\n".join([f"{item['name']} - ${item['price']}" for item in menu_items if "drink" in item["tags"]])
    return f"At Taco Bell, we offer a variety of refreshing drinks to complement your meal. Here's what we have:\n\n{drinks}"

def show_sauces():
    sauces = "\n\n".join([f"{item['name']} - ${item['price']}" for item in menu_items if "sauce" in item["tags"]])
    return f"At Taco Bell, we have a variety of delicious sauces to choose from! Here’s a list of what we offer:\n\n{sauces}"

def show_dairy():
    dairy = "\n\n".join([f"{item['name']} - ${item['price']}" for item in menu_items if "dairy" in item["tags"]])
    return f"Many of our menu items contain dairy, including cheese, sour cream, and sauces. Some of the items that typically contain dairy include:\n\n{dairy}"

def show_gluten_free():
    gluten_free = "\n\n".join([f"{item['name']} - ${item['price']}" for item in menu_items if "gluten" not in item["tags"]])
    return f"At Taco Bell, we offer several gluten-free options, though please keep in mind that cross-contamination is always possible due to shared kitchen equipment. Here are some of our gluten-free choices:\n\n{gluten_free}"

def show_menu():
    menu_str = "\n\n".join([f"{item['name']} - ${item['price']} : {item['description']}" for item in menu_items])
    return f"Here's what's on our Taco Bell menu:\n\n{menu_str}"

# Function to generate conversational responses using GPT-2 or another model
def generate_conversational_response(context):
    # Define the system prompt that sets the behavior of the chatbot
    system_prompt = (
        "You are a chatbot for a Taco Bell restaurant. Your job is to assist customers in answering questions about the menu and placing their orders. "
        "Only respond to questions or commands related to ordering food. Do not generate any other kind of response. "
    )
    
    # Combine the system prompt with the current context
    full_prompt = f"{system_prompt}\n\n{context}"
    
    # Tokenize the prompt
    inputs = tokenizer(full_prompt, return_tensors="pt", padding=True, truncation=True).to(model.device)

    # Generate a response from the model using the input tokens and attention mask
    outputs = model.generate(
        inputs["input_ids"], 
        attention_mask=inputs["attention_mask"],  
        max_length=150, 
        pad_token_id=tokenizer.eos_token_id,  
        do_sample=True
    )

    # Decode the model's output to get the generated text
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.strip()