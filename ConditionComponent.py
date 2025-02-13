import py_trees as pt
from utils import json_extract, parse_scene
from check.syntax_checker_rule import json_valid_check
from check.condition_check import *


ConditionMeetSystemPrompt = "You are a world state determiner who can recognize and understand various scenes in the real world very well. The robot is executing a task in a real-life scenario, and you need to accurately determine whether the current world state meets a given condition."

def getThinkPrompCM(current_states, states_des, condition_name, condition_des, cm_think_shot_lst):
    
    # Generate few-shots
    condition_shot_str = ""
    i=0
    for condition_shot_dict in cm_think_shot_lst:
        states_dict = condition_shot_dict["states"]
        agents, objects, relationship, environment = parse_scene(states_dict)
        states_str = f"""agents: {str(agents)}
objects: {str(objects)}
relationship: {str(relationship)}
environment: {str(environment)}"""
        task_str = condition_shot_dict["agent_task"]
        condition_str = condition_shot_dict["conditon_name"]
        condition_des_str = condition_shot_dict["condition_des"]
        output_str = condition_shot_dict["output"]
        states_description_str = str(condition_shot_dict["state_description"])
        condition_shot_str += f"""Example {str(i)}

*Current States*:
{states_str}
*Current States Description*:
{states_description_str}
*Condition*:
name:{condition_str}
description:{condition_des_str}
*Output*:
```json
{output_str}
```
"""
        condition_shot_str += "\n\n"
        i+=1
    condition_shot_str = condition_shot_str.rstrip(condition_shot_str[-1])
    
    # Generate condition_prompt
    prompts = f"""{ConditionMeetSystemPrompt}
### Task Description
Based on your understanding of the current world states and semantics of the given condition, your task is to determine which states in the current world states are important to help you determine whether the provided condition is met. 

### Input Description
I will give you 
(1) the current world states (denoted as *Current States*). Specifically, we use a nested list in the state of the 'content' to show the affliation relationshiop of objects. For example. '[]' denotes nothing included in the object, [['bowl']] denotes a bowl included in the object, [['fruit_tray',['apple']]] denotes a fruit_tray with an apple inside includes in the object, [['fruit_tray',['apple']], ['knife']] denotes the object has a fruit_tray with apple inside and a knife.
(2) the description of the current world states (denoted as *Current States Description*)
(3) the detailed information of the condition needed to be checked (denoted as *Condition*)

### Output Rules
1. Your output must be a dictionary. Just Two keys are included: 'thought' and 'corestates'. Please do not output irrelevant content.
2. In the 'thought' key, you must give your reason about which states in the current world states are important to check the condition.
3. In the 'corestates' key, yous must extract the state names from the current world states based on your analysis in 'thought'. The state names should be represented as A-B-C. Keys from different levels are connected with hyphen.
4. The response should be output in the JSON format as shown in the example below, which should begins with ```json and ends with ```.

***** Example *****
{condition_shot_str}
***** Example Ends *****

Here is the task whose world states you need to determine.

*Current States*:
{current_states}
*Current States Description*:
{states_des}
*Condition*:
name:{condition_name}
description:{condition_des}
*Output*:
"""
    return prompts


