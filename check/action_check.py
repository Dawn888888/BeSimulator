
from utils import python_extract, write_to_txt
import copy

def think_st_key_check(out_dict, logger):
        
    key_lst = ["states_transferred", "thought"]
    error_tag = False
    check_response = ""
    
    for key in out_dict:
        if key not in key_lst:
            error_tag = True
            check_response += f"ERROR: the key '{key}' is not correct and it should be one of in {key_lst}.\n"
            logger.info(f"true_key_lst={key_lst}")
            logger.info(f"generate_key_lst={[key for key in out_dict]}")

    if error_tag:
        check_response += "Note: Your output must be a dictionary. Just Two keys are included: 'thought' and 'states_transferred'. Please do not output irrelevant content. \n"
    return error_tag, check_response

def think_content_check(out_dict, state_manager):
    
    error_tag = False
    check_response = ""
    
    if isinstance(out_dict["states_transferred"],list):
        
        if "None" in out_dict["states_transferred"]:
            if len(out_dict["states_transferred"]) != 1:
                error_tag = True
                check_response += f"ERROR: the value of 'states_transferred' is not correct.\n"
        else:
            
            tmp_dict = {"agents":state_manager.agents, 
                        "objects":state_manager.objects, 
                        "relationship":state_manager.relationship, 
                        "environment":state_manager.environment}
            
            for states in out_dict["states_transferred"]:
                states_lst = states.split("-")
                tmp = copy.deepcopy(tmp_dict)
                for i in range(len(states_lst)):
                    if states_lst[i] in tmp:
                        tmp = tmp[states_lst[i]]
                    else:
                        error_tag = True
                        check_response += f"ERROR: the key '{states}' of 'states_transferred' is not defined in the current world state.\n"
    else:
        error_tag = True
        check_response += f"ERROR: the value of 'states_transferred' should be a list. \n"
    
    
    return error_tag, check_response



def think_ae_key_check(out_dict):
    
    
    key_lst = ["corestates", "thought", "corestates_successtag"]
    error_tag = False
    check_response = "" 
    
    if len(out_dict) != len(key_lst):
        error_tag = True
        check_response += f"ERROR: the numer of keys in your response is not correct. \n"
       
    for key in key_lst:
        if key not in out_dict:
            error_tag = True
            check_response += f"ERROR: the key '{key}' does not exist in your response. \n"

    if error_tag:
        check_response += "Note: Your output must be a dictionary. Just Three keys are included: 'thought', 'corestates', and 'corestates_successtag'. Please do not output irrelevant content. \n"
        
    return error_tag, check_response


def think_ae_content_check(out_dict, state_manager):

    error_tag = False
    check_response = ""
    
    corestates_successtag_dict = out_dict['corestates_successtag']
    core_states_dict = out_dict['corestates']
    thought = out_dict['thought']
    
    if len(corestates_successtag_dict) != len(core_states_dict):
        error_tag = True
        check_response += f"ERROR: the number of items in 'corestates_successtag_dict' is not the same with the number of items in 'core_states_dict'. \n"
    else:
        for key in corestates_successtag_dict:
            if key not in core_states_dict:
                error_tag = True
                check_response += f"ERROR: the preconditions in 'corestates_successtag_dict' and 'core_states_dict' are different. \n"
    
    if error_tag:
        return error_tag, check_response
    
    
    for key in corestates_successtag_dict:
        bool_value = corestates_successtag_dict[key]
        if bool_value not in [False, True]:
            error_tag = True
            check_response += f"ERROR: the value of corestates_successtag[{key}] is not a bool variable. "
    
    if error_tag:
        return error_tag, check_response
    
    
    if not isinstance(core_states_dict, dict):
        error_tag = True
        check_response += f"ERROR: the value of 'corestates' is not a dict. \n"
    elif len(core_states_dict) == 0:
        error_tag = True
        check_response += f"ERROR: You generate nothing in 'corestates'. \n"
    else:
        for cond in core_states_dict:
            if not isinstance(core_states_dict[cond], list):
                error_tag = True
                check_response += f"ERROR: the value of '{cond}' is not a list. \n"
                
            elif len(core_states_dict[cond]) == 0:
                error_tag = True
                check_response += f"ERROR: You generate an empty list in the value of '{cond}'. \n"
            else:
                tmp_dict = {"agents":state_manager.agents, 
                            "objects":state_manager.objects, 
                            "relationship":state_manager.relationship, 
                            "environment":state_manager.environment}
                for states in core_states_dict[cond]:
                    states_lst = states.split("-")
                    tmp = copy.deepcopy(tmp_dict)
                    for i in range(len(states_lst)):
                        if states_lst[i] in tmp:
                            tmp = tmp[states_lst[i]]
                        else:
                            error_tag = True
                            check_response += f"ERROR: the key '{states}' in the value of '{cond}' is not defined in the current world state.\n"
    if error_tag:
        return error_tag, check_response
    
    
    for precondition in corestates_successtag_dict:
        
        tag_oppo = not corestates_successtag_dict[precondition]
        tag_str = str(corestates_successtag_dict[precondition])
        oppo_str = str(tag_oppo)
        check_str = f"{precondition}={oppo_str.lower()}"
        if check_str in thought.lower():
            error_tag = True
            check_response += f"ERROR: the boolean value of '{precondition}' in 'corestates_successtag' is not consistent with 'thought'. The boolean value of '{precondition}' in 'corestates_successtag' is {tag_str}. But in the 'thought', you think the condition should be {oppo_str}. Please modify your 'corestates_successtag' to be consistent with 'thought'\n"
            print(check_response)
    
    return error_tag, check_response
    
        



