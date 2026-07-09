import os
import requests
from django.conf import settings

# ============================================================
# 对话存储（暂时还是内存字典，阶段二会换成数据库）
# ============================================================
conversations: dict[str, list[dict]] = {}


def call_llm_api(messages: list[dict], stream: bool = False) -> requests.Response:
    """调用 DeepSeek API（用 Django settings 的配置）"""
    response = requests.post(
        f"{settings.LLM_BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.LLM_MODEL,
            "messages": messages,
            "stream": stream,
        },
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"API 返回错误 {response.status_code}: {response.text[:200]}"
        )
    return response


def chat_with_history(session_id: str, user_input: str) -> str:
    """多轮对话——跟你在 chat_with_memory.py 里写的一样"""
    if session_id not in conversations:
        conversations[session_id] = []

    # 加用户消息
    conversations[session_id].append(
        {"role": "user", "content": user_input}
    )

    # 截断历史（防 token 超限）
    MAX_ROUNDS = getattr(settings, 'MAX_CONTEXT_ROUNDS', 20)
    history = conversations[session_id][-(MAX_ROUNDS * 2):]

    # 调用 API
    response = call_llm_api(history)

    # 取回复
    reply = response.json()["choices"][0]["message"]["content"]

    # 加 AI 回复
    conversations[session_id].append(
        {"role": "assistant", "content": reply}
    )

    return reply
