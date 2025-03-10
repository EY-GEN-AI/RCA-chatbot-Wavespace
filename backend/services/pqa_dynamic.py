# Plan Quality Comparision and Summary Generator using Open Interpreter
import asyncio

from interpreter import interpreter

interpreter.llm.model = "azure/gpt-4"
interpreter.custom_instructions = "If anyone asks you who made you then keep  in mind that you are an ai made by EY India GEN AI Engineers and your name is 'Maddy' and always you will support end user to analysize, summarize, forecast, an in ml tasks."
interpreter.auto_run = True


docs_path="backend\docs"

#docs_path = r"C:\Users\EQ363EQ\Downloads\ESP_Reports_Output_Tables"

scenarios = {
    "MONTHLY_BASE": {
        "description": "A balanced approach, avoiding extreme fluctuations.",
        "path": docs_path + r"\MB.csv"
    },
    "MONTHLY_DEM_SAT": {
        "description": "Prioritize meeting demand, ensuring high service levels.",
        "path": docs_path + r"\MMD.csv"
    },
    "MONTHLY_MAX_PROFIT": {
        "description": "Maximize profit while potentially reducing demand fulfillment.",
        "path": docs_path + r"\MMP.csv"
    }
}

scenarios_order_summary = {
    "MONTHLY_BASE": {
        "description": "A balanced approach, avoiding extreme fluctuations.",
        "path": docs_path + r"\20250223024320_MONTHLY_BASE_OUT_INDDMDVIEW_ESP.csv"
    },
    "MONTHLY_DEM_SAT": {
        "description": "Prioritize meeting demand, ensuring high service levels.",
        "path": docs_path + r"\20250223024311_MONTHLY_MAX_DEMSAT_OUT_INDDMDVIEW_ESP.csv"
    },
    "MONTHLY_MAX_PROFIT": {
        "description": "Maximize profit while potentially reducing demand fulfillment.",
        "path": docs_path + r"\20250223024224_MONTHLY_MAX_PROFIT_OUT_INDDMDVIEW_ESP.csv"
    }
}

scenarios_supply_summary = {
    "MONTHLY_BASE": {
        "description": "A balanced approach, avoiding extreme fluctuations.",
        "inventory_path": docs_path + r"\20250223023443_MONTHLY_BASE_OUT_PROJECTED_OH_ESP.csv"
    },
    "MONTHLY_DEM_SAT": {
        "description": "Prioritize meeting demand, ensuring high service levels.",
        "inventory_path": docs_path + r"\20250223023521_MONTHLY_MAX_DEMSAT_OUT_PROJECTED_OH_ESP.csv"
    },
    "MONTHLY_MAX_PROFIT": {
        "description": "Maximize profit while potentially reducing demand fulfillment.",
        "inventory_path": docs_path + r"\20250223023406_MONTHLY_MAX_PROFIT_OUT_PROJECTED_OH_ESP.csv"
    }
}

scenarios_production_summary = {
    "MONTHLY_BASE": {
        "description": "A balanced approach, avoiding extreme fluctuations.",
        "path": docs_path + r"\20250223023726_MONTHLY_BASE_OUT_INDDMDLINK_ESP.csv"
    },
    "MONTHLY_DEM_SAT": {
        "description": "Prioritize meeting demand, ensuring high service levels.",
        "path": docs_path + r"\20250223023757_MONTHLY_MAX_DEMSAT_OUT_INDDMDLINK_ESP.csv"
    },
    "MONTHLY_MAX_PROFIT": {
        "description": "Maximize profit while potentially reducing demand fulfillment.",
        "path": docs_path + r"\20250223023651_MONTHLY_MAX_PROFIT_OUT_INDDMDLINK_ESP.csv"
    }
}

