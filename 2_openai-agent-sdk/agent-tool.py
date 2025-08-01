from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
import asyncio


load_dotenv(override=True)

OPENAI_MODEL = "gpt-4o-mini"


instruction1 = "you are a sales agent working for ComplAI, \
a company that provides SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI \
you write professional, serious cold emails."


instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."


instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."


sales_agent1 = Agent(
    name="Professional Sales Agent", instructions=instruction1, model=OPENAI_MODEL
)

sales_agent2 = Agent(
    name="Engaging Sales Agent", instructions=instructions2, model=OPENAI_MODEL
)

sales_agent3 = Agent(
    name="Busy Sales Agent", instructions=instructions3, model=OPENAI_MODEL
)


@function_tool
def send_email(body: str):
    """Send out an email with the given body to all sales prospects"""
    print("send email...")
    return {"status": "success"}


description = "Write a cold sales email"
tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)


tools = [tool1, tool2, tool3, send_email]

instructions = "You are a sales manager working for ComplAI. You use the tools given to you to generate cold sales emails. \
You never generate sales emails yourself; you always use the tools. \
You try all 3 sales_agent tools once before choosing the best one. \
You pick the single best email and use the send_email tool to send the best email (and only the best email) to the user."

sales_manager = Agent(
    name="Sales Manager", instructions=instructions, tools=tools, model=OPENAI_MODEL
)


async def main():
    with trace("Test1-Sales Manager"):
        result = await Runner.run(
            sales_manager, "Send a cold sales email addressed to 'Dear CEO'"
        )
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
