import streamlit as st
import pandas as pd
import openai
import shelve
from config import API_KEY

# Set the page configuration
st.set_page_config(page_title="Maverick Chatbot")

# Ensure openai_model is initialized in session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Set the OpenAI API key
api_key = API_KEY
openai.api_key = api_key

# Load the dataset
df = pd.read_csv('/workspaces/test_app/file.csv')

# Load chat history from shelve file
def load_chat_history():
    try:
        with shelve.open("chat_history") as db:
            return db.get("messages", [])
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        return []

# Save chat history to shelve file
def save_chat_history(messages):
    try:
        with shelve.open("chat_history") as db:
            db["messages"] = messages
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

# Delete chat history
def delete_chat_history():
    try:
        with shelve.open("chat_history") as db:
            if "messages" in db:
                del db["messages"]
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Error deleting chat history: {e}")

# Function to process queries
def process_query(query):
    query = query.lower()
    response = "I'm not sure about that. Can you please rephrase?"

    if "total sales of" in query:
        parts = query.split("total sales of")[-1].strip().split("in")
        brand = parts[0].strip().upper()
        city = parts[1].strip().capitalize() if len(parts) > 1 else None
        filtered_data = df[df['brand'].str.upper() == brand]
        if city:
            filtered_data = filtered_data[filtered_data['city'].str.capitalize() == city]
        if not filtered_data.empty:
            total_sales_value = filtered_data['sales_value'].sum()
            response = f"The total sales value of {brand} in {city} is {total_sales_value:.2f}." if city else f"The total sales value of {brand} is {total_sales_value:.2f}."
        else:
            response = f"No data available for {brand} in {city}." if city else f"No data available for {brand}."

    elif "current inventory level for" in query:
        item = query.split("for")[-1].strip().upper()
        item_data = df[df['item_name'].str.upper() == item]
        if not item_data.empty:
            inventory_level = item_data['inventory_turnover'].sum()
            response = f"The current inventory turnover for {item} is {inventory_level}."
        else:
            response = f"No data available for {item}."
    
    elif "unit price for" in query:
        item = query.split("for")[-1].strip().upper()
        item_data = df[df['item_name'].str.upper() == item]
        if not item_data.empty():
            unit_price = item_data['unit_price'].mean()
            response = f"The average unit price for {item} is {unit_price:.2f}."
        else:
            response = f"No data available for {item}."

    elif "sales performance of" in query:
        item = query.split("of")[-1].strip().upper()
        item_data = df[df['item_name'].str.upper() == item]
        if not item_data.empty:
            total_sales_volume = item_data['sales_volume'].sum()
            response = f"The total sales volume for {item} is {total_sales_volume}."
        else:
            response = f"No data available for {item}."

    elif "inventory level of" in query:
        item = query.split("of")[-1].strip().upper()
        item_data = df[df['item_name'].str.upper() == item]
        if not item_data.empty:
            inventory_turnover = item_data['inventory_turnover'].sum()
            response = f"The inventory turnover for {item} is {inventory_turnover}."
        else:
            response = f"No data available for {item}."

    elif "best performing brand in" in query:
        city = query.split("in")[-1].strip().capitalize()
        city_data = df[df['city'].str.lower() == city.lower()]
        if not city_data.empty:
            best_brand = city_data.groupby('brand')['sales_volume'].sum().idxmax()
            response = f"The best performing brand in {city} is {best_brand}."
        else:
            response = f"No data available for {city}."

    elif "top performing brands in the last quarter" in query:
        latest_period = df['period'].max()
        period_data = df[df['period'] == latest_period]
        if not period_data.empty:
            top_brands = period_data.groupby('brand')['sales_volume'].sum().sort_values(ascending=False).head(3)
            response = f"The top performing brands in the last quarter are: {', '.join(top_brands.index)}."
        else:
            response = "No data available for the last quarter."

    elif "performance of brand" in query and "compared with" in query:
        parts = query.split("performance of brand")[-1].split("compared with")
        brand_a = parts[0].strip().title()
        brand_b = parts[1].strip().title()
        latest_period = df['period'].max()
        period_data = df[(df['period'] == latest_period) & (df['brand'].isin([brand_a, brand_b]))]
        if not period_data.empty:
            comparison = period_data.groupby('brand')['sales_volume'].sum()
            response = f"Performance of {brand_a}: {comparison[brand_a]:.2f}, Performance of {brand_b}: {comparison[brand_b]:.2f}"
        else:
            response = f"No data available for comparison between {brand_a} and {brand_b} in the last quarter."

    elif "market size in each quarter" in query:
        market_size = df.groupby('period')['sales_value'].sum()
        response = "Market size in each quarter:\n" + market_size.to_string()

    return response

def chat_interface():
    st.title("Mav Chatbot Interface")

    # Sidebar
    with st.sidebar:
        st.header("Chat Summary")
        
        # Display user questions
        if "messages" in st.session_state:
            user_questions = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
            for i, question in enumerate(user_questions[-5:], 1):  # Display last 5 questions
                st.write(f"{i}. {question[:50]}...")  # Truncate long questions
        
        # Delete chat history button
        if st.button("Delete Chat History"):
            delete_chat_history()
            st.success("Chat history deleted!")
            st.rerun()

    # Main chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about our retail data?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = process_query(prompt)
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        save_chat_history(st.session_state.messages)

chat_interface()