scenarios_res_util_summary = {
    "MONTHLY_BASE": {
        "description": "A balanced approach, avoiding extreme fluctuations.",
        "path": docs_path + r"\20250223024526_MONTHLY_BASE_OUT_RESPROJSTATIC_ESP.csv"
    },
    "MONTHLY_DEM_SAT": {
        "description": "Prioritize meeting demand, ensuring high service levels.",
        "path": docs_path + r"\20250223024504_MONTHLY_MAX_DEMSAT_OUT_RESPROJSTATIC_ESP.csv"
    },
    "MONTHLY_MAX_PROFIT": {
        "description": "Maximize profit while potentially reducing demand fulfillment.",
        "path": docs_path + r"\20250223024429_MONTHLY_MAX_PROFIT_OUT_RESPROJSTATIC_ESP.csv"
    }
}


async def generate_plan_summary_1(name_list):
    # Parse the name_list parameter to determine which scenarios to include
    selected_scenarios = []
    if "all" in name_list:
        selected_scenarios = list(scenarios.keys())
    else:
        # Filter only valid scenarios from the list
        selected_scenarios = [s for s in name_list if s in scenarios]
    
    if not selected_scenarios:
        return "Error: No valid scenarios selected."
    
    # Build the scenario descriptions and file information only for selected scenarios
    scenario_descriptions = []
    file_info = []
    
    for scenario in selected_scenarios:
        if scenario in scenarios:
            scenario_descriptions.append(f"- **{scenario}**: {scenarios[scenario]['description']}")
            file_info.append(f"{scenario} at path {scenarios[scenario]['path']}")
    
    scenario_text = "\n".join(scenario_descriptions)
    file_info_text = "\n            ".join(file_info)
    
    SINGLE_SUMMARY_PROMPT_1 = f"""
        You are an Supply Chain Expert and Your task is to follow below steps and generate a textual summary, think Deeply and include more points as per your expertise.

        ⚠️ **STRICT RULES:**  
        - DO NOT print anything to the browser, every result must be printed in the terminal.
        - ALWAYS Follow the structure of report given below.
        - **DO NOT INCLUDE:** Steps, instructions, prompts, meta-information, or file paths in the response.
        - STRICTLY WAIT FOR EACH STEP TO COMPLETE, do not jump to next till current one is completed

        1) You have access to the following file(s):
            {file_info_text}

            Select ONLY {", ".join(selected_scenarios)} those file/files and start forming report as below.

        2) Report (EXPLAIN ONLY SELECTED SCENARIOS {", ".join(selected_scenarios)}):
                1. Overview of Selected Scenarios only {scenario_text}

                2. Analysis of Overall Fill Rates
                    
                    a. Total allocation =  sum(TOTAL_ALLOCATION)
                    b. Total order =  sum(TOTAL_ORDER)
                    c. Overall Fill rate = sum(TOTAL_ALLOCATION)/sum(TOTAL_ORDER) 
                
                    For each scenario seperately and **STRICTLY show actual numbers from data in tabular form ONLY.**

                    Scenario-wise Fill Rate (%):
                    | Scenario                    |Total Allocation | Total Order | Fill Rate (%) |
                    |------------------------------|-----------------|-------------|---------------|

                            
                    Key Observations (Give 4-5 points and explain in detail):


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
        print(output_message)
        return output_message
    
    except Exception as e:
        print("Debug: Exception encountered:", e)
        return f"Error generating summary: {e}"



async def generate_plan_summary_2(name_list):
    # Parse the name_list parameter to determine which scenarios to include
    selected_scenarios = []
    if "all" in name_list:
        selected_scenarios = list(scenarios.keys())
    else:
        # Filter only valid scenarios from the list
        selected_scenarios = [s for s in name_list if s in scenarios]
    
    if not selected_scenarios:
        return "Error: No valid scenarios selected."
    
    # Build the scenario descriptions and file information only for selected scenarios
    scenario_descriptions = []
    file_info = []
    
    for scenario in selected_scenarios:
        if scenario in scenarios:
            scenario_descriptions.append(f"- **{scenario}**: {scenarios[scenario]['description']}")
            file_info.append(f"{scenario} at path {scenarios[scenario]['path']}")
    
    scenario_text = "\n".join(scenario_descriptions)
    file_info_text = "\n            ".join(file_info)
    
    SINGLE_SUMMARY_PROMPT_2 = f"""
        You are an Supply Chain Expert and Your task is to follow below steps and generate a textual summary, think Deeply and do following.

        ⚠️ **STRICT RULES:**  
        - Never include example formats or dummy values in your answer, always use provided data only
        - **DO NOT INCLUDE:** Steps, instructions, prompts, meta-information, or file paths in the response.
        - STRICTLY WAIT FOR EACH STEP TO COMPLETE, do not jump to next till current one is completed

        1) You have access to the following file(s):
            {file_info_text}

            STRICTLY Access those file/files and start forming report as below.

        2) Report (EXPLAIN ONLY SELECTED SCENARIOS {", ".join(selected_scenarios)}):

                Demand Summary (**STRICTLY CALCULATE using python, do NOT generate random or placeholder values. Wait for step to complete then proceed further**) 
                    
                    Fill Rate Analysis by Product Group for each scenario
                    **FOR EACH selected scenario ACCESS FILES and ITERATIVELY group by PRODUCT_GRP, compute fill rate per product, and EXTRACT 3 highest and lowest fill rate products.**## 

                    a. Total allocation =  sum(TOTAL_ALLOCATION)
                    b. Total order =  sum(TOTAL_ORDER)
                    c. Overall Fill rate = sum(TOTAL_ALLOCATION)/sum(TOTAL_ORDER) 

                    Example Format:

                    Scenario:
                    | Product Group | Total Allocation | Total Order | Fill Rate (%) |  
                    |----------------------|-----------------|-------------|---------------|  
                    | Highest Product - X    | X               | X           | X             |   
                    | Highest Product - X    | X               | X           | X             |   
                    | Highest Product - X    | X               | X           | X             |   
                    | Lowest Product - X     | X               | X           | X             |  
                    | Lowest Product - X     | X               | X           | X             |  
                    | Lowest Product - X     | X               | X           | X             |  


                4. Insights & Key Takeaways (**Please look at above data and explain in detail as industry expert**)  

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
        for chunk in interpreter.chat(SINGLE_SUMMARY_PROMPT_2, stream=True, display=False):
            if chunk.get('type') in['message'] and chunk.get('role') in ['assistant']:
                content = chunk.get('content')
                if content:
                    ms.append(str(content))
        
        output_message = "".join(ms)
        print(output_message)
        return output_message
    
    except Exception as e:
        print("Debug: Exception encountered:", e)
        return f"Error generating summary: {e}"



