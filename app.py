from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage, ChatMessage, FunctionMessage
import os
from dotenv import load_dotenv
from datetime import datetime
import json

def _get_restaurant_info(restaurant_name):
    print (f"Here is the information about {restaurant_name}...")

    # This is a placeholder function that would typically query a database or API
    # to get information about a specific restaurant
    restaurant_info = {
        "name": restaurant_name,
        "cuisine": "Italian",
        "location": "123 Main St, New York, NY",
        "rating": 4.5,
        "price_range": "$$"
    }

    return restaurant_info

# Define the function schema
restaurant_info_schema = {
    "name": "get_restaurant_info",
    "description": "Get information about a specific restaurant",
    "parameters": {
        "type": "object",
        "properties": {
            "restaurant_name": {
                "type": "string",
                "description": "The name of the restaurant"
            }
        },
        "required": ["restaurant_name"]
    }
}

# Define the system prompt
SYSTEM_PROMPT = """You are a helpful restaurant recommendation assistant. You can:
1. Provide information about specific restaurants
2. Make restaurant recommendations based on user preferences
3. Answer questions about dining and cuisines

When users ask about specific restaurants, use the get_restaurant_info function to retrieve details.
Keep your responses friendly and concise."""

def main():
    # Load environment variables
    load_dotenv()

    # Check if DEEPSEEK_API_KEY is set
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("Please set your DEEPSEEK_API_KEY in the .env file")
        return

    # Initialize the language model with function calling
    llm = ChatOpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/",  # Adjust this URL according to Deepseek's API documentation
        temperature=0.7,
        model_name="deepseek-chat",  # Adjust the model name according to Deepseek's available models
        functions=[restaurant_info_schema]
    )
    
    # Create a conversation chain with memory
    conversation = ConversationChain(
        llm=llm,
        memory=ConversationBufferMemory()
    )

    # Get current user and time information
    current_user = "pablo-lozano-martin"
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Welcome to the Terminal Chatbot, {current_user}!")
    print(f"Session started at: {current_time} UTC")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['quit', 'exit']:
            print("\nGoodbye!")
            break

        try:
            # Create messages for the conversation with system prompt
            messages = [
                ChatMessage(role="system", content=SYSTEM_PROMPT),
                HumanMessage(content=user_input)
            ]
            
            # Get the response from the model
            response = llm.invoke(messages)

            # Check if the model wants to call a function
            if response.additional_kwargs.get('function_call'):
                print("\nBot: Calling a function...")

                function_call = response.additional_kwargs['function_call']
                
                if function_call['name'] == 'get_restaurant_info':
                    # Parse the arguments and call the function
                    args = json.loads(function_call['arguments'])
                    restaurant_info = _get_restaurant_info(args['restaurant_name'])
                    
                    # Add the function result to the conversation
                    messages.append(FunctionMessage(
                        content=restaurant_info,
                        name='get_restaurant_info'
                    ))
                    
                    # Get the final response
                    final_response = llm.invoke(messages)
                    print("\nBot:", final_response.content)
            else:
                print("\nBot:", response.content)
                
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()