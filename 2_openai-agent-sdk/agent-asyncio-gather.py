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


# program 2

# message = "write an cold sales email"


# async def main():
#     with trace("Parallel cold emails"):
#         results = await asyncio.gather(
#             Runner.run(sales_agent1, message),
#             Runner.run(sales_agent2, message),
#             Runner.run(sales_agent3, message),
#         )

#     outputs = [result.final_output for result in results]

#     for output in outputs:
#         print(output + "\n")


# if __name__ == "__main__":
#     asyncio.run(main())


# program 3
sales_picker = Agent(
    name="sales_picker",
    instructions="You pick the best cold sales email from the given options. \
Imagine you are a customer and pick the one you are most likely to respond to. \
Do not give an explanation; reply with the selected email only.",
    model="gpt-4o-mini",
)


message = "Write a cold sales email"


async def main():
    with trace("Selection from sales people"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )
        outputs = [result.final_output for result in results]

        emails = "Cold sales emails:\n\n".join(outputs)

        best = await Runner.run(sales_picker, emails)

        print(f"Best sales email:\n{best.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
