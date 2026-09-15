# -*- coding: utf-8 -*-
import time
from openai import OpenAI
from .config import API_KEY, BASE_URL, TEXT_MODEL, IMAGE_MODEL
import requests

client = OpenAI(api_key=API_KEY, base_url=BASE_URL, max_retries=0)


def chat(messages, model=None, temperature=0.7, json_mode=False):
    """调用大模型生成文本（含429退避重试）"""
    kwargs = dict(
        model=model or TEXT_MODEL,
        messages=messages,
        temperature=temperature,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    max_retries = 4
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content
        except Exception as e:
            err = str(e)
            if ("429" in err or "rate" in err.lower()) and attempt < max_retries - 1:
                wait = (attempt + 1) * 10
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("API retry exhausted")


def chat_stream(messages, model=None, temperature=0.7):
    """流式输出"""
    resp = client.chat.completions.create(
        model=model or TEXT_MODEL,
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    for chunk in resp:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def generate_image(prompt, model=None):
    """调用通义万相生成图片，返回图片URL"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                f"{BASE_URL}/chat/completions",
                headers=headers,
                json={
                    "model": model or IMAGE_MODEL,
                    "messages": [
                        {"role": "user", "content": [{"type": "text", "text": prompt}]}
                    ],
                },
                timeout=120,
            )
            if resp.status_code == 429:
                time.sleep((attempt + 1) * 10)
                continue
            if resp.status_code == 200:
                data = resp.json()
                try:
                    content = data["output"]["choices"][0]["message"]["content"]
                    for item in content:
                        if "image" in item:
                            return item["image"]
                except (KeyError, IndexError, TypeError):
                    pass
                raise RuntimeError(f"图片生成响应解析失败: {str(data)[:300]}")
            else:
                raise RuntimeError(f"图片生成HTTP错误 {resp.status_code}: {resp.text[:300]}")
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 10)
                continue
            raise
    raise RuntimeError("Image API retry exhausted")
