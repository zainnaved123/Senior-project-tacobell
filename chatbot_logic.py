import spacy

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

def process_user_input(user_input, menu_collection):
    # Process the input using spaCy
    doc = nlp(user_input.lower())
    
    # Initialize variables for extracted entities
    order_item = None
    quantity = 1  # Default quantity is 1
    
    # Extract entities from user input (we'll assume quantity is a number and food items are nouns)
    item_name = None
    for token in doc:
        if token.pos_ == 'NOUN':  # Assuming food items are nouns in the input
            item_name = token.text
        elif token.like_num:  # Assuming quantities are numbers
            quantity = int(token.text)
    
    if item_name:
        # Search the menu collection for the extracted item name
        menu_item = menu_collection.find_one({"name": {"$regex": item_name, "$options": "i"}})
        
        if menu_item:
            response = f"Adding {menu_item['name']} (x{quantity}) to your order."
            order_item = {
                "name": menu_item['name'],
                "price": menu_item['price'],
                "quantity": quantity
            }
        else:
            response = "Sorry, I didn't find that item on the menu."
    else:
        response = "Sorry, I couldn't understand your order. Could you please specify the item?"

    return response, order_item