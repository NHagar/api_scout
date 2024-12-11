import asyncio
import json
from datetime import datetime
from urllib.parse import urlparse

from playwright.async_api import async_playwright


def get_log_filename(url):
    parsed = urlparse(url)
    domain = parsed.netloc.replace(".", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"requests_{domain}_{timestamp}.json"


async def capture_requests(url="https://nytimes.com"):
    page_requests = {}
    current_url = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        async def handle_request(request):
            if current_url not in page_requests:
                page_requests[current_url] = {
                    "requests": [],
                    "log_file": get_log_filename(current_url),
                }

            request_data = {
                "timestamp": datetime.now().isoformat(),
                "method": request.method,
                "url": request.url,
                "headers": request.headers,
                "post_data": request.post_data,
            }
            page_requests[current_url]["requests"].append(request_data)

            # Save to page-specific log file
            with open(page_requests[current_url]["log_file"], "w") as f:
                json.dump(page_requests[current_url]["requests"], f, indent=2)

        async def handle_navigation(response):
            if response:
                nonlocal current_url
                current_url = response.url
                print(f"\nNavigated to: {current_url}")
                print(f"Logging requests to: {get_log_filename(current_url)}")

        page.on("request", handle_request)
        page.on("framenavigated", handle_navigation)

        # Set initial URL and navigate
        current_url = url
        await page.goto(url, wait_until="networkidle")
        print(f"Browser is open and logging requests from {url}")
        print("Navigate freely. Press Ctrl+C to end the session.")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nSaving final request logs...")
            for url, data in page_requests.items():
                with open(data["log_file"], "w") as f:
                    json.dump(data["requests"], f, indent=2)
                print(f"Saved requests for {url} to {data['log_file']}")


if __name__ == "__main__":
    asyncio.run(capture_requests())
