import os
import py_trees
import creat_bt
from py_trees.blackboard import Client
from EmulatorAgent import EmulatorAgent
from EvalAgent import EvalAgent
import argparse
from utils import read_jsonfile, get_states_from_blackboard,get_logger,write_to_json
import numpy as np
from py_trees.behaviour import common
import random
random.seed(2024)

def create_blackboard(blackboard_item, agents, objects, relationship, environment, state_description):

    # create blackboard client and set scene information onto the blackboard
    blackboard = Client(name="Tester")

    for item in blackboard_item:
        blackboard.register_key(key=item, access=py_trees.common.Access.WRITE)

    # write blackboard
    blackboard.agents = agents
    blackboard.objects = objects
    blackboard.relationship = relationship
    blackboard.environment = environment
    blackboard.state_description = state_description
   
    return blackboard


def main(args):
    
    
    scene_file_path = os.path.join("scenes", 
                                   f"scene_{str(args.run_task_id)}.json")
    
   
    
    des_file_path = os.path.join(os.path.join(args.data_path_prefix, 
                                              args.category, 
                                              "des"), 
                                 str(args.run_task_id) +".json")
    
    bt_des = read_jsonfile(des_file_path)
    
    xml_file_path = os.path.join(os.path.join(args.data_path_prefix, 
                                              args.category, 
                                              "xml"), 
                                 str(args.run_task_id)+".xml")
    
    
    log_model_path = os.path.join(args.log_path_prefix,
                                  args.llm_model, 
                                  args.category)
     
    if not os.path.exists(log_model_path):
        os.makedirs(log_model_path)
    
  
    bt_task = bt_des["bt_task"]
    action_node_des = bt_des["action_node"]
    condition_node_des = bt_des["condition_node"]
    bt_name = bt_des['name']
    
    log_file_path = os.path.join(log_model_path, f'{str(bt_des["id"])}_log.log')
    logger = get_logger(bt_name, log_file_path)


    logger.info(f"---ID: {str(bt_des['id'])}, Task:{bt_name}---")
    print(f"---ID: {str(bt_des['id'])}, Task:{bt_name}---")
    
    scene_lst = read_jsonfile(scene_file_path)
    # success:0, checkerror:1, IncorrectLogic:2, Unreachable, 3
    count = np.zeros(4)
    endstates_lst = []
    
    scene = scene_lst[0]
    
    agents = scene["agents"]
    objects = scene["objects"]
    relationship = scene["relationship"]
    environment = scene["environment"]
    state_description = scene["state_description"]
    state_type = scene["state_type"]
    # Generate blackboard
    blackboard_item = ["agents", "objects", "relationship", "environment", "state_description"]
    blackboard = create_blackboard(blackboard_item, agents, objects, relationship, environment, state_description)
    
    
    initial_states = get_states_from_blackboard(blackboard)
    # Generate emulator
    emulator = EmulatorAgent(args, bt_task, agents, objects, relationship, environment, state_description, state_type, logger)

    # Parse and execute behavior tree
    root = creat_bt.xml_loader(args, xml_file_path, emulator, blackboard, action_node_des, condition_node_des, logger)
    if root == "XML_ERROR":
        logger.error("XML_ERROR")
        print("XML_ERROR")
    else:
        tree = py_trees.trees.BehaviourTree(root)

        check_error = False
        
        try:
            tree.tick()
        except AssertionError as e:
            print(f"!!!!!!!!!!!!!!!!!Exception:{e}")
            logger.error(f"!!!!!!!!!!!!!!!!!Exception:{e}")
            check_error = True

        #tree.tick()
        
        logger.info(f"-----------RootStatus={tree.root.status}-----------")
        print(f"-----------RootStatus={tree.root.status}-----------")
        
        if check_error:
            count[1] += 1
            logger.info(f"\ncheck_error={check_error}, failure_reason=Interative Check Error\n")
            print(f"\ncheck_error={check_error},  failure_reason=Interative Check Error\n")

        else:
            if tree.root.status == common.Status.FAILURE:
                count[2] += 1
                logger.info(f"\ncheck_error={check_error}, failure_reason=Incorrect Action Logic\n")
                print(f"\ncheck_error={check_error}, failure_reason=Incorrect Action Logic\n")
            
            elif tree.root.status == common.Status.SUCCESS:
                logger.info("\n!!!!! in Eval Agent!!!!\n")
                print("\n!!!!! in Eval Agent!!!!\n")
                
                evalagent = EvalAgent(args, log_file_path, logger)
                eval_response = evalagent.generate_eval(bt_task, action_node_des, initial_states, 
                                                        get_states_from_blackboard(blackboard), 
                                                        emulator.action_lst)
                eval_tag = eval_response['eval']
                if eval_tag == 'success':
                    count[0] += 1
                    logger.info(f"\ncheck_error={check_error}, eval_tag={eval_tag}, success_reason={eval_response} \n")
                    print(f"eval_tag={eval_tag}, success_reason={eval_response}\n")
                
                elif eval_tag == 'failure':
                    count[3] += 1
                    logger.info(f"\ncheck_error={check_error}, eval_tag={eval_tag}, failure_reason={eval_response}\n")
                    print(f"\ncheck_error={check_error}, eval_tag={eval_tag}, failure_reason={eval_response}\n")

                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
            
        end_state = {"agents":emulator.sm.agents, 
                        "objects":emulator.sm.objects,
                        "relationship":emulator.sm.relationship,
                        "environment":emulator.sm.environment}
        endstates_lst.append(end_state)
        
        logger.info(f"END STATE:\n{emulator.sm.get_world_states()}")
        
        logger.info(f"=======================================")
        print(f"=======================================")
            
        logger.info(f"\n!!!!{args.llm_model} on task {args.run_task_id}!!!!\n")
        logger.info("\ncount=")
        logger.info(count)
        
        prop = count / np.sum(count)
        logger.info("\nproportion=")
        logger.info(prop)
        
        np.savetxt(os.path.join(log_model_path, f"{str(args.run_task_id)}_result.txt"), prop)
        write_to_json(os.path.join(log_model_path, f"{str(args.run_task_id)}_endstates.json"), endstates_lst)
    


if __name__ == '__main__':
    
    arg_parser = argparse.ArgumentParser(prog="arguments")
    
    arg_parser.add_argument('--llm_model', type=str, default="deepseek-chat")
    # good, badlogic, unreachable
    arg_parser.add_argument('--category', type=str, default="good")
    arg_parser.add_argument('--log_path_prefix', type=str, default="./result")
    arg_parser.add_argument('--shot_path_prefix', type=str, default="./shots")
    arg_parser.add_argument('--data_path_prefix', type=str, default="./BTSIMBENCH")
    arg_parser.add_argument('--run_task_id', type=int, default=1)
    arg_parser.add_argument('--max_check_iter', type=int, default=5)
    arg_parser.add_argument('--emulate_iter', type=int, default=1)
    arg_parser.add_argument('--max_ticks', type=int, default=1)
    parsed_args = arg_parser.parse_args()


    main(parsed_args)
