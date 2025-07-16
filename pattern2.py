from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr
import os
from pydantic import BaseModel
import json


load_dotenv(override=True)
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = "gpt-4o"
GOOGLE_MODEL = "gemini-2.0-flash"


class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str


reader = PdfReader("resources/france.pdf")
helpdocs = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        helpdocs += text.strip() + "\n"


system_prompt = f"""You are a helpful and informative country assistant.
You have access to the following official document:

--- DOCUMENT START ---
{helpdocs}
--- DOCUMENT END ---

Use this document to answer questions about the country’s geography, government, culture, landmarks,
language, currency, population, and international role. Always provide accurate answers strictly based on the document.
Do not make assumptions or add external knowledge. If the answer is not found in the document, say:
"I couldn’t find this information in the current document." Maintain a neutral and informative tone.
"""


def evaluate_response(
    user_question: str, chatbot_response: str, history: list
) -> Evaluation:
    eval_prompt = f"""
                You are an evaluator that decides whether a response to a question is acceptable. \
                You are provided with a conversation between a User and an Agent. \
                Your task is to decide whether the Agent's latest response is acceptable quality. \
                
                ---
                You are provided with a conversation between a User and an Agent. \
                Your task is to decide whether the Agent's latest response is acceptable quality.:
                {history}

                Here's the latest message from the User::
                {user_question}

                Here's the latest response from the chatbot:
                {chatbot_response}

                Reference Document:
                {helpdocs}

                Please evaluate the response, replying with whether it is acceptable and your feedback.
                """

    eval_response = openai.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {"role": "user", "content": eval_prompt},
        ],
        response_format=Evaluation,
    )

    data = json.loads(eval_response.choices[0].message.content)

    return Evaluation(**data)


def rerun(reply, user_question, history, feedback):
    updated_system_prompt = (
        system_prompt
        + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
    )
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = (
        [{"role": "system", "content": updated_system_prompt}]
        + history
        + [{"role": "user", "content": user_question}]
    )
    response = openai.chat.completions.create(model=OPENAI_MODEL, messages=messages)
    return response.choices[0].message.content


def chat(user_question, history):

    messages = (
        [{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": user_question}]
    )

    response = openai.chat.completions.create(model=OPENAI_MODEL, messages=messages)
    reply = response.choices[0].message.content

    # evaluate a response to a model
    evaluation = evaluate_response(user_question, reply, history)

    if evaluation.is_acceptable:
        print("Passed evaluation - returning reply")
    else:
        print("Failed evaluation - retrying")
        print(evaluation.feedback)
        reply = rerun(reply, user_question, history, evaluation.feedback)
    return reply


gr.ChatInterface(chat, type="messages").launch()
