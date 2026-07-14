"""TTS (文本转语音) 管理器。

支持三种引擎：
- pyttsx3 : 离线本地引擎
- bailian  : 阿里百炼 API (CosyVoice) — 旧版，保留兼容
- qwen     : 阿里百炼 API (Qwen3-TTS-Flash)
"""

from PyQt5.QtCore import QObject, QThread, pyqtSignal


# ======================================================================
# pyttsx3 引擎（离线）
# ======================================================================

class TTSThread(QThread):
    """后台 TTS 朗读线程 (pyttsx3)，避免阻塞 UI。"""

    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, engine_name, text, voice="", speed=1.0):
        super().__init__()
        self._engine_name = engine_name
        self._text = text
        self._voice = voice
        self._speed = speed
        self._stopped = False

    def stop(self):
        self._stopped = True

    def run(self):
        try:
            import pyttsx3
            engine = pyttsx3.init()
        except Exception as e:
            self.error_occurred.emit(f"TTS 引擎初始化失败: {e}")
            return

        try:
            rate = engine.getProperty("rate")
            engine.setProperty("rate", int(rate * self._speed))

            if self._voice:
                voices = engine.getProperty("voices")
                for v in voices:
                    if self._voice in v.id:
                        engine.setProperty("voice", v.id)
                        break

            engine.startLoop(False)

            def on_word(name, location, length):
                if self._stopped:
                    engine.endLoop()
                    return

            engine.connect("started-word", on_word)
            engine.say(self._text)

            if not self._stopped:
                engine.iterate()
                while engine.isBusy() and not self._stopped:
                    engine.iterate()
                    QThread.msleep(50)

            engine.endLoop()

            if not self._stopped:
                self.finished.emit()

        except Exception as e:
            self.error_occurred.emit(f"TTS 朗读出错: {e}")


# ======================================================================
# TTS 管理器
# ======================================================================

class TTSManager(QObject):
    """TTS 管理器，对外提供 speak / stop / is_speaking 接口。"""

    error_occurred = pyqtSignal(str)
    speaking_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        # 保存旧线程引用，防止 wait() 超时后线程仍在运行被 GC 销毁
        self._old_threads = set()
        # pyttsx3 配置
        self._engine_name = "qwen"  # 默认引擎改为 qwen
        self._voice = ""
        self._speed = 1.0
        # bailian 配置
        self._bailian_api_key = ""
        self._bailian_voice = "longxiaochun"
        self._bailian_speed = 1.0
        self._bailian_pitch = 1.0
        self._bailian_volume = 50
        # qwen 配置
        self._qwen_api_key = ""
        self._qwen_voice = "Cherry"
        self._speaking = False

    def configure(self, engine="qwen", voice="", speed=1.0,
                  bailian_api_key="", bailian_voice="longxiaochun",
                  bailian_speed=1.0, bailian_pitch=1.0, bailian_volume=50,
                  qwen_api_key="", qwen_voice="Cherry"):
        """更新 TTS 引擎配置，立即生效。如果正在朗读，先停止。"""
        if self._speaking:
            self.stop()
        self._engine_name = engine
        self._voice = voice
        self._speed = speed
        # bailian
        self._bailian_api_key = bailian_api_key
        self._bailian_voice = bailian_voice
        self._bailian_speed = bailian_speed
        self._bailian_pitch = bailian_pitch
        self._bailian_volume = bailian_volume
        # qwen
        self._qwen_api_key = qwen_api_key
        self._qwen_voice = qwen_voice

    def speak(self, text):
        """异步朗读文本。如果正在朗读则先停止再开始新朗读。"""
        if not text or not text.strip():
            return

        if self._speaking:
            self.stop()

        self._speaking = True

        if self._engine_name == "qwen":
            from tts_qwen import QwenTTSThread
            self._thread = QwenTTSThread(
                api_key=self._qwen_api_key,
                text=text,
                voice=self._qwen_voice,
            )
        elif self._engine_name == "bailian":
            from tts_bailian import BailianTTSThread
            self._thread = BailianTTSThread(
                api_key=self._bailian_api_key,
                text=text,
                voice=self._bailian_voice,
                speed=self._bailian_speed,
                pitch=self._bailian_pitch,
                volume=self._bailian_volume,
            )
        else:
            self._thread = TTSThread(
                engine_name=self._engine_name,
                text=text,
                voice=self._voice,
                speed=self._speed,
            )

        self._thread.finished.connect(self._on_thread_finished)
        self._thread.error_occurred.connect(self._on_thread_error)
        self._thread.start()

    def stop(self):
        """停止当前朗读。"""
        if self._thread and self._thread.isRunning():
            self._thread.stop()
            self._thread.wait(3000)
            # 如果 wait 超时线程还在运行，将其移入旧线程集合保活
            if self._thread.isRunning():
                self._old_threads.add(self._thread)
                self._thread.finished.connect(
                    lambda t=self._thread: self._old_threads.discard(t)
                )
        self._speaking = False
        self._thread = None

    def is_speaking(self):
        """查询是否正在朗读。"""
        return self._speaking

    def _on_thread_finished(self):
        self._speaking = False
        # 如果还有旧线程引用此线程，从旧集合中清理
        if self._thread in self._old_threads:
            self._old_threads.discard(self._thread)
        self._thread = None
        self.speaking_finished.emit()

    def _on_thread_error(self, msg):
        self._speaking = False
        if self._thread in self._old_threads:
            self._old_threads.discard(self._thread)
        self._thread = None
        self.error_occurred.emit(msg)