async def generate_plan_summary_3(name_list): #(Large Bulk orders, Total order by Customer)
    # Parse the name_list parameter to determine which scenarios to include
    selected_scenarios = []
    if "all" in name_list:
        selected_scenarios = list(scenarios_order_summary.keys())
    else:
        # Filter only valid scenarios from the list
        selected_scenarios = [s for s in name_list if s in scenarios_order_summary]
    

    if not selected_scenarios:
        return "Error: No valid scenarios selected."
    
    # Build the scenario descriptions and file information only for selected scenarios
    scenario_descriptions = []
    file_info = []
    
    for scenario in selected_scenarios:
        if scenario in scenarios_order_summary:
            scenario_descriptions.append(f"- **{scenario}**: {scenarios_order_summary[scenario]['description']}")
            file_info.append(f"{scenario} at path {scenarios_order_summary[scenario]['path']}")


    print('-'*80, '\n', file_info, '\n', '-'*80)
    print('-'*80, '\n', scenario_descriptions, '\n', '-'*80)

    scenario_text = "\n".join(scenario_descriptions)
    file_info_text = "\n            ".join(file_info)
    
    
    SINGLE_SUMMARY_PROMPT_3 = f"""
            You are an Supply Chain Expert and Your task is to follow below steps and generate a textual summary, think Deeply and do following.

            ⚠️ **STRICT RULES:**  
            - Never include example formats or dummy values in your answer, always use provided data only
            - **DO NOT INCLUDE:** Steps, instructions, prompts, meta-information, or file paths in the response.
            - STRICTLY WAIT FOR EACH STEP TO COMPLETE, do not jump to next till current one is completed

            1) You have access to the following file(s):
                {file_info_text}

                STRICTLY Access those file/files and start forming report as below.


            Report:
                Order Summary (Calculate for each selected Scenario seperately)
                    a. Large Bulk Orders
                        Group by ITEM take SUM on QTY where DMDTYPE=1, report top 3 item with qty in TABULAR FORMAT

                    b. Total Orders by Top Customers
                        Group by CUST,ITEM take SUM on QTY where DMDTYPE=1, report top 3 customers, item with qty in tabular format
                        Report top 3 Customer names, item with qty in TABULAR FORMAT


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
        for chunk in interpreter.chat(SINGLE_SUMMARY_PROMPT_3, stream=True, display=False):
            if chunk.get('type') in['message'] and chunk.get('role') in ['assistant']:
                content = chunk.get('content')
                if content:
                    ms.append(str(content))
        
        output_message = "".join(ms)
        print(output_message)
        return output_message
    
    except Exception as e:
        print("Debug: Exception encountered:", e)
        return f"Error generating summary: {e}"
    






async def generate_plan_summary_4(name_list): #(Avg Inventory next 3 months)
    # Parse the name_list parameter to determine which scenarios to include
    selected_scenarios = []
    if "all" in name_list:
        selected_scenarios = list(scenarios_supply_summary.keys())
    else:
        # Filter only valid scenarios from the list
        selected_scenarios = [s for s in name_list if s in scenarios_supply_summary]
    

    if not selected_scenarios:
        return "Error: No valid scenarios selected."
    
    # Build the scenario descriptions and file information only for selected scenarios
    scenario_descriptions = []
    file_info = []
    
    for scenario in selected_scenarios:
        if scenario in scenarios_supply_summary:
            scenario_descriptions.append(f"- **{scenario}**: {scenarios_supply_summary[scenario]['description']}")
            file_info.append(f"{scenario} Inventory data at path {scenarios_supply_summary[scenario]['inventory_path']}")
            # file_info.append(f"{scenario} Production data at path {scenarios_supply_summary[scenario]['production_path']}")


    print('-'*80, '\n', file_info, '\n', '-'*80)
    print('-'*80, '\n', scenario_descriptions, '\n', '-'*80)

    scenario_text = "\n".join(scenario_descriptions)
    file_info_text = "\n            ".join(file_info)
    
    print('-'*80, '\n File Info text', file_info_text, '\n', '-'*80)

    
    SINGLE_SUMMARY_PROMPT_4 = f"""
            You are an Supply Chain Expert and Your task is to follow below steps and generate a textual summary, think Deeply and do following.

            ⚠️ **STRICT RULES:**  
            - Never include example formats or dummy values in your answer, always use provided data only
            - **DO NOT INCLUDE:** Steps, instructions, prompts, meta-information, or file paths in the response.
            - STRICTLY WAIT FOR EACH STEP TO COMPLETE, do not jump to next till current one is completed

            1) You have access to the following file(s):
                {file_info_text}
                Use inventory_path and production_path correctly as required

                STRICTLY Access those file/files and start forming report as below.


            Report:
                Supply Summary (Calculate for each selected Scenario seperately)

                    a. Average Inventory for Next 3 Months	
                        Filter data for next 3 months only (column - ENDDATE)
                        Group by UDC_PRODUCT_GROUP take sum on PROJECTED_OH
                        Give top 5 Product group, Project Inventory in TABULAR FORMAT


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
    
                    # b. Total Production for Next 3 Months
                    #     Filter data where SUPPLYTYPE = 2
                    #     Then Filter data for next 3 months only (column - SUPPLYAVAILDATE)
                    #     Then Finally group by SUPPLYITEM and take sum on SUPPLYPEGQTY
                    #     Give top 5 ITEM group, Qty in TABULAR FORMAT

    try:
        ms=[]
        interpreter.auto_run = True
        # for chunk in interpreter.chat(CUSTOM_PROMPT, stream=True, display=False):
        for chunk in interpreter.chat(SINGLE_SUMMARY_PROMPT_4, stream=True, display=False):
            if chunk.get('type') in['message'] and chunk.get('role') in ['assistant']:
                content = chunk.get('content')
                if content:
                    ms.append(str(content))
        
        output_message = "".join(ms)
        print(output_message)
        return output_message
    
    except Exception as e:
        print("Debug: Exception encountered:", e)
        return f"Error generating summary: {e}"
    