def decide_ae_nl_content_check(out_dict, corestates):
    
    error_tag = False
    check_response = ""
    
    result = out_dict["result"]
    
    if result not in [False, True]:
        error_tag = True
        check_response += f"ERROR: the result key is not a bool variable. "
    
    
    return error_tag, check_response
 
 
def decide_ae_code_content_check(out_dict, corestates):
    
    error_tag = False
    check_response = ""
       
    codes_lst = python_extract(out_dict["code"])
    
    if len(codes_lst) == 0:
        error_tag = True
        check_response += f"ERROR: the python codes in the value of key 'code' does not start with ###python and ends with ###. \n"
        python_codes = ""
    else:
        python_codes = codes_lst[0]
    
    
    namespace = {}
    try:
        exec(python_codes, namespace)
    except Exception as e:
        error_tag = True
        check_response += f"""The codes are:
```
{python_codes}
```
However, when running these codes, errors are reported: {e}.
"""
    else:
        if "resp" not in namespace:
            error_tag = True
            check_response += f"ERROR: In Python Code {python_codes}, the condition judge result does not assign to the 'resp' variable. Or you defined the 'resp' variable in the function, not the main function. \n"
        elif namespace["resp"] not in[False, True]:
            error_tag = True
            check_response += f"ERROR: In Python Code {python_codes}, the 'resp' variable value is not a bool variable. \n"
   
    return error_tag, check_response



def decide_ae_code_key_check(out_dict):
    
    
    key_lst = ["thought", "code"]
    error_tag = False
    check_response = ""    
    for key in key_lst:
        if key not in out_dict:
            error_tag = True
            check_response += f"ERROR: the key '{key}' does not exist in your response. \n"

    if error_tag:
        check_response += "Note: Your output must be a dictionary. Just Two keys are included: 'thought' and 'code'. Please do not output irrelevant content. \n"
    return error_tag, check_response

def decide_ae_nl_key_check(out_dict):
    
    
    key_lst = ["result", "thought"]
    error_tag = False
    check_response = ""
    
    for key in key_lst:
        if key not in out_dict:
            error_tag = True
            check_response += f"ERROR: the key '{key}' does not exist in your response. \n"

    if error_tag:
        check_response += "Note: Your output must be a dictionary. Just Two keys are included: 'thought' and 'result'. Please do not output irrelevant content. \n"
    return error_tag, check_response

def check_codes_format(value, error_tag, check_response):
    
    codes_lst = python_extract(value)
    
    if len(codes_lst) == 0:
        error_tag = True
        check_response += f"ERROR: the python codes {value} does not start with ###python and ends with ###. \n"
        python_codes = ""
    else:
        python_codes = codes_lst[0]
    
    return error_tag, check_response, python_codes
    

def check_codes_execute(value, python_codes, error_tag, check_response, state_manager):
    
    agents = state_manager.get("agents")
    objects = state_manager.get("objects")
    relationship = state_manager.get("relationship")
    environment = state_manager.get("environment")
    namespace = {"agents": agents, "objects": objects, "relationship": relationship, "environment": environment}

    try:
        exec(python_codes, namespace)
    except Exception as e:
        error_tag = True
        check_response += f"""The codes are:
```
{value}
```
However, when running these codes, errors are reported: {e}.
"""
    else:
        if "result" not in namespace:
            error_tag = True
            check_response += f"ERROR: In Python Code {python_codes} the final state transition value does not assign to the 'result' variable. Or you defined the 'result' variable in the function, not the main function. \n"
        
    return error_tag, check_response


def check_codes(value, error_tag, check_response, state_manager):
    error_tag, check_response, python_codes = check_codes_format(value, error_tag, check_response)
    if error_tag == False:
        error_tag, check_response = check_codes_execute(value, python_codes, error_tag, check_response, state_manager)
    return error_tag, check_response

def decide_st_key_check(out_dict, state_transferred, logger):
    
    
    state_high = state_transferred.split("-")[0]
    
    key_lst = ["agents", "objects", "relationship", "environment"]
    error_tag = False
    check_response = ""
    
    for key in out_dict:
        if key == state_high:
            pass
        elif key in key_lst and len(out_dict[key]) == 0:
            pass
        else:
            error_tag = True
            check_response += f"ERROR: you should not output the states about '{key}'. You should only output states about {state_transferred}.\n"
            logger.info(f"gt_key_lst={key_lst}")
            logger.info(f"out_dict_key_lst={[out_dict[item] for item in out_dict]}")
            logger.info(f"out_dict={out_dict}")

    return error_tag, check_response

