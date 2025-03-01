from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
import json

def _get_restaurant_info(restaurant_name):
    print(f"Fetching information about {restaurant_name}...")
    
    # This is a placeholder function that would typically query a database or API
    # You could modify this to return None if the restaurant isn't found
    restaurant_info = {
        "name": restaurant_name,
        "cuisine": "Italian",
        "location": "123 Main St, New York, NY",
        "rating": 4.5,
        "price_range": "$$",
    }
    
    return restaurant_info

# Define the tool schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_restaurant_info",
            "description": "Get information about any restaurant. Always use this function when a user asks about a specific restaurant, even if you're not sure if it exists in the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_name": {
                        "type": "string",
                        "description": "The name of the restaurant to look up"
                    }
                },
                "required": ["restaurant_name"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are a helpful restaurant recommendation assistant. You have access to a function called get_restaurant_info that can retrieve information about restaurants.

IMPORTANT: Whenever a user asks about ANY specific restaurant, you MUST use the get_restaurant_info function to get the information. Do not make assumptions or give generic responses.
Even if you're not sure if the restaurant exists in the database, you should still attempt to use the function to check.

Once you have the information, you can use it to provide a helpful response to the user. Communicate in natural language and do not include any raw or structured data in your response."""

def send_messages(client, messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

def main():
    # Load environment variables
    load_dotenv()

    # Check if DEEPSEEK_API_KEY is set
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("Please set your DEEPSEEK_API_KEY in the .env file")
        return

    # Initialize the OpenAI client
    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com"
    )

    # Get current user and time information
    current_user = "pablo-lozano-martin"
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Welcome to the Terminal Chatbot, {current_user}!")
    print(f"Session started at: {current_time} UTC")
    print("-" * 50)

    # Initialize conversation with system message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['quit', 'exit']:
            print("\nGoodbye!")
            break

        try:
            # Add user message to conversation
            messages.append({"role": "user", "content": user_input})
            
            # Get initial response from model
            message = send_messages(client, messages)
            messages.append(message)

            # Handle tool calls if present
            if message.tool_calls:
                print("\n(Retrieving restaurant information...)")
                
                for tool_call in message.tool_calls:
                    if tool_call.function.name == "get_restaurant_info":
                        # Parse arguments and call function
                        args = json.loads(tool_call.function.arguments)
                        restaurant_info = _get_restaurant_info(args["restaurant_name"])
                        
                        # Add function result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(restaurant_info)
                        })
                
                # Get final response after function call
                final_message = send_messages(client, messages)
                messages.append(final_message)
                print("\nBot:", final_message.content)
            else:
                print("\nBot:", message.content)
                print("\n(Tool was not called)")

        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()