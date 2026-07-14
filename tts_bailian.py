"""阿里百炼 (DashScope) TTS 合成模块。

调用 CosyVoice 模型将文本转为语音，通过 winsound 播放。
"""

import json
import os
import tempfile
import warnings

from PyQt5.QtCore import QThread, pyqtSignal

try:
    import requests
except ImportError:
    requests = None  # type: ignore


# CosyVoice 预置的音色列表
BAILIAN_VOICES = [
    ("longxiaochun", "龙小纯 (女声)"),
    ("longmei", "龙梅 (女声)"),
    ("longyu", "龙宇 (男声)"),
    ("longtao", "龙涛 (男声)"),
    ("longbao", "龙宝 (童声)"),
    ("longjuan", "龙娟 (女声)"),
    ("longheng", "龙恒 (男声)"),
    ("longtian", "龙甜 (女声)"),
    ("longgang", "龙刚 (男声)"),
    ("longjia", "龙佳 (女声)"),
]

TTS_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/tts/text-to-speech"


class BailianTTSThread(QThread):
    """后台线程：调用阿里百炼 TTS API → 下载音频 → 播放。"""

    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        api_key: str,
        text: str,
        voice: str = "longxiaochun",
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: int = 50,
    ):
        super().__init__()
        self._api_key = api_key
        self._text = text
        self._voice = voice
        self._speed = speed
        self._pitch = pitch
        self._volume = volume
        self._stopped = False
        self._temp_path: str | None = None

    def stop(self):
        self._stopped = True

    def run(self):
        if requests is None:
            self.error_occurred.emit("缺少 requests 库，无法调用 TTS API")
            return

        if not self._api_key:
            self.error_occurred.emit("未设置阿里百炼 API Key")
            return

        if not self._text or not self._text.strip():
            self.error_occurred.emit("合成的文本为空")
            return

        try:
            # ------------------------------------------------------------
            # 1. 调用 DashScope TTS API
            # ------------------------------------------------------------
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": "cosyvoice-v1",
                "input": {"text": self._text.strip()},
                "parameters": {
                    "voice": self._voice,
                    "speed": self._speed,
                    "pitch": self._pitch,
                    "volume": self._volume,
                },
            }

            resp = requests.post(TTS_API_URL, headers=headers, json=body, timeout=30)

            if self._stopped:
                return

            if resp.status_code != 200:
                detail = ""
                try:
                    detail = resp.json().get("message", resp.text[:200])
                except Exception:
                    detail = resp.text[:200]
                self.error_occurred.emit(f"TTS API 错误 ({resp.status_code}): {detail}")
                return

            # ------------------------------------------------------------
            # 2. 音频数据保存到临时文件
            # ------------------------------------------------------------
            content_type = resp.headers.get("Content-Type", "")
            suffix = ".mp3" if "mp3" in content_type else ".wav"

            fd, path = tempfile.mkstemp(suffix=suffix, prefix="bailian_tts_")
            os.close(fd)
            self._temp_path = path

            with open(path, "wb") as f:
                f.write(resp.content)

            if self._stopped:
                self._cleanup_temp()
                return

            # ------------------------------------------------------------
            # 3. 播放音频 (Windows winsound)
            # ------------------------------------------------------------
            self._play_audio(path)

            if not self._stopped:
                self.finished.emit()

        except requests.Timeout:
            self.error_occurred.emit("TTS API 请求超时，请检查网络")
        except requests.ConnectionError:
            self.error_occurred.emit("无法连接到 TTS API，请检查网络")
        except Exception as e:
            self.error_occurred.emit(f"TTS 合成失败: {e}")
        finally:
            self._cleanup_temp()

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _play_audio(self, path: str):
        """阻塞播放音频文件。"""
        import winsound

        flags = winsound.SND_FILENAME | winsound.SND_NODEFAULT
        winsound.PlaySound(path, flags)

    def _cleanup_temp(self):
        """删除临时音频文件。"""
        if self._temp_path and os.path.exists(self._temp_path):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    os.remove(self._temp_path)
            except Exception:
                pass
            self._temp_path = None
