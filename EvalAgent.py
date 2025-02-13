

from utils import json_extract
import os
from utils import read_jsonfile
from LLMTool import LLMTool
from check.syntax_checker_rule import (json_valid_check)
from SelfCorrect import SelfCorrect

class EvalAgent:

    def __init__(self, args, log_path_bt, logger):
                
        self.eval_shot_lst = read_jsonfile(os.path.join(args.shot_path_prefix, "eval_shot.json"))

        self.max_check_iter = args.max_check_iter
        self.llm_instance = LLMTool(args)
        self.logger = logger
        self.sc = SelfCorrect(self.llm_instance, logger)
               
    def generate_eval(self, bt_task, action_node_des, initial_states, end_states, action_lst):
        

        # Generate Prompt
        eval_prompt = self.get_eval_prompts(bt_task, action_node_des, initial_states, end_states, action_lst)
        self.logger.info(f"eval_prompt:\n{eval_prompt}\n")
        
        # Call llm
        eval_response = self.llm_instance.query_llm(eval_prompt)
        self.logger.info(f"eval_response:\n{eval_response}\n")

        eval_reponse_aftercheck = self.eval_response_check(eval_response, eval_prompt, self.max_check_iter)
        self.logger.info(f"eval_reponse_aftercheck:\n{eval_reponse_aftercheck}\n")
        
        return eval_reponse_aftercheck


    def get_eval_prompts(self, bt_task, action_node_des, initial_states, end_states, action_lst):
        
        eval_shot_str = ""
        for eval_shot in self.eval_shot_lst:
            
            agent_task_shot = eval_shot['agent_task']
            initial_states_shot = eval_shot['initial_states']
            action_description_shot = eval_shot['action_description']
            action_description_str_shot = ""
            i = 0
            for action in action_description_shot:
                action_description_str_shot += f"{str(i)}. {action}:{action_description_shot[action]}\n"
                i+=1
            current_states_shot = eval_shot['end_states']
            output_shot = eval_shot['output']
            eval_shot_str+=f"""
*Agent Task*: 
{agent_task_shot}
*Initial States*:
{initial_states_shot}
*Actions Sequence*:
{action_description_str_shot}
*End States*:
{current_states_shot}
*Output*:
{str(output_shot)}

"""
        action_description_str = ""
        i = 0
        for i in range(len(action_lst)):
            action = action_lst[i]
            description = action_node_des[action]["description"]
            action_description_str += f"{str(i)}. {action}:{description}\n"
            
        eval_prompt = f"""You are an evaluator to evaluate whether the task is completed based on the provided task descriptions and current world states.

### Task Description
Your task is to evaluate whether the agent task (or robot task) is completed based on the provided task descriptions, initial world states, a series of actions that have been carried out in sequence, and end world states. Specifically, you can only output 'success' or 'failure' to represent whether the task is completed or not.
Please give the reason why the task is failed or success. The reason should include two parts. In the first part, please use your world knowledge to analyze and summarize the keys to complete the agent task. This part should begin with "We think the key to complete the task is that" followed by your summarization of the key to completing the task.  In the second part, based on the given sequence of actions, end world states, and your summarized key to completing the task, you need to determine whether the task is completed and provide the reason.
The response should be output in JSON format as shown in the example below, which should begin with ```json and ends with ```.

### I will give you 
(1) the agent task in detail (denoted as *Agent Task*)
(2) the initial and end world states (denoted as *Initial States* and *End States*, respectively). Specifically, we use a nested list in the state of the 'content' to show the affliation relationshiop of objects. For example. '[]' denotes nothing included in the object, [['bowl']] denotes a bowl included in the object, [['fruit_tray',['apple']]] denotes a fruit_tray with an apple inside includes in the object, [['fruit_tray',['apple']], ['knife']] denotes the object has a fruit_tray with apple inside and a knife.
(3) the successfully executed actions (denoted as *Actions Sequence*)
(4) the detailed information of the condition needed to be checked (denoted as *Condition*)

***** Example *****
{eval_shot_str}
***** Example Ends *****

Here is the task that you need to evaluate whether it is completed.

*Agent Task*:
{bt_task}
*Initial States*:
{initial_states}
*Actions Sequence*:
{action_description_str}
*Ends States*:
{end_states}
*Output*:
"""
        return eval_prompt

    
    def eval_response_check(self, response, prompts, check_iter):
        
        iter = 0
        check_pass_tag = False
        history = ""

        while (iter < check_iter):
            self.logger.info(f"??????? {iter}-th Check ???????")
            json_extraction_lst = json_extract(response)

            
            out_dict, json_check_error_tag, json_check_response = json_valid_check(json_extraction_lst, response)
            
            if json_check_error_tag: 
                self.logger.info(f"Json_check_response:\n{json_check_response}\n")
                self.logger.info(f"{str(iter)}-th iter Fail. In JSON Format Check")
                history, iter, response = self.sc.llm_correct(history, 
                                                    iter, 
                                                    json_check_response, 
                                                    response, 
                                                    prompts
                                                    )
                continue

            key_error_tag, key_check_response = self.eval_out_key_check(out_dict)
            
            if key_error_tag:
                self.logger.info(f"key_check_response:\n{key_check_response}\n")
                self.logger.info(f"{str(iter)}-th iter Fail. In Key Check")
                history, iter, response = self.sc.llm_correct(history, 
                                                    iter, 
                                                    key_check_response, 
                                                    response, 
                                                    prompts)
                continue

            
            content_error_tag, content_check_response = self.eval_out_key_content_check(out_dict)
            
            if content_error_tag:
                self.logger.info(f"content_check_response:\n{content_check_response}\n")
                self.logger.info(f"{str(iter)}-th iter Fail. In Key Content Check.")
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
        

        return out_dict
    


    def eval_out_key_check(self, out_dict):
        
        
        key_lst = ["eval", "reason"]
        error_tag = False
        check_response = ""
        
        if len(out_dict) != len(key_lst):
            error_tag = True
            check_response += f"ERROR: the keys in your json response are incorrect. "
            self.logger.info(f"true_key_lst={key_lst}")
            self.logger.info(f"generate_key_lst={[key for key in out_dict]}")
            
        for key in key_lst:
            if key not in out_dict:
                error_tag = True
                check_response += f"ERROR: the key '{key}' is not correct and it should be one of in {key_lst}. "
                self.logger.info(f"true_key_lst={key_lst}")
                self.logger.info(f"generate_key_lst={[key for key in out_dict]}")
        
        return error_tag, check_response

    def eval_out_key_content_check(self, out_dict):
        
        error_tag = False
        check_response = ""
        
        
        if out_dict["eval"] not in ['success', 'failure']:
            error_tag = True
            check_response += f"ERROR: the value '{out_dict['eval']}' of the key 'eval' is incorrect. "
        
       
        return error_tag, check_response