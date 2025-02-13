"""
Implementing various py trees behaviors
"""

from py_trees.behaviour import Behaviour
from utils import blackboard_update, get_states_from_blackboard,get_description_from_blackboard


class Condition_Behavior(Behaviour):
    """
    Condition Node
    """
    def __init__(self, name, emulator, blackboard, node_str, logger):
        self.state = None
        self.condition_name = name
        self.condition_des = node_str
        self.emulator = emulator
        self.blackboard = blackboard
        self.logger = logger
        super(Condition_Behavior, self).__init__(name)

    def update(self):
        
        current_states = get_states_from_blackboard(self.blackboard)
        states_description = get_description_from_blackboard(self.blackboard)
        
        self.state = self.emulator.execute_condition_node(self.condition_name, 
                                                          self.condition_des, 
                                                          current_states, 
                                                          states_description)

        #self.logger.info("Node state "+str(self.state))
        # print("Node state "+str(self.state))
        self.logger.info(f"\nNode state: {str(self.state)}\n")
        
        return self.state


class Action_Behavior(Behaviour):
    """
    Action Node
    """
    def __init__(self, name, instance_name, action_description_dict, emulator, blackboard, logger):
        
        self.state = None
        self.action_name = name
        self.instance_name = instance_name
        self.action_description_dict = action_description_dict
        self.emulator = emulator
        self.blackboard = blackboard
        self.logger = logger
        
        super(Action_Behavior, self).__init__(name)
        

    def update(self):
        
        
            
        current_states = get_states_from_blackboard(self.blackboard)
        states_description = get_description_from_blackboard(self.blackboard)
        
        self.state, state_transition = self.emulator.execute_action_node(self.action_name, 
                                                                         self.instance_name, 
                                                                         self.action_description_dict, 
                                                                         current_states,
                                                                         states_description)
        
        self.blackboard = blackboard_update(state_transition, self.blackboard)

        self.logger.info(f"\nNode state: {str(self.state)}\n")
        
        return self.state
