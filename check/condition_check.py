from utils import python_extract,write_to_txt
import copy

def think_cm_key_check(out_dict):
    
    key_lst = ["corestates", "thought"]
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
        check_response += "Note: Your output must be a dictionary. Just Two keys are included: 'thought' and 'corestates'. Please do not output irrelevant content. \n"
    return error_tag, check_response


def think_cm_content_check(out_dict, state_manager):

    error_tag = False
    check_response = ""
    

    
    core_states_lst = out_dict['corestates']

    if not isinstance(core_states_lst,list):
        error_tag = True
        check_response += f"ERROR: the value of 'corestates' is not a list. \n"
    elif len(core_states_lst) == 0:
        error_tag = True
        check_response += f"ERROR: You generate nothing in 'corestates'. \n"
    else:
        
        tmp_dict = {"agents":state_manager.agents, 
                    "objects":state_manager.objects, 
                    "relationship":state_manager.relationship, 
                    "environment":state_manager.environment}
        
        for states in core_states_lst:
            states_lst = states.split("-")
            tmp = copy.deepcopy(tmp_dict)
            for i in range(len(states_lst)):
                if states_lst[i] in tmp:
                    tmp = tmp[states_lst[i]]
                else:
                    error_tag = True
                    check_response += f"ERROR: the key '{states}' of 'corestates' is not defined in the current world state.\n"

            if isinstance(tmp, dict):
                error_tag = True
                check_response += f"ERROR: the format of the key '{states}' is not correct.\n"

        
    return error_tag, check_response



def decide_cm_nl_content_check(out_dict):
    
    error_tag = False
    check_response = ""
    result = out_dict["result"]
    
    if result not in [False, True]:
        error_tag = True
        check_response += f"ERROR: the result key is not a bool variable. "
        
    return error_tag, check_response
 
 
def decide_cm_code_content_check(out_dict):
    
    error_tag = False
    check_response = ""
   
    code = out_dict["code"]
    codes_lst = python_extract(code)
    
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


def decide_cm_code_key_check(out_dict):
    
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

def decide_cm_nl_key_check(out_dict):
    
    key_lst = ["result", "thought"]
    error_tag = False
    check_response = ""
    
    if len(out_dict) != len(key_lst):
        error_tag = True
        check_response += f"ERROR: the number of key '{key}' is incorrect. Only 'thought' and 'result' could be the key in your response \n"
    
    for key in key_lst:
        if key not in out_dict:
            error_tag = True
            check_response += f"ERROR: the key '{key}' does not exist in your response. \n"

    if error_tag:
        check_response += "Note: Your output must be a dictionary. Just Two keys are included: 'thought' and 'result'. Please do not output irrelevant content. \n"
    return error_tag, check_response