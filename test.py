# https://inspectelement.org/apis.html
# parse logfile data
# test w/LLM
# integrate LLM workflow
# prototype interaction model
# prototype UI
import json


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
