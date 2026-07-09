from django.contrib import admin
from django.urls import path
from chat.views import chat_api      # ← 引入你的 view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', chat_api),     # ← 加上这一行
]