def decide_st_content_check(out_dict, state_transferred, logger):
    
    error_tag = False
    check_response = ""
    
    states_lst = state_transferred.split("-")
    
    tmp_dict = copy.deepcopy(out_dict)
    for i in range(len(states_lst)):
        if states_lst[i] in tmp_dict:
            tmp_dict = tmp_dict[states_lst[i]]
            if i!=(len(states_lst)-1) and len(tmp_dict) != 1:
                error_tag = True
                check_response += f"ERROR: You have output extra states in  {tmp_dict}. Note that you only need to transfer the {state_transferred} state.\n"
        else:
            error_tag = True
            check_response += f"ERROR: the state '{state_transferred}' that you need to change in 'states_transferred' does not change.\n"
    
    return error_tag, check_response

def decide_st_code_check(out_dict, state_manager, logger):
    
    error_tag = False
    check_response = ""
    
    for item in out_dict:
        if item == "agents":
            for key_id, value_agent in out_dict[item].items():
                for key, value in value_agent.items():
                    # check if the state which will change is in the state_manager
                    # error_tag, check_response = check_state_tochange(["agents", key_id, key], error_tag, check_response, state_manager)
                    # deal with code
                    if isinstance(value, str) and value.startswith("###python"):
                        error_tag, check_response = check_codes(value, error_tag, check_response, state_manager)
                        check_response = f"Codes in the values of agent['{key}'] are not correct.\n" + check_response
                    # If this state needs to be updated, it cannot be read in dictionary form in the updates of other states
                    # copy_dict = copy.deepcopy(out_dict)
                    # del copy_dict['agents'][key_id][key]
                    # state_rep = f"agents['{key_id}']['{key}']"
                    # if state_rep in str(copy_dict):
                    #     error_tag = True
                    #     check_response += f"ERROR: The state {state_rep} will also be modified in state transition.To be safety, in other state transitions, you cannot read the value in dictionary form, but directly take the value and use it. "
        
        elif item == "objects":
            for key_id, value_object in out_dict[item].items():
                for key, value in value_object.items():
                    # check if the state which will change is in the state_manager
                    # error_tag, check_response = check_state_tochange(["objects", key_id, key], error_tag, check_response, state_manager)
                    
                    # deal with code
                    if isinstance(value, str) and value.startswith("###python"):
                        error_tag, check_response = check_codes(value, error_tag, check_response, state_manager)
                        check_response = f"The codes in the values of objects['{key}'] are not correct.\n" + check_response
                    # If this state needs to be updated, it cannot be read in dictionary form in the updates of other states
                    # copy_dict = copy.deepcopy(out_dict)
                    # del copy_dict['objects'][key_id][key]
                    # state_rep = f"objects['{key_id}']['{key}']"
                    # if state_rep in str(copy_dict):
                    #     error_tag = True
                    #     check_response += f"ERROR: The state {state_rep} will also be modified in state transition.To be safety, in other state transitions, you cannot read the value in dictionary form, but directly take the value and use it. "

        elif item == "relationship":
            for key, value in out_dict[item].items():
                # check if the state which will change is in the state_manager
                # error_tag, check_response = check_state_tochange(["relationship", key], error_tag, check_response, state_manager)
                
                # deal with code
                if isinstance(value, str) and value.startswith("###python"):
                    error_tag, check_response = check_codes(value, error_tag, check_response, state_manager)
                    check_response = f"The codes in the values of relationship['{key}'] are not correct.\n" + check_response
                # If this state needs to be updated, it cannot be read in dictionary form in the updates of other states
                # copy_dict = copy.deepcopy(out_dict)
                # del copy_dict['relationship'][key]
                # state_rep = f"relationship['{key}']"
                # if state_rep in str(copy_dict):
                #     error_tag = True
                #     check_response += f"ERROR: The state {state_rep} will also be modified in state transition.To be safety, in other state transitions, you cannot read the value in dictionary form, but directly take the value and use it. "
        
        elif item == "environment":
            for key, value in out_dict[item].items():
                # check if the state which will change is in the state_manager
                # error_tag, check_response = check_state_tochange(["environment", key], error_tag, check_response, state_manager)
                
                # deal with code
                if isinstance(value, str) and value.startswith("###python"):
                    error_tag, check_response = check_codes(value, error_tag, check_response, state_manager)
                    check_response = f"The codes in the values of environment['{key}'] are not correct.\n" + check_response
                # If this state needs to be updated, it cannot be read in dictionary form in the updates of other states
                # copy_dict = copy.deepcopy(out_dict)
                # del copy_dict['environment'][key]
                # state_rep = f"environment['{key}']"
                # if state_rep in str(copy_dict):
                #     error_tag = True
                #     check_response += f"ERROR: The state {state_rep} will also be modified in state transition.To be safety, in other state transitions, you cannot read the value in dictionary form, but directly take the value and use it. "
        
        else:
            pass
    return error_tag, check_response