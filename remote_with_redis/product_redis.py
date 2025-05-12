import os
import time
import json

from redis import Redis

from remote_with_redis.config import REDIS_URL, QUEUE_NAME, REDIS_EX
from selenium.common.exceptions import WebDriverException

from utils import create_driver, fetch_url_content


def main():
    print("Worker started, waiting for tasks...")
    redis_conn = Redis.from_url(REDIS_URL)
    driver = None
    error_count = 0
    task_count = 0
    max_errors = 10
    max_tasks = 100

    while True:
        try:
            if driver is None:
                print("[*] Initializing Chrome driver...")
                driver = create_driver()

            task = redis_conn.brpop(QUEUE_NAME, timeout=0)
            if task:
                _, raw_data = task
                data = json.loads(raw_data)
                url = data.get("url")

                if not url:
                    print("[!] Received task without URL")
                    continue
                print(f"[x] Processing URL: {url}")
                result = redis_conn.get(url)
                if not result:
                    result = fetch_url_content(driver, url)
                    redis_conn.set(url, json.dumps(result, ensure_ascii=False), ex=REDIS_EX)
                    print("[✓] Fetched and cached.")
                else:
                    print("[✓] Cache hit.")

                task_count += 1
                if task_count >= max_tasks:
                    print("[*] Restarting Chrome after max tasks.")
                    driver.quit()
                    driver = None
                    task_count = 0

        except WebDriverException as we:
            print(f"[!] WebDriver Error: {we}")
            error_count += 1
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                driver = None

        except Exception as e:
            print(f"[!] Error: {e}")
            error_count += 1

        if error_count >= max_errors:
            print("[!!] Too many errors, resetting driver.")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            driver = None
            error_count = 0

        time.sleep(0.5)  # 防止 CPU 占用过高


if __name__ == "__main__":
    main()
