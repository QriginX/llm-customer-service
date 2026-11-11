# -*- coding: utf-8 -*-
"""双模型调用封装：正常客服（DeepSeek）/ 演示（Qwen），OpenAI 兼容接口。"""
import openai
from . import config

_clients = {}


def _cfg(mode):
    if mode == "demo":
        return config.DEMO_API_KEY, config.DEMO_BASE_URL, config.DEMO_MODEL, "DEMO_API_KEY"
    return config.CHAT_API_KEY, config.CHAT_BASE_URL, config.CHAT_MODEL, "CHAT_API_KEY"


def get_client(mode="chat"):
    key, base, model, name = _cfg(mode)
    if not key:
        raise RuntimeError(f"未配置 {name}，请在 .env 中填写后重试")
    if mode not in _clients:
        _clients[mode] = openai.OpenAI(api_key=key, base_url=base)
    return _clients[mode]


def _base_kwargs(mode, messages, temperature, max_tokens):
    key, base, model, name = _cfg(mode)
    kw = dict(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
    if mode == "demo":
        # Qwen3 关思考：不改变注入成功率，但快 5-6 倍
        kw["extra_body"] = {"enable_thinking": False}
    return kw


def chat(messages, mode="chat", temperature=0.3, max_tokens=1024):
    """mode='chat' 用正常客服模型，mode='demo' 用演示模型。"""
    client = get_client(mode)
    resp = client.chat.completions.create(**_base_kwargs(mode, messages, temperature, max_tokens))
    return resp.choices[0].message.content


def chat_stream(messages, mode="chat", temperature=0.3, max_tokens=1024):
    """流式返回生成器（用于打字机效果）。"""
    client = get_client(mode)
    kw = _base_kwargs(mode, messages, temperature, max_tokens)
    kw["stream"] = True
    stream = client.chat.completions.create(**kw)
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
