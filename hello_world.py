from selenium import webdriver
import time


# 连接到新的浏览器
def new_chrome():
    b = webdriver.Chrome()
    b.get('https://www.baidu.com')
    time.sleep(5)
    b.quit()


# 连接已有浏览器
def exist_chrome():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.debugger_address = "127.0.0.1:9222"

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://example.com")
    print(driver.title)
    driver.quit()


if __name__ == '__main__':
    # 测试浏览器驱动、新创建的调试浏览器是否正常
    new_chrome()
    exist_chrome()
