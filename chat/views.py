from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .llm_client import chat_with_history


@api_view(['POST'])            # ← 只接受 POST 请求
def chat_api(request):
    """聊天 API 端点

    请求格式（JSON）：
    {
        "message": "你好",
        "session_id": "user-001"
    }

    响应格式（JSON）：
    {
        "reply": "你好！有什么可以帮你的？",
        "session_id": "user-001"
    }
    """
    # 1. 从请求中取参数（Django 已经把 HTTP 请求解析成了 request 对象）
    user_input = request.data.get('message', '')
    session_id = request.data.get('session_id', 'default')

    # 2. 校验（不能让空消息进到 LLM）
    if not user_input.strip():
        return Response(
            {'error': '消息不能为空'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 3. 调你的聊天逻辑（这就是你在 chat_with_memory.py 里写的函数！）
    try:
        reply = chat_with_history(session_id, user_input)
    except Exception as e:
        return Response(
            {'error': f'AI 暂时无法回复: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # 4. 返回 JSON 响应
    return Response({
        'reply': reply,
        'session_id': session_id,
    })

# Create your views here.
