# https://inspectelement.org/apis.html
# test w/LLM
# integrate LLM workflow
# prototype interaction model
# prototype UI
import json

from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")


def parse_logfile(logfile):
    with open(logfile, "r") as f:
        logs = json.load(f)

    items = logs["log"]["entries"]
    items_formatted = []

    for item in items:
        item_formatted = f"""---------------------
        Request URL: {item["request"]["url"]}

        Response Content: {item["response"]["content"]["text"]}
        Response Type: {item["response"]["content"]["mimeType"]}

        Request Headers: {item["request"]["headers"]}
        Response Headers: {item["response"]["headers"]}
        ---------------------
        """
        items_formatted.append(item_formatted)

    return items_formatted


def process_item(item):
    with open("prompts/assess.txt", "r") as f:
        prompt_decide = f.read()

    with open("prompts/document.txt", "r") as f:
        prompt_document = f.read()

    messages = [
        {"role": "system", "content": prompt_decide},
        {"role": "user", "content": item},
    ]

    resp = client.chat.completions.create(model="gemma-2-9b-it", messages=messages)

    decision = resp.choices[0].message.content

    if decision == "yes":
        messages = [
            {"role": "system", "content": prompt_document},
            {"role": "user", "content": item},
        ]

        resp = client.chat.completions.create(model="gemma-2-9b-it", messages=messages)

        document = resp.choices[0].message.content

        return document
    else:
        return None
