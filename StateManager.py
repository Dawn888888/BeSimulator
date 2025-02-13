
class StateManager:
    '''
    World State Manager
    '''
    def __init__(self, agents, objects, relationship, environment, state_description, state_type):
        
        self.agents = agents
        self.objects = objects
        self.relationship = relationship
        self.environment = environment
        self.state_description = state_description
        self.state_type = state_type
        
        
    def get_world_states(self):
        '''
        Return the current world states, five parts
        '''
        states = f"""agents: {str(self.agents)}
objects: {str(self.objects)}
relationship: {str(self.relationship)}
environment: {str(self.environment)}"""
        return states

    def get_states_type(self):
        
        states_type = f"""states_type: {str(self.state_type)}"""
        
        return states_type
    
    def get_states_description(self):
        states_description = f"""state_description: {str(self.state_description)}"""
        return states_description
    
    def get(self, state_name):
        '''
        Query: get the current state of the world
        '''
        state = {}
        if state_name == "agents":
            state = self.agents
        elif state_name == "objects":
            state = self.objects
        elif state_name == "relationship":
            state = self.relationship
        elif state_name == "environment":
            state = self.environment
        elif state_name == "state_description":
            state = self.state_description
        elif state_name == "state_type":
            state = self.state_type
        else:
            raise ValueError("Invalid state name")
        return state

    def set(self, state_name_list, value):
        '''
        Modify: set the current state of the world
        '''
        try:
            if state_name_list[0] == "agents":
                self.agents[state_name_list[1]][state_name_list[2]] = value
            elif state_name_list[0] == "objects":
                self.objects[state_name_list[1]][state_name_list[2]] = value
            elif state_name_list[0] == "relationship":
                self.relationship[state_name_list[1]] = value
            elif state_name_list[0] == "environment":
                self.environment[state_name_list[1]] = value
            else:
                raise ValueError(f"Invalid state name: {state_name_list[0]}")
        except Exception as e:
            raise ValueError("Modify state error!")
        
    def check_state_exist(self, error_tag, check_response, state_name_list):
        '''
        Check if this state exists in the state manager
        '''
        if state_name_list[0] == "agents":
            if not (state_name_list[1] in self.agents and state_name_list[2] in self.agents[state_name_list[1]]):
                error_tag = True
                check_response += f"ERROR: {state_name_list[0]}['{state_name_list[1]}']['{state_name_list[2]}'] does not exist in Current States. Please do not add state without authorization."
        elif state_name_list[0] == "objects":
            if not (state_name_list[1] in self.objects and state_name_list[2] in self.objects[state_name_list[1]]):
                error_tag = True
                check_response += f"ERROR: {state_name_list[0]}['{state_name_list[1]}']['{state_name_list[2]}'] does not exist in Current States. Please do not add state without authorization."
        elif state_name_list[0] == "relationship":
            if not (state_name_list[1] in self.relationship):
                error_tag = True
                check_response += f"ERROR: {state_name_list[0]}['{state_name_list[1]}'] does not exist in Current States. Please do not add state without authorization."
        elif state_name_list[0] == "environment":
            if not (state_name_list[1] in self.environment):
                error_tag = True
                check_response += f"ERROR: {state_name_list[0]}['{state_name_list[1]}'] does not exist in Current States. Please do not add state without authorization."
        else:
            raise ValueError(f"Invalid state name: {state_name_list[0]}")
        
        return error_tag, check_response

