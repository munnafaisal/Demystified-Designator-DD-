
def manager_agent_logic(llm_response):

    if llm_response[0].SERVICE_TYPE == "NA":

        cont = 1
        handover = 0
        status = {"cont": cont,"handover": handover}
        return status

    elif llm_response[0].SERVICE_TYPE == "BOOKING":
        cont = 0
        handover = 1
        status = {"cont": cont, "handover": handover, 'agent_node':"booking_agent"}
        return status

    elif llm_response[0].SERVICE_TYPE == "RESCHEDULE":
        cont = 0
        handover = 1
        status = {"cont": cont, "handover": handover, 'agent_node': "rescheduling_agent"}

        return status

    elif llm_response[0].SERVICE_TYPE == "CANCEL":
        cont = 0
        handover = 1
        status = {"cont": cont, "handover": handover, 'agent_node': "cancel_agent"}
        return status

    else:
        status = {"cont": 0, "handover": -1, 'msg': "It has not been possible to undersatnd your query"}
        return status


def booking_agent_logic(llm_response):

   if llm_response[0].SERVICE_STATUS == "DONE":

       cont = 0
       handover = 1
       status = {"cont": cont, "handover": handover,'agent_node':"agent_manager" , "service_status": llm_response[0].SERVICE_STATUS }
       return status

   elif llm_response[0].SERVICE_STATUS == "PENDING":
       cont = 1
       handover = 0
       status = {"cont": cont, "handover": handover, "service_status": llm_response[0].SERVICE_STATUS }
       return status

   elif llm_response[0].SERVICE_STATUS == "NA":
       cont = 0
       handover = 1
       status = {"cont": cont, "handover": handover, 'agent_node': "agent_manager", "service_status": llm_response[0].SERVICE_STATUS }
       return status

   else:
       status = {"cont": 0, "handover": -1, 'msg': "It has not been possible to undersatnd your query"}
       return status


def reschedule_agent_logic(llm_response):

   if llm_response[0].SERVICE_STATUS == "DONE":

       cont = 0
       handover = 1
       status = {"cont": cont, "handover": handover,'agent_node':"agent_manager", "service_status": llm_response[0].SERVICE_STATUS}
       return status

   elif llm_response[0].SERVICE_STATUS == "PENDING":
       cont = 1
       handover = 0
       status = {"cont": cont, "handover": handover, "service_status": llm_response[0].SERVICE_STATUS}
       return status

   elif llm_response[0].SERVICE_STATUS == "NA":
       cont = 0
       handover = 1
       status = {"cont": cont, "handover": handover, 'agent_node': "agent_manager", "service_status": llm_response[0].SERVICE_STATUS}
       return status

   else:
       status = {"cont": 0, "handover": -1, 'msg': "It has not been possible to undersatnd your query"}
       return status