# necessary fields from requests
# preliminary filtering?

import asyncio
import json
from datetime import datetime
from urllib.parse import urlparse

from playwright.async_api import async_playwright


def get_log_filename(url):
    parsed = urlparse(url)
    domain = parsed.netloc.replace(".", "_")
    path = parsed.path.replace("/", "_").strip("_")
    if path:
        domain = f"{domain}_{path}"
    return f"requests_{domain}.json"


class RequestLogger:
    def __init__(self):
        self.page_requests = {}
        self.current_main_url = None

    def get_or_create_log(self, url):
        if url not in self.page_requests:
            self.page_requests[url] = {
                "requests": [],
                "log_file": get_log_filename(url),
            }
            with open(self.page_requests[url]["log_file"], "w") as f:
                json.dump([], f)

        return self.page_requests[url]

    async def handle_request(self, request):
        if not self.current_main_url:
            return

        log_data = self.get_or_create_log(self.current_main_url)
        request_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": request.url,
            "headers": request.headers,
            "post_data": request.post_data,
        }
        log_data["requests"].append(request_data)

        # Save to page-specific log file
        with open(log_data["log_file"], "a") as f:
            json.dump(log_data["requests"], f, indent=2)

    async def handle_navigation(self, response):
        if response and response == response.page.main_frame:
            self.current_main_url = response.url
            print(f"\nNavigated to: {self.current_main_url}")
            print(f"Logging requests to: {get_log_filename(self.current_main_url)}")
            self.get_or_create_log(self.current_main_url)


async def capture_requests(url="https://nytimes.com"):
    logger = RequestLogger()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        page.on("request", logger.handle_request)
        page.on("framenavigated", logger.handle_navigation)

        # Set initial URL and navigate
        await page.goto(url, wait_until="networkidle")
        print(f"Browser is open and logging requests from {url}")
        print("Navigate freely. Press Ctrl+C to end the session.")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nSaving final request logs...")
            for url, data in logger.page_requests.items():
                with open(data["log_file"], "a") as f:
                    json.dump(data["requests"], f, indent=2)
                print(f"Saved requests for {url} to {data['log_file']}")


if __name__ == "__main__":
    asyncio.run(capture_requests())
