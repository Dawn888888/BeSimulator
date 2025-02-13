from utils import write_to_json, json_extract, write_to_txt
import os
from utils import read_jsonfile
from LLMTool import LLMTool
from check.syntax_checker_rule import json_valid_check,is_dict_dict
from SelfCorrect import SelfCorrect


class SceneGenAgent:

    def __init__(self, args, bt_task, action_node_des, condition_node_des, logger=None):
                
        self.shot_path = os.path.join(args.shot_path_prefix, "scene_shot.json")
        self.scene_shot_list = read_jsonfile(self.shot_path)

        self.max_check_iter = args.max_check_iter
        
        self.bt_task = bt_task
        self.action_node_des = action_node_des 
        self.condition_node_des = condition_node_des
        self.llm_instance = LLMTool(args)
        
        self.sc = SelfCorrect("", self.llm_instance, logger)
        
        
    def generate_scene(self):

        # Generate Prompt
        scene_prompt = self.get_scene_prompts() 
        # Call llm
        scene_response = self.llm_instance.query_llm(scene_prompt)
        # print("scene_response:\n")
        # print(scene_response)
        # scene_dict = eval(json_extract(scene_response)[0],{"true":True,"false":False,"null":None})
        
        # write_to_json(self.response_path, 
        #         eval(json_extract(scene_response)[0],{"true":True,"false":False,"null":None}))
        
        # Iterative check
        scene_reponse_aftercheck, state_description = self.scene_response_check(scene_response, 
                                                        scene_prompt,
                                                        self.max_check_iter)

        return scene_reponse_aftercheck, state_description


    def get_scene_prompts(self):
        
        action_node_str = str(self.action_node_des)
        condition_node_str = str(self.condition_node_des)

        
        print("keyinprompt:\n")
        print("task=",self.bt_task)
        print("action-space=\n")
        print(action_node_str)
        
        # Generate few-shots
        scene_shot_str = ""
        for scene_shot_dict in self.scene_shot_list:
            task_str = scene_shot_dict["task"]
            action_node = str(scene_shot_dict["action_node"])
            condition_node = str(scene_shot_dict["condition_node"])
            scene_dict_str = str(scene_shot_dict["scene"])

            scene_shot_str += f"""*Agent Task*:
{task_str}
*Action Space*:
{action_node}
*Conditions*:
{condition_node}
*Output*:
```json
{scene_dict_str}
```
"""        
            scene_shot_str += "\n\n"
        scene_shot_str = scene_shot_str.rstrip(scene_shot_str[-1])
        scene_prompt = f"""You are a scene generation engine that has excellent reasoning and scene imagination abilities. Agent will execute a task, and you need to set the initial scenario configuration.

### Input Description
I will give you 
(1) the agent task in detail (denoted as *Agent Task*)
(2) the action space could used in the task (denoted as *Action Space*)
(3) the condition check agent will make in the task (denoted as *Conditions*)

###Task Description
Based on your understanding of agent's task, action space and check abilities, your task is to design the initial task scene. The task scene consists of the following four parts.

1. The first part is agent information. The agents are the main roles in scenes and they aim to complete the given task. The "agents" information is represented by a dictionary, with each dictionary representing an agent. For each agent, you should generate a dictionary. Its name is the unique identifier. It includes 'type', 'position', 'size', 'setting', and other necessary properties. 'type' information is the type of the entity, 'size' information is the size of the entity using 1 number in meters which should match real everyday entities. E.g., an apple is of scale 0.08m. You can think of the 'size' information to be the longest dimension of the entity, 'position' information is the 3D coordinates of the entity which describes the world coordinate system. The x-axis represents the east-west direction, the y-axis represents the north-south direction, and the z-axis represents the vertical direction away from the ground. 'setting' is the requirement of the corresponding agent.
2. The second part is "object" that includes other entities in the scene. The "object" information is also represented by a dictionary, with each dictionary representing an object. For each object, you should generate a dictionary that includes 'type', 'position', 'size', and other necessary properties of the object.
3. The third part is "relationship" information, including the relationship between objects, agents, agent-object, agent-environment, object-environment. The "relationship" information is represented by a dictionary. To generate this part, you need to understand agent's check abilities deeply and think about the relationship in scenes.
For each pair of the relationship, you should output their absolute and relative relationships. For example, according the relationship between robot and cutboard, you should give the distance_robot_to_cutboard=7.2 and robot_hold_cutboard=False.
4. The fourth part is "environment" information which is related to task setting, such as terrain, weather and goal position. The "environment" information is represented by a dictionary. 
5. The fifth part is "state_description" information, which is a dictionary that describes the scene information that you generate.
6. There should be a certain distance between different objects and agents.
7. Very importantly, you should generate comprehensive, realistic and task related scene information. And be careful not to be redundant. This will help build the task in a simulator and observe & evaluate the process of Agent performs the task.
8. Specifically, we use a nested list in the state of the 'content' to show the affliation relationshiop of objects. For example. '[]' denotes nothing included in the object, [['bowl']] denotes a bowl included in the object, [['fruit_tray',['apple']]] denotes a fruit_tray with an apple inside includes in the object, [['fruit_tray',['apple']], ['knife']] denotes the object has a fruit_tray with apple inside and a knife.
9. The generated scene should be output in the standard JSON format as shown in the example below.

***** Example *****
{scene_shot_str}
***** Example Ends *****

Here is the task that you need to generated scenes according to it.
*Agent Task*: 
{self.bt_task}
*Action Space*:
{action_node_str}
*Conditions*:
{condition_node_str}
*Output*:
"""

        return scene_prompt

    
    def scene_response_check(self, response, prompts, check_iter):
        
        iter = 0
        check_pass_tag = False
        history = ""

        while (iter < check_iter):
            json_extraction_lst = json_extract(response)

            
            out_dict, json_check_error_tag, json_check_response = json_valid_check(json_extraction_lst, response)
            
            if json_check_error_tag: 
                print(f"{str(iter)}-th iter Fail. In JSON Format Check")
                history, iter, response = self.sc.llm_correct(history, 
                                                    iter, 
                                                    json_check_response, 
                                                    response, 
                                                    prompts
                                                    )
                continue

            
            key_error_tag, key_check_response = self.scene_out_key_check(out_dict)
            
            if key_error_tag:
                print(f"{str(iter)}-th iter Fail. In Key Check")
                print(key_check_response)
                history, iter, response = self.sc.llm_correct(history, 
                                                    iter, 
                                                    key_check_response, 
                                                    response, 
                                                    prompts)
                continue

            
            content_error_tag, content_check_response = self.scene_out_key_content_check(out_dict)
            
            if content_error_tag:
                print(f"{str(iter)}-th iter Fail. In Key Content Check.")
                print(content_check_response)
                history, iter, response = self.sc.llm_correct(history, 
                                                    iter, 
                                                    content_check_response, 
                                                    response, 
                                                    prompts)
            else:
                check_pass_tag = True
                #print("Pass Scene Checks")
                break

        assert check_pass_tag
        
        state_description = out_dict["state_description"]
        del out_dict["state_description"]

        return out_dict, state_description
    
    
    def scene_out_key_check(self, out_dict):
        
        
        key_lst = ["agents", "objects", "relationship", "environment", "state_description"]
        error_tag = False
        check_response = ""
        
        if len(out_dict) != len(key_lst):
            error_tag = True
            check_response += f"ERROR: the number of keys in your response is incorrect. "
        for key in key_lst:
            if key not in out_dict:
                error_tag = True
                check_response += f"ERROR: the key {key} does not exist in your response. "
                
        return error_tag, check_response


    def scene_out_key_content_check(self, out_dict):
        
        
        error_tag = False
        check_response = ""
        
        if not is_dict_dict(out_dict["agents"]):
            error_tag = True
            check_response += f"ERROR: the format of the value of 'agent' is not correct."
        if not is_dict_dict(out_dict["objects"]):
            error_tag = True
            check_response += f"ERROR: the format of the value of 'objects' is not correct."
        if not isinstance(out_dict["relationship"], dict):
            error_tag = True
            check_response += f"ERROR: the value of 'relationship' is not a dictionary."
        if not isinstance(out_dict["environment"], dict):
            error_tag = True
            check_response += f"ERROR: the value of 'environment' is not a dictionary."
        if not isinstance(out_dict["state_description"], dict):
            error_tag = True
            check_response += f"ERROR: the value of 'state_description' is not a dictionary."
        
        return error_tag, check_response
