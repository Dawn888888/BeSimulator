from utils import json_extract, parse_scene
from check.syntax_checker_rule import json_valid_check
from check.action_check import *
    
ActionExecuteSystemPrompt = "You are a world model that can recognize and understand various scenes in the real world well, and can determine whether the action could be executed successfully."
StateTransferSystemPrompt = "You are a world model that can recognize and understand various scenes in the real world well, and can predict and future situations."


def getThinkPrompAE(current_states_str, description_str, agent_tasks, action_description_dict, instance_name, ae_think_shot_lst):
    
    ae_think_shot_str = ""
    i = 0
    for ae_think_shot_dict in ae_think_shot_lst:
        agents, objects, relationship, environment = parse_scene(ae_think_shot_dict["states"])
        states_str = f"""agents: {str(agents)}
objects: {str(objects)}
relationship: {str(relationship)}
environment: {str(environment)}"""

        task_str = ae_think_shot_dict["agent_task"]
        output_str = ae_think_shot_dict["output"]
        ae_think_shot_str += f"""Example {str(i)}
        
*Current States*:
{states_str}
*Current States Description*:
{str(ae_think_shot_dict["state_description"])}
*Action*:
name: {ae_think_shot_dict["action"]["action_class"]}
description:{ae_think_shot_dict["action"]["description"]}
*Output*:
```json
{output_str}
```
"""
        ae_think_shot_str += "\n\n"
        i +=1
    ae_think_shot_str = ae_think_shot_str.rstrip(ae_think_shot_str[-1])
    
    # Generate decide_prompt
    prompts = f"""{ActionExecuteSystemPrompt}

### Task Description
Based on your understanding of the current world state, the task, and semantics of the given action, your task is to determine whether this provided action could be executed successfully based on the current states and action description, and gives your reason process. 

### Input Description
I will give you 
(1) the current world state in dictionary (denoted as *Current States*). Specifically, we use a nested list in the state of the 'content' to show the affliation relationshiop of objects. For example. '[]' denotes nothing included in the object, [['bowl']] denotes a bowl included in the object, [['fruit_tray',['apple']]] denotes a fruit_tray with an apple inside includes in the object, [['fruit_tray',['apple']], ['knife']] denotes the object has a fruit_tray with apple inside and a knife.
(2) the detailed description of current world states in dictionary (denoted as *Current States Description*) 
(3) the detailed information of the action including name and description(denoted as *Action*)

### Output Rules

1. Your output must be a dictionary. Just Three keys are included: 'thought', 'corestates', and 'corestates_successtag'. Please do not output irrelevant content.
2. In the 'thought' key, you should first summarize the conditions that need to be met and the corresponding boolean value, based on the current world states, for the action to be executed successfully. Then, identify which states in the current world states are crucial for influencing each condition. Boolean value is true, indicating that these conditions should be met for the action execution; Boolean value is false, indicating that these conditions should not be met for the action execution. You should express it as 'condition?=true' or 'condition?=false'.
3. In the 'corestates' key, the value is a dictionary. The dictionary includes all preconditions that affect the execution of the action. The keys of the dictionary should be expressed as complete question sentences, representing each precondition. The corresponding values should be the core states from the current world states that are necessary to check each precondition. The state names should be represented as A-B-C. Keys from different levels are connected with hyphen. Each condition corresponds to several states in a list.
4. In the 'corestates_successtag' key, it shows the boolean value that each precondition in the 'corestates' dictionary should return for the action to be executed successfully. Ensure that information in 'corestates_successtag' should be consisted with the meaning in 'corestates'.
5. The response should be output in the JSON format as shown in the example below, which should begins with ```json and ends with ```.

***** Example *****
{ae_think_shot_str}
***** Example Ends *****

*Current States*:
{current_states_str}
*Current States Description*:
{description_str}
*Action*:
name: {instance_name}
description: {action_description_dict['description']}
*Output*:
"""
    return prompts


