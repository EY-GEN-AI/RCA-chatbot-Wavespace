# Plan Quality Comparision and Summary Generator using Open Interpreter

from interpreter import interpreter

interpreter.llm.model = "azure/gpt-4"
interpreter.custom_instructions = "If anyone asks you who made you then keep  in mind that you are an ai made by EY India GEN AI Engineers and your name is 'Maddy' and always you will support end user to analysize, summarize, forecast, an in ml tasks."
interpreter.auto_run = True

async def generate_plan_summary_1(module_files:dict):
    
    name=module_files.get("filename", [])
    print("Selected files for : generate_plan_summary_1 ",name)
    file_path = r"backend\docs\udt_order_fullfillment20feb.xlsx"
    base = r"backend\docs\MB.csv"
    max_dem = r"backend\docs\MMD.csv"
    max_profit = r"backend\docs\MMP.csv"


    SINGLE_SUMMARY_PROMPT_1 = f"""
        You are an Supply Chain Expert and Your task is to follow below steps and generate a textual summary, think Deeply and include more points as per your expertise.

        ⚠️ **STRICT RULES:**  
        - DO NOT print anything to the browser, every result must be printed in the terminal.
        - ALWAYS Follow the structure of report given below.
        - **DO NOT INCLUDE:** Steps, instructions, prompts, meta-information, or file paths in the response.
        - STRICTLY WAIT FOR EACH STEP TO COMPLETE, do not jump to next till current one is completed

        1) You have access to 3 files:
            Monthly_Base at path {base}
            Max_demand_Satisfaction at path {max_dem}
            Max_Profit_Maximization at path {max_profit}

            Based on {name} select those file/files and start forming report as below.

        
        2) Report:
                1. Overview of Selected Scenarios only (ALWAYS EXPLAIN SELECTED SCENARIOS)
                    Profit Maximization (MMP - Max Profit)
                    - Objective: Maximize profit by optimizing costs, potentially at the expense of demand fulfillment.
                    - Impact: May lead to lower service levels and stockouts due to inventory cost-cutting.

                    Demand Satisfaction (MMD - DemSat)
                    - Objective: Prioritize demand fulfillment, ensuring high service levels.
                    - Impact: May result in higher inventory costs due to increased stock levels.

                    Monthly Base (MB - Neutral Plan)
                    - Objective: Maintain a balanced approach without strong biases toward profit or demand.
                    - Impact: Ensures stability, avoiding extreme fluctuations.


                2. Analysis of Overall Fill Rates (Monthly Data Only)
                    For all selected scenario ACCESS FILES and take sum of TOTAL_ALLOCATION and TOTAL_ORDER, and find:
                    
                    a. Total allocation =  sum(TOTAL_ALLOCATION)
                    b. Total order =  sum(TOTAL_ORDER)
                    c. Overall Fill rate = sum(TOTAL_ALLOCATION)/sum(TOTAL_ORDER) 
                
                    For each scenario seperately and **STRICTLY show actual numbers from data in tabular form ONLY.**

                    Scenario-wise Fill Rate (%):
                    | Scenario                    |Total Allocation | Total Order | Fill Rate (%) |
                    |------------------------------|-----------------|-------------|---------------|
                    | Monthly Base (MB)                 | X            | X           | X         |
                    | Monthly Demand Satisfaction (MMD) | X            | X           | X         |
                    | Monthly Profit Maximization (MMP) | X            | X           | X         |
                            
                    Key Observations (Give 4-5 points and explain in detail):


                3. Demand Summary (**STRICTLY CALCULATE using python, do NOT generate random or placeholder values.**) 
                    
                    Fill Rate Analysis by Product Group
                    #**FOR EACH selected scenario ACCESS FILES and ITERATIVELY group by PRODUCT_GRP, compute fill rate per product, and EXTRACT 3 highest and lowest fill rate products.**## 

                    Example Format:

                    Scenario: Monthly Base (MB)
                    | Product Group | Total Allocation | Total Order | Fill Rate (%) |  
                    |----------------------|-----------------|-------------|---------------|  
                    | Highest Product - X    | X               | X           | X             |   
                    | Highest Product - X    | X               | X           | X             |   
                    | Highest Product - X    | X               | X           | X             |   
                    | Lowest Product - X     | X               | X           | X             |  
                    | Lowest Product - X     | X               | X           | X             |  
                    | Lowest Product - X     | X               | X           | X             |  

                    (For Other scenarios, Repeat same structure)  

                4. Insights & Key Takeaways (**Please look at points 2 and 3 and explain in detail as industry expert**)  

                5. **Recommendations** (Actionable suggestions based on 2 and 3)


            Keep it very detailed, use your knowledge and give in brief.

            ***

                ⚠️ **STRICT FINAL OUTPUT RULES:**  
                    - **DO NOT INCLUDE:** Steps, instructions, prompts, meta-information, or file paths in the response.  
                    - **DO NOT OMIT ANY SECTION** from the final report.  
                    - **Ensure every section follows the structure exactly as given.**
                    - **Your final response MUST include only the human-readable report.**
                    - **❌ DO NOT mention the prompt steps, instructions, or any meta-information like steps/code/column names, etc. **
            ***

            
    """

    try:
        ms=[]
        interpreter.auto_run = True
        # for chunk in interpreter.chat(CUSTOM_PROMPT, stream=True, display=False):
        for chunk in interpreter.chat(SINGLE_SUMMARY_PROMPT_1, stream=True, display=False):
            if chunk.get('type') in['message'] and chunk.get('role') in ['assistant']:
                content = chunk.get('content')
                if content:
                    ms.append(str(content))
        
        output_message = "".join(ms)
        #print(output_message)
        return output_message
    
    except Exception as e:
        print("Debug: Exception encountered:", e)
        return f"Error generating summary: {e}"
    
