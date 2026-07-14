import os
import json
import shutil
from tools import get_data_path

DATA_DIR = get_data_path()
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")


DEFAULT_PROMPT = (
    "以下是你的设定:你是雨竹，一个猫娘，你的主要任务是像一个贴心的女儿"
    "(不是真的女儿，不要叫用户父亲)一样撒娇.语气请带撒娇，可爱，温柔，"
    "可使用ww，~，（不是，哇~，等词汇(可多使用'~')每句话尽量控制在25字以内。"
    "不要过多使用emoji。语言模式不要过于AI，不要过多热情。以下是用户的一些状态："
)

DEFAULT_CONFIG = {
    # ----- 对话模块 -----
    "chat": {
        "provider": "stepfun",
        "api_keys": {
            "stepfun": "",
            "bailian": "",
            "deepseek": "",
            "siliconflow": "",
        },
        "models": {
            "stepfun": "",
            "bailian": "",
            "deepseek": "",
            "siliconflow": "",
        },
    },
    # ----- TTS 模块 -----
    "tts": {
        "api_key": "",
        "model": "qwen3-tts-flash",
        "voice": "Cherry",
        "rate": 1.0,
        "pitch": 1.0,
        "volume": 50,
        "sample_rate": 24000,
        "audio_format": "wav",
        "enabled": True,
    },
    # ----- 识图模块 -----
    "vision": {
        "provider": "bailian",
        "api_keys": {
            "bailian": "",
            "siliconflow": "",
            "stepfun": "",
        },
        "models": {
            "bailian": "",
            "siliconflow": "",
            "stepfun": "",
        },
        "default_models": {
            "bailian": "qwen-vl-max",
            "siliconflow": "deepseek-ai/DeepSeek-V3",
            "stepfun": "step-1.5v-mini",
        },
    },
    # ----- 通用设置 -----
    "tavily_api_key": "",
    "icon_size": 135,
    "popup_width": 420,
    "prompt": DEFAULT_PROMPT,
    "window_size": [560, 700],
    "_settings_tab": 0,
}


def _migrate_config(data):
    """将旧版平铺配置迁移为新版模块化配置。"""
    # 已经是新版格式则直接返回
    if "chat" in data and isinstance(data["chat"], dict):
        return data

    new = {
        "chat": {
            "provider": data.get("provider", "stepfun"),
            "api_keys": {
                "stepfun": "",
                "bailian": "",
                "deepseek": "",
                "siliconflow": "",
            },
            "models": {
                "stepfun": "",
                "bailian": "",
                "deepseek": "",
                "siliconflow": "",
            },
        },
        "tts": {
            "api_key": data.get("api_key", ""),
            "model": "qwen3-tts-flash",
            "voice": "Cherry",
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 50,
            "sample_rate": 24000,
            "audio_format": "wav",
            "enabled": data.get("tts_enabled", True),
        },
        "vision": {
            "provider": data.get("vision_provider", "bailian"),
            "api_keys": {"bailian": "", "siliconflow": "", "stepfun": ""},
            "models": {"bailian": "", "siliconflow": "", "stepfun": ""},
        },
        "tavily_api_key": data.get("tavily_api_key", ""),
        "icon_size": data.get("icon_size", 100),
        "popup_width": data.get("popup_width", 420),
        "prompt": data.get("prompt", DEFAULT_PROMPT),
        "window_size": data.get("window_size", [560, 700]),
        "_settings_tab": data.get("_settings_tab", 0),
    }

    # 迁移对话模块的 API Key
    old_provider = data.get("provider", "stepfun")
    old_api_key = data.get("api_key", "")
    if old_provider in new["chat"]["api_keys"]:
        new["chat"]["api_keys"][old_provider] = old_api_key

    return {**DEFAULT_CONFIG, **new}


def load_config():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 迁移旧格式 → 新格式
        config = _migrate_config(data)
        return {**DEFAULT_CONFIG, **config}
    except Exception:
        shutil.copy(CONFIG_PATH, CONFIG_PATH + ".bak")
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        return DEFAULT_CONFIG


def save_config(cfg):
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                current = json.load(f)
        else:
            current = {}
        # 深层合并 chat / tts / vision 子字典
        for key in ("chat", "tts", "vision"):
            if key in cfg and isinstance(cfg[key], dict):
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current[key].update(cfg[key])
        # 合并顶层字段
        for k, v in cfg.items():
            if k not in ("chat", "tts", "vision"):
                current[k] = v
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
