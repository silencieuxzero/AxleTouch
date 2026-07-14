from datetime import datetime
import os
from copy import deepcopy
from pathlib import Path
from config_manager import save_config, load_config
import base64

from schedule import Poller
from tts_manager import TTSManager

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLineEdit, QPushButton, QLabel, QApplication,
                              QMenu, QAction, QDialog, QFormLayout,
                              QDialogButtonBox, QComboBox, QSpinBox,
                              QCheckBox, QDoubleSpinBox, QShortcut,
                              QGroupBox, QMessageBox, QGraphicsOpacityEffect,
                              QTabWidget)
from PyQt5.QtCore import (Qt, QPoint, QRectF, QPropertyAnimation,
                           QEasingCurve, QTimer, pyqtSignal, QElapsedTimer,
                           QBuffer, QEvent, QAbstractAnimation)
from PyQt5.QtGui import (QPainter, QBrush, QColor, QPen, QPainterPath,
                          QRegion, QCursor, QFontMetrics, QPixmap, QIcon,
                          QKeySequence)

from tools import _log_to_json, get_base_path, capture_screen
from tts_bailian import BAILIAN_VOICES
from tts_qwen import QWEN_VOICES


# ── 模块级时间戳格式化 ──
_NOW = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ── 统一色彩主题 ──
COLOR_PRIMARY = "#5078f0"         # 主色调（蓝）
COLOR_PRIMARY_LIGHT = "#7099ff"
COLOR_PRIMARY_DARK = "#4060d0"
COLOR_BG_CARD = "#fbfbfd"        # 卡片背景
COLOR_BORDER = "#e4e7ec"         # 边框
COLOR_BORDER_INPUT = "#d0d5dd"   # 输入框边框
COLOR_TEXT_PRIMARY = "#1e2026"   # 主文字
COLOR_TEXT_SECONDARY = "#344054"
COLOR_TEXT_MUTED = "#667085"     # 次要文字
COLOR_SHADOW_BASE = (60, 65, 80) # 阴影基色(RGB)
COLOR_SUCCESS = "#12b76a"        # 成功
COLOR_ERROR = "#f04438"          # 错误
COLOR_PROGRESS = "#5078f0"       # 进度条

current_dir = get_base_path()

image_path = os.path.join(current_dir, "assets", "image.svg")

