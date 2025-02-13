import os

class SelfCorrect:
    
    def __init__(self, llm_instance, logger):
        
        # self.correct_prompts_path = os.path.join(log_path_bt, "correct_prompts.txt")
        self.llm_instance = llm_instance
        self.logger = logger
        
    def get_correct_prompts(self, prompts, history):
        
        correct_prompts = f"""
{prompts}
**********
You have regenerated several steps.
{history}
Please regenerate a new response under the above instructions and avoid the above errors.
"""
        return correct_prompts

    def concatenate_check_response(self, history, iter, check_resp, response):

#         all_prompts = f"""{history}
# In {str(iter)}-th steps, your response is:
# {response}
# However errors are reported as {check_resp}
# """
        all_prompts = f"""
Your last response is:
{response}
However errors are reported as {check_resp}
"""
        history = all_prompts

        return history, all_prompts

    def llm_correct(self, history, iter, check_response, response, prompts):
        
        # Generate prompt for iteration
        history, history_prompts = self.concatenate_check_response(history,
                                                                   iter,
                                                                   check_response,
                                                                   response)
        correct_prompt = self.get_correct_prompts(prompts, history_prompts)
        if self.logger != None:
            pass
            # self.logger.info(f"CorrectPrompt:\n{correct_prompt}\n")
        # Call llm for iteration
        response = self.llm_instance.query_llm(correct_prompt)

        iter += 1
        
        return history, iter, response