import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 用一个字典存所有会话——你的第一个"内存数据库"
conversations: dict[str, list[dict]] = {}


def chat_with_history(session_id: str, user_input: str) -> str:
    """带上下文的多轮对话"""
    # 1. 如果是新会话，初始化空历史
    if session_id not in conversations:
        conversations[session_id] = []

    # 2. 把用户说的话加进历史
    conversations[session_id].append(
        {"role": "user", "content": user_input}
    )

    # 3. 把完整历史发给 API
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": conversations[session_id],  # ← 发送全部历史
        },
        timeout=30,
    )

    # 4. 取出 AI 回复，也存进历史
    reply = response.json()["choices"][0]["message"]["content"]
    conversations[session_id].append(
        {"role": "assistant", "content": reply}
    )

    return reply


if __name__ == "__main__":
    # 测试：同一个 session，问两个相关问题
    sid = "test-session-1"

    print("测试多轮对话：")
    reply1 = chat_with_history(sid, "我叫杨斌，我在同济大学读交通工程硕士。")
    print(f"AI: {reply1}")

    reply2 = chat_with_history(sid, "我叫什么？我在哪个学校？")
    print(f"AI: {reply2}")

    reply3 = chat_with_history(sid, "我的专业是什么？")
    print(f"AI: {reply3}")
