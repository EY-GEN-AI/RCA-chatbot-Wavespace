# dataframe_summary.py

import pandas as pd
from interpreter import interpreter  # Assuming `generate_response` is your LLM interaction function.
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
import logging
from copy import deepcopy
import time
from backend.services.session_manager import SessionManager
from backend.utils.logger import SessionLogger

class DataframeSummary:
    _executor = ThreadPoolExecutor(max_workers=10)  # Dedicated thread pool for summaries
    
    def __init__(self, dataframe: pd.DataFrame, session_id: str = None):
        """Initialize with a dataframe and optional session_id"""
        self.df = dataframe
        self.session_id = session_id
        
        self.session_manager = SessionManager.get_instance()
        session = self.session_manager.get_session_interpreter(session_id)
        self.interpreter = session['interpreter']
        
        # Use a single temp file for both operations
        timestamp = int(time.time())
        self.temp_filename = os.path.join(
            session['temp_dir'], 
            f"analysis_{timestamp}_{session_id}.csv"
        )
        SessionLogger.log(session_id, 'file', f'Created temporary file: {os.path.basename(self.temp_filename)}')

    def _configure_interpreter(self):
        """Configure interpreter instance for this specific session"""
        self.interpreter.llm.model = "azure/gpt-4"
        self.interpreter.llm.temperature = 0.7
        self.interpreter.auto_run = True
        self.interpreter.computer.emit_images = False
        self.interpreter.verbose = False
        
        # Configure system messages
        self.interpreter.system_message = """Run shell commands with -y so the user doesn't have to confirm them."""
        self.interpreter.custom_instructions = """You are 'Maddy', an AI assistant created by EY India GEN AI Engineers.
                                                    Your primary focus is on:
                                                    1. Supply chain analysis and optimization
                                                    2 Root cause analysis (RCA)
                                                    3 Predictive quality analysis (PA)
                                                    4 Data summarization and forecasting
                                                    5 Machine learning insights
                                                    Always maintain a professional tone while being helpful and precise in your responses.
                                                    Focus on providing actionable insights and clear explanations."""  # Your existing instructions

    def custom_code_output_sender(content):
        # Print output to the console only
        output = f"Code output:\n{content}\n\n"
        print(output)  # Send to console
        return output  # Prevent browser rendering

    def generate_tailored_prompt(self, question: str) -> str:
        """Construct the tailored prompt based on the dataframe columns."""
        try:
            SessionLogger.log(self.session_id, 'analyze', 'Analyzing DataFrame schema')
            column_names = self.df.columns.tolist()
            schema_desc = "\n".join([
                                    f"- {col}: {dtype}"
                                    for col, dtype in self.df.dtypes.items()
                                    ])
            
            SessionLogger.log(self.session_id, 'process', f'Generating prompt with {len(column_names)} columns')
            tailored_prompt = (f"""
      
    Act as an expert supply chain operations analyst. Analyze {self.temp_filename} (Columns: {', '.join(column_names)}, Schema: {schema_desc}) to generate **dynamic insights** and **executable actions** for {question}.  

    **Insight Generation RULES:**  
    1. **Insight Format**:  
       - **Every insight MUST start with** `for ex:` and use:  
         `[Emoji] [Metric] → [Impact] → [Action]`  
       - **Emojis**: 📉(risk)/📈(opportunity)/📦(inventory)/⚙️(process)/💰(cost)/🚚(logistics)
        - **Metrics**: Inventory, lead time, cost, demand, etc.
            

    2 . **Silent Data Preprocessing:**  
        - **Text-to-Value Conversion:** Automatically clean and convert columns with numeric values stored as text (e.g., "10%" → 0.1, "₹1,000" → 1000, "5 days" → 5).  
        - **Ambiguity Handling:** Assume business context for conversions (e.g., "qty: 85%" → treat as 85% utilization, not 85 units).  
        - **Decimal Standardization:** Convert commas to periods for numeric values (e.g., "1,5" → 1.5).  

    3. **Unit Enforcement:**  
        - **Time:** Hours/days (never weeks/months). Example: "14hr delay" not "2 weeks".  
        - **Inventory:** Units/days of cover (not ₹ value unless explicitly asked). Example: "22 days of stock" not "₹45L inventory".  
        - **Performance:** Percentage points (e.g., "7pp gap", not "7% gap").  
        - **Quantities:** Integers or floats only. Example: "Order gap: 1,250 units" → "1250 units".  

**Response Structure (EXACT TEMPLATE):- NUMBER DRIVEN RESONSE MUST BE THERE ON ECAH AND EVERY SECTION. AND DO NOT INCLUDE THE ANALYSIS PLAN**     

    ### 🚨 **Critical Alerts**:
    - Min 4-5 bullets with *business-specific Critical Alerts*. Examples:  
    - 📉 Safety stock at 1.2σ → 82% stockout risk! → 🛠️ Increase buffer by 22%  
    - 📈 Supplier lead time ↗️37% → ₹8K/day delays → 🔍 Audit Vendor X   

    ### 💡 **Deep Insights** :  
    - Min 3-4 bullets with *Deep business insights where business can get impacted*. Examples: 
    - 📦 Inventory turnover ↗️15% → ₹50K/month savings → 🔄 Optimize reorder points  
    -  💰 Cost per unit ↓8% → ₹120K/year savings → 📊 Review supplier contracts  


    ### 🎯 **Action Plan ** :
    # 🚀 Quick Wins :
      - Min 3-4 bullets with *Business quick wins where business can get impacted*. Examples: 
      - 🛠️ Reroute 30% shipments → Save 14hrs/week → ₹5K savings  

    # 🌐 Strategic Plays :
      - Min 3-4 bullets with *for Business Strategic Plays *. Examples:  
      - 🔄 Dynamic replenishment → 62% fewer stockouts → ₹1.2M/year saved 

    ### 🎯 **A Quick Summary Recap **:   
        - Single <100-word paragraph with Covering all the insights and actions.:  
        1. **Critical gap** ("Text-formatted quantities caused 83% underdelivery")  
        2. **Immediate fix** ("ERP validation rules")  
        3. **Business outcome** ("98% allocation accuracy, 11% fewer stockouts")  

    --------------------------------------------------
    Compliance Check:
        - Neutral language & policy-safe emojis 
        - Hypothetical figures (₹XK). Allfinancial figures must be in Rupees.
        - No health/combat metaphors .Always maintain a professional tone and focus on actionable insights.
        **Critical Content Rules:**  
        - **Never** mention preprocessing steps. Example: *Say "1500-unit gap" not "converted '1,500' text to 1500". or "It seems there was a problem accessing the file due to an invalid path argument....."*  
        - **Data Types:** Assume all numbers are usable post-silent cleaning. Never say, "The data had formatting issues."  
        - **Demand Errors:** Attribute gaps to business decisions, not data entry. Example: *"12pp forecast bias" not "dirty data".*  

        **Penalty:** Format deviations or mentions of data cleaning trigger full regeneration.

                """)
            return tailored_prompt
            
        except Exception as e:
            SessionLogger.log(self.session_id, 'error', f'Error generating prompt: {str(e)}', 'error')
            raise
    

    async def generate_summary_async(self, question: str) -> str:
        """
        Asynchronously generate summary using thread pool for CPU-bound operations
        """
        try:
            SessionLogger.log(self.session_id, 'summary', f'Starting summary generation for question: {question[:50]}...')
            # Get session-specific lock
            lock = await self.session_manager.get_session_lock(self.session_id)
            
            async with lock:
                # Save DataFrame only once
                if not os.path.exists(self.temp_filename):
                    SessionLogger.log(self.session_id, 'file', 'Saving DataFrame to temporary file')
                    self.df.to_csv(self.temp_filename, index=False)
                
                # Run in thread pool
                SessionLogger.log(self.session_id, 'process', 'Running summary generation in thread pool')
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    self.session_manager._executor,
                    self._generate_summary_sync,
                    question
                )
                
                # Clean up immediately after use
                if os.path.exists(self.temp_filename):
                    SessionLogger.log(self.session_id, 'cleanup', f'Removing temporary file: {os.path.basename(self.temp_filename)}')
                    os.remove(self.temp_filename)
                
                SessionLogger.log(self.session_id, 'success', 'Summary generation completed successfully', 'success')
                return result
                
        except Exception as e:
            SessionLogger.log(self.session_id, 'error', f'Summary generation error: {str(e)}', 'error')
            if os.path.exists(self.temp_filename):
                os.remove(self.temp_filename)
            logging.error(f"Summary generation error for session {self.session_id}: {e}")
            return f"Error generating summary: {e}"

    def _generate_summary_sync(self, question: str) -> str:
        try:
            SessionLogger.log(self.session_id, 'analyze', 'Starting LLM analysis')
            prompt = self.generate_tailored_prompt(question)
            messages = []
            
            total_chunks = 500  # Expected total chunks
            current_chunk = 0
            last_update = 0
            
            for chunk in self.interpreter.chat(prompt, stream=True, display=False):
                if chunk.get('type') in ['message'] and chunk.get('role') in ['assistant']:
                    content = chunk.get('content')
                    if content:
                        messages.append(str(content))
                        current_chunk += 1
                        
                        # Update progress only every 5% to avoid spam
                        progress = int((current_chunk / total_chunks) * 100)
                        if progress % 5 == 0 and progress != last_update:
                            SessionLogger.progress(
                                current_chunk,
                                total_chunks,
                                "Generating insights",
                                self.session_id
                            )
                            last_update = progress
            
            # Final progress update
            SessionLogger.progress(total_chunks, total_chunks, "Generating insights", self.session_id)
            summary = "".join(messages)
            SessionLogger.log(self.session_id, 'success', f'Generated summary ({len(summary)} chars)')
            return summary
        except Exception as e:
            SessionLogger.log(self.session_id, 'error', str(e), 'error')
            raise