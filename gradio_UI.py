import gradio as gr
import datetime
from bigtree import Node, find_name
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
import logging # Import the logging module

from AGENT_FUNCTIONS.booking_agent_function import get_func_response
from AGENT_FUNCTIONS.reschedule_agent_function import get_reschedule_func_response
from HAND_OVER_LOGICS.agent_logic import manager_agent_logic, booking_agent_logic, reschedule_agent_logic

# load_dotenv()

# Configure logging
log_filename = datetime.datetime.now().strftime('App_Log/my_app_%Y%m%d_%H%M%S.log')
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Starting gradio_UI.py script") # Log script start

client = genai.Client()

class MANAGER_FUNC(BaseModel):
    SERVICE_TYPE: str
    AGENT_REPLY: str


class BOOKING_FUNC(BaseModel):
    SERVICE_STATUS: str
    AGENT_REPLY: str


def get_ANS_FROM_MNG_LLM(my_prompt, my_content, my_query):
    logging.info(f"Calling Manager LLM with query: {my_query[:50]}...") # Log LLM call
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=my_prompt + my_content + my_query,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[MANAGER_FUNC],
            },
        )
        logging.info(f"Manager LLM response received: {response.parsed}") # Log LLM response
        return response.parsed
    except Exception as e:
        logging.error(f"Error calling Manager LLM: {e}") # Log any errors
        return None


def get_ANS_FROM_SERVICE_LLM(my_prompt, my_content, my_query):
    logging.info(f"Calling Service LLM with query: {my_query[:50]}...") # Log LLM call
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=my_prompt + my_content + my_query,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[BOOKING_FUNC],
            },
        )
        logging.info(f"Service LLM response received: {response.parsed}") # Log LLM response
        return response.parsed
    except Exception as e:
        logging.error(f"Error calling Service LLM: {e}") # Log any errors
        return None


agent_manager_prompt = """ You are a customer service manager, start conversation in a very friendly manner and your team can help you booking appoinments, rescheduling and canceling the booking
and also ask the customer regarding what kind of service he/she wants.

1.If customer wants to book an appointment, return "SERVICE_TYPE" as "BOOKING" and also thankfully reply and say you are going to assign a booking agent for him/her.
2.If customer wants to reschedule the appointment, return "SERVICE_TYPE" as "RESCHEDULE" and also thankfully reply and say you are going to assign a booking rescheduling agent for him/her.
3.IF customer wants to cancel the appointment, return "SERVICE_TYPE" as "CANCEL" and also thankfully reply and say you are going to assign a booking cancel agent for him/her.
4.IF customer customer's query is anything else then return "SERVICE_TYPE" as "NA" and also reply in a way that your role is a service manager and the services of your team offered to customer. 
he/she is looking for and advise to contact with the customer relation manager.  
Read the following customer query section :
"""

booking_agent_prompt = """ You are a booking agent, you will start dialog by following
Hi, I am your booking agent. could you pls tell me the date and time you want to book the 
Doctor appointment?

1. In the content section if you see "FUNCTION_CALL" is successfull then give thanks to customer with warm heart and also tell him/her that booking is confirmed return "SERVICE_STATUS" as "DONE" 
2. In the content section if you see "FUNCTION_CALL" is not successfull then you again ask the customer to provide the date and time properly for booking and return "SERVICE_STATUS" as "PENDING"
3. In the content section if you see "FUNCTION_CALL" is not successfull and customer is asking for help or instructions then request the customer to provide date and time for appointment and return "SERVICE_STATUS" as "PENDING"
4. In the content section if you see "FUNCTION_CALL" is not successfull and customer is talking about something else other than booking an appointment like reschedule or cancelation of existing booking, then return "SERVICE_STATUS" as "NA" and also reply that you are a booking agent only and you are going to handover this query to another agent.   
4. In the content section if you see "FUNCTION_CALL" is not successfull and customer is talking about something else other than booking an appointment, reschedule or cancelation of existing booking, then return "SERVICE_STATUS" as "NA" and also reply that this query is out of your scope and you are going to handover this query to another agent.   
Now read the following content section and customer query section: 
"""

