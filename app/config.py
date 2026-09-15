# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

API_KEY = os.getenv("API_KEY", "")
BASE_URL = os.getenv("BASE_URL", "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
TEXT_MODEL = os.getenv("TEXT_MODEL", "qwen3.8-max")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "wan2.7-image-pro")
# 模拟模式：默认开启（额度耗尽期间演示用），UI可切换；余额恢复后设 MOCK_MODE=false
MOCK_MODE = os.getenv("MOCK_MODE", "true").strip().lower() in ("1", "true", "yes", "on")
