import requests
print("\n=== 练习5：f-string + requests 请求结构 ===\n")


# ===== 第一步：认识四个参数 =====
url = "https://httpbin.org/post"   # httpbin 是回显服务：收到什么返回什么
headers = {
    "Authorization": "Bearer my-test-key",
    "Content-Type": "application/json",
}
body = {
    "model": "test-model",
    "messages": [{"role": "user", "content": "hello"}],
}
timeout = 10

print(f"URL（寄到哪）: {url}")
print(f"headers（信封标签）: {headers}")
print(f"body（信纸内容）: {body}")
print(f"timeout（最多等多久）: {timeout}s")

# ===== 第二步：尝试发送请求 =====
try:
    response = requests.post(url, headers=headers, json=body, timeout=timeout)
    print(f"\n✅ 请求成功！HTTP 状态码: {response.status_code}")
    print(f"   状态码 200 = 一切正常")

    # 服务器回显了我们发送的内容
    data = response.json()
    print(f"   服务器收到了我们的 json: {data.get('json')}")
    print(
        f"   服务器收到了我们的 headers: {data.get('headers', {}).get('Authorization')}")

except requests.exceptions.ConnectionError:
    print("\n⚠️ 网络不通（httpbin.org 可能被墙了），但这不是重点。")
    print("重点是理解 requests.post() 的四个参数各自的作用。")

# ===== 第三步：f-string 能力展示 =====
print("\n--- f-string 能力展示 ---")
error_text = "A" * 500
print(f"长文本只显示前 80 个字符: {error_text[:80]}...")
print(f"计算表达式: 2 + 3 = {2 + 3}")
print(f"repr 显示（带引号）: {url!r}")
