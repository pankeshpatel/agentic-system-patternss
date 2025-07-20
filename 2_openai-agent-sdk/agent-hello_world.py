from dotenv import load_dotenv
from agents import Agent, Runner, trace


load_dotenv(override=True)

OPENAI_MODEL = "gpt-4o-mini"


agent = Agent(
    name="Assistant", instructions="You are a helpful assistant", model=OPENAI_MODEL
)

with trace("Telling a joke"):
    result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)
