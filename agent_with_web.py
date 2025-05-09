import time
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from config import api_key
from utils import fetch_url_content, create_driver, search_google_direct_and_fetch

model = ChatOpenAI(
    api_key=api_key,
    model="Qwen/Qwen2.5-72B-Instruct",
    base_url="https://api.siliconflow.cn/v1",
    temperature=0.01
)


@tool
def get_content_with_url(url: str) -> str:
    """根据URL地址，使用浏览器渲染后返回页面文本内容

    Args:
        url: 需要访问的网址
    Returns:
        页面文本内容
    """
    driver = create_driver()
    res = fetch_url_content(driver, url)
    driver.quit()
    return str(res)


@tool
def search_content_with_google(keyword):
    """根据关键词使用 Google 搜索，提取前若干网页的标题和正文内容

        Args:
            keyword: 搜索关键词
        Returns:
            包含每个搜索结果的URL、标题和正文内容的文本
    """
    res = search_google_direct_and_fetch(keyword, results_number=2)
    return str(res)


@tool
def write_to_file(file_name: str, content: str) -> str:
    """将内容写入本地文件

    Args:
        file_name: 文件名
        content: 要写入的文本内容
    Returns:
        写入的提示信息
    """
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            # 修正可能的字符串字面量换行问题
            if "\\n" in content and "\n" not in content:
                content = content.replace("\\n", "\n")
            f.write(content)
        return f"内容已成功写入文件：{file_name}"
    except Exception as e:
        return f"写入文件失败：{str(e)}"


memory = MemorySaver()
tools = [get_content_with_url, search_content_with_google, write_to_file]
agent_executor = create_react_agent(model, tools, checkpointer=memory)

config = {"configurable": {"thread_id": str(int(time.time()))}}

while 1:
    question = input("用户：")
    print("机器人：", end="")
    for chunk, metadata in agent_executor.stream({"messages": [HumanMessage(question)]},
                                                 config,
                                                 stream_mode="messages"):
        if isinstance(chunk, AIMessage):
            print(chunk.content, end="")
    print()

"""
请访问以下网页并总结其主要内容：https://www.ithome.com/0/851/586.htm。要求如下：1. 以清晰、简洁的语言撰写总结，适合写入 Markdown 文件。2. 总结应覆盖网页的核心信息，避免复制粘贴原文。3. 使用 Markdown 格式组织输出（如标题、小节等）。4. 将总结内容保存为 `.md` 文件。5. 文件名请根据内容含义自动生成（使用简短英文拼音或英文关键词，便于识别和管理）。
帮我搜索今天北京的天气怎么样
"""
