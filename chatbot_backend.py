import pymongo
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re

# Load GPT-2 or a similar model (replace with your model if needed)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2").to("cuda" if torch.cuda.is_available() else "cpu")

# Set the padding token to eos_token (End of Sequence token) to avoid padding errors
tokenizer.pad_token = tokenizer.eos_token

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://tacobot1:chalupa@cluster0.u91bm.mongodb.net/")
db = client["taco_bell_menu"]
menu_collection = db["menu_items"]

# Function to retrieve all menu items
def get_menu_items():
    return list(menu_collection.find({}))

# Function to extract full menu items by checking against the entire input string
def extract_menu_items(user_input):
    user_input_lower = user_input.lower()
    found_items = []
    menu_items_in_db = get_menu_items()

    for item in menu_items_in_db:
        if "name" in item:
            # Check if the item name is in the user's input
            if item["name"].lower() in user_input_lower:
                # Look for a quantity preceding the item name (e.g., "two soft tacos")
                match = re.search(r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+' + re.escape(item["name"].lower()), user_input_lower)
                quantity = 1  # Default quantity is 1 if no number is specified
                
                if match:
                    quantity_str = match.group(1)
                    # Convert quantity to an integer (support for "one" to "ten")
                    quantity_words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, 
                                      "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
                    quantity = int(quantity_words.get(quantity_str, quantity_str))  # Convert word to number if needed

                found_items.append({"name": item["name"].lower(), "quantity": quantity})

    return found_items
def get_price(item_name):
    menu_items = get_menu_items()
    for item in menu_items:
        if item['name'].lower() == item_name.lower():
            return item['price']
    return None  # Return None if the item is not found

def get_description(user_input):
    menu_items = get_menu_items()
    for item in menu_items:
        if item['name'].lower() in user_input.lower():
            return f"{item['description']}"
    return ""

def show_menu():
    menu_items = get_menu_items()

    # Initialize categories in the specified order
    categories = [
        "Tacos",
        "Burritos",
        "Quesadillas",
        "Specialties",
        "Bowls & Salads",
        "Sides & Snacks",
        "Desserts",
        "Sauces & Extras",
        "Drinks",
    ]

    categorized_menu = {category: [] for category in categories}  # Create empty lists for each category

    # Categorize items based on their tags
    for item in menu_items:
        if "tags" in item:  # Check if tags exist
            for category in categories:
                if category in item["tags"]:  # Match tags to categories
                    categorized_menu[category].append({
                        "name": item["name"],
                        "price": item["price"],
                        "description": item["description"],
                    })
                    break  # Stop after assigning the item to the first matching category

    return categorized_menu

# Function to generate conversational responses using GPT-2 or another model
def generate_conversational_response(context):
    system_prompt = (
        "You are a chatbot for a Taco Bell restaurant. Your job is to assist customers in answering questions about the menu and placing their orders. "
        "Only respond to questions or commands related to ordering food. Do not generate any other kind of response. "
    )
    
    # Combine the system prompt with the current context
    full_prompt = f"{system_prompt}\n\n{context}"
    
    inputs = tokenizer(full_prompt, return_tensors="pt", padding=True, truncation=True).to(model.device)
    outputs = model.generate(
        inputs["input_ids"], 
        attention_mask=inputs["attention_mask"],  
        max_length=150, 
        pad_token_id=tokenizer.eos_token_id,  
        do_sample=True
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.strip()