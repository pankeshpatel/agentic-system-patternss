"""
Handoffs represent a way an agent can delegate to an agent, passing control to it
Handoffs and Agents-as-tools are similar:
In both cases, an Agent can collaborate with another Agent
With tools, control passes back
With handoffs, control passes across"""

from dotenv import load_dotenv
from agents import Agent, function_tool, trace, Runner
from typing import Dict
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

description = "Write a cold sales email"
tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)


subject_instructions = "You can write a subject for a cold sales email. \
You are given a message and you need to write a subject for an email that is likely to get a response."

subject_writer = Agent(
    name="Email subject writer", instructions=subject_instructions, model=OPENAI_MODEL
)
subject_tool = subject_writer.as_tool(
    tool_name="subject_writer",
    tool_description="Write a subject for a cold sales email",
)


html_instructions = "You can convert a text email body to an HTML email body. \
You are given a text email body which might have some markdown \
and you need to convert it to an HTML email body with simple, clear, compelling layout and design."


html_converter = Agent(
    name="HTML email body converter",
    instructions=html_instructions,
    model=OPENAI_MODEL,
)
html_tool = html_converter.as_tool(
    tool_name="html_converter",
    tool_description="Convert a text email body to an HTML email body",
)


@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send out an email with the given subject and HTML body to all sales prospects"""
    print("sent an html email....")
    return {"status": "success"}


instructions = "You are an email formatter and sender. You receive the body of an email to be sent. \
You first use the subject_writer tool to write a subject for the email, then use the html_converter tool to convert the body to HTML. \
Finally, you use the send_html_email tool to send the email with the subject and HTML body."


emailer_agent = Agent(
    name="Email Manager",
    instructions=instructions,
    tools=[subject_tool, html_tool, send_html_email],
    model=OPENAI_MODEL,
    handoff_description="Convert an email to HTML and send it",
)


sales_manager_instructions = "You are a sales manager working for ComplAI. You use the tools given to you to generate cold sales emails. \
You never generate sales emails yourself; you always use the tools. \
You try all 3 sales agent tools at least once before choosing the best one. \
You can use the tools multiple times if you're not satisfied with the results from the first try. \
You select the single best email using your own judgement of which email will be most effective. \
After picking the email, you handoff to the Email Manager agent to format and send the email."


sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=[tool1, tool2, tool3],
    handoffs=[emailer_agent],
    model=OPENAI_MODEL,
)


message = "Send out a cold sales email addressed to Dear CEO from Alice"


async def main():
    with trace("Test1 - Automated SDR"):
        result = await Runner.run(sales_manager, message)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
