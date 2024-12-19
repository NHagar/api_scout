# https://inspectelement.org/apis.html
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
        request_url = item["request"]["url"]
        try:
            response_content = item["response"]["content"]["text"]
        except KeyError:
            response_content = None

        try:
            response_type = item["response"]["content"]["mimeType"]
        except KeyError:
            response_type = None

        request_headers = item["request"]["headers"]
        response_headers = item["response"]["headers"]

        item_formatted = f"""---------------------
        Request URL: {request_url}

        Response Content: {response_content}
        Response Type: {response_type}

        Request Headers: {request_headers}
        Response Headers: {response_headers}
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

    decision = resp.choices[0].message.content.strip().lower()

    if decision == "yes":
        messages = [
            {"role": "system", "content": prompt_document},
            {"role": "user", "content": item},
        ]

        resp = client.chat.completions.create(model="gemma-2-9b-it", messages=messages)

        document = resp.choices[0].message.content

        return document
    elif decision == "no":
        return None
    else:
        print("Invalid decision")
        print(decision)


items = parse_logfile("www.nytimes.com.har")
test = process_item(items[0])
print(test)