reschedule_agent_prompt = """ You are a rescheduling agent, you will start dialog by following
Hi, I am your rescheduling agent. could you pls tell me your booking ID and the new date and time you want to rescheduling the 
Doctor appointment?

1. In the content section if you see "FUNCTION_CALL" is successfull then give thanks to customer with warm heart and also tell him/her that rescheduling has been confirmed return "SERVICE_STATUS" as "DONE" 
2. In the content section if you see "FUNCTION_CALL" is not successfull then you again ask the customer to provide the booking ID, date and time properly for rescheduling and return "SERVICE_STATUS" as "PENDING"
3. In the content section if you see "FUNCTION_CALL" is not successfull and customer is asking for help or instructions then request the customer to provide date and time for appointment and return "SERVICE_STATUS" as "PENDING"
4. In the content section if you see "FUNCTION_CALL" is not successfull and customer is talking about something else other than rescheduling an appointment, then return "SERVICE_STATUS" as "NA" and also reply that you are only a rescheduler agent and 
this query is out of your scope and you are going to handover this query to another agent.   
Now read the following content section and customer query section: 
"""

## Create manager agent
agent_manager = Node("agent_manager", role=agent_manager_prompt, llm_res=get_ANS_FROM_MNG_LLM,
                     agent_logic=manager_agent_logic, func_call=False)
logging.info("Manager agent created.") # Log agent creation

## Create booking agent
booking_agent = Node("booking_agent", role=booking_agent_prompt, parent=agent_manager, llm_res=get_ANS_FROM_SERVICE_LLM,
                     agent_logic=booking_agent_logic, func_call=True, fucn_name=get_func_response)
logging.info("Booking agent created.") # Log agent creation

## Create rescheduling agent
rescheduling_agent = Node("rescheduling_agent", role=reschedule_agent_prompt, parent=agent_manager,
                          llm_res=get_ANS_FROM_SERVICE_LLM, agent_logic=reschedule_agent_logic, func_call=True,
                          fucn_name=get_reschedule_func_response)
logging.info("Rescheduling agent created.") # Log agent creation

## Left for your homework
# cancel_agent = Node("cancel_agent", role = cancel_agent_prompt,parent= agent_manager)

## Start conversation with manager agent
current_node = agent_manager
logging.info(f"Current active agent initialized to: {current_node.name}") # Log initial agent