def checkThinkRespCM(response, prompts, sc, state_manager, logger, max_check_iter):
    
    iter = 0
    check_pass_tag = False
    history = ""
    
    while (iter < max_check_iter):
        json_extraction_lst = json_extract(response)
        
        out_dict, json_check_error_tag, json_check_response = json_valid_check(json_extraction_lst, response)
        
        if json_check_error_tag:
            logger.info(f"{str(iter)}-th iter Fail. In JSON Format Check")
            print(f"{str(iter)}-th iter Fail. In JSON Format Check")
            logger.info(f"{json_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                json_check_response, 
                                                response, 
                                                prompts
                                                )
            logger.info(f"correct_response:\n{response}\n")
            continue
        
        
        key_error_tag, key_check_response = think_cm_key_check(out_dict)
        
        if key_error_tag:
            logger.info(f"{str(iter)}-th iter Fail. In Key Check")
            print(f"{str(iter)}-th iter Fail. In Key Check")
            logger.info(f"{key_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                key_check_response, 
                                                response, 
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
            continue
        
        
        content_error_tag, content_check_response = think_cm_content_check(out_dict, state_manager)
        
        if content_error_tag:
            logger.info(f"{str(iter)}-th iter Fail. In Key Content Check.")
            print(f"{str(iter)}-th iter Fail. In Key Content Check.")
            logger.info(f"{content_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                content_check_response, 
                                                response, 
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
        else:
            check_pass_tag = True
            #self.logger.info("Pass Condition Checks")
            break
        
        
        
    assert check_pass_tag
    
    return out_dict


def getDecidePrompCM_NL(current_states_str, states_des, condition_name, condition_des, core_states, cm_decide_nl_shot_lst):
    
    # Generate few-shots
    condition_shot_str = ""
    i=0
    for condition_shot_dict in cm_decide_nl_shot_lst:
        states_dict = condition_shot_dict["states"]
        agents, objects, relationship, environment = parse_scene(states_dict)
        states_str = f"""agents: {str(agents)}
objects: {str(objects)}
relationship: {str(relationship)}
environment: {str(environment)}"""
        task_str = condition_shot_dict["agent_task"]
        condition_str = condition_shot_dict["conditon_name"]
        condition_des_str = condition_shot_dict["condition_des"]
        output_str = condition_shot_dict["output"]
        states_description_str = str(condition_shot_dict["state_description"])
        core_states_str = str(condition_shot_dict["corestates"])
        condition_shot_str += f"""Example {str(i)}
*Current States*:
{states_str}
*Current States Description*:
{states_description_str}
*Condition*:
name:{condition_str}
description:{condition_des_str}
*Core States*
{core_states_str}
*Output*:
```json
{output_str}
```
"""
        condition_shot_str += "\n\n"
    condition_shot_str = condition_shot_str.rstrip(condition_shot_str[-1])
    # Generate condition_prompt
    prompts = f"""{ConditionMeetSystemPrompt}
    
### Task Description
Based on your understanding of the current world state, the task, and semantics of the given condition, your task is to determine whether the condition is met or not based on the give current world states and core states. 

### Input Description
I will give you 
(1) the current world states (denoted as *Current States*). Specifically, we use a nested list in the state of the 'content' to show the affliation relationshiop of objects. For example. '[]' denotes nothing included in the object, [['bowl']] denotes a bowl included in the object, [['fruit_tray',['apple']]] denotes a fruit_tray with an apple inside includes in the object, [['fruit_tray',['apple']], ['knife']] denotes the object has a fruit_tray with apple inside and a knife.
(2) the description of the current world states (denoted as *Current States Description*)
(3) the detailed information of the condition needed to be checked (denoted as *Condition*)
(4) the core states that affect condition check (denoted as *Core States*). The state name is represented as A-B-C. Keys from different levels are connected with hyphen.

### Output Rules
1. Your output must be a dictionary. Just Two keys are included: "thought" and "result". Please do not output irrelevant content.
2. In the 'thought' key, you should give your reasoning process to make the decision based on the current world states.
3. In the 'result' key, You need to output the judge result on whether the current world state meets a given condition. 'True' indicates that the current world state meets the condition. 'False' indicates that the current world state does not meet the condition. 
4. The response should be output in the JSON format as shown in the example below, which should begins with ```json and ends with ```.

***** Example *****
{condition_shot_str}
***** Example Ends *****

Here is the task whose world states you need to determine.

*Current States*:
{current_states_str}
*Current States Description*:
{states_des}
*Condition*:
name:{condition_name}
description:{condition_des}
*Core States*:
{core_states}
*Output*:
"""
    return prompts


def getDecidePrompCM_Code(current_states, states_des, condition_name, condition_des, corestates, cm_decide_code_shot_lst):
    # Generate few-shots
    condition_shot_str = ""
    i=0
    for condition_shot_dict in cm_decide_code_shot_lst:
        states_dict = condition_shot_dict["states"]
        agents, objects, relationship, environment = parse_scene(states_dict)
        states_str = f"""agents: {str(agents)}
objects: {str(objects)}
relationship: {str(relationship)}
environment: {str(environment)}"""
        task_str = condition_shot_dict["agent_task"]
        condition_str = condition_shot_dict["conditon_name"]
        condition_des_str = condition_shot_dict["condition_des"]
        output_str = condition_shot_dict["output"]
        states_description_str = str(condition_shot_dict["state_description"])
        corestates_str = str(condition_shot_dict["corestates"])
        condition_shot_str += f"""Example {str(i)}
*Current States*:
{states_str}
*Current States Description*:
{states_description_str}
*Condition*:
name:{condition_str}
description:{condition_des_str}
*Core States*
{corestates_str}
*Output*:
```json
{output_str}
```
"""
        condition_shot_str += "\n\n"
    condition_shot_str = condition_shot_str.rstrip(condition_shot_str[-1])
    # Generate condition_prompt
    prompts = f"""{ConditionMeetSystemPrompt}
    
### Task Description
Based on your understanding of the current world state, the task, and semantics of the given condition, your task is to determine whether the condition is met or not based on the give current world states and core states. 

### Input Description
I will give you 
(1) the current world states (denoted as *Current States*). Specifically, we use a nested list in the state of the 'content' to show the affliation relationshiop of objects. For example. '[]' denotes nothing included in the object, [['bowl']] denotes a bowl included in the object, [['fruit_tray',['apple']]] denotes a fruit_tray with an apple inside includes in the object, [['fruit_tray',['apple']], ['knife']] denotes the object has a fruit_tray with apple inside and a knife.
(2) the description of the current world states (denoted as *Current States Description*)
(3) the detailed information of the condition needed to be checked (denoted as *Condition*)
(4) the core states that affect conditional determination (denoted as *Core States*) The state name is represented as A-B-C. Keys from different levels are connected with hyphen.

### Output Rules
1. Your output must be a dictionary. Just Two keys are included: "thought" and "code". Please do not output irrelevant content.
2. In the 'thought' key, you should give your reasoning process to make the decision based on the current world states and the core states. 
3. In the 'code' key, you must generate python codes to calculate these values of core states. Specifically, the codes should be between with '###python' and ends with '###'. And lastly must get a boolean variable "resp" in final. The line break is '\n' not '\\n'. The line break is '\n' not '\\n'. Please output in a line, just like the examples we provided. Please output in a line, just like the examples we provided.
4. The response should be output in the JSON format as shown in the example below, which should begins with ```json and ends with ```. And the keys and values both begins with \" and ends with \".

***** Example *****
{condition_shot_str}
***** Example Ends *****

Here is the task whose world states you need to determine.

*Current States*:
{current_states}
*Current States Description*:
{states_des}
*Condition*:
name:{condition_name}
description:{condition_des}
*Core States*
{corestates}
*Output*:
"""
    return prompts


def checkDecideRespCM(response, prompts, branch_tag, max_check_iter, sc, logger):
    iter = 0
    check_pass_tag = False
    history = ""
    
    while (iter < max_check_iter):
        json_extraction_lst = json_extract(response)

        
        out_dict, json_check_error_tag, json_check_response = json_valid_check(json_extraction_lst, response)
        if json_check_error_tag:            
            logger.info(f"{str(iter)}-th iter Fail. In JSON Format Check")
            print(f"{str(iter)}-th iter Fail. In JSON Format Check")
            logger.info(f"{json_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                json_check_response, 
                                                response, 
                                                prompts
                                                )
            logger.info(f"correct_response:\n{response}\n")
            continue
        
        
        if branch_tag == "code_branch":
            key_error_tag, key_check_response = decide_cm_code_key_check(out_dict)
        elif branch_tag == "nl_branch":
            key_error_tag, key_check_response = decide_cm_nl_key_check(out_dict)
        else:
            raise NotImplementedError
        if key_error_tag:
            logger.info(f"{str(iter)}-th iter Fail. In Key Check")
            print(f"{str(iter)}-th iter Fail. In Key Check")
            logger.info(f"{key_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                key_check_response, 
                                                response, 
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
            continue
        
        
        if branch_tag == "code_branch":
            content_error_tag, content_check_response = decide_cm_code_content_check(out_dict)
        elif branch_tag == "nl_branch":
            content_error_tag, content_check_response = decide_cm_nl_content_check(out_dict)
        else:
            raise NotImplementedError
        if content_error_tag:            
            logger.info(f"{str(iter)}-th iter Fail. In Key Content Check.")
            print(f"{str(iter)}-th iter Fail. In Key Content Check.")
            logger.info(f"{content_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                content_check_response, 
                                                response, 
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
        else:
            check_pass_tag = True
            #self.logger.info("Pass Condition Checks")
            break
        
        
        
    assert check_pass_tag


        
    return out_dict