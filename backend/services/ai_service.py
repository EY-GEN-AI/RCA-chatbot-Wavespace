# Now implemeneting the logic of displaying the dataframe on the frontend,
#challenge is : message is first stored in mongoDB then it is being displayed on frontend
#but we don't want to store the entire DF on mongoDB


from interpreter import interpreter
from typing import Optional,List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from fastapi import HTTPException, status

import os
import random
import time
import json
from backend.services.sahdevvv import sd
from datetime import datetime
from backend.services.custom_json import TableDataSerializer
from backend.services.summary_generator import DataframeSummary
from backend.services.prompt_next_question import PromptQuestion
from backend.services.get_history import GetContext  # Import the GetContext class
from backend.core.security import get_current_persona


from diskcache import Cache
 
cache_dir = os.path.join(os.path.dirname(__file__), "../cache_directory")
#cache_dir = "./backend/cache_directory"
cache = Cache(cache_dir,size_limit=int(1e12),eviction_policy="none")


class AIService:
    _instance = None
    _executor = ThreadPoolExecutor(max_workers=10)
    _active_sessions = {} 

    def __init__(self):
        # Configure environment first
        self._configure_environment()
     
        # Single interpreter configuration for Azure
        interpreter.reset()
        interpreter.llm.model = "azure/gpt-4"
        interpreter.llm.temperature=0.2
        interpreter.system_message += """
        Run shell commands with -y so the user doesn't have to confirm them.
        """

    def _configure_environment(self):
        """Configure environment settings for OpenAI and SSL"""
        try:
       
            
            logging.info("Configuration completed successfully")
            
        except Exception as e:
            logging.error(f"Failed to configure environment: {str(e)}")
            raise



            




    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AIService()
        return cls._instance
    

    async def _check_rca_request(self, user_question: str, persona: str) -> Optional[dict]:
        """
        Check if the user's question is requesting RCA information.
        Returns a response dict if it's an RCA request, None otherwise.
        
        Args:
            user_question (str): The user's input question
            persona (str): The persona context for the conversation
        
        Returns:
            Optional[dict]: Response dictionary if RCA request is detected, None otherwise
        """

        self.esp_overall_rca_link="https://docs.google.com/document/d/1Za_VO-Za7nLLBzqAe56Wp05LJpmHvRex/edit?usp=sharing&ouid=113013828525814109060&rtpof=true&sd=true"  # Replace with actual link
        self.dp_overall_rca_link="https://github.com/"
        self.fp_overall_rca_link="https://github.com/"
        self.op_overall_rca_link="https://github.com/"
        self.inventory_overall_rca_link="https://github.com/"
        self.forecast_overall_rca_link="https://github.com/"
        # Convert question to lowercase for case-insensitive matching
        question_lower = user_question.lower()
        
        # Define keyword mappings with their variations and corresponding link variables
        keyword_mappings = {
            'esp_overall_rca_link': ['esp', 'enterprise supply planning'],
            'dp_overall_rca_link': ['dp', 'demand planning'],
            'fp_overall_rca_link': ['fp', 'factory planning'],
            'op_overall_rca_link': ['op', 'order promising'],
            'inventory_overall_rca_link': ['il', 'inventory liquidation'],
            'forecast_overall_rca_link': ['forecast']
        }
        
        # Check if 'rca' is present in the question
        if 'rca' not in question_lower:
            return None
        
        # Find the text after 'for' in the question
        for_index = question_lower.find('for')
        if for_index == -1:
            return None
            
        # Extract the text after 'for' and clean it
        target_text = question_lower[for_index + 4:].strip()
        
        # Find matching link variable based on the target text
        matching_link_var = None
        for link_var, keywords in keyword_mappings.items():
            if any(keyword in target_text for keyword in keywords):
                matching_link_var = link_var
                break
                
        if not matching_link_var:
            return None
            
        # Get the actual link from the class variable
        file_location = getattr(self, matching_link_var)
        
        # Calculate response time
        wait_time = random.uniform(5, 8)
        start_time = time.time()
        await asyncio.sleep(wait_time)
        time_taken = round(time.time() - start_time, 2)
        
        prompt_question_object = PromptQuestion
        next_question = prompt_question_object.get_similar_question(user_question, persona)
        # Generate response with the appropriate link
        response_content = (
            f"I have prepared the RCA report for you.\n"
          #  f"You can access it here: [RCA Report]({file_location})\n\n"
            #f"You can access it here: <a href='{file_location}' target='_blank'>RCA Report</a></p>\n\n"
            f"You can access it here: <a href='{file_location}' target='_blank' style='color: blue; text-decoration: underline; font-weight: bold;'>RCA Report</a></p>"
            f"Time taken for RCA: {time_taken} seconds"
        )
        
        return {
            'type': 'text',
            'content': response_content,
            'next_question': next_question
        }
    

    # async def get_ai_response(self, message: str, user_id: str,session_id:str) -> str:
    async def get_ai_response(self, user_message: str, user_id: str, session_id: str, current_user: dict) -> dict:
        """Get AI response asynchronously with user-isolated context"""
        try:
            # Grab persona from current_user
        
            persona = current_user.get("persona", None)
            rca_response = await self._check_rca_request(user_message,persona)
            if rca_response:
                return rca_response
            get_context = GetContext()
            
            context_str = await get_context.get_session_context(session_id, user_id)


            response = await asyncio.get_event_loop().run_in_executor(
                self._executor,
                self._process_user_message,
                user_message,
               context_str,
                persona    # <--- pass it to the sync method
            )



            return response
        except Exception as e:
            logging.error(f"AI Service error for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate AI response"
            )
        




        

    def _process_user_message(self, message: str,context_str:str,persona: str) -> dict:
        """Process message with user-specific interpreter context"""


        #### Cache #########

        cache_key = message
    
        # Check cache
        cached_response = cache.get(cache_key)
        if cached_response:
            print("Cache hit!")
            return cached_response
    
        print("Cache miss! Processing...")
        prompt_question_object=PromptQuestion
        print("*"*80)
        print(context_str)
        print("*"*80)

        print("Suggested next question : ",prompt_question_object.get_similar_question(message,persona))
        next_question=prompt_question_object.get_similar_question(message,persona)

        print("Got history")

        try:
          
            extracted_sql,df,msg = sd.execute_query_with_retries(message,context_str)

            print(df.head())
            
            if not df.empty:
                # Convert DataFrame to dict for JSON serialization
                df.to_csv("temp.csv")
                tds=TableDataSerializer
                df_dict = df.to_dict('records')
                df_dict_serialized = tds.serialize_records(df_dict)
                df_columns = df.columns.tolist()
                summary_object=DataframeSummary(df)
                summary=summary_object.generate_summary(question=message)
                ai_response = {
                    'type': 'sql_response',
                    'content': extracted_sql,
                    'data': {
                        'records': df_dict_serialized,
                        'columns': df_columns
                    },
                    'summary':summary,
                    'next_question':next_question
                }
                

            else:
                ai_response = {
                    'type': 'text',
                    'content': msg,
                    'next_question': next_question
                }

            #self._save_chat_interaction(user_id, message, ai_response['content'])
            cache.set(cache_key, ai_response, expire=None)
            return ai_response

        except Exception as e:
            logging.error(f"Chat processing error: {e}")
            fallback_response=sd.generate_fallback_response(message,"",context_str)
            return {
                'type': 'text',
               'content':fallback_response,
               'next_question':next_question
            }