import os
from openai import OpenAI


class LLMTool:
    def __init__(self, args) -> None:
        
        if args.llm_model == "deepseek-chat":
            self.client = OpenAI(
                base_url="https://api.deepseek.com",
                api_key=os.environ.get("OPENAI_API_KEY")) 
            self.llm_model = args.llm_model

        
        else:
            raise Exception("Please use the available models!")
        
        
        
        
    def query_llm(self, prompt):

        messages = [{'role': 'user','content': prompt},]        
        
        completion = self.client.chat.completions.create(model=self.llm_model, 
                                                        messages=messages,
                                                        temperature=0,
                                                        seed=2024,
                                                        top_p=1) 
        resp = completion.choices[0].message.content
        
        return resp
    