class ContentBar(QWidget):

    def __init__(self, parent_floating):
        super().__init__()
        self._parent = parent_floating
        self._progress = 0.0
        self._cached_card_rect = None
        self._elapsed = QElapsedTimer()
        self._progress_timer = QTimer(self)
        self._progress_timer.setInterval(30)
        self._progress_timer.timeout.connect(self._tick_progress)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(68)
        self.setFixedWidth(130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 16px;
                line-height: 1.4;
                background: transparent;
            }
        """)
        self._label.setWordWrap(True)
        layout.addWidget(self._label)

    def show_content(self, text):
        self._label.setText(text)
        self._adjust_size(text)
        self._update_position()
        self._progress = 1.0
        self._elapsed.start()
        self._progress_timer.start()
        self._show_animated()
        QTimer.singleShot(5000, self._hide_animated)

    def _tick_progress(self):
        elapsed_ms = self._elapsed.elapsed()
        self._progress = max(0.0, 1.0 - elapsed_ms / 5000)
        self.update()
        if self._progress <= 0.0:
            self._progress_timer.stop()

    def _final_pos(self):
        fx = self._parent.x()
        fy = self._parent.y()
        fw = self._parent.width()
        pw = self.width()
        ph = self.height()

        screen = QApplication.primaryScreen().geometry()
        sw = screen.width()

        edge = self._parent._edge_side
        if edge == 'left':
            px = fx
        elif edge == 'right':
            px = fx + fw - pw
        else:
            px = fx + fw // 2 - pw // 2

        if px < 0:
            px = 0
        elif px + pw > sw:
            px = sw - pw

        py = fy - ph - 6
        if py < 0:
            py = fy + self._parent.height() + 6

        return QPoint(px, py)

    def _show_animated(self):
        final = self._final_pos()
        start = QPoint(final.x(), self._parent.y() - self.height())

        self.setWindowOpacity(0.0)
        self.move(start)
        self.show()

        anim_p = QPropertyAnimation(self, b"pos")
        anim_p.setDuration(350)
        anim_p.setStartValue(start)
        anim_p.setEndValue(final)
        anim_p.setEasingCurve(QEasingCurve.OutCubic)
        anim_p.start()
        self._show_anim_p = anim_p

        anim_o = QPropertyAnimation(self, b"windowOpacity")
        anim_o.setDuration(250)
        anim_o.setStartValue(0.0)
        anim_o.setEndValue(1.0)
        anim_o.setEasingCurve(QEasingCurve.OutCubic)
        anim_o.start()
        self._show_anim_o = anim_o

    def _hide_animated(self):
        self._progress_timer.stop()
        cur = self.pos()
        target = QPoint(cur.x(), self._parent.y() - self.height())

        anim_p = QPropertyAnimation(self, b"pos")
        anim_p.setDuration(300)
        anim_p.setStartValue(cur)
        anim_p.setEndValue(target)
        anim_p.setEasingCurve(QEasingCurve.InCubic)
        anim_p.start()
        self._hide_anim_p = anim_p

        anim_o = QPropertyAnimation(self, b"windowOpacity")
        anim_o.setDuration(250)
        anim_o.setStartValue(self.windowOpacity())
        anim_o.setEndValue(0.0)
        anim_o.setEasingCurve(QEasingCurve.InCubic)
        anim_o.finished.connect(self._after_hide)
        anim_o.start()
        self._hide_anim_o = anim_o

    def _after_hide(self):
        self.hide()
        self.setWindowOpacity(1.0)
        self.setFixedHeight(68)
        self.setFixedWidth(130)
        self._progress = 0.0
        self._cached_card_rect = None

    def _adjust_size(self, text):
        """根据文本内容自动调整气泡宽度和高度，支持多行换行。"""
        fm = QFontMetrics(self._label.font())
        text_w = fm.horizontalAdvance(text)
        max_w = 160
        w = min(max(text_w + 24 * 2 + 20, 130), max_w)
        self.setFixedWidth(w)

        # 计算文本在限定宽度下的实际高度（多行换行）
        content_w = w - 24  # 左右 layout margin (12+12)
        self._label.setFixedWidth(content_w)
        rect = fm.boundingRect(
            QRect(0, 0, content_w, 2000),
            Qt.AlignCenter | Qt.TextWordWrap, text
        )
        text_h = rect.height() + 4
        h = text_h + 24  # 上下 padding
        h = max(h, 68)
        h = min(h, 280)  # 不超过屏幕 1/3
        self.setFixedHeight(h)

    def _update_position(self):
        self.move(self._final_pos())

    def reposition(self):
        if self.isVisible():
            self._update_position()

    def _card_rect(self):
        if self._cached_card_rect is None:
            self._cached_card_rect = QRectF(10, 10, self.width() - 20, self.height() - 20)
        return self._cached_card_rect

    def paintEvent(self, event):
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        card = self._card_rect()

        for i in range(5):
            offset = 8 - i * 1.6
            r = card.adjusted(-offset, -offset + 2, offset, offset + 2)
            alpha = 6 + i * 7
            painter.setBrush(QBrush(QColor(*COLOR_SHADOW_BASE, alpha)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(r, 14 + offset, 14 + offset)

        painter.setBrush(QBrush(QColor(COLOR_BG_CARD)))
        painter.setPen(QPen(QColor(COLOR_BORDER), 0.5))
        painter.drawRoundedRect(card, 14, 14)

        if self._progress > 0.0 and card.height() > 2:
            bar_w = card.width() * self._progress
            bar_x = card.x()
            bar_y = card.bottom() - 3
            _c = QColor(COLOR_PROGRESS)
            _c.setAlpha(200)
            painter.setBrush(QBrush(_c))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, 3), 1, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._cached_card_rect = None
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 14, 14)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))



class InputPopup(QWidget):

    submitted = pyqtSignal(str)
    image = pyqtSignal(str)
    not_image = pyqtSignal()
    no_vlm = pyqtSignal()

    def __init__(self, parent_floating):
        super().__init__()
        self._parent = parent_floating
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(self._parent.collapsed_size)
        self.setFixedWidth(420)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._edit = QLineEdit(self)
        self._edit.setPlaceholderText("输入...")
        self._edit.setStyleSheet("""
            QLineEdit {
                background: """ + COLOR_BG_CARD + """;
                border: 1px solid """ + COLOR_BORDER + """;
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 12px;
                color: #333;
            }
            QLineEdit:focus {
                border: 1.5px solid """ + COLOR_PRIMARY + """;
            }
        """)
        self._edit.returnPressed.connect(self._on_submit)
        layout.addWidget(self._edit)

        self._btn = QPushButton("✓", self)
        self._btn.setFixedSize(28, 28)
        self._btn.setStyleSheet("""
            QPushButton {
                background: """ + COLOR_PRIMARY + """;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: """ + COLOR_PRIMARY_LIGHT + """;
            }
            QPushButton:pressed {
                background: """ + COLOR_PRIMARY_DARK + """;
            }
        """)
        self._btn.clicked.connect(self._on_submit)
        layout.addWidget(self._btn)

    def _on_submit(self):
        text = self._edit.text().strip()
        if text:
            self.submitted.emit(text)
        self.hide_popup()

    def _calc_position(self):
        fx = self._parent.x()
        fy = self._parent.y()
        fh = self._parent.height()
        fw = self._parent.width()
        pw = self.width()
        ph = self.height()

        screen = QApplication.primaryScreen().geometry()
        sw = screen.width()
        sh = screen.height()

        edge = self._parent._edge_side
        if edge == 'left':
            px = fx
        elif edge == 'right':
            px = fx + fw - pw
        else:
            px = fx + fw // 2 - pw // 2

        if px < 0:
            px = 0
        elif px + pw > sw:
            px = sw - pw

        py = fy + fh + 4
        if py + ph > sh:
            py = fy - ph - 4

        return QPoint(px, py)

    def popup(self):
        pos = self._calc_position()
        self.move(pos)
        self.show()
        self._edit.setFocus()

    def reposition(self):
        if self.isVisible():
            pos = self._calc_position()
            self.move(pos)

    def hide_popup(self):
        self.hide()
        self._edit.clear()

    def apply_config(self, config):
        width = config.get("popup_width", 420)
        self.setFixedWidth(width)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()  

    def dropEvent(self, event):
        config = load_config()
        chat_cfg = config.get("chat", {})
        chat_provider = chat_cfg.get("provider", "stepfun")
        if chat_provider not in ("stepfun", "bailian", "siliconflow", "qwen"):
            self.no_vlm.emit()
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                with open(file_path, "rb") as image_file:
                    base64_bytes = base64.b64encode(image_file.read()).decode('utf-8')
                    image_data = f"data:image/{Path(file_path).suffix[1:].lower()};base64,{base64_bytes}"
                    self.image.emit(image_data)
            else:
                self.not_image.emit()




# ── 各模块厂商选项 ──────────────────────────────────────
CHAT_PROVIDER_OPTIONS = [
    ("stepfun", "阶跃星辰"),
    ("bailian", "阿里百炼"),
    ("deepseek", "DeepSeek"),
    ("siliconflow", "硅基流动"),
]

VISION_PROVIDER_OPTIONS = [
    ("bailian", "阿里百炼"),
    ("siliconflow", "硅基流动"),
    ("stepfun", "阶跃星辰"),
]

TTS_PROVIDER_OPTIONS = [
    ("qwen", "阿里百炼 Qwen-TTS"),
    ("bailian", "阿里百炼 CosyVoice"),
]

# ── 通用样式 ───────────────────────────────────────────
INPUT_STYLE = f"""
    QLineEdit {{
        border: 1px solid {COLOR_BORDER_INPUT};
        border-radius: 8px; padding: 10px 14px;
        background: white; color: {COLOR_TEXT_PRIMARY}; font-size: 16px;
    }}
    QLineEdit:focus {{ border-color: {COLOR_PRIMARY}; }}
