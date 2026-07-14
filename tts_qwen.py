"""Qwen3-TTS-Flash 非实时语音合成模块。

调用阿里百炼 DashScope 的 aigc/multimodal-generation/generation 接口，
使用 qwen3-tts-flash 模型将文本转为语音，通过 winsound 播放。

API 文档: https://help.aliyun.com/zh/model-studio/qwen-tts-api

注意: Qwen-TTS 非实时 HTTP API 不直接支持 rate/pitch/volume/sample_rate/format
等参数，这些参数仅 CosyVoice 端点支持。音频始终以 WAV 格式返回。
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


# Qwen3-TTS-Flash 预置音色列表（非实时 HTTP API）
QWEN_VOICES = [
    ("Cherry", "芊悦（阳光小姐姐）"),
    ("Serena", "苏瑶（温柔小姐姐）"),
    ("Ethan", "晨煦（阳光男生）"),
    ("Chelsie", "千雪（二次元女友）"),
    ("Momo", "茉兔（撒娇搞怪）"),
    ("Vivian", "十三（可爱小暴躁）"),
    ("Moon", "月白（率性帅气）"),
    ("Maia", "四月（知性温柔）"),
    ("Kai", "凯（磁性男声）"),
    ("Nofish", "不吃鱼（设计师男声）"),
    ("Bella", "萌宝（小萝莉）"),
    ("Mia", "乖小妹（温顺乖巧）"),
    ("Mochi", "沙小弥（聪明小大人）"),
    ("Nini", "邻家妹妹（软糯甜声）"),
    ("Bunny", "萌小姬（萌属性萝莉）"),
]

# Qwen3-TTS-Flash 非实时 HTTP API 端点
# 注意: 这是 DashScope MultiModalConversation 统一接口,
# 与 CosyVoice 的 SpeechSynthesizer 端点不同。
TTS_API_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/"
    "aigc/multimodal-generation/generation"
)


class QwenTTSThread(QThread):
    """后台线程：调用 qwen3-tts-flash API → 下载音频 → 播放。"""

    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        api_key: str,
        text: str,
        voice: str = "Cherry",
        language_type: str = "Chinese",
    ):
        super().__init__()
        self._api_key = api_key
        self._text = text
        self._voice = voice
        self._language_type = language_type
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
            # 1. 调用 DashScope MultiModalConversation API (qwen3-tts-flash)
            # ------------------------------------------------------------
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": "qwen3-tts-flash",
                "input": {
                    "text": self._text.strip(),
                    "voice": self._voice,
                    "language_type": self._language_type,
                },
            }

            resp = requests.post(TTS_API_URL, headers=headers, json=body, timeout=60)

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
            # 2. 解析响应，获取音频 URL
            # ------------------------------------------------------------
            resp_data = resp.json()
            audio_url = resp_data.get("output", {}).get("audio", {}).get("url", "")

            if not audio_url:
                self.error_occurred.emit("TTS 响应中未找到音频 URL")
                return

            if self._stopped:
                return

            # ------------------------------------------------------------
            # 3. 下载音频文件到临时路径 (API 始终返回 WAV 格式)
            # ------------------------------------------------------------
            fd, path = tempfile.mkstemp(suffix=".wav", prefix="qwen_tts_")
            os.close(fd)
            self._temp_path = path

            audio_resp = requests.get(audio_url, timeout=60)
            if audio_resp.status_code != 200:
                self.error_occurred.emit(f"音频下载失败 ({audio_resp.status_code})")
                self._cleanup_temp()
                return

            with open(path, "wb") as f:
                f.write(audio_resp.content)

            if self._stopped:
                self._cleanup_temp()
                return

            # ------------------------------------------------------------
            # 4. 播放音频 (Windows winsound)
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
        """使用 Windows MCI API 阻塞播放 WAV 文件（比 winsound 更可靠）。"""
        import ctypes
        from ctypes import wintypes

        mci = ctypes.windll.winmm.mciSendStringW
        mci.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR,
                        wintypes.UINT, wintypes.HANDLE]
        mci.restype = wintypes.UINT

        # 确保路径中没有空格问题 - 用短路径或加引号
        escaped = f'"{path}"'
        open_cmd = f'open {escaped} type waveaudio alias qwen_tts'
        play_cmd = 'play qwen_tts wait'
        close_cmd = 'close qwen_tts'

        ret = mci(open_cmd, None, 0, None)
        if ret != 0:
            raise RuntimeError(f"MCI open 失败 (code={ret})")

        try:
            ret = mci(play_cmd, None, 0, None)
            if ret != 0:
                raise RuntimeError(f"MCI play 失败 (code={ret})")
        finally:
            mci(close_cmd, None, 0, None)

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