with (gr.Blocks() as demo):
    logging.info("Gradio Blocks created.") # Log Gradio UI creation
    with gr.Column():

        chatbot = gr.Chatbot(type="messages")
        msg = gr.Textbox()
        clear = gr.ClearButton([msg, chatbot])
        logging.info("Gradio UI components initialized.") # Log UI components

        def respond(message, chat_history):
            logging.info(f"User message received: {message}") # Log user input

            global current_node
            query = message
            prompt = current_node.role

            # conduct function call if the agent has associated functions to call
            if current_node.func_call:
                logging.info(f"Agent '{current_node.name}' has function call enabled. Calling its function.") # Log function call attempt
                func_response = current_node.fucn_name(query)
                content = "\n content :" + func_response + "\n" + "query : \n" + query
                logging.info(f"Function call response: {func_response}") # Log function call result
            else:
                logging.info(f"Agent '{current_node.name}' does not have function call enabled.") # Log no function call
                content = "\n content : empty \n" + query

            res = current_node.llm_res(my_prompt=prompt, my_content=content, my_query=query)
            logging.info(f"LLM response from '{current_node.name}': {res}") # Log LLM response received

            state = current_node.agent_logic(llm_response=res) ## Get hand over status using agent logic
            logging.info(f"Agent logic state for '{current_node.name}': {state}") # Log agent logic decision

            print(res) # Existing print
            print(state) # Existing print

            if state['handover'] :
                logging.info(f"Handover initiated from agent '{current_node.name}'.") # Log handover decision

                print(res) # Existing print
                print(state) # Existing print

                if "service_status" in list(state.keys()):
                    logging.info(f"Service status detected: {state['service_status']}") # Log service status

                    if state['service_status'] == "DONE":
                        logging.info(f"Service status is DONE. Handing over to '{state['agent_node']}'.") # Log DONE status
                        prev_node = current_node
                        current_node = find_name(agent_manager, state['agent_node'])
                        bot_message = "# " + prev_node.name + " \n " + res[0].AGENT_REPLY + "\n Now I am taking you back to my " + state['agent_node'] + "If you have any further inquiry"
                        chat_history.append({"role": "user", "content": message})
                        chat_history.append({"role": "assistant", "content": bot_message})
                        logging.info(f"Appended bot message for DONE status: {bot_message}") # Log appended message

                        comp_msg = f"\n Thank you for your co-operation.Your query has been successfully resolved by our **{prev_node.name}** agent"
                        chat_history.append({"role": "user", "content": "..."})
                        chat_history.append({"role": "assistant", "content": "# " + current_node.name + comp_msg})
                        logging.info(f"Appended completion message: {comp_msg}") # Log appended message

                    elif state['service_status'] == "NA":
                        logging.info(f"Service status is NA. Handing over to '{state['agent_node']}'.") # Log NA status
                        prev_node = current_node
                        current_node = find_name(agent_manager, state['agent_node'])
                        bot_message = "# " + prev_node.name + " \n " + res[
                            0].AGENT_REPLY + "\n Now I am taking you back to my " + "**"+ state[
                                          'agent_node'] +"**"+ " Hope he may help you"
                        logging.info(f"Appended bot message for NA status: {bot_message}") # Log appended message

                        comp_msg = f"\n Thank you for your co-operation.Our **{prev_node.name}** agent tried it's best to resolve you query. Could you pls explain your query again."

                        chat_history.append({"role": "user", "content": message})
                        chat_history.append({"role": "assistant", "content": bot_message})

                        chat_history.append({"role": "user", "content": "..."})
                        chat_history.append({"role": "assistant", "content": "# " + current_node.name + comp_msg})
                        logging.info(f"Appended completion message for NA status: {comp_msg}") # Log appended message

                    else: # service_status is PENDING
                        logging.info(f"Service status is PENDING. Continuing with agent '{current_node.name}'.") # Log PENDING status
                        bot_message = "# " + current_node.name + " \n " + "\n" + res[0].AGENT_REPLY
                        chat_history.append({"role": "user", "content": message})
                        chat_history.append({"role": "assistant", "content": bot_message})
                        logging.info(f"Appended bot message for PENDING status: {bot_message}") # Log appended message

                else: # For manager agent, no service_status, only service_type
                    logging.info(f"No service status (Manager Agent). Handing over to '{state['agent_node']}'.") # Log manager handover
                    prev_node = current_node
                    current_node = find_name(agent_manager, state['agent_node'])
                    bot_message = "# " + prev_node.name + " \n " + "\n" + res[0].AGENT_REPLY
                    chat_history.append({"role": "user", "content": message})
                    chat_history.append({"role": "assistant", "content": bot_message})
                    logging.info(f"Appended manager handover bot message: {bot_message}") # Log appended message

                    chat_history.append({"role": "user", "content": "..."})
                    chat_history.append({"role": "assistant", "content": "# " + current_node.name +" \n I am here to help you..."})
                    logging.info("Appended manager follow-up message.") # Log appended message


            else:
                # Continue conversation with current agent until a handover condition is met
                logging.info(f"No handover. Continuing conversation with current agent '{current_node.name}'.") # Log no handover
                bot_message = "# " + current_node.name + " \n " + "\n" + res[0].AGENT_REPLY
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": bot_message})
                logging.info(f"Appended current agent's response: {bot_message}") # Log appended message

            return "", chat_history


        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        logging.info("Gradio message submit event configured.") # Log event config

if __name__ == "__main__":
    demo.height = 25
    demo.width = 25
    demo.launch()
    logging.info("Gradio demo launched.") # Log demo launch