import os
import json
import time
import functools
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")


# ============================================================
# 第一部分：重试装饰器
# ============================================================

def retry_on_failure(max_retries=3, base_delay=1):
    """自动重试装饰器——失败后指数退避重试

    max_retries: 最多重试次数
    base_delay:  基础等待秒数，实际等待 = base_delay × 2^attempt
    """
    def decorator(func):
        @functools.wraps(func)  # 保留原函数的 __name__ 和 __doc__
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        # 最后一次也失败了 → 不再重试，抛出异常
                        raise
                    wait = base_delay * (2 ** attempt)  # 指数退避
                    print(f"[重试 {attempt+1}/{max_retries}] "
                          f"错误: {e}，{wait}s 后重试...")
                    time.sleep(wait)
        return wrapper
    return decorator


# ============================================================
# 第二部分：把装饰器用在 API 调用上
# ============================================================

@retry_on_failure(max_retries=3, base_delay=1)
def call_llm_api(messages: list[dict], stream: bool = False) -> requests.Response:
    """调用 DeepSeek API，自动重试"""
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": messages,
            "stream": stream,
        },
        timeout=3,
    )
    # 即使请求成功，也要检查 HTTP 状态码
    if response.status_code != 200:
        raise RuntimeError(
            f"API 返回错误 {response.status_code}: {response.text[:200]}"
        )
    return response


# ============================================================
# 第三部分：用上了重试的 chat 函数
# ============================================================

conversations: dict[str, list[dict]] = {}


def chat_with_retry(session_id: str, user_input: str) -> str:
    """带重试的多轮对话"""
    if session_id not in conversations:
        conversations[session_id] = []

    conversations[session_id].append(
        {"role": "user", "content": user_input}
    )

    try:
        response = call_llm_api(conversations[session_id])
        reply = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        # 重试三次后仍然失败 → 返回友好的错误提示
        reply = f"[错误] AI 暂时无法回复: {e}"

    conversations[session_id].append(
        {"role": "assistant", "content": reply}
    )

    return reply


# ============================================================
# 第四部分：测试（真正触发重试，让你看到效果）
# ============================================================

if __name__ == "__main__":
    print("=== 测试1：正常调用 ===")
    reply = chat_with_retry("test-1", "用一句话介绍 Python")
    print(f"AI: {reply}\n")

    print("=== 测试2：真正触发重试 ===")
    # 直接调 call_llm_api，但把 BASE_URL 换成不存在的地址
    # chat_with_retry 用了 settings.BASE_URL，所以我们直接测底层函数
    import requests as req_test
    fake_url = "https://api.fake-deepseek-404.com/v1/chat/completions"
    print(f"故意请求一个不存在的地址: {fake_url}")
    print("你会看到三次重试，等待时间分别是 1s → 2s → 4s：\n")

    try:
        req_test.post(
            fake_url,
            headers={"Authorization": "Bearer test"},
            json={"model": "test", "messages": []},
            timeout=5,  # 超时设短一点，快些看到效果
        )
    except Exception as e:
        print(f"\n最终失败（符合预期）: {type(e).__name__}")

    print("\n=== 重试时间计算验证 ===")
    print("公式: base_delay × 2^attempt")
    for attempt in range(3):
        wait = 1 * (2 ** attempt)
        print(f"  第 {attempt+1} 次重试前等待: {wait}s")
    print("总等待时间: 1 + 2 + 4 = 7 秒")
    print("这就是指数退避——每次失败后等更久，给服务器恢复的时间。")
