import py_trees as pt
from utils import read_jsonfile,python_extract, string_to_bool, exec_code_string
import os
from LLMTool import LLMTool
from ConditionComponent import (getThinkPrompCM,
                                checkThinkRespCM,
                                getDecidePrompCM_NL,
                                getDecidePrompCM_Code,
                                checkDecideRespCM)

from ActionComponent import (getThinkPrompAE, 
                             getDecidePrompAE_NL, 
                             getDecidePrompAE_Code, 
                             getThinkPrompST, 
                             getDecidePrompST,
                             checkThinkRespAE,
                             checkDecideRespAE,
                             checkThinkRespST,
                             checkDecideRespST)

from SelfCorrect import SelfCorrect
from StateManager import StateManager



class EmulatorAgent:
    '''
    Behaviour Tree Emulator
    '''
    def __init__(self, 
                 args, 
                 bt_task, 
                 agents, 
                 objects, 
                 relationship, 
                 environment, 
                 state_description, 
                 state_type, 
                 logger):
        
        self.bt_task = bt_task
        self.llm_model = args.llm_model
        self.max_check_iter = args.max_check_iter

        self.llm_instance = LLMTool(args)
        self.logger = logger
        
        self.sc = SelfCorrect(self.llm_instance, self.logger)

        self.cm_think_shot_lst = read_jsonfile(os.path.join(args.shot_path_prefix, 
                                                                   "cm_think_shot.json"))
        self.cm_decide_code_shot_lst = read_jsonfile(os.path.join(args.shot_path_prefix, 
                                                                    "cm_decide_code_shot.json"))

        self.cm_decide_nl_shot_lst = read_jsonfile(os.path.join(args.shot_path_prefix, 
                                                                    "cm_decide_nl_shot.json"))
        
        self.ae_think_shot_lst = read_jsonfile(os.path.join(args.shot_path_prefix, 
                                                                   "ae_think_shot.json"))
        self.ae_decide_code_shot_lst = read_jsonfile(os.path.join(args.shot_path_prefix, 
                                                                    "ae_decide_code_shot.json"))

        self.ae_decide_nl_shot_lst = read_jsonfile(os.path.join(args.shot_path_prefix, 
                                                                    "ae_decide_nl_shot.json"))
        
        
        self.st_think_shot_lst = read_jsonfile(os.path.join(args.shot_path_prefix,
                                                            "st_think_shot.json"))
        self.st_decide_shot_lst = read_jsonfile(os.path.join(args.shot_path_prefix,
                                                            "st_decide_shot.json"))
        
        
        self.sm = StateManager(agents, objects, relationship, environment, state_description, state_type)
        
        self.action_lst = []
        
    def execute_condition_node(self, condition_name, condition_des, current_states, states_des):
        '''
        Emulate the execution of condition node
        '''
        self.logger.info(f"!!!!!!!!!!!!!!!!condition_name:{condition_name}!!!!!!!!!!!!!!!!")
        print(f"!!!!!!!!!!!!!!!!condition_name:{condition_name}!!!!!!!!!!!!!!!!")
        
        node_state = None
        
        # Condition node --- Think Stage

        # generate prompt
        self.logger.info(f"curr_world_states:\n{current_states}")        
        print(f"*****In Think_CM of {condition_name}*****")
        self.logger.info(f"***In Think_CM of {condition_name}***")
        
        thinkpromp_cm = getThinkPrompCM(current_states, states_des, condition_name, condition_des, self.cm_think_shot_lst)
        # self.logger.info(f"condition_prompts:\n{condition_prompts}")
        
        # call llm
        thinkresp_cm = self.llm_instance.query_llm(thinkpromp_cm)
        self.logger.info(f"Think_CM_response:\n{thinkresp_cm}\n")
        
        # Iterative check
        thinkresp_cm_check = checkThinkRespCM(thinkresp_cm, thinkpromp_cm, self.sc, self.sm, self.logger, self.max_check_iter)
        print(f"Think_CM_Core_States: {thinkresp_cm_check['corestates']}")
        self.logger.info(f"Think_CM_Core_States: {thinkresp_cm_check['corestates']}")
        
        core_states_lst = [state_level.split('-')[-1] for state_level in thinkresp_cm_check['corestates']]
        


        # Condition node --- Decide Stage

        if any('float' in self.sm.state_type[state] for state in core_states_lst):
            
            
            print(f"***In DecideCode_CM of {condition_name}***")
            self.logger.info(f"*****In DecideCode_CM of {condition_name}*****")
            
            decidepromp_cm = getDecidePrompCM_Code(current_states, 
                                                   states_des, 
                                                   condition_name, 
                                                   condition_des, 
                                                   thinkresp_cm_check,  
                                                   self.cm_decide_code_shot_lst)
            decideresp_cm = self.llm_instance.query_llm(decidepromp_cm)
            self.logger.info(f"Decide_CM_response:\n{decideresp_cm}\n")
            decideresp_cm_check = checkDecideRespCM(decideresp_cm, 
                                                    decidepromp_cm, 
                                                    "code_branch",
                                                    self.max_check_iter, 
                                                    self.sc, 
                                                    self.logger)
            self.logger.info(f"Decide_CM_check_response:\n{decideresp_cm_check}\n")            
            codes_lst = python_extract(decideresp_cm_check["code"])
            python_codes = codes_lst[0]

            namespace = {}
            exec(python_codes, namespace) 
            success = namespace.get("resp")
        
        
        else:
            
            print(f"***In DecideNL_CM of {condition_name}***")
            self.logger.info(f"***In DecideNL_CM of {condition_name}***")
            
            
            decidepromp_cm = getDecidePrompCM_NL(current_states, 
                                                 states_des, 
                                                 condition_name, 
                                                 condition_des, 
                                                 thinkresp_cm_check,
                                                 self.cm_decide_nl_shot_lst)
            # self.logger.info(f"condition_prompts:\n{condition_prompts}")
            decideresp_cm = self.llm_instance.query_llm(decidepromp_cm)
            self.logger.info(f"Decide_CM_response:\n{decideresp_cm}\n")
            decideresp_cm_check = checkDecideRespCM(decideresp_cm, 
                                                    decidepromp_cm, 
                                                    "nl_branch",
                                                    self.max_check_iter, 
                                                    self.sc, 
                                                    self.logger)
            self.logger.info(f"Decide_CM_check_response:\n{decideresp_cm_check}\n")   
            success = decideresp_cm_check['result']
            
        print(f"llm_response={success}")
        # write_to_json(self.aftercheck_response_output_path, condition_reponse_aftercheck)
        self.logger.info(f"condition_check:\n{success}\n")
        if success:
            node_state =  pt.common.Status.SUCCESS
        else:
            node_state =  pt.common.Status.FAILURE

       
        return node_state

    def execute_action_node(self, action_name, instance_name, action_description_dict, current_states, states_description):
        '''
        Emulate the execution of action node
        '''
        self.logger.info(f"!!!!!!!!!!!!!!!!action_name:{action_name}!!!!!!!!!!!!!!!!")
        print(f"!!!!!!!!!!!!!!!!action_name:{action_name}!!!!!!!!!!!!!!!!")
        node_state = None
        

        # Think in Action Execuate

        # generate prompt
        print(f"*****In Think_AE of {action_name}*****")
        self.logger.info(f"*****In Think_AE of {action_name}*****")
        self.logger.info(f"curr_world_states:\n{current_states}")
        thinkpromp_ae = getThinkPrompAE(current_states, 
                                         states_description, 
                                         self.bt_task, 
                                         action_description_dict, 
                                         instance_name,
                                         self.ae_think_shot_lst)
        #self.logger.info(f"Think_AE_prompts:\n{thinkpromp_ae}")
        
        # call llm
        thinkresp_ae = self.llm_instance.query_llm(thinkpromp_ae)
        self.logger.info(f"Think_AE_response:\n{thinkresp_ae}\n")
        
        # iterative check
        thinkresp_ae_check = checkThinkRespAE(thinkresp_ae,
                                              thinkpromp_ae,
                                              self.max_check_iter,
                                              self.sm, 
                                              self.sc, 
                                              self.logger)
        
        self.logger.info(f"\nThink_AE_check_response:\n{thinkresp_ae_check}")
        
        # print("CoreStatesinThinking:",thinkresp_ae_check['corestates'])
        self.logger.info(f"Think_AE_Core_States:\n{thinkresp_ae_check['corestates']}\n")
        print(f"Think_AE_core-states:{thinkresp_ae_check['corestates']}")
        self.logger.info(f"Think_AE_Core_States_Successtag:\n{thinkresp_ae_check['corestates_successtag']}\n")
        print(f"Think_AE_core-states_Successtag:{thinkresp_ae_check['corestates_successtag']}")



        # Decide in Action Execuate


        condition_lst = []
        for precondition in thinkresp_ae_check['corestates']:
            ae_cond_corestates = thinkresp_ae_check['corestates'][precondition]
            expect_result = string_to_bool(thinkresp_ae_check['corestates_successtag'][precondition])
            states_lst = [state_level.split('-')[-1] for state_level in ae_cond_corestates]
        
            if any('float' in self.sm.state_type[state] for state in states_lst):
                
                
                print(f"*****In DecideCode_AE '{precondition}' of {action_name}*****")
                self.logger.info(f"*****In DecideCode_AE '{precondition}' of {action_name}*****")
                
                decidepromp_ae = getDecidePrompAE_Code(current_states, 
                                                    states_description, 
                                                    self.bt_task,
                                                    action_description_dict, 
                                                    instance_name,
                                                    precondition,
                                                    ae_cond_corestates,
                                                    self.ae_decide_code_shot_lst)
                
                decideresp_ae = self.llm_instance.query_llm(decidepromp_ae)
                self.logger.info(f"Decide_AE_response:\n{decideresp_ae}\n")
                
                decideresp_ae_check = checkDecideRespAE(decidepromp_ae, 
                                                        decideresp_ae,
                                                        {precondition:ae_cond_corestates}, 
                                                        "code_branch",
                                                        self.max_check_iter, 
                                                        self.sc, 
                                                        self.logger)
                
                self.logger.info(f"Decide_AE_check_response:\n{decideresp_ae_check}\n")            
                codes_lst = python_extract(decideresp_ae_check["code"])
                python_codes = codes_lst[0]

                namespace = {}
                exec(python_codes, namespace) 
                success = string_to_bool(namespace.get("resp"))

            else:
                
                print(f"*****In DecideNL_AE '{precondition}' of {action_name}*****")
                self.logger.info(f"*****In DecideNL_AE '{precondition}' of {action_name}*****")
                
                
                decidepromp_ae = getDecidePrompAE_NL(current_states, 
                                                    states_description, 
                                                    self.bt_task,
                                                    action_description_dict, 
                                                    instance_name,
                                                    precondition,
                                                    ae_cond_corestates,
                                                    self.ae_decide_nl_shot_lst)
                # self.logger.info(f"Decide_AE_prompts:\n{decidepromp_ae}")
                decideresp_ae = self.llm_instance.query_llm(decidepromp_ae)
                self.logger.info(f"Decide_AE_response:\n{decideresp_ae}\n")
                decideresp_ae_check = checkDecideRespAE(decidepromp_ae,
                                                        decideresp_ae,
                                                        {precondition:ae_cond_corestates}, 
                                                        "nl_branch",
                                                        self.max_check_iter, 
                                                        self.sc, 
                                                        self.logger)
                self.logger.info(f"\nDecide_AE_check_response:\n{decideresp_ae_check}")  
                success = string_to_bool(decideresp_ae_check['result'])
            
            if expect_result == success:
                print(f"action_precondition '{precondition}' is met?: True")
                self.logger.info(f"action_precondition '{precondition}' is met?: True\n")
                condition_lst.append(True)
            else:
                print(f"action_precondition '{precondition}' is met?: False")
                self.logger.info(f"action_precondition '{precondition}' is met?: False\n")
                condition_lst.append(False)
        


        # Think in State Transfer
            

        state_transition = {}
        if not all(condition_lst):
            self.logger.info(f"Action_Successfully_Executed:False\n")
            node_state =  pt.common.Status.FAILURE
        else:
            self.logger.info(f"Action_Successfully_Executed:True\n")
            node_state =  pt.common.Status.SUCCESS
                    
            print(f"*****In Think_ST Stage of {action_name}*****")
            self.logger.info(f"*****In Think_ST Stage of {action_name}*****")            
            self.logger.info(f"curr_world_states:\n{current_states}")
            
            # generate prompt
            thinkpromp_st = getThinkPrompST(current_states, 
                                            states_description, 
                                            self.bt_task, 
                                            action_description_dict, 
                                            instance_name,
                                            self.st_think_shot_lst)
            # self.logger.info(f"think_prompts:\n{think_prompts}")
            
            # call llm
            thinkresp_st = self.llm_instance.query_llm(thinkpromp_st)
            self.logger.info(f"Think_ST_response:\n{thinkresp_st}\n")

            # iterative check
            thinkresp_st_check = checkThinkRespST(thinkresp_st, 
                                                  thinkpromp_st,
                                                  self.sc, 
                                                  self.sm, 
                                                  self.logger,
                                                  self.max_check_iter)
            self.logger.info(f"\nThink_ST_check_response:\n{thinkresp_st_check}")
            
            # parse result and states transition 
            thought = thinkresp_st_check["thought"]
            states_transferred = thinkresp_st_check['states_transferred']
            
            
            print(f"Think_ST_Transfer_States:{states_transferred}")
            self.logger.info(f"Think_ST_Transfer_States:{states_transferred}\n")
            


            # Decide in State Transfer


            print(f"*****In Decide_ST of {action_name}*****")
            self.logger.info(f"*****In Decide_ST of {action_name}*****")

            if "None" not in states_transferred:
                past_states_transferred_action = []
                
                for state_transferred in states_transferred:
                    self.logger.info(f"Transferring {state_transferred}")
                    print(f"Transferring '{state_transferred}'")
                    
                    cur_world_states = self.sm.get_world_states()
                    cur_world_states_description = self.sm.get_states_description()
                    
                    # self.logger.info(f"cur_world_states=\n{cur_world_states}")
                    
                    decidepromp_st = getDecidePrompST(cur_world_states,
                                                      cur_world_states_description, 
                                                      self.bt_task, 
                                                      action_description_dict,
                                                      state_transferred,
                                                      thought, 
                                                      past_states_transferred_action,
                                                      instance_name,
                                                      self.st_decide_shot_lst)
                    
                    # self.logger.info(f"transfer_prompts:\n{transfer_prompts}\n")
                    
                    # Call llm
                    decideresp_st = self.llm_instance.query_llm(decidepromp_st)
                    self.logger.info(f"Decide_ST_response:\n{decideresp_st}\n")

                    # Iterative check
                    decideresp_st_check = checkDecideRespST(decideresp_st,
                                                            decidepromp_st,
                                                            state_transferred,
                                                            self.sc, 
                                                            self.sm, 
                                                            self.logger, 
                                                            self.max_check_iter)

                    self.logger.info(f"\nDecide_ST_check_response:\n{decideresp_st_check}")
                    print(f"llm_response:\nchanged_states:{decideresp_st_check}")
                    
                    state_transition = self.transfer(decideresp_st_check, state_transition)
                    
                    past_states_transferred_action.append(state_transferred)
                    
            self.action_lst.append(action_name)
        
        
        return node_state, state_transition
    
    
    def transfer(self, response, state_transition):
        '''
        Perform state transition
        '''
        
        
        if "agents" in response:
            agents = response["agents"]
            # agents
            if "agents" not in state_transition:
                state_transition["agents"] = {}
            for key_id, value_agent in agents.items():
                if key_id not in state_transition["agents"]:
                    state_transition["agents"][key_id] = {}
                for key, value in value_agent.items():
                    # deal with code
                    if isinstance(value, str) and value.startswith("###python"):
                        pass
                    #blackboard.agents[key_id][key] = value
                    self.sm.set(["agents", key_id, key], value)
                    state_transition["agents"][key_id][key] = value
                    self.logger.info(f"Update States: {key_id} {key} {value}")

        if "objects" in response:
            objects = response["objects"]
            # objects
            if "objects" not in state_transition:
                state_transition["objects"] = {}
            for key_id, value_object in objects.items():
                if key_id not in state_transition["objects"]:
                    state_transition["objects"][key_id] = {}
                for key, value in value_object.items():
                    # deal with code
                    if isinstance(value, str) and value.startswith("###python"):
                        pass
                    #blackboard.objects[key_id][key] = value
                    self.sm.set(["objects", key_id, key], value)
                    state_transition["objects"][key_id][key] = value
                    self.logger.info(f"Update States: {key_id} {key} {value}")
        
        if "relationship" in response:  
            relationship = response["relationship"]
            # relationship
            if "relationship" not in state_transition:
                state_transition["relationship"] = {}
            for key, value in relationship.items():
                # deal with code
                if isinstance(value, str) and value.startswith("###python"):
                    pass
                #blackboard.relationship[key] = value
                self.sm.set(["relationship", key], value)
                state_transition["relationship"][key] = value
                self.logger.info(f"Update States: {key} {value}")
        
        if "environment" in response:
            environment = response["environment"]
            # environment
            if "environment" not in state_transition:
                state_transition["environment"] = {}
            for key, value in environment.items():
                # deal with code
                if isinstance(value, str) and value.startswith("###python"):
                    pass
                #blackboard.environment[key] = value
                self.sm.set(["environment", key], value)
                state_transition["environment"][key] = value
                self.logger.info(f"Update States: {key} {value}")
        
        # -------------------
        
        if "agents" in response:
            agents = response["agents"]
            # agents     
            if "agents" not in state_transition:
                state_transition["agents"] = {}
            for key_id, value_agent in agents.items():
                if key_id not in state_transition["agents"]:
                    state_transition["agents"][key_id] = {}
                for key, value in value_agent.items():
                    # deal with code
                    if isinstance(value, str) and value.startswith("###python"):
                        value = exec_code_string(value, self.sm)
                        #blackboard.agents[key_id][key] = value
                        self.sm.set(["agents", key_id, key], value)
                        state_transition["agents"][key_id][key] = value
                        self.logger.info(f"Update States: {key_id} {key} {value}")

        if "objects" in response:
            objects = response["objects"]
            # objects
            if "objects" not in state_transition:
                state_transition["objects"] = {}
            for key_id, value_object in objects.items():
                if key_id not in state_transition["objects"]:
                    state_transition["objects"][key_id] = {}
                for key, value in value_object.items():
                    # deal with code
                    if isinstance(value, str) and value.startswith("###python"):
                        value = exec_code_string(value, self.sm)
                        #blackboard.objects[key_id][key] = value
                        self.sm.set(["objects", key_id, key], value)
                        state_transition["objects"][key_id][key] = value
                        self.logger.info(f"Update States: {key_id} {key} {value}")
        
        if "relationship" in response:  
            relationship = response["relationship"]
            # relationship
            if "relationship" not in state_transition:
                state_transition["relationship"] = {}
            for key, value in relationship.items():
                # deal with code
                if isinstance(value, str) and value.startswith("###python"):
                    value = exec_code_string(value, self.sm)
                    #blackboard.relationship[key] = value
                    self.sm.set(["relationship", key], value)
                    state_transition["relationship"][key] = value
                    self.logger.info(f"Update States: {key} {value}")
        
        if "environment" in response:
            environment = response["environment"]
            # environment
            if "environment" not in state_transition:
                state_transition["environment"] = {}
            for key, value in environment.items():
                # deal with code
                if isinstance(value, str) and value.startswith("###python"):
                    value = exec_code_string(value, self.sm)
                    #blackboard.environment[key] = value
                    self.sm.set(["environment", key], value)
                    state_transition["environment"][key] = value
                    self.logger.info(f"Update States: {key} {value}")
        
        return state_transition