def checkThinkRespAE(response, prompts, max_check_iter, state_manager, sc, logger):
    iter = 0
    check_pass_tag = False
    history = ""
    
    while (iter < max_check_iter):
        
        logger.info(f"{iter}-th Think Response Check")
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
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
            continue
        
        
        key_error_tag, key_check_response = think_ae_key_check(out_dict)
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
                    
        
        value_error_tag, value_check_response = think_ae_content_check(out_dict, state_manager)
        if value_error_tag:
            logger.info(f"{str(iter)}-th iter Fail. In Content Check.")
            print(f"{str(iter)}-th iter Fail. In Content Check.")
            logger.info(f"{value_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                value_check_response, 
                                                response, 
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
        else:
            check_pass_tag = True
            #self.logger.info("Pass Action Responses Checks")
            break
        
        
    assert check_pass_tag
    
    return out_dict


def getDecidePrompAE_NL(current_states_str, description_str, agent_tasks, action_description_dict, instance_name, precondition, ae_cond_corestates, ae_decide_nl_shot_lst):
    
    ae_decide_nl_shot_str = ""
    i = 0
    for ae_decide_nl_shot_dict in ae_decide_nl_shot_lst:
        
        agents, objects, relationship, environment = parse_scene(ae_decide_nl_shot_dict["states"])
        states_str = f"""agents: {str(agents)}
objects: {str(objects)}
relationship: {str(relationship)}
environment: {str(environment)}"""

        task_str = ae_decide_nl_shot_dict["agent_task"]
        output_str = ae_decide_nl_shot_dict["output"]
        precondition_str = list(ae_decide_nl_shot_dict["corestates"].keys())[0]
        corestates_str = str(ae_decide_nl_shot_dict["corestates"][precondition_str])
        ae_decide_nl_shot_str += f"""Example {str(i)}
        
*Current States*:
{states_str}
*Current States Description*:
{str(ae_decide_nl_shot_dict["state_description"])}
*Action*:
name: {ae_decide_nl_shot_dict["action"]["action_class"]}
description:{ae_decide_nl_shot_dict["action"]["description"]}
*Condition*
{precondition_str}
*Core States*:
{corestates_str}
*Output*:
```json
{output_str}
```
"""
        ae_decide_nl_shot_str += "\n\n"
        i +=1
    ae_decide_nl_shot_str = ae_decide_nl_shot_str.rstrip(ae_decide_nl_shot_str[-1])
    
    prompts = f"""You are a world model that can recognize and understand various scenes in the real world well, and can determine whether the action could be executed successfully.

### Task Description
Based on your understanding of the current world state, and semantics of the given action, and a condition related to whether the action can be executed. Your task is to determine whether the condition is true based on the current states and the core states, and gives your reason process. 

### Input Description
I will give you 
(1) the current world state in dictionary (denoted as *Current States*). Specifically, we use a nested list in the state of the 'content' to show the affliation relationshiop of objects. For example. '[]' denotes nothing included in the object, [['bowl']] denotes a bowl includs in the object, [['fruit_tray',['apple']]] denotes a fruit_tray with an apple inside includes in the object, [['fruit_tray',['apple']], ['knife']] denotes the object has a fruit_tray with apple inside and the object also has a knife inside.
(2) the detailed description of current world states in dictionary (denoted as *Current States Description*) 
(3) the detailed information of the action including name and description (denoted as *Action*)
(4) one condition related to whether the action can be executed successfully (denoted as *Condition*).
(5) the core states which are key basis for you to determine whether this condition is true or false (denoted as *Core States*)

### Output Rules
1. Your output must be a dictionary. Just Two keys are included: "thought" and "result". Please do not output irrelevant content.
2. In the 'thought' key, you should give your reasoning process about whether the condition is true based on the current world states and provided core states.
3. In the 'result' key, You need to output the judge result on whether the condition is true or false. 'True' indicates that the condition is true in the current world state. 'False' indicates that the condition is false in the current world state. 
4. The response should be output in the JSON format as shown in the example below, which should begins with ```json and ends with ```.

***** Example *****
{ae_decide_nl_shot_str}
***** Example Ends *****

*Current States*:
{current_states_str}
*Current States Description*:
{description_str}
*Action*:
name: {instance_name}
description: {action_description_dict['description']}
*Condition*:
name: {precondition}
*Core States*:
{ae_cond_corestates}
*Output*:
"""
    return prompts

def getDecidePrompAE_Code(current_states_str, description_str, agent_tasks, action_description_dict, instance_name, precondition, ae_cond_corestates, ae_decide_code_shot_lst):
    
    ae_decide_code_shot_str = ""
    i = 0
    for ae_decide_code_shot_dict in ae_decide_code_shot_lst:
        
        agents, objects, relationship, environment = parse_scene(ae_decide_code_shot_dict["states"])
        states_str = f"""agents: {str(agents)}
objects: {str(objects)}
relationship: {str(relationship)}
environment: {str(environment)}"""

        task_str = ae_decide_code_shot_dict["agent_task"]
        output_str = ae_decide_code_shot_dict["output"]
        precondition_str = list(ae_decide_code_shot_dict["corestates"].keys())[0]
        corestates_str = str(ae_decide_code_shot_dict["corestates"][precondition_str])
        ae_decide_code_shot_str += f"""Example {str(i)}
        
*Current States*:
{states_str}
*Current States Description*:
{str(ae_decide_code_shot_dict["state_description"])}
*Action*:
name: {ae_decide_code_shot_dict["action"]["action_class"]}
description:{ae_decide_code_shot_dict["action"]["description"]}
*Condition*
{precondition_str}
*Core States*:
{corestates_str}
*Output*:
```json
{output_str}
```
"""
        ae_decide_code_shot_str += "\n\n"
        i +=1
    ae_decide_code_shot_str = ae_decide_code_shot_str.rstrip(ae_decide_code_shot_str[-1])
    
    prompts = f"""{ActionExecuteSystemPrompt}

### Task Description
Based on your understanding of the current world state, and semantics of the given action, your task is to determine whether this provided condition is met based on the current states and the core states, and gives your reason process. 

### Input Description
I will give you 
(1) the current world state in dictionary (denoted as *Current States*). Specifically, we use a nested list in the state of the 'content' to show the affliation relationshiop of objects. For example. '[]' denotes nothing included in the object, [['bowl']] denotes a bowl includs in the object, [['fruit_tray',['apple']]] denotes a fruit_tray with an apple inside includes in the object, [['fruit_tray',['apple']], ['knife']] denotes the object has a fruit_tray with apple inside and the object also has a knife inside.
(2) the detailed description of current world states in dictionary (denoted as *Current States Description*) 
(3) the detailed information of the action including name and description (denoted as *Action*)
(4) one condition related to whether the action can be executed successfully (denoted as *Condition*).
(5) the core states which are key basis for you to determine whether this condition is true or false (denoted as *Core States*)

### Output Rules
1. Your output must be a dictionary. Just Two keys are included: "thought" and "code". Please do not output irrelevant content.
2. In the 'thought' key, you should give your reasoning process to make the decision based on the current world states and the core states. 
3. In the 'code' key, you must generate python codes to calculate these values of core states. Specifically, the codes should be between with '###python' and ends with '###'. And lastly must get a boolean variable "resp" in final. The line break is '\n' not '\\n'. The line break is '\n' not '\\n'. Please output in a line, just like the examples we provided.Please output in a line, just like the examples we provided.
4. The response should be output in the JSON format as shown in the example below, which should begins with ```json and ends with ```. And the keys and values both begins with \" and ends with \".

***** Example *****
{ae_decide_code_shot_str}
***** Example Ends *****

*Current States*:
{current_states_str}
*Current States Description*:
{description_str}
*Action*:
name: {instance_name}
description: {action_description_dict['description']}
*Condition*:
name: {precondition}
*Core States*:
{ae_cond_corestates}
*Output*:
"""
    return prompts


def checkDecideRespAE(prompts, response, corestates, branch_tag, max_check_iter, sc, logger):
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
        else:
            logger.info(f"pass json check")

        
        if branch_tag == "code_branch":
            key_error_tag, key_check_response = decide_ae_code_key_check(out_dict)
        elif branch_tag == "nl_branch":
            key_error_tag, key_check_response = decide_ae_nl_key_check(out_dict)
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
            content_error_tag, content_check_response = decide_ae_code_content_check(out_dict, corestates)
        elif branch_tag == "nl_branch":
            content_error_tag, content_check_response = decide_ae_nl_content_check(out_dict, corestates)
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


def getThinkPrompST(current_states_str, description_str, agent_tasks, action_description_dict, instance_name, st_think_shot_lst):
    st_think_shot_str = ""
    i = 0
    for think_shot_dict in st_think_shot_lst:
        states_dict = think_shot_dict["states"]
        agents, objects, relationship, environment = parse_scene(states_dict)
        states_str = f"""agents: {str(agents)}
objects: {str(objects)}
relationship: {str(relationship)}
environment: {str(environment)}"""

        task_str = think_shot_dict["agent_task"]

        
        output_str = think_shot_dict["output"]
        state_description_shot_str = str(think_shot_dict["state_description"])

        
        st_think_shot_str += f"""Example {str(i)}

*Current States*:
{states_str}
*Current States Description*:
{state_description_shot_str}
*Action*:
name: {think_shot_dict["action"]["action_class"]}
description:{think_shot_dict["action"]["description"]}
*Output*:
```json
{output_str}
```
"""
        st_think_shot_str += "\n\n"
        i +=1
    st_think_shot_str = st_think_shot_str.rstrip(st_think_shot_str[-1])
    
    # Generate think_prompt
    prompts = f"""{StateTransferSystemPrompt}

### Task Description
Based on your understanding of the current world state, the task, and semantics of the given action, your task is to output all states needed to be changed after the action is executed, and gives your reason process. 
You need to consider the attributes of agent, objects, world environment, as well as the complex intersections of their relationships.

### Input Description
I will give you 

(1) the current world state in dictionary (denoted as *Current States*). Specifically, we use a nested list in the state of the 'content' to show the affliation relationshiop of objects. For example. '[]' denotes nothing included in the object, [['bowl']] denotes a bowl included in the object, [['fruit_tray',['apple']]] denotes a fruit_tray with an apple inside includes in the object, [['fruit_tray',['apple']], ['knife']] denotes the object has a fruit_tray with apple inside and a knife.
(2) the detailed description of current world states in dictionary (denoted as *Current States Description*) 
(3) the detailed information of the action including name and description(denoted as *Action*)

### Output Rules
1. Your output must be a dictionary. Just Two keys are included: "states_transferred" and "thought". Please do not output irrelevant content.
2. For "thought" key, please output your thought and reason process about which states needed to be changed.
3. For "states_transferred" key, its value is a list of all states from the current world states that are changed by this action '{instance_name}' with considering of the world common knowledge and the affliation relationship provided in the current states. The state name should be represented as A-B-C. Keys from different levels are connected with short lines. Considering the dependency relationship between the states needed to be changed, these states should be output sequentially in the order in which they are updated. If there are no states needed to be changed, please output ['None'].
4. Please only consider the direct effects brought by this one action '{instance_name}' according to its description.
5. The response should be output in the standard JSON format as shown in the example below.

***** Example *****
{st_think_shot_str}
***** Example Ends *****

*Agent Task*:
{agent_tasks}
*Current States*:
{current_states_str}
*Current States Description*:
{description_str}
*Action*:
name: {instance_name}
description: {action_description_dict['description']}
*Output*:
"""
    return prompts



def checkThinkRespST(response, prompts, sc, state_manager, logger,max_check_iter):
    iter = 0
    check_pass_tag = False
    history = ""
    
    while (iter < max_check_iter):
        
        logger.info(f"{iter}-th Think Response Check")
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
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
            continue
        
        
        key_error_tag, key_check_response = think_st_key_check(out_dict, logger)
        if key_error_tag:
            logger.info(f"{str(iter)}-th iter Fail. In Think Key Check")
            print(f"{str(iter)}-th iter Fail. In Think Key Check")
            logger.info(f"{key_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                key_check_response, 
                                                response, 
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
            continue
                    
        
        value_error_tag, value_check_response = think_content_check(out_dict, state_manager)
        if value_error_tag:
            logger.info(f"{str(iter)}-th iter Fail. In Think Value Check.")
            print(f"{str(iter)}-th iter Fail. In Think Value Check.")
            logger.info(f"{value_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                value_check_response, 
                                                response, 
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
        
        else:
            check_pass_tag = True
            #self.logger.info("Pass Action Responses Checks")
            break
        
    assert check_pass_tag
    
    return out_dict


def getDecidePrompST(current_states_str, states_description, agent_tasks, action_description_dict, state_transferred, thought, past_states_transferred_action, instance_name,st_decide_shot_lst):
    
    st_decide_shot_str = ""
    i = 0
    for decide_shot_dict in st_decide_shot_lst:
        states_dict = decide_shot_dict["states"]
        agents, objects, relationship, environment = parse_scene(states_dict)
        states_str = f"""agents: {str(agents)}
objects: {str(objects)}
relationship: {str(relationship)}
environment: {str(environment)}"""
        task_str = decide_shot_dict["agent_task"]

            
        output_str = decide_shot_dict["output"]
        thought_str = decide_shot_dict["thought"]
        state_description_shot_str = str(decide_shot_dict["state_description"])
        st_decide_shot_str += f"""Example {str(i)}
*Agent Task*:
{task_str}
*Current States*:
{states_str}
*Current States Description*:
{state_description_shot_str}
*Action*:
{decide_shot_dict["action"]["action_class"]}:{decide_shot_dict["action"]["description"]}
*Thought*:
{thought_str}
*Changed States*
{str(decide_shot_dict['past_states_transferred'])}
*States Need To Be Transferred*:
{decide_shot_dict["states_transferred"]}
*Output*:
```json
{output_str}
```
"""
        st_decide_shot_str += "\n\n"
        i+=1
    st_decide_shot_str = st_decide_shot_str.rstrip(st_decide_shot_str[-1])
    
    # Generate action_prompt
    prompts = f"""{StateTransferSystemPrompt} 

### Task Description
Based on your understanding of the current world state, the agent task, and semantics of the given action, your task is to simulate the execution of the given action and predict the transition of the designated world state after the action happens. You need to consider the attributes of agent, objects, world environment, as well as the complex intersections of their relationships. Consider the immediate and potential future consequences of each action iteratively, which must be realistic and meet real-world physical laws.

### Input Description
I will give you 
(1) the current world state (denoted as *Current States*) 
(2) the detailed description of the current world state (denoted as *Current States Description*). Specifically, we use a nested list in the state of the 'content' to show the affliation relationshiop of objects. For example. '[]' denotes nothing included in the object, [['bowl']] denotes a bowl included in the object, [['fruit_tray',['apple']]] denotes a fruit_tray with an apple inside includes in the object, [['fruit_tray',['apple']], ['knife']] denotes the object has a fruit_tray with apple inside and a knife.
(3) the detailed information of the action (denoted as *Action*)
(4) the complete thought about the action and its effects on the current states (denoted as *Thought*).
(5) the states have been changed after this action being executed (denoted as *Changed States*). You Do not need to change these states!
(6) the one state you need to change after this action is executed (denoted as *States To Be Transferred*)

### Output Rules
1. You need to output the new state of '{state_transferred}' based on the information in *Thought*.
2. The response should be output in the standard JSON format as shown in the example below.

***** Example *****
{st_decide_shot_str}
***** Example Ends *****

*Current States*:
{current_states_str}
*Current States Description*:
{states_description}
*Action*:
{instance_name}:{action_description_dict["description"]}
*Thought*:
{thought}
*Changed States*
{past_states_transferred_action}
*States Need To Be Transferred*:
{state_transferred}
*Output*:
"""
    return prompts


def checkDecideRespST(response, prompts, state_transferred, sc, state_manager, logger, max_check_iter):
    iter = 0
    check_pass_tag = False
    history = ""
    
    while (iter < max_check_iter):
        logger.info(f"{iter}-th Transfer Response Check")
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
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
            continue
        
        
        key_error_tag, key_check_response = decide_st_key_check(out_dict, state_transferred, logger)
        if key_error_tag:
            logger.info(f"{str(iter)}-th iter Fail. In Transfer Key Check")
            print(f"{str(iter)}-th iter Fail. In Transfer Key Check")
            logger.info(f"{key_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                key_check_response, 
                                                response, 
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
            continue
        
        
        content_error_tag, content_check_response = decide_st_content_check(out_dict,  state_transferred, logger)
        if content_error_tag:
            logger.info(f"{str(iter)}-th iter Fail. In Transfer Value Check.")
            print(f"{str(iter)}-th iter Fail. In Transfer Value Check.")
            logger.info(f"{content_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                content_check_response, 
                                                response, 
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
            continue

        
        code_error_tag, code_check_response = decide_st_code_check(out_dict, state_manager, logger)
        if code_error_tag:
            logger.info(f"{str(iter)}-th iter Fail. In Code Check.")
            print(f"{str(iter)}-th iter Fail. In Code Check.")
            logger.info(f"{code_check_response}\n")
            history, iter, response = sc.llm_correct(history, 
                                                iter, 
                                                code_check_response, 
                                                response, 
                                                prompts)
            logger.info(f"correct_response:\n{response}\n")
        else:
            check_pass_tag = True
            #self.logger.info("Pass Action Responses Checks")
            break
        
    assert check_pass_tag
    
    return out_dict