# answer_2 = generate_plan_summary_2()
    





# async def generate_plan_summary_5(name_list): #PROD
#     # Parse the name_list parameter to determine which scenarios to include
#     selected_scenarios = []
#     if "all" in name_list:
#         selected_scenarios = list(scenarios_production_summary.keys())
#     else:
#         # Filter only valid scenarios from the list
#         selected_scenarios = [s for s in name_list if s in scenarios_production_summary]
    

#     if not selected_scenarios:
#         return "Error: No valid scenarios selected."
    
#     # Build the scenario descriptions and file information only for selected scenarios
#     scenario_descriptions = []
#     file_info = []
    
#     for scenario in selected_scenarios:
#         if scenario in scenarios_production_summary:
#             scenario_descriptions.append(f"- **{scenario}**: {scenarios_production_summary[scenario]['description']}")
#             file_info.append(f"{scenario} at path {scenarios_production_summary[scenario]['path']}")


#     print('-'*80, '\n', file_info, '\n', '-'*80)
#     print('-'*80, '\n', scenario_descriptions, '\n', '-'*80)

#     scenario_text = "\n".join(scenario_descriptions)
#     file_info_text = "\n            ".join(file_info)
    
    
#     SINGLE_SUMMARY_PROMPT_3 = f"""
#             You are an Supply Chain Expert and Your task is to follow below steps and generate a textual summary, think Deeply and do following.

