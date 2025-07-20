from dotenv import load_dotenv
from openai import OpenAI
import json
import os
from pypdf import PdfReader
import gradio as gr


load_dotenv(override=True)
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = "gpt-4o"


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
"I couldn’t find this information in the current document.", use your record_unknown_question tool to record the question that 
you couldn't answer, even if it's about something trivial or unrelated.  

If the user is engaging in discussion, try to steer them towards getting in touch via email; ask 
for their email and record it using your record_user_details tool. 

Maintain a neutral and informative tone.
"""


def record_user_details(email, name="Name not provided", notes="not provided"):
    return {"recorded": "ok"}


def record_unknown_question(question):
    return {"recorded": "ok"}


record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user",
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it",
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered",
            },
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}


tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if tool_name == "record_user_details":
            result = record_user_details(**arguments)
        elif tool_name == "record_unknown_question":
            result = record_unknown_question(**arguments)

        results.append(
            {
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id,
            }
        )
    return results


def chat(user_question, history):
    messages = (
        [{"role": "system", "content": system_prompt}]
        + history
        + [{"role": "user", "content": user_question}]
    )
    done = False

    while not done:

        response = openai.chat.completions.create(
            model=OPENAI_MODEL, messages=messages, tools=tools
        )

        finish_reason = response.choices[0].finish_reason

        # if LLM wants to call a tool, we can do that
        if finish_reason == "tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True

    return response.choices[0].message.content


gr.ChatInterface(chat, type="messages").launch()
