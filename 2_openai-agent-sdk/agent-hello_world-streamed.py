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


async def main():
    result = Runner.run_streamed(sales_agent1, input="Write a cold sales email")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