#             ⚠️ **STRICT RULES:**  
#             - Never include example formats or dummy values in your answer, always use provided data only
#             - **DO NOT INCLUDE:** Steps, instructions, prompts, meta-information, or file paths in the response.
#             - STRICTLY WAIT FOR EACH STEP TO COMPLETE, do not jump to next till current one is completed

#             1) You have access to the following file(s):
#                 {file_info_text}

#                 STRICTLY Access those file/files and start forming report as below.


#             Report:
#                 Total Production for Next 3 Months (Do seperately for each selected Scenarios)
#                     Filter data where SUPPLYTYPE = 2
#                     Then Filter data for next 3 months only (column - SUPPLYAVAILDATE)
#                     Then Finally group by SUPPLYITEM and take sum on SUPPLYPEGQTY
#                     Give top 5 ITEM group, Qty in TABULAR FORMAT
            

#                 Keep it very detailed, use your knowledge and give in brief.

#                 ***

#                     ⚠️ **STRICT FINAL OUTPUT RULES:**  
#                         - **DO NOT INCLUDE:** Steps, instructions, prompts, meta-information, or file paths in the response.  
#                         - **DO NOT OMIT ANY SECTION** from the final report.  
#                         - **Ensure every section follows the structure exactly as given.**
#                         - **Your final response MUST include only the human-readable report.**
#                         - **❌ DO NOT mention the prompt steps, instructions, or any meta-information like steps/code/column names, etc. **
#                 ***

                
#         """
    


#     try:
#         ms=[]
#         interpreter.auto_run = True
#         # for chunk in interpreter.chat(CUSTOM_PROMPT, stream=True, display=False):
#         for chunk in interpreter.chat(SINGLE_SUMMARY_PROMPT_3, stream=True, display=False):
#             if chunk.get('type') in['message'] and chunk.get('role') in ['assistant']:
#                 content = chunk.get('content')
#                 if content:
#                     ms.append(str(content))
        
#         output_message = "".join(ms)
#         print(output_message)
#         return output_message
    
