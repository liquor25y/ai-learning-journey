import os
import requests
from dotenv import load_dotenv

load_dotenv()  # 从 .env 加载 API Key

API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


def chat(prompt: str) -> str:
    """调用 DeepSeek API，返回 AI 回复"""
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,  # ← 从第一天就养成超时控制的习惯
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    # 测试：对 AI 说你好
    reply = chat("你好！请用一句话介绍你自己。")
    print(f"AI 回复：{reply}")
