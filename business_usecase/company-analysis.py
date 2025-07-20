"""
This pattern is about the Orchestrator–Worker pattern,
where a planner sends the same question to multiple agents, and a judge assesses their responses to evaluate agent intelligence.
"""

import os
import json
import dotenv
from openai import OpenAI
from anthropic import Anthropic

dotenv.load_dotenv()

OPENAI_MODEL = "gpt-4o"
ANTHROPIC_MODEL = "claude-3-7-sonnet-latest"
GOOGLE_MODEL = "gemini-2.0-flash"
DEEPSEEK_MODEL = "deepseek-chat"
GROQ_MODEL = "llama-3.3-70b-versatile"
OPENAI_MODEL_JUDGE = "gpt-4o"

# List of companies
COMPANIES = [
    "Volta Group",
    "Estrada Law Group",
    "Laitram Machinery",
    "Club Car",
    "Bard",
    "Centri Goup",
    "McCrometer",
    "Luminator Technology Group",
    "InCharge Energy",
    "American Research Bureau",
]

# Setup LLM clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
gemini_client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1"
)
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"
)


def analyze_company(company_name):
    request = f"""You are a professional business analyst assistant.

Create an in-depth company analysis for the following company: {company_name}

Your response should include the following information:
- **Company Description**: A concise overview of the company, including what it does and its core focus.
- **Sector / Industry**: The market sector and industry in which the company operates.
- **Size**: Number of employees (if available).
- **Revenue and/or Profitability**: Any known figures on annual revenue or overall financial health.
- **Key Products or Services**: A summary of the company’s main products, solutions, or services.

In addition, research and summarize any **recent press releases or news** about the company offering **IoT (Internet of Things)** services.
If available, include a clearly labeled section titled **"IoT Offerings"** summarizing their relevance, scope, and any notable implementations.

Output Format:

- Company Analysis: {company_name}
- **Company Description**:
- **Sector / Industry**:
- **Size**:
- **Revenue and/or Profitability**:
- **Key Products or Services**:
- **IoT Offerings**:
[Include only if relevant information is found. Provide notable IoT initiatives, services, or press releases.]

Please include relevant weblinks for press releases, services, IoT initiatives, and key products or services.
Only include verified and relevant information. If any information is not available, clearly state "Information not available" rather than guessing."""

    models = []
    answers = []

    # OpenAI
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL, messages=[{"role": "user", "content": request}]
    )
    models.append(OPENAI_MODEL)
    answers.append(response.choices[0].message.content)

    # Anthropic
    response = anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": request}],
    )
    answer = "".join(getattr(block, "text", "") for block in response.content)
    models.append(ANTHROPIC_MODEL)
    answers.append(answer)

    # Deepseek
    response = deepseek_client.chat.completions.create(
        model=DEEPSEEK_MODEL, messages=[{"role": "user", "content": request}]
    )
    models.append(DEEPSEEK_MODEL)
    answers.append(response.choices[0].message.content)

    # Groq
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL, messages=[{"role": "user", "content": request}]
    )
    models.append(GROQ_MODEL)
    answers.append(response.choices[0].message.content)

    # Judging
    together = ""
    for index, answer in enumerate(answers):
        together += f"# Response from model {index+1} ({models[index]})\n\n"
        together += answer + "\n\n"

    judge_prompt = f"""You are judging a competition between {len(models)} competitors.
Each model has been given this question:

{request}

Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
Respond ONLY with JSON in this format:
{{"results": [1, 2, 3, ...]}}  # These are the model indices, ranked from best (1) to worst

Here are the responses from each competitor:

{together}

Now respond ONLY with the JSON (do not include markdown, explanation, or code blocks)."""

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL_JUDGE, messages=[{"role": "user", "content": judge_prompt}]
    )
    results = response.choices[0].message.content.strip()

    try:
        ranks = [int(i) for i in json.loads(results)["results"]]
    except Exception as e:
        print(f"\n[ERROR] Failed to parse judge result:\n{results}\n")
        raise e

    # Build output content
    final_output = f"### Company Analysis: {company_name}\n\n"
    for rank, index in enumerate(ranks):
        model = models[int(index) - 1]
        answer = answers[int(index) - 1]
        final_output += f"## Rank {rank+1}: {model}\n\n{answer}\n\n"

    # Clean filename
    safe_filename = company_name.strip().replace(" ", "_").replace("/", "_")
    with open(f"{safe_filename}.txt", "w", encoding="utf-8") as f:
        f.write(final_output)

    print(f"Saved analysis for '{company_name}' to '{safe_filename}.txt'")


# Run for all companies
for company in COMPANIES:
    analyze_company(company)


# """
# This pattern is about the Orchestrator–Worker pattern,
# where a planner sends the same question to multiple agents, and a judge assesses their responses to evaluate agent intelligence.
# """

# import os
# import json
# import dotenv
# from openai import OpenAI
# from anthropic import Anthropic

# dotenv.load_dotenv()

