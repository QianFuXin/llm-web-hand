import json
import time

from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


def create_driver():
    chrome_options = Options()
    chrome_options.debugger_address = "127.0.0.1:9222"
    return webdriver.Chrome(options=chrome_options)


def fetch_url_content(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        body_text = soup.body.get_text(separator="\n", strip=True) if soup.body else ""
        title = driver.title
        return {"url": url, "title": title, "content": body_text}
    except Exception as e:
        return {"url": url, "error": str(e)}


def safe_get(driver, url, timeout=10):
    driver.get(url)
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def search_google_direct_and_fetch(keyword, results_number=10):
    driver = create_driver()
    results = []
    try:
        # 1. 构造搜索 URL
        query = keyword.replace(" ", "+")
        search_url = f"https://www.google.com/search?q={query}"
        # 2. 打开搜索结果页
        safe_get(driver, search_url)
        # 3. 等待 h3 存在
        WebDriverWait(driver, 10).until(
            lambda d: d.find_elements(By.XPATH, "//h3")
        )
        # 4. 获取前十个搜索结果链接
        h3_elements = driver.find_elements(By.XPATH, "//h3")
        urls = []

        for h3 in h3_elements:
            try:
                parent = h3.find_element(By.XPATH, "./ancestor::a")
                href = parent.get_attribute("href")
                if href:
                    urls.append(href)
                if len(urls) >= results_number:
                    break
            except:
                continue
        # 5. 遍历提取每个页面内容
        for url in urls:
            result = fetch_url_content(driver, url)
            results.append(result)
            time.sleep(1)

        return results

    except Exception as e:
        return {"error": str(e)}
    finally:
        driver.quit()


if __name__ == '__main__':
    keyword = '东方树叶'
    data = search_google_direct_and_fetch(keyword, results_number=2)
    print(json.dumps(data, indent=2, ensure_ascii=False))
