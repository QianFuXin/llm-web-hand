import json
import time
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from redis import Redis

from config import api_key
from remote_with_redis.config import REDIS_URL, QUEUE_NAME

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
    redis_conn = Redis.from_url(REDIS_URL)

    task_data = json.dumps({"url": url})
    redis_conn.lpush(QUEUE_NAME, task_data)
    timeout = 10
    poll_interval = 0.5
    waited = 0
    while waited < timeout:
        res = redis_conn.get(url)
        if res:
            res_str = res.decode('utf-8')
            return str(res_str)
        time.sleep(poll_interval)
        waited += poll_interval
    return str("no data")


memory = MemorySaver()
tools = [get_content_with_url]
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
