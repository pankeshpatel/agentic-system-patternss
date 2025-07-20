"""

This pattern is about  Orchestrator–Worker pattern,
where a planner sent the same question to multiple agents, and a judge assessed their responses to evaluate agent intelligence.
"""

import os
import dotenv
from openai import OpenAI
from anthropic import Anthropic
import json

dotenv.load_dotenv()

OPENAI_MODEL = "gpt-4o-mini"
ANTHROPIC_MODEL = "claude-3-7-sonnet-latest"
GOOGLE_MODEL = "gemini-2.0-flash"
DEEPSEEK_MODEL = "deepseek-chat"
GROQ_MODEL = "llama-3.3-70b-versatile"
OPENAI_MODEL_JUDGE = "o3-mini"


# request = """Create an analysis of the company: Concentric Security
#             Find the:
#             - Company Description
#             - Sector / Industry
#             - Size (number of employees)
#             - Revenue and/or Profitability
#             - Key Products or Services
#             I would also like to know if this company has any press releases about offering IoT services for its products,
#             and if so summarize them into a section called "IoT Offerings".

#             Format the analysis as a simple business formatted write up, including a bullet list of the items above and sub-sections
#             for the press releases and other items."""

request = "What is the capital of France?"
request = request + "Do not include markdown formatting or code blocks."

models = []
answers = []

# OpenAI model

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model=OPENAI_MODEL, messages=[{"role": "user", "content": request}]
)
answer = response.choices[0].message.content
# print(answer)

models.append(OPENAI_MODEL)
answers.append(answer)

# Anthropic model

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model=ANTHROPIC_MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": request}],
)
answer = "".join(getattr(block, "text", "") for block in response.content)
# print(answer)

models.append(ANTHROPIC_MODEL)
answers.append(answer)


# Google model

# give me code code google model gemini 2.0 flash
gemini = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


response = gemini.chat.completions.create(
    model=GOOGLE_MODEL, messages=[{"role": "user", "content": request}]
)

answer = response.choices[0].message.content
# print(answer)

models.append(GOOGLE_MODEL)
answers.append(answer)


# deepseek
deepseek = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1"
)
model_name = DEEPSEEK_MODEL

response = deepseek.chat.completions.create(
    model=DEEPSEEK_MODEL, messages=[{"role": "user", "content": request}]
)
answer = response.choices[0].message.content
# print(answer)

models.append(DEEPSEEK_MODEL)
answers.append(answer)


# Groq model
groq = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"
)
response = groq.chat.completions.create(
    model=GROQ_MODEL, messages=[{"role": "user", "content": request}]
)
answer = response.choices[0].message.content
# print(answer)

models.append(GROQ_MODEL)
answers.append(answer)


# formatting the response

# for models, answer in zip(models, answers):
#     print(f"model: {models}\n\n{answer}")


together = ""
for index, answer in enumerate(answers):
    together += f"# Response from model {index+1}\n\n"
    together += answer + "\n\n"


judge_prompt = f"""You are judging a competition between {len(models)} competitors.
Each model has been given this question:

{request}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
Respond with JSON, and only JSON, with the following format:
{{"results": ["best competitor number", "second best competitor number", "third best competitor number", ...]}}

Here are the responses from each competitor:

{together}

Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks."""


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model=OPENAI_MODEL_JUDGE, messages=[{"role": "user", "content": judge_prompt}]
)
results = response.choices[0].message.content


results_dict = json.loads(results)
ranks = results_dict["results"]
for index, result in enumerate(ranks):
    model = models[int(result) - 1]
    answer = answers[int(result) - 1]
    print(f"Rank {index+1}: {model} \n {answer} ")