#     except Exception as e:
#         print("Debug: Exception encountered:", e)
#         return f"Error generating summary: {e}"
    




async def generate_plan_summary_6(name_list): #RES UTILISATION
    # Parse the name_list parameter to determine which scenarios to include
    selected_scenarios = []
    if "all" in name_list:
        selected_scenarios = list(scenarios_res_util_summary.keys())
    else:
        # Filter only valid scenarios from the list
        selected_scenarios = [s for s in name_list if s in scenarios_res_util_summary]
    

    if not selected_scenarios:
        return "Error: No valid scenarios selected."
    
    # Build the scenario descriptions and file information only for selected scenarios
    scenario_descriptions = []
    file_info = []
    
    for scenario in selected_scenarios:
        if scenario in scenarios_res_util_summary:
            scenario_descriptions.append(f"- **{scenario}**: {scenarios_res_util_summary[scenario]['description']}")
            file_info.append(f"{scenario} at path {scenarios_res_util_summary[scenario]['path']}")


    print('-'*80, '\n', file_info, '\n', '-'*80)
    print('-'*80, '\n', scenario_descriptions, '\n', '-'*80)

    scenario_text = "\n".join(scenario_descriptions)
    file_info_text = "\n            ".join(file_info)
    
    
    SINGLE_SUMMARY_PROMPT_3 = f"""
            You are an Supply Chain Expert and Your task is to follow below steps and generate a textual summary, think Deeply and do following.

            ⚠️ **STRICT RULES:**  
            - Never include example formats or dummy values in your answer, always use provided data only
            - **DO NOT INCLUDE:** Steps, instructions, prompts, meta-information, or file paths in the response.
            - STRICTLY WAIT FOR EACH STEP TO COMPLETE, do not jump to next till current one is completed

            1) You have access to the following file(s):
                {file_info_text}

                STRICTLY Access those file/files and start forming report as below.


            Report:
                Average Resource Utilization by Plants (Calculate for each selected Scenario seperately)
                    Drop data where LOC is blank
                    Group by LOC, RES and take avg of PCTUSED
                    Report top 3 and bottom 3 (**Non-zero**) in TABULAR FORMAT (include columns - LOC, RES, Utilisation)
            

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
        for chunk in interpreter.chat(SINGLE_SUMMARY_PROMPT_3, stream=True, display=False):
            if chunk.get('type') in['message'] and chunk.get('role') in ['assistant']:
                content = chunk.get('content')
                if content:
                    ms.append(str(content))
        
        output_message = "".join(ms)
        print(output_message)
        return output_message
    
    except Exception as e:
        print("Debug: Exception encountered:", e)
        return f"Error generating summary: {e}"
    




async def generate_plan_summary(module_files:dict):
    input_scenarios=module_files["filename"]
    print(input_scenarios)
    #input_scenarios = [ 'MONTHLY_DEM_SAT', 'MONTHLY_BASE', 'MONTHLY_MAX_PROFIT']
    answer_1 = await generate_plan_summary_1(input_scenarios)
    answer_2 = await generate_plan_summary_2(input_scenarios)
    answer_3 = await generate_plan_summary_3(input_scenarios)
    answer_4 = await generate_plan_summary_4(input_scenarios)
    # answer_5 = generate_plan_summary_5(input_scenarios)
    answer_6 = await generate_plan_summary_6(input_scenarios)
    final_answer = answer_1 + "\n\n" + answer_2 + "\n\n" + answer_3 + "\n\n" + answer_4 + "\n\n" + answer_6
    return {"summary": final_answer}



#final_summary = asyncio.run(generate_plan_summary(sample_dict))
#a = generate_plan_summary(sample_dict)
#print(a)

# summary_path = r"C:\DJ\Udemy\Gen_AI\OpenInterpreter\split_summary_report6.txt"
# with open(summary_path, "w", encoding="utf-8") as file:  # Use "a" instead of "w"
#     # file.write("\n\n")  # Add some spacing before appending new content
#     file.write(a)
# print("Report appended successfully")

