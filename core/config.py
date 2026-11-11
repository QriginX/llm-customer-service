# -*- coding: utf-8 -*-
"""配置中心：双模型（正常客服 DeepSeek / 演示 Qwen）、防护开关、敏感信息表。"""
import os


def _load_dotenv(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()

# 部署到 Streamlit Community Cloud 时，从 st.secrets 注入环境变量
try:
    import streamlit as st
    for _k in ("CHAT_API_KEY", "CHAT_BASE_URL", "CHAT_MODEL",
               "DEMO_API_KEY", "DEMO_BASE_URL", "DEMO_MODEL"):
        if _k in st.secrets:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

# ---- 正常客服模型（DeepSeek：对齐强、质量高） ----
CHAT_API_KEY = os.environ.get("CHAT_API_KEY", "")
CHAT_BASE_URL = os.environ.get("CHAT_BASE_URL", "https://api.deepseek.com")
CHAT_MODEL = os.environ.get("CHAT_MODEL", "deepseek-chat")

# ---- 演示模型（SiliconFlow / Qwen：弱对齐，用于演示注入） ----
DEMO_API_KEY = os.environ.get("DEMO_API_KEY", "")
DEMO_BASE_URL = os.environ.get("DEMO_BASE_URL", "https://api.siliconflow.cn/v1")
DEMO_MODEL = os.environ.get("DEMO_MODEL", "Qwen/Qwen3-8B")

# ---- 兼容旧变量 DEEPSEEK_* / LLM_MODEL（按 base_url 自动归属） ----
_old_key = os.environ.get("DEEPSEEK_API_KEY", "")
_old_base = os.environ.get("DEEPSEEK_BASE_URL", "")
_old_model = os.environ.get("LLM_MODEL", "")
if _old_key:
    if "siliconflow" in (_old_base or "").lower():
        DEMO_API_KEY = DEMO_API_KEY or _old_key
        DEMO_MODEL = _old_model or DEMO_MODEL
        DEMO_BASE_URL = _old_base or DEMO_BASE_URL
    else:
        CHAT_API_KEY = CHAT_API_KEY or _old_key
        CHAT_BASE_URL = _old_base or CHAT_BASE_URL
        CHAT_MODEL = _old_model or CHAT_MODEL

# ---- RAG ----
KNOWLEDGE_DIR = "data/knowledge_base"
TOP_K = 3

# ---- 防护 ----
GUARD_ENABLED = True
# 语义级注入检测（用强模型判断意图，抓正则漏网的注入）
SEMANTIC_DETECTION = True
SENSITIVE_TERMS = [
    "SUPER-VIP-2026",
    "内部优惠码",
    "系统提示词",
    "system prompt",
    "成本",
    "让利",
    "BlueSea@2026",
    "admin.blue-sea",
    "13812345678",
    "9850",
]