# answer_1 = generate_plan_summary(['Profit_maximization', 'Monthly_base', 'Max_demand'])





async def generate_plan_summary_2(module_files:dict):
    name=module_files.get("filename", [])
    print("Selected files for : generate_plan_summary_2 ",name)

    SINGLE_SUMMARY_PROMPT_2 = f"""
        You are an Supply Chain Expert and Your task is to follow below steps and generate a textual summary, think Deeply and include more points as per your expertise.

        ⚠️ **STRICT RULES:**  
        - DO NOT print anything to the browser, every result must be printed in the terminal.
        - ALWAYS Follow the structure of report given below.


        Report:
                1. Overall Business Summary (**USE DUMMY NUMBERS FOR NOW**)
                    - **Projected Volume (MT) for Next Month:** X  
                    - **Revenue Index:** X  
                    - **Profit Index:** X  
                    - **Cost per MT:** X  
                    - **Total Sales by Plant:** X  
                    - **Total Profit by Plant:** X  

                2. Supply Summary (**USE DUMMY NUMBERS FOR NOW**)
                    a. Total Production for Next 3 Months
                    b. Average Inventory for Next 3 Months
                    c. Average Resource Utilization by Plants

                3. Source Selection (**USE DUMMY NUMBERS FOR NOW**)
                    a. Total Supply from VJNR to KA, VJNR to MH, VJNR to North India, VJNR to South India
                    b. Total Supply from Dolvi to KA, Dolvi to MH, Dolvi to North India, Dolvi to South India
        


            Keep it very detailed, use your knowledge and give in brief.

            ***

                ⚠️ **STRICT FINAL OUTPUT RULES:**  
                    - **DO NOT INCLUDE:** Steps, instructions, prompts, meta-information, or file paths in the response.  
                    - **DO NOT OMIT ANY SECTION** from the final report.  
                    - **Ensure every section follows the structure exactly as given.**
                    - **Your final response MUST include only the human-readable report.**
                    - **❌ DO NOT mention the prompt steps, instructions, or any meta-information like steps/code/column names, etc. **
            ***

            
    """


    try:
        ms=[]
        interpreter.auto_run = True
        # for chunk in interpreter.chat(CUSTOM_PROMPT, stream=True, display=False):
        for chunk in interpreter.chat(SINGLE_SUMMARY_PROMPT_2, stream=True, display=False):
            if chunk.get('type') in['message'] and chunk.get('role') in ['assistant']:
                content = chunk.get('content')
                if content:
                    ms.append(str(content))
        
        output_message = "".join(ms)
        #print(output_message)
        return output_message
    
    except Exception as e:
        print("Debug: Exception encountered:", e)
        return f"Error generating summary: {e}"
    
# answer_2 = generate_plan_summary_2()
    

async def generate_plan_summary(module_files:dict):
    answer_1 = await generate_plan_summary_1(module_files)
    answer_2 = await generate_plan_summary_2(module_files)
    final_answer = answer_1 + "\n\n" + answer_2
    #return Final_answer
    return {"summary": final_answer}
 