from typing import Optional

async def generate_rca_report(module: str) -> Optional[str]:
    """
    Generate an RCA report link based on the selected module.
    
    Args:
        module (str): The selected module (e.g., "ESP", "DP").
    
    Returns:
        Optional[str]: A message with the RCA report link or an update message.
    """
    
    rca_links = {
        "ESP": "https://docs.google.com/document/d/1Za_VO-Za7nLLBzqAe56Wp05LJpmHvRex/edit?usp=sharing&ouid=113013828525814109060&rtpof=true&sd=true",
        "DP": "The RCA report for this module is under development. Stay tuned!"
    }
    
    if module in rca_links:
        return f"You can access the RCA report here: <a href='{rca_links[module]}' target='_blank' style='color: blue; text-decoration: underline; font-weight: bold;'>RCA Report</a>"
    else:
        return "The RCA report for this module is under development. Stay tuned!"
