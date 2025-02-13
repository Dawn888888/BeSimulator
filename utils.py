import json
import os
import re
import logging





def string_to_bool(s):
    if s in [True, False]:
        return s
    else:
        if s.lower() == "true":
            return True
        elif s.lower() == "false":
            return False
        else:
            raise ValueError("Invalid input. Expected 'true' or 'false'.")

def is_subset(a, b, error_str):
    
    for key_a, value_a in a.items():
        if key_a not in b:
            error_str += f"In your output {a}, {key_a} not in {b}\n"
            print("Error:", key_a, b)
            return False, error_str
        if isinstance(value_a, dict):
            if not is_subset(value_a, b[key_a], error_str):
                return False, error_str
        elif value_a != b[key_a]:
            error_str += f"You output {{{key_a}:{value_a}}} is not equal to {b}\n"
            print("Error:", value_a, b[key_a])
            return False, error_str
    return True, error_str


def get_states_from_blackboard(blackboard):
    states = f"""agents: {str(blackboard.agents)}
objects: {str(blackboard.objects)}
relationship: {str(blackboard.relationship)}
environment: {str(blackboard.environment)}"""
    return states

def get_description_from_blackboard(blackboard):
    description = f"""state_description: {str(blackboard.state_description)}"""
    return description


def get_logger(task_name, logpath):
    
    logger = logging.getLogger(task_name)
    
    filename = os.path.join(logpath)
    
    fh = logging.FileHandler(filename, mode='w+', encoding='utf-8')
    
    logger.setLevel(logging.INFO)
    logger.addHandler(fh)
    
    return logger


def exec_code_string(code_s, state_manager):

    agents = state_manager.get("agents")
    objects = state_manager.get("objects")
    relationship = state_manager.get("relationship")
    environment = state_manager.get("environment")
    namespace = {"agents": agents, "objects": objects, "relationship": relationship, "environment": environment}

    exec(code_s, namespace) 
    
    result = namespace.get("result")
    
    return result


def blackboard_update(response, blackboard):
    '''
    Simulate action execution and perform state transition
    '''
    if "agents" in response:
        agents = response["agents"]
        # agents     
        for key_id, value_agent in agents.items():
            for key, value in value_agent.items():
                blackboard.agents[key_id][key] = value    
    if "objects" in response:
        objects = response["objects"]
        # objects
        for key_id, value_object in objects.items():
            for key, value in value_object.items():
                blackboard.objects[key_id][key] = value
                
    if "relationship" in response:
        relationship = response["relationship"]
        # relationship
        for key, value in relationship.items():
            blackboard.relationship[key] = value
    
    if "environment" in response:
        environment = response["environment"]
        # environment
        for key, value in environment.items():
            blackboard.environment[key] = value

    return blackboard


def read_json_eachline(data_path):
    '''
    return json list
    '''
    data_lst = []
    with open(data_path, "r", encoding='utf-8') as f:
        for l in f:
            item = json.loads(l)
            data_lst.append(item)            
    f.close()
    return 

def read_jsonfile(path):
    
    with open(path, "r", encoding='utf-8') as f:
        lst = json.load(f)

    return lst
    

def json_extract(response):
    
    if "### Output" in response:
        output_index = response.find("### Output")
        response = response[output_index:]

    if "**Output:**" in response:
        output_index = response.find("**Output:**")
        response = response[output_index:]
    
    if "*Output:*" in response:
        output_index = response.find("*Output:*")
        response = response[output_index:]

    pattern = r'```json(.*?)```'
    lst = re.findall(pattern, response, re.S)
    
    return lst


def python_extract(response):
    
    pattern = r'###python(.*?)###'
    lst = re.findall(pattern, response, re.S)
    
    return lst


def write_to_json(path, infor):
    
    with open(path, mode='w', encoding='utf-8') as f:
        json.dump(infor, f, indent=4, ensure_ascii=False)
    f.close()


def write_to_txt(path, info):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(info)

def parse_scene(State):

    #agents
    agents = {}
    state_agents = State["agents"]
    for id_name in state_agents:
        attributes = {}
        for key in state_agents[id_name]:
            if key == "properties":
                for subkey in state_agents[id_name]["properties"]:
                    attributes[subkey] = state_agents[id_name]["properties"][subkey]
            # elif key != "id":
            else:
                attributes[key] = state_agents[id_name][key]
        agents[id_name] = attributes
    

    # objects
    objects = {}
    state_objects = State["objects"]
    for id_name in state_objects:
        attributes = {}
        for key in state_objects[id_name]:
            if key == "properties":
                for subkey in state_objects[id_name]["properties"]:
                    attributes[subkey] = state_objects[id_name]["properties"][subkey]
            # elif key != "id":
            else:
                attributes[key] = state_objects[id_name][key]
        objects[id_name] = attributes

    # relationship
    relationship = State["relationship"]

    # environment
    environment = State["environment"]


    
    return agents, objects, relationship, environment