"""

COMBO_STYLE = f"""
    QComboBox {{
        border: 1px solid {COLOR_BORDER_INPUT};
        border-radius: 8px; padding: 10px 14px;
        background: white; color: {COLOR_TEXT_PRIMARY}; font-size: 16px;
        min-width: 140px;
    }}
    QComboBox::drop-down {{ border: none; width: 30px; }}
    QComboBox::down-arrow {{ width: 14px; height: 14px; }}
"""

SPIN_STYLE = f"""
    QSpinBox, QDoubleSpinBox {{
        border: 1px solid {COLOR_BORDER_INPUT};
        border-radius: 8px; padding: 8px 12px;
        background: white; color: {COLOR_TEXT_PRIMARY}; font-size: 16px;
        min-width: 100px;
    }}
"""

CHECK_STYLE = f"color: {COLOR_TEXT_SECONDARY}; font-size: 16px;"

GROUP_STYLE = f"""
    QGroupBox {{
        font-size: 16px; font-weight: bold;
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        margin-top: 14px;
        padding: 18px 14px 14px 14px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 12px;
        color: {COLOR_TEXT_SECONDARY};
    }}
"""

STATUS_CONFIGURED = f'<span style="color:{COLOR_SUCCESS}; font-size:15px;">● 已配置</span>'
STATUS_NOT_CONFIGURED = f'<span style="color:{COLOR_ERROR}; font-size:15px;">● 未配置</span>'

# ── 标签页样式 ──────────────────────────────────────────
TAB_STYLE = f"""
    QTabWidget::pane {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        background: white;
        top: -1px;
    }}
    QTabBar::tab {{
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        padding: 10px 24px;
        margin-right: 6px;
        font-size: 16px;
        color: {COLOR_TEXT_MUTED};
        min-height: 30px;
    }}
    QTabBar::tab:selected {{
        color: {COLOR_PRIMARY};
        border-bottom: 2px solid {COLOR_PRIMARY};
        font-weight: bold;
    }}
    QTabBar::tab:hover:!selected {{
        color: {COLOR_TEXT_SECONDARY};
        border-bottom: 2px solid {COLOR_BORDER_INPUT};
    }}
"""


class AnimatedTabWidget(QTabWidget):
    """带淡入动画的标签页组件，切换页面时有过渡效果。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fade_anim = None
        self.currentChanged.connect(self._animate_page)

    def _animate_page(self, index):
        page = self.widget(index)
        if not page:
            return
        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        self._fade_anim = QPropertyAnimation(effect, b"opacity")
        self._fade_anim.setDuration(150)
        self._fade_anim.setStartValue(0.65)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._fade_anim.start(QAbstractAnimation.DeleteWhenStopped)


