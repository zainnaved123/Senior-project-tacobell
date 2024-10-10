import spacy
import pymongo
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load GPT-2 or a similar model (replace with your model if needed)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2").to("cuda" if torch.cuda.is_available() else "cpu")

# Set the padding token to eos_token (End of Sequence token) to avoid padding errors
tokenizer.pad_token = tokenizer.eos_token

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["tacobell"]
menu_collection = db["menu"]

# Function to extract full menu items by checking against the entire input string
def extract_menu_items(user_input):
    user_input_lower = user_input.lower()
    found_items = []
    menu_items_in_db = list(menu_collection.find({}))
    
    for item in menu_items_in_db:
        if "name" in item:
            if item["name"].lower() in user_input_lower:
                found_items.append(item["name"].lower())
    return found_items

# Function to generate conversational responses using GPT-2 or another model
def generate_conversational_response(context):
    system_prompt = (
        "You are a chatbot for a Taco Bell restaurant. Your job is to assist customers in placing food orders. "
        "Only respond to questions or commands related to ordering food. Do not generate any other kind of response."
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