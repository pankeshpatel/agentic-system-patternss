from dotenv import load_dotenv
from agents import Agent, WebSearchTool, trace, Runner, gen_trace_id, function_tool
from agents.model_settings import ModelSettings
import asyncio
from pydantic import Field, BaseModel


load_dotenv(override=True)


HOW_MANY_SEARCHES = 3

INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."


class WebSearchItem(BaseModel):
    reason: str = Field(
        description="Your reasoning for why this search is important to the query."
    )
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(
        description="A list of web searches to perform to best answer the query."
    )


planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,
)

message = "Latest AI Agent frameworks in 2025"


async def main():
    with trace("Search"):
        result = await Runner.run(planner_agent, message)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