# OPENAI_MODEL = "gpt-4o"
# ANTHROPIC_MODEL = "claude-3-7-sonnet-latest"
# GOOGLE_MODEL = "gemini-2.0-flash"
# DEEPSEEK_MODEL = "deepseek-chat"
# GROQ_MODEL = "llama-3.3-70b-versatile"
# OPENAI_MODEL_JUDGE = "gpt-4o"

# # List of companies
# COMPANIES = [
#     "Volta Group",
#     "Estrada Law Group",
#     "Laitram Machinery",
#     "Club Car",
#     "Bard",
#     "Centri Goup",
#     "McCrometer",
#     "Luminator Technology Group",
#     "InCharge Energy",
#     "American Research Bureau",
# ]

# # Setup LLM clients
# openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# gemini_client = OpenAI(
#     api_key=os.getenv("GOOGLE_API_KEY"),
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
# )
# deepseek_client = OpenAI(
#     api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1"
# )
# groq_client = OpenAI(
#     api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"
# )


# def analyze_company(company_name):
#     request = f"""You are a professional business analyst assistant.

# Create an in-depth company analysis for the following company: {company_name}

# Your response should include the following information:
# - **Company Description**: A concise overview of the company, including what it does and its core focus.
# - **Sector / Industry**: The market sector and industry in which the company operates.
# - **Size**: Number of employees (if available).
# - **Revenue and/or Profitability**: Any known figures on annual revenue or overall financial health.
# - **Key Products or Services**: A summary of the company’s main products, solutions, or services.

# In addition, research and summarize any **recent press releases or news** about the company offering **IoT (Internet of Things)** services.
# If available, include a clearly labeled section titled **"IoT Offerings"** summarizing their relevance, scope, and any notable implementations.

# Output Format:

# - Company Analysis: {company_name}
# - **Company Description**:
# - **Sector / Industry**:
# - **Size**:
# - **Revenue and/or Profitability**:
# - **Key Products or Services**:
# - **IoT Offerings**:
# [Include only if relevant information is found. Provide notable IoT initiatives, services, or press releases.]

# Please include relevant weblinks for press releases, services, IoT initiatives, and key products or services.
# Only include verified and relevant information. If any information is not available, clearly state "Information not available" rather than guessing."""

#     models = []
#     answers = []

#     # OpenAI
#     response = openai_client.chat.completions.create(
#         model=OPENAI_MODEL, messages=[{"role": "user", "content": request}]
#     )
#     models.append(OPENAI_MODEL)
#     answers.append(response.choices[0].message.content)

#     # Anthropic
#     response = anthropic_client.messages.create(
#         model=ANTHROPIC_MODEL,
#         max_tokens=1024,
#         messages=[{"role": "user", "content": request}],
#     )
#     answer = "".join(getattr(block, "text", "") for block in response.content)
#     models.append(ANTHROPIC_MODEL)
#     answers.append(answer)

#     # Google
#     # response = gemini_client.chat.completions.create(
#     #     model=GOOGLE_MODEL, messages=[{"role": "user", "content": request}]
#     # )
#     # models.append(GOOGLE_MODEL)
#     # answers.append(response.choices[0].message.content)

#     # Deepseek
#     response = deepseek_client.chat.completions.create(
#         model=DEEPSEEK_MODEL, messages=[{"role": "user", "content": request}]
#     )
#     models.append(DEEPSEEK_MODEL)
#     answers.append(response.choices[0].message.content)

#     # Groq
#     response = groq_client.chat.completions.create(
#         model=GROQ_MODEL, messages=[{"role": "user", "content": request}]
#     )
#     models.append(GROQ_MODEL)
#     answers.append(response.choices[0].message.content)

#     # Judging
#     together = ""
#     for index, answer in enumerate(answers):
#         together += f"# Response from model {index+1} ({models[index]})\n\n"
#         together += answer + "\n\n"

#     judge_prompt = f"""You are judging a competition between {len(models)} competitors.
# Each model has been given this question:

# {request}

# Your job is to evaluate each response for clarity and strength of argument, and rank them in order of best to worst.
# Respond with JSON, and only JSON, with the following format:
# {{"results": ["best competitor number", "second best competitor number", "third best competitor number", ...]}}

# Here are the responses from each competitor:

# {together}

# Now respond with the JSON with the ranked order of the competitors, nothing else. Do not include markdown formatting or code blocks."""

#     response = openai_client.chat.completions.create(
#         model=OPENAI_MODEL_JUDGE, messages=[{"role": "user", "content": judge_prompt}]
#     )
#     results = response.choices[0].message.content
#     ranks = json.loads(results)["results"]

#     # Build output content
#     final_output = f"### Company Analysis: {company_name}\n\n"
#     for rank, index in enumerate(ranks):
#         model = models[int(index) - 1]
#         answer = answers[int(index) - 1]
#         final_output += f"## Rank {rank+1}: {model}\n\n{answer}\n\n"

#     # Clean filename
#     safe_filename = company_name.strip().replace(" ", "_").replace("/", "_")
#     with open(f"{safe_filename}.txt", "w", encoding="utf-8") as f:
#         f.write(final_output)

#     print(f"Saved analysis for '{company_name}' to '{safe_filename}.txt'")


# # Run for all companies
# for company in COMPANIES:
#     analyze_company(company)
