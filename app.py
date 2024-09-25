import streamlit as st
from pymongo import MongoClient
from chatbot_logic import process_user_input  # Your chatbot logic

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection
db = client['taco_bell']
menu_collection = db['menu']

# Store user session state
if 'order' not in st.session_state:
    st.session_state['order'] = []

st.title("Taco Bell Chatbot")

# Display current order
st.subheader("Your Current Order:")
if st.session_state['order']:
    for item in st.session_state['order']:
        st.write(f"- {item['name']} (x{item['quantity']}) - ${item['price'] * item['quantity']}")
else:
    st.write("No items in your order yet.")

# User Input
user_input = st.text_input("What would you like to order?")

# Process the user's input
if st.button("Submit"):
    if user_input:
        # Process input with chatbot logic
        response, order_item = process_user_input(user_input, menu_collection)
        st.write(response)

        # If an order item was added, update the session state
        if order_item:
            st.session_state['order'].append(order_item)

# Finalize the order
if st.button("Finalize Order"):
    st.write("Your order has been placed!")
    st.write("Order Summary:")
    for item in st.session_state['order']:
        st.write(f"- {item['name']} (x{item['quantity']}) - ${item['price'] * item['quantity']}")
    
    # Reset the order after placing
    st.session_state['order'] = []
