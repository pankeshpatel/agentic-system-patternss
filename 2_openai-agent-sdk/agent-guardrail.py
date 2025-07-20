from pydantic import BaseModel
from agents import Agent, Runner, input_guardrail, GuardrailFunctionOutput, trace
import asyncio
from dotenv import load_dotenv


OPENAI_MODEL = "gpt-4o-mini"

load_dotenv(override=True)


class NameCheckOutput(BaseModel):
    is_name_in_message: bool
    name: str


guardrail_agent = Agent(
    name="Name check",
    instructions="Check if the user is including someone's personal name in what they want you to do.",
    output_type=NameCheckOutput,
    model=OPENAI_MODEL,
)

sales_assistant_instructions = """You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails.
"""


@input_guardrail
async def guardrail_against_name(ctx, agent, message):
    result = await Runner.run(guardrail_agent, message, context=ctx.context)
    is_name_in_message = result.final_output.is_name_in_message
    return GuardrailFunctionOutput(
        output_info={"found_name": result.final_output},
        tripwire_triggered=is_name_in_message,
    )


careful_sales_assistant = Agent(
    name="Sales Assistant",
    instructions=sales_assistant_instructions,
    model=OPENAI_MODEL,
    input_guardrails=[guardrail_against_name],
)

message = "Send out a cold sales email addressed to Dear CEO"


async def main():
    with trace("Protected Automated SDR"):
        result = await Runner.run(careful_sales_assistant, message)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
