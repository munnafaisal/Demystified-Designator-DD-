
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

# Define the function declaration for the model
schedule_meeting_function = {
    "name": "booking_appointment",
    "description": "Book an appointment at a given time and date.",
    "parameters": {
        "type": "object",
        "properties": {

            "date": {
                "type": "string",
                "description": "Date of the booking (e.g., '2024-07-29')",
            },
            "time": {
                "type": "string",
                "description": "Time of the booking (e.g., '15:00')",
            },

        },
        "required": ["date", "time"],
    },
}


# # Define a function that the model can call to control smart lights
# set_light_values_declaration = {
#     "name": "set_light_values",
#     "description": "Sets the brightness and color temperature of a light.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "brightness": {
#                 "type": "integer",
#                 "description": "Light level from 0 to 100. Zero is off and 100 is full brightness",
#             },
#             "color_temp": {
#                 "type": "string",
#                 "enum": ["daylight", "cool", "warm"],
#                 "description": "Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.",
#             },
#         },
#         "required": ["brightness", "color_temp"],
#     },
# }

# Configure the client and tools
client = genai.Client()
#tools = types.Tool(function_declarations=[schedule_meeting_function,set_light_values_declaration])
tools = types.Tool(function_declarations=[schedule_meeting_function])
config = types.GenerateContentConfig(tools=[tools])


# booking_agent_prompt = """ You are a booking agent, you will start dialog by following
# Hi, I am your booking agent. could you pls tell me the date and time you want to book the
# Doctor appointment?
#
# Instruction:
# 1.If customer gives you the date and time together then give thanks to the customer for providing the information
# 2.If any required data like date or time is missing then request the customer to provide date and time for booking again
# Read the following customer query :
# """

#query = "\n I want to Schedule a meeting with Bob and Alice for 03/14/2025 at 10:00 AM about the Q3 planning."
# Send request with function declarations

def get_func_response(query):

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        #contents="Schedule a meeting with Bob and Alice for 03/14/2025 at 10:00 AM about the Q3 planning.",
        #contents="Set the brightness level 50.",
        contents=query,
        config=config,
    )

    # Check for a function call
    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        print(f"Function to call: {function_call.name}")
        print(f"Arguments: {function_call.args}")

        #  In a real app, you would call your function here:
        #  result = schedule_meeting(**function_call.args)
        return "FUNCTION_CALL: successful"
    else:
        return "FUNCTION_CALL: not successful"
