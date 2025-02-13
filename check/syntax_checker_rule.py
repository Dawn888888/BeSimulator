from utils import python_extract,write_to_txt

def json_valid_check(lst, response):
    error_tag = False
    check_response = ""
    
    if len(lst) == 0:
        try:
            #print(response)
            response = response.replace("\n","")
            out_dict = eval(response, {"true":True,"false":False,"null":None})
            #out_dict = json.loads(response)
        except Exception as e:
            print("no json")
            out_dict = {}
            error_tag = True
            
            check_response = f"ERROR: response does not follow the JSON format. The reported errors are {e}."
            
    else:
        out = lst[0]
        out = out.strip()
        out = out.replace('\\\\n','\\n')
        out = out.replace('\\\\','')
        
        try:
            out_dict = eval(out, {"true":True,"false":False,"null":None})
            #out_dict = json.loads(out)
        except Exception as e: 
            out_dict = {}
            error_tag = True
            check_response = f"ERROR: response does not follow the JSON format. The reported errors are {e}. \nNote: if you output code, please output in a line, just like the examples we provided. Use '\\n' in the code string to represent line breaks."
            
    return out_dict, error_tag, check_response



def is_valid_3d_position(var):
    
    if not isinstance(var, list):
        return False

    if len(var) != 3:
        return False

    for element in var:
        if not (isinstance(element, int) or isinstance(element, float)):
            return False

    return True



def check_state_tochange(state, error_tag, check_response, state_manager):
    
    error_tag, check_response = state_manager.check_state_exist(error_tag, check_response, state)
    return error_tag, check_response 



def is_valid_3d_position(var):
    
    if not isinstance(var, list):
        return False

    if len(var) != 3:
        return False

    for element in var:
        if not (isinstance(element, int) or isinstance(element, float)):
            return False

    return True



def is_dict_dict(value): 
    
    if not isinstance(value, dict):

        return False

    for item in value:
        if not isinstance(value[item], dict):

            return False
    return True