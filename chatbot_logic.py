def process_user_input(user_input, menu_collection):
    # Simplified chatbot logic (NLP would be here)
    user_input = user_input.lower()
    order_item = None

    # Check if the input contains any menu item from the database
    menu_item = menu_collection.find_one({"name": {"$regex": user_input, "$options": "i"}})
    
    if menu_item:
        response = f"Adding {menu_item['name']} to your order."
        order_item = {
            "name": menu_item['name'],
            "price": menu_item['price'],
            "quantity": 1  # You can parse quantity from user input
        }
    else:
        response = "Sorry, I didn't find that item on the menu."

    return response, order_item