class SettingsDialog(QDialog):
    """模块化设置对话框 — 对话、TTS、识图三大模块独立配置。"""

    config_saved = pyqtSignal(dict)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self._config = deepcopy(config)
        self.setWindowTitle("设置")
        flags = Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # 整体增大基础字号
        font = self.font()
        font.setPointSize(font.pointSize() + 2)
        self.setFont(font)

        self.setMinimumSize(520, 620)
        win_size = self._config.get("window_size", [560, 700])
        self.resize(win_size[0], win_size[1])

        self._saved_geometry = None
        icon_path = os.path.join(current_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._minimize_shortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        self._minimize_shortcut.activated.connect(self.showMinimized)

        self._save_size_timer = QTimer(self)
        self._save_size_timer.setSingleShot(True)
        self._save_size_timer.timeout.connect(self._flush_window_size)

        self.init_ui()
        self._sync_all_status()

    # ═══════════════════════════════════════════════════════
    #  UI 构建
    # ═══════════════════════════════════════════════════════

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # ── 标签页导航 ──
        self._tab_widget = AnimatedTabWidget()
        self._tab_widget.setStyleSheet(TAB_STYLE)
        self._tab_widget.addTab(self._build_chat_section(), "💬 对话")
        self._tab_widget.addTab(self._build_tts_section(), "🔊 TTS")
        self._tab_widget.addTab(self._build_vision_section(), "🖼️ 识图")
        self._tab_widget.addTab(self._build_common_section(), "⚙️ 通用")
        layout.addWidget(self._tab_widget, 1)

        # ── 底部按钮 ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("保存配置")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_PRIMARY}; color: white; border: none;
                border-radius: 8px; padding: 12px 36px;
                font-size: 16px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {COLOR_PRIMARY_DARK}; }}
        """)
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: white; color: {COLOR_TEXT_SECONDARY};
                border: 1px solid {COLOR_BORDER_INPUT}; border-radius: 8px;
                padding: 12px 36px; font-size: 16px;
            }}
            QPushButton:hover {{ background: #f9fafb; }}
        """)
        save_btn.clicked.connect(self._on_save)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        # ── 恢复上次标签页 ──
        saved_tab = self._config.get("_settings_tab", 0)
        if 0 <= saved_tab < self._tab_widget.count():
            self._tab_widget.setCurrentIndex(saved_tab)
        # 监听标签切换以便持久化
        self._tab_widget.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        """标签切换时持久化当前索引。"""
        self._config["_settings_tab"] = index

    # ── 对话模块 ──────────────────────────────────────

    def _build_chat_section(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 厂商
        self._chat_provider = QComboBox()
        self._chat_provider.setStyleSheet(COMBO_STYLE)
        for pid, pname in CHAT_PROVIDER_OPTIONS:
            self._chat_provider.addItem(pname, pid)
        chat_cfg = self._config.get("chat", {})
        idx = self._chat_provider.findData(chat_cfg.get("provider", "stepfun"))
        if idx >= 0:
            self._chat_provider.setCurrentIndex(idx)

        self._chat_status = QLabel()
        row_w = QHBoxLayout()
        row_w.addWidget(self._chat_provider, 1)
        row_w.addWidget(self._chat_status)
        form.addRow("厂商:", row_w)

        # API Key
        self._chat_api_key = QLineEdit()
        self._chat_api_key.setStyleSheet(INPUT_STYLE)
        self._chat_api_key.setPlaceholderText("输入当前厂商的 API Key")
        self._chat_api_key.textChanged.connect(self._update_chat_status)
        form.addRow("API Key:", self._chat_api_key)

        # 模型名称
        self._chat_model = QLineEdit()
        self._chat_model.setStyleSheet(INPUT_STYLE)
        self._chat_model.setPlaceholderText("输入模型名称（留空使用厂商默认）")
        form.addRow("模型:", self._chat_model)

        layout.addLayout(form)
        layout.addStretch()

        # 加载当前厂商的 key / model（在信号连接之后）
        self._chat_provider.currentIndexChanged.connect(self._on_chat_provider_switched)
        self._chat_last_provider = self._chat_provider.currentData()
        self._load_chat_provider_state()

        return page

    # ── TTS 模块 ──────────────────────────────────────

    def _build_tts_section(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        tts_cfg = self._config.get("tts", {})

        # ═══════════════════════════════════════════════════
        #  总开关
        # ═══════════════════════════════════════════════════

        self._tts_enabled = QCheckBox("启用文字转语音 (TTS)")
        self._tts_enabled.setStyleSheet(f"""
            QCheckBox {{
                font-size: 16px;
                font-weight: bold;
                color: {COLOR_TEXT_PRIMARY};
                spacing: 8px;
            }}
        """)
        self._tts_enabled.setChecked(tts_cfg.get("enabled", True))
        layout.addWidget(self._tts_enabled)

        help_label = QLabel(
            "开启后，AI 回复的文字内容将自动通过阿里百炼语音合成模型朗读出来。"
            "需确保下方已填写有效的 API Key 并选中音色。"
        )
        help_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 13px; padding-left: 24px;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        layout.addSpacing(4)

        # ═══════════════════════════════════════════════════
        #  参数区域容器（开关关闭时整体禁用）
        # ═══════════════════════════════════════════════════

        self._tts_params_widget = QWidget()
        params_layout = QVBoxLayout(self._tts_params_widget)
        params_layout.setContentsMargins(0, 0, 0, 0)
        params_layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # 先创建 status 避免回调冲突
        self._tts_status = QLabel()

        # API Key
        self._tts_api_key = QLineEdit()
        self._tts_api_key.setStyleSheet(INPUT_STYLE)
        self._tts_api_key.setPlaceholderText("输入阿里百炼 API Key（TTS 专用）")
        self._tts_api_key.textChanged.connect(self._update_tts_status)
        self._tts_api_key.setText(tts_cfg.get("api_key", ""))
        form.addRow("API Key:", self._tts_api_key)

        # 模型名称
        current_engine = tts_cfg.get("model", "qwen3-tts-flash")
        self._tts_model = QComboBox()
        self._tts_model.setStyleSheet(COMBO_STYLE)
        self._tts_model.addItem("Qwen3-TTS-Flash (推荐)", "qwen3-tts-flash")
        self._tts_model.addItem("CosyVoice-v1 (旧版)", "cosyvoice-v1")
        model_idx = self._tts_model.findData(current_engine)
        if model_idx >= 0:
            self._tts_model.setCurrentIndex(model_idx)
        self._tts_model.currentIndexChanged.connect(self._on_tts_model_switched)
        form.addRow("模型:", self._tts_model)

        # ── Qwen 参数组 ──
        self._qwen_group = QGroupBox("Qwen3-TTS-Flash 参数")
        self._qwen_group.setStyleSheet(GROUP_STYLE)
        qwen_layout = QFormLayout()
        qwen_layout.setSpacing(8)

        self._tts_voice_qwen = QComboBox()
        self._tts_voice_qwen.setStyleSheet(COMBO_STYLE)
        current_v = tts_cfg.get("voice", "Cherry")
        v_idx = 0
        for i, (vid, vname) in enumerate(QWEN_VOICES):
            self._tts_voice_qwen.addItem(vname, vid)
            if vid == current_v:
                v_idx = i
        self._tts_voice_qwen.setCurrentIndex(v_idx)
        qwen_layout.addRow("音色:", self._tts_voice_qwen)

        self._tts_rate = QDoubleSpinBox()
        self._tts_rate.setStyleSheet(SPIN_STYLE)
        self._tts_rate.setRange(0.5, 2.0)
        self._tts_rate.setSingleStep(0.1)
        self._tts_rate.setValue(tts_cfg.get("rate", 1.0))
        self._tts_rate.setSuffix("x")
        qwen_layout.addRow("语速:", self._tts_rate)

        self._tts_pitch_qwen = QDoubleSpinBox()
        self._tts_pitch_qwen.setStyleSheet(SPIN_STYLE)
        self._tts_pitch_qwen.setRange(0.5, 2.0)
        self._tts_pitch_qwen.setSingleStep(0.1)
        self._tts_pitch_qwen.setValue(tts_cfg.get("pitch", 1.0))
        self._tts_pitch_qwen.setSuffix("x")
        qwen_layout.addRow("语调:", self._tts_pitch_qwen)

        self._tts_volume_qwen = QSpinBox()
        self._tts_volume_qwen.setStyleSheet(SPIN_STYLE)
        self._tts_volume_qwen.setRange(0, 100)
        self._tts_volume_qwen.setValue(tts_cfg.get("volume", 50))
        self._tts_volume_qwen.setSuffix("%")
        qwen_layout.addRow("音量:", self._tts_volume_qwen)

        self._tts_sample_rate = QComboBox()
        self._tts_sample_rate.setStyleSheet(COMBO_STYLE)
        sr_options = [("8000", 8000), ("16000", 16000), ("22050", 22050),
                       ("24000 (推荐)", 24000), ("44100", 44100), ("48000", 48000)]
        current_sr = tts_cfg.get("sample_rate", 24000)
        sr_idx = 0
        for i, (_, sv) in enumerate(sr_options):
            self._tts_sample_rate.addItem(sr_options[i][0], sv)
            if sv == current_sr:
                sr_idx = i
        self._tts_sample_rate.setCurrentIndex(sr_idx)
        qwen_layout.addRow("采样率:", self._tts_sample_rate)

        self._tts_audio_format = QComboBox()
        self._tts_audio_format.setStyleSheet(COMBO_STYLE)
        fmt_options = [("WAV (推荐)", "wav"), ("MP3", "mp3"), ("PCM", "pcm"), ("OPUS", "opus")]
        current_fmt = tts_cfg.get("audio_format", "wav")
        fmt_idx = 0
        for i, (_, fv) in enumerate(fmt_options):
            self._tts_audio_format.addItem(fmt_options[i][0], fv)
            if fv == current_fmt:
                fmt_idx = i
        self._tts_audio_format.setCurrentIndex(fmt_idx)
        qwen_layout.addRow("音频格式:", self._tts_audio_format)

        self._qwen_group.setLayout(qwen_layout)

        # ── CosyVoice 参数组 ──
        self._cosy_group = QGroupBox("CosyVoice 参数")
        self._cosy_group.setStyleSheet(GROUP_STYLE)
        cosy_layout = QFormLayout()
        cosy_layout.setSpacing(8)

        self._tts_voice_cosy = QComboBox()
        self._tts_voice_cosy.setStyleSheet(COMBO_STYLE)
        current_cv = tts_cfg.get("voice", "longxiaochun")
        c_idx = 0
        for i, (vid, vname) in enumerate(BAILIAN_VOICES):
            self._tts_voice_cosy.addItem(vname, vid)
            if vid == current_cv:
                c_idx = i
        self._tts_voice_cosy.setCurrentIndex(c_idx)
        cosy_layout.addRow("音色:", self._tts_voice_cosy)

        self._tts_speed_cosy = QDoubleSpinBox()
        self._tts_speed_cosy.setStyleSheet(SPIN_STYLE)
        self._tts_speed_cosy.setRange(0.5, 2.0)
        self._tts_speed_cosy.setSingleStep(0.1)
        self._tts_speed_cosy.setValue(tts_cfg.get("rate", 1.0))
        self._tts_speed_cosy.setSuffix("x")
        cosy_layout.addRow("语速:", self._tts_speed_cosy)

        self._tts_pitch_cosy = QDoubleSpinBox()
        self._tts_pitch_cosy.setStyleSheet(SPIN_STYLE)
        self._tts_pitch_cosy.setRange(0.5, 2.0)
        self._tts_pitch_cosy.setSingleStep(0.1)
        self._tts_pitch_cosy.setValue(tts_cfg.get("pitch", 1.0))
        self._tts_pitch_cosy.setSuffix("x")
        cosy_layout.addRow("语调:", self._tts_pitch_cosy)

        self._tts_volume_cosy = QSpinBox()
        self._tts_volume_cosy.setStyleSheet(SPIN_STYLE)
        self._tts_volume_cosy.setRange(0, 100)
        self._tts_volume_cosy.setValue(tts_cfg.get("volume", 50))
        self._tts_volume_cosy.setSuffix("%")
        cosy_layout.addRow("音量:", self._tts_volume_cosy)

        self._cosy_group.setLayout(cosy_layout)

        form.addRow("", self._qwen_group)
        form.addRow("", self._cosy_group)

        # TTS 状态
        self._update_tts_status()
        form.addRow("状态:", self._tts_status)

        params_layout.addLayout(form)
        layout.addWidget(self._tts_params_widget)
        layout.addStretch()

        # ═══════════════════════════════════════════════════
        #  开关联动：关闭时禁用所有参数控件
        # ═══════════════════════════════════════════════════
        self._tts_enabled.toggled.connect(self._on_tts_enabled_toggled)
        self._on_tts_enabled_toggled(self._tts_enabled.isChecked())

        # 根据当前模型显示/隐藏对应参数组
        self._on_tts_model_switched()
        return page

    def _on_tts_enabled_toggled(self, checked: bool):
        """TTS 开关切换时，启用/禁用参数区域。"""
        self._tts_params_widget.setEnabled(checked)

    def _on_tts_model_switched(self):
        """根据选中的模型切换音色列表和参数组。"""
        model = self._tts_model.currentData()
        is_qwen = "qwen" in model
        self._qwen_group.setVisible(is_qwen)
        self._cosy_group.setVisible(not is_qwen)

    # ── 识图模块 ──────────────────────────────────────

    def _build_vision_section(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self._vision_provider = QComboBox()
        self._vision_provider.setStyleSheet(COMBO_STYLE)
        for pid, pname in VISION_PROVIDER_OPTIONS:
            self._vision_provider.addItem(pname, pid)
        vis_cfg = self._config.get("vision", {})
        idx = self._vision_provider.findData(vis_cfg.get("provider", "bailian"))
        if idx >= 0:
            self._vision_provider.setCurrentIndex(idx)

        self._vision_status = QLabel()
        row_w = QHBoxLayout()
        row_w.addWidget(self._vision_provider, 1)
        row_w.addWidget(self._vision_status)
        form.addRow("厂商:", row_w)

        self._vision_api_key = QLineEdit()
        self._vision_api_key.setStyleSheet(INPUT_STYLE)
        self._vision_api_key.setPlaceholderText("输入当前厂商的 API Key")
        self._vision_api_key.textChanged.connect(self._update_vision_status)
        form.addRow("API Key:", self._vision_api_key)

        self._vision_model = QLineEdit()
        self._vision_model.setStyleSheet(INPUT_STYLE)
        self._vision_model.setPlaceholderText("输入模型名称（留空使用厂商默认）")
        form.addRow("模型:", self._vision_model)

        layout.addLayout(form)
        layout.addStretch()

        self._vision_provider.currentIndexChanged.connect(self._on_vision_provider_switched)
        self._vision_last_provider = self._vision_provider.currentData()
        self._load_vision_provider_state()

        return page

    # ── 通用设置 ──────────────────────────────────────

    def _build_common_section(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self._tavily_key = QLineEdit()
        self._tavily_key.setStyleSheet(INPUT_STYLE)
        self._tavily_key.setPlaceholderText("Tavily API Key（用于联网搜索，可留空）")
        self._tavily_key.setText(self._config.get("tavily_api_key", ""))
        form.addRow("Tavily Key:", self._tavily_key)

        self._icon_size = QSpinBox()
        self._icon_size.setStyleSheet(SPIN_STYLE)
        self._icon_size.setRange(50, 300)
        self._icon_size.setValue(self._config.get("icon_size", 100))
        self._icon_size.setSuffix(" px")
        form.addRow("图标大小:", self._icon_size)

        self._popup_width = QSpinBox()
        self._popup_width.setStyleSheet(SPIN_STYLE)
        self._popup_width.setRange(200, 800)
        self._popup_width.setValue(self._config.get("popup_width", 420))
        self._popup_width.setSuffix(" px")
        form.addRow("输入框宽度:", self._popup_width)

        self._prompt = QLineEdit()
        self._prompt.setStyleSheet(INPUT_STYLE)
        self._prompt.setPlaceholderText("自定义角色 prompt")
        self._prompt.setText(self._config.get("prompt", ""))
        form.addRow("Prompt:", self._prompt)

        layout.addLayout(form)
        layout.addStretch()
        return page

    # ═══════════════════════════════════════════════════════
    #  模块共享方法
    # ═══════════════════════════════════════════════════════

    def _load_chat_provider_state(self):
        """从 self._config 加载当前选中厂商的 API Key / Model 到输入框。"""
        chat_cfg = self._config.get("chat", {})
        pid = self._chat_provider.currentData()
        api_keys = chat_cfg.get("api_keys", {})
        models = chat_cfg.get("models", {})
        self._chat_api_key.setText(api_keys.get(pid, ""))
        self._chat_model.setText(models.get(pid, ""))

    def _on_chat_provider_switched(self, new_index):
        """厂商切换时保存旧值、加载新值。"""
        chat_cfg = self._config.setdefault("chat", {})
        api_keys = chat_cfg.setdefault("api_keys", {})
        models = chat_cfg.setdefault("models", {})
        api_keys[self._chat_last_provider] = self._chat_api_key.text().strip()
        models[self._chat_last_provider] = self._chat_model.text().strip()
        new_pid = self._chat_provider.itemData(new_index)
        self._chat_api_key.setText(api_keys.get(new_pid, ""))
        self._chat_model.setText(models.get(new_pid, ""))
        self._chat_last_provider = new_pid
        self._update_chat_status()

    def _save_chat_provider_state(self):
        chat_cfg = self._config.setdefault("chat", {})
        api_keys = chat_cfg.setdefault("api_keys", {})
        models = chat_cfg.setdefault("models", {})
        pid = self._chat_provider.currentData()
        api_keys[pid] = self._chat_api_key.text().strip()
        models[pid] = self._chat_model.text().strip()

    def _update_chat_status(self):
        if not hasattr(self, '_chat_status'):
            return
        key = self._chat_api_key.text().strip()
        self._chat_status.setText(STATUS_CONFIGURED if key else STATUS_NOT_CONFIGURED)

    def _update_tts_status(self):
        if not hasattr(self, '_tts_status'):
            return
        key = self._tts_api_key.text().strip()
        self._tts_status.setText(STATUS_CONFIGURED if key else STATUS_NOT_CONFIGURED)

    def _load_vision_provider_state(self):
        vis_cfg = self._config.get("vision", {})
        pid = self._vision_provider.currentData()
        api_keys = vis_cfg.get("api_keys", {})
        models = vis_cfg.get("models", {})
        self._vision_api_key.setText(api_keys.get(pid, ""))
        self._vision_model.setText(models.get(pid, ""))

    def _on_vision_provider_switched(self, new_index):
        vis_cfg = self._config.setdefault("vision", {})
        api_keys = vis_cfg.setdefault("api_keys", {})
        models = vis_cfg.setdefault("models", {})
        api_keys[self._vision_last_provider] = self._vision_api_key.text().strip()
        models[self._vision_last_provider] = self._vision_model.text().strip()
        new_pid = self._vision_provider.itemData(new_index)
        self._vision_api_key.setText(api_keys.get(new_pid, ""))
        self._vision_model.setText(models.get(new_pid, ""))
        self._vision_last_provider = new_pid
        self._update_vision_status()

    def _save_vision_provider_state(self):
        vis_cfg = self._config.setdefault("vision", {})
        api_keys = vis_cfg.setdefault("api_keys", {})
        models = vis_cfg.setdefault("models", {})
        pid = self._vision_provider.currentData()
        api_keys[pid] = self._vision_api_key.text().strip()
        models[pid] = self._vision_model.text().strip()

    def _update_vision_status(self):
        if not hasattr(self, '_vision_status'):
            return
        key = self._vision_api_key.text().strip()
        self._vision_status.setText(STATUS_CONFIGURED if key else STATUS_NOT_CONFIGURED)

    # ── 状态同步 ──────────────────────────────────────

    def _sync_all_status(self):
        self._update_chat_status()
        self._update_tts_status()
        self._update_vision_status()

    # ═══════════════════════════════════════════════════════
    #  保存逻辑
    # ═══════════════════════════════════════════════════════

    def _on_save(self):
        """收集所有模块的配置并持久化保存。"""
        # ── 对话 ──
        self._save_chat_provider_state()
        chat_cfg = self._config.setdefault("chat", {})
        chat_cfg["provider"] = self._chat_provider.currentData()

        # ── TTS ──
        tts_cfg = self._config.setdefault("tts", {})
        tts_cfg["api_key"] = self._tts_api_key.text().strip()
        tts_cfg["model"] = self._tts_model.currentData()
        is_qwen = "qwen" in tts_cfg["model"]
        tts_cfg["enabled"] = self._tts_enabled.isChecked()
        if is_qwen:
            tts_cfg["voice"] = self._tts_voice_qwen.currentData()
            tts_cfg["rate"] = self._tts_rate.value()
            tts_cfg["pitch"] = self._tts_pitch_qwen.value()
            tts_cfg["volume"] = self._tts_volume_qwen.value()
            tts_cfg["sample_rate"] = self._tts_sample_rate.currentData()
            tts_cfg["audio_format"] = self._tts_audio_format.currentData()
        else:
            tts_cfg["voice"] = self._tts_voice_cosy.currentData()
            tts_cfg["rate"] = self._tts_speed_cosy.value()
            tts_cfg["pitch"] = self._tts_pitch_cosy.value()
            tts_cfg["volume"] = self._tts_volume_cosy.value()
            tts_cfg["sample_rate"] = 22050
            tts_cfg["audio_format"] = "wav"

        # ── 识图 ──
        self._save_vision_provider_state()
        vis_cfg = self._config.setdefault("vision", {})
        vis_cfg["provider"] = self._vision_provider.currentData()

        # ── 通用 ──
        self._config["tavily_api_key"] = self._tavily_key.text().strip()
        self._config["icon_size"] = self._icon_size.value()
        self._config["popup_width"] = self._popup_width.value()
        self._config["prompt"] = self._prompt.text().strip()

        # ── 验证 ──
        chat_key = chat_cfg.get("api_keys", {}).get(chat_cfg["provider"], "")
        if not chat_key:
            ret = QMessageBox.question(
                self, "提示",
                "对话模块尚未配置 API Key，确定要保存吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
            )
            if ret == QMessageBox.No:
                return

        save_config(self._config)
        self.config_saved.emit(self._config)
        self.accept()

    # ═══════════════════════════════════════════════════════
    #  窗口管理
    # ═══════════════════════════════════════════════════════

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            old = event.oldState()
            new = self.windowState()
            if not (old & Qt.WindowMinimized) and (new & Qt.WindowMinimized):
                self._saved_geometry = self.geometry()
            if (old & Qt.WindowMinimized) and not (new & Qt.WindowMinimized):
                if self._saved_geometry is not None:
                    self.setGeometry(self._saved_geometry)
        super().changeEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._save_size_timer.start(500)

    def _flush_window_size(self):
        size = self.size()
        self._config["window_size"] = [size.width(), size.height()]
        try:
            cfg = load_config()
            cfg["window_size"] = [size.width(), size.height()]
            save_config(cfg)
        except Exception:
            pass



class EdgeFloatingBlock(QWidget):
    def __init__(self):
        super().__init__()
        self.collapsed_size = 135
        self._cached_card_rect = None
        self._edge_side = 'right'
        self._animating = False

        self._press_pos = None
        self._drag_offset = None
        self._long_press_fired = False
        self._is_dragging = False
        self._long_press_timer = QTimer(self)
        self._long_press_timer.setSingleShot(True)
        self._long_press_timer.timeout.connect(self._on_long_press)

        self._input_popup = InputPopup(self)
        self._input_popup.submitted.connect(self._on_input_submitted)
        self._input_popup.not_image.connect(self._not_image)
        self._input_popup.image.connect(self._image)
        self._input_popup.no_vlm.connect(self._no_vlm)
        


        self._content_bar = ContentBar(self)

        pixmap = QPixmap(image_path)
        self.image = pixmap.scaled(720, 720,
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self._ai = None
        self._config = None

        self._poller = Poller(self) 
        self._poller.status_ready.connect(self._on_poller_status)
        self._tts_manager = TTSManager(self)
        self._tts_manager.error_occurred.connect(self._on_tts_error)

        self.init_ui()

    def _on_tts_error(self, msg):
        """TTS 错误时打印到控制台以便排查。"""
        print(f"[TTS 错误] {msg}")

    def _on_poller_status(self, status_text):
        if self._ai:
            self._ai.send_message(status_text)

    def set_ai_client(self, client, config=None):
        self._ai = client
        self._config = config or {}
        self._ai.response_ready.connect(self._on_ai_response)
        self._apply_size_config()
        self._init_tts()


    def _apply_size_config(self):
        icon_size = max(135, self._config.get("icon_size", 135))
        self.collapsed_size = icon_size
        self.resize(icon_size, icon_size)

        pixmap = QPixmap(image_path)
        self.image = pixmap.scaled(int(icon_size * 7.2), int(icon_size * 7.2),
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self._input_popup.apply_config(self._config)

        screen = QApplication.primaryScreen().geometry()
        if self._edge_side == 'left':
            self.move(0, self.y())
        else:
            self.move(screen.width() - icon_size, self.y())

    def _init_tts(self):
        """根据配置初始化 TTS 管理器。"""
        if not self._config:
            return
        tts_cfg = self._config.get("tts", {})
        tts_enabled = tts_cfg.get("enabled", True)
        tts_model = tts_cfg.get("model", "qwen3-tts-flash")
        is_qwen = "qwen" in tts_model
        if tts_enabled:
            if is_qwen:
                self._tts_manager.configure(
                    engine="qwen",
                    qwen_api_key=tts_cfg.get("api_key", ""),
                    qwen_voice=tts_cfg.get("voice", "Cherry"),
                )
            else:
                self._tts_manager.configure(
                    engine="bailian",
                    voice="",
                    speed=1.0,
                    bailian_api_key=tts_cfg.get("api_key", ""),
                    bailian_voice=tts_cfg.get("voice", "longxiaochun"),
                    bailian_speed=tts_cfg.get("rate", 1.0),
                    bailian_pitch=tts_cfg.get("pitch", 1.0),
                    bailian_volume=tts_cfg.get("volume", 50),
                )


    def _on_ai_response(self, text):
        self._content_bar.show_content(text)
        print(f"[{_NOW()}] 雨竹：\"{text}\"\n")
        _log_to_json(text)
        if self._config and self._config.get("tts", {}).get("enabled", True):
            self._tts_manager.speak(text)

    def _on_input_submitted(self, text):
        print(f"[{_NOW()}] -----[ user input ]----- \"{text}\"\n")
        if self._ai:
            self._ai.send_message(text)

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        default_size = self.collapsed_size
        self.resize(default_size, default_size)
        cy = (screen.height() - default_size) // 2
        self.move(screen.width() - default_size, cy)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

    def moveEvent(self, event):
        super().moveEvent(event)
        self._input_popup.reposition()
        self._content_bar.reposition()

    def _snap_to_edge(self):
        screen = QApplication.primaryScreen().geometry()
        center_x = self.x() + self.width() / 2
        self._edge_side = 'left' if center_x < screen.width() / 2 else 'right'

        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.InOutCubic)

        cur_y = self.y()
        if self._edge_side == 'left':
            target = QPoint(0, cur_y)
        else:
            target = QPoint(screen.width() - self.width(), cur_y)

        anim.setStartValue(self.pos())
        anim.setEndValue(target)
        anim.start()

    def _on_long_press(self):
        self._long_press_fired = True
        self._is_dragging = True
        self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        self._press_pos = event.globalPos()
        self._drag_offset = event.globalPos() - self.pos()
        self._long_press_fired = False
        self._is_dragging = False
        self._long_press_timer.start(300)

    def mouseMoveEvent(self, event):
        if not event.buttons() & Qt.LeftButton or self._press_pos is None:
            return
        dist = (event.globalPos() - self._press_pos).manhattanLength()
        if dist > 5 and not self._long_press_fired:
            self._long_press_timer.stop()
            self._long_press_fired = True
            self._is_dragging = True
            self.setCursor(QCursor(Qt.ClosedHandCursor))

        if self._is_dragging:
            self.move(event.globalPos() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        self._long_press_timer.stop()

        if self._is_dragging:
            self._snap_to_edge()
        else:
            if self._input_popup.isVisible():
                self._input_popup.hide_popup()
            else:
                self._input_popup.popup()

        self._long_press_fired = False
        self._is_dragging = False
        self._press_pos = None
        self.setCursor(QCursor(Qt.ArrowCursor))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 10px 32px;
                border-radius: 4px;
                font-size: 16px;
            }}
            QMenu::item:selected {{
                background: {COLOR_PRIMARY};
                color: white;
            }}
        """)

        settings_action = QAction("配置文件设置", self)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        capture_action = QAction("让雨竹看看！", self)
        capture_action.triggered.connect(self._capture)
        menu.addAction(capture_action)

        menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)

        menu.exec_(event.globalPos())

    def _open_settings(self):
        dialog = SettingsDialog(self._config or {}, self)
        dialog.config_saved.connect(self._on_config_saved)
        dialog.exec_()

    def _capture(self):
        try:
            pixmap = capture_screen()
        except Exception:
            print("截图失败：无法获取屏幕图像")
            return

        if pixmap.isNull():
            print("截图失败：获取的图像无效")
            return
        
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        pixmap = pixmap.scaled(1280, 720, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap.save(buffer, "PNG")
        data = buffer.data().toBase64().data().decode()
        image_url = f"data:image/png;base64,{data}"
        #此处不复用_image其实是有说法的 image发送路径的可自定义性太低。
        print(f"[{_NOW()}] -----[ Action ]----- \"雨竹看了一眼你的屏幕\"\n")
        _data = [
            {"type": "text", "text": "这是用户桌面截图。"},
            {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
        ]
        if self._ai:
            self._ai.send_message(_data)

    def _on_config_saved(self, config):
        self._config = config
        self._apply_size_config()

        # ── 更新对话 AI 客户端 ──
        chat_cfg = config.get("chat", {})
        chat_provider = chat_cfg.get("provider", "stepfun")
        chat_api_key = chat_cfg.get("api_keys", {}).get(chat_provider, "")
        chat_model = chat_cfg.get("models", {}).get(chat_provider, "")
        if self._ai:
            self._ai.update(
                chat_provider,
                chat_api_key,
                config.get("tavily_api_key", ""),
                model=chat_model,
            )

        # ── 更新 TTS ──
        tts_cfg = config.get("tts", {})
        tts_enabled = tts_cfg.get("enabled", True)
        tts_model = tts_cfg.get("model", "qwen3-tts-flash")
        is_qwen = "qwen" in tts_model
        if tts_enabled:
            if is_qwen:
                self._tts_manager.configure(
                    engine="qwen",
                    qwen_api_key=tts_cfg.get("api_key", ""),
                    qwen_voice=tts_cfg.get("voice", "Cherry"),
                )
            else:
                self._tts_manager.configure(
                    engine="bailian",
                    voice="",
                    speed=1.0,
                    bailian_api_key=tts_cfg.get("api_key", ""),
                    bailian_voice=tts_cfg.get("voice", "longxiaochun"),
                    bailian_speed=tts_cfg.get("rate", 1.0),
                    bailian_pitch=tts_cfg.get("pitch", 1.0),
                    bailian_volume=tts_cfg.get("volume", 50),
                )
        else:
            self._tts_manager.stop()

    def _card_rect(self):
        if self._cached_card_rect is None:
            self._cached_card_rect = QRectF(15, 15, self.width() - 30, self.height() - 30)
        return self._cached_card_rect

    def paintEvent(self, event):
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        card = self._card_rect()

        for i in range(4):
            offset = 9 - i * 2.25
            r = card.adjusted(-offset, -offset + 3, offset, offset + 3)
            alpha = 8 + i * 8
            painter.setBrush(QBrush(QColor(*COLOR_SHADOW_BASE, alpha)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(r, 18 + offset, 18 + offset)

        painter.setBrush(QBrush(QColor(COLOR_BG_CARD)))
        painter.setPen(QPen(QColor(COLOR_BORDER), 0.5))
        painter.drawRoundedRect(card, 18, 18)

        painter.setPen(QPen(QColor(100, 105, 115)))
        painter.setFont(painter.font())
        font = painter.font()
        font.setPixelSize(int(card.height() * 0.45))
        painter.setFont(font)

        painter.save()
        clip_path = QPainterPath()
        clip_path.addRoundedRect(card, 18, 18)
        painter.setClipPath(clip_path)
        painter.drawPixmap(card.toRect(), self.image)
        painter.restore()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._cached_card_rect = None
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 18, 18)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def _not_image(self):
        self._content_bar.show_content("不是图片文件，拖进来也没用ww")

    def _no_vlm(self):
        self._content_bar.show_content("当前对话厂商不支持图片识别哦，试试阶跃星辰/阿里百炼/硅基流动吧~")

    def _image(self, data):
        print(f"[{_NOW()}] -----[ user input ]----- \"图片\"\n")
        data = [
        {"type": "image_url", "image_url": {"url": data,"detail":"high"}}
    ]
        if self._ai:
            self._ai.send_message(data)

