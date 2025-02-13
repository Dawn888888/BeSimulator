import os
import argparse
from tqdm import tqdm
from SceneGenAgent import SceneGenAgent
from utils import read_jsonfile, parse_scene
from utils import write_to_json


def main(args):

    scene_path = os.path.join(args.data_path_prefix, "scenes")
    if not os.path.exists(scene_path):
        os.makedirs(scene_path)

    des_folder_path = os.path.join(args.data_path_prefix, args.category, "des")
    
    des_file_path = os.path.join(des_folder_path, str(args.run_task_id)+".json")
    bt_des = read_jsonfile(des_file_path)    
    print(f"loading {des_file_path}")
    
    idx = bt_des["id"]
    bt_task = bt_des["bt_task"]
    action_node_des = bt_des["action_node"]
    condition_node_des = bt_des["condition_node"]
    
    # Generate Scene
    scene_lst = []
    for i in tqdm(range(args.scene_num)):
        scene_agent = SceneGenAgent(args, bt_task, action_node_des, condition_node_des)
        # Generate and parse emulation scene
        scene_state, state_description = scene_agent.generate_scene()
        agents, objects, relationship, environment = parse_scene(scene_state)
        
        scene = {"agents":agents, 
                 "objects":objects, 
                 "relationship":relationship,
                 "environment":environment, 
                 "state_description":state_description}
        
        scene_lst.append(scene)
    write_to_json(scene_path + "/" + f"scene_{str(idx)}.json", scene_lst)

if __name__ == '__main__':
    
    arg_parser = argparse.ArgumentParser(prog="arguments")
    arg_parser.add_argument('--llm_model', type=str, default="gpt-4")
    arg_parser.add_argument('--shot_path_prefix', type=str, default="./shots")
    arg_parser.add_argument('--data_path_prefix', type=str, default="./BTGenDataset")
    arg_parser.add_argument('--category', type=str, default="good")
    arg_parser.add_argument('--run_task_id', type=int, default=0)
    arg_parser.add_argument('--max_check_iter', type=int, default=10)
    arg_parser.add_argument('--scene_num', type=int, default=1)
    
    parsed_args = arg_parser.parse_args()


    main(parsed_args)