import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

conversations: dict[str, list[dict]] = {}


def chat_stream(session_id: str, user_input: str):
    """流式多轮对话——逐字输出"""
    # 初始化会话
    if session_id not in conversations:
        conversations[session_id] = []

    # 把用户消息加进历史
    conversations[session_id].append(
        {"role": "user", "content": user_input}
    )

    # 发起流式请求
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": conversations[session_id],
            "stream": True,  # ← 告诉服务器：逐块发给我
        },
        stream=True,  # ← 告诉 requests：别一次性读完
        timeout=30,
    )

    # 逐块读取服务器的推送
    full_reply = ""
    for line in response.iter_lines():
        if not line:
            continue
        # 每行格式：data: {"choices":[{"delta":{"content":"一"}}]}
        line = line.decode("utf-8")
        if line.startswith("data: "):
            data_str = line[6:]  # 去掉 "data: " 前缀
            if data_str == "[DONE]":
                break  # 流结束
            chunk = json.loads(data_str)
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                word = delta["content"]
                print(word, end="", flush=True)  # 逐字打印，不换行
                full_reply += word

    print()  # 最后换行

    # 把完整回复存进历史
    conversations[session_id].append(
        {"role": "assistant", "content": full_reply}
    )

    return full_reply


if __name__ == "__main__":
    sid = "stream-test"

    print("流式对话测试：")
    reply1 = chat_stream(sid, "用三句话介绍同济大学")
    print(f"\n[完整回复长度：{len(reply1)} 字]")

    reply2 = chat_stream(sid, "刚才提到的三个点，展开说说第一个")
    print(f"\n[完整回复长度：{len(reply2)} 字]")
