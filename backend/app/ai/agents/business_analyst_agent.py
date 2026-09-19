from app.ai.agents.base_tool_agent import ToolCallingAgent
from app.ai.prompts.business_analyst import SYSTEM_PROMPT, build_user_prompt


class BusinessAnalystAgent(ToolCallingAgent):
    AGENT_NAME = "BusinessAnalystAgent"
    ALLOWED_TOOLS = [
        "get_revenue", "get_sales_by_product", "get_rejected_orders",
        "get_online_offline_sales", "get_outstanding_invoices", "calculate_lost_revenue",
    ]
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def build_user_prompt(self, question, transcript, correction_hint):
        return build_user_prompt(question, transcript, correction_hint)