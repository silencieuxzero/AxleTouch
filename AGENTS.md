# AxleTouch — AI桌宠项目说明

## 项目概述

一个基于 **PyQt5** 的桌面宠物应用，核心角色是"雨竹"——一只可爱的猫娘 AI。她贴边吸附在屏幕侧边，用户单击唤出输入框与她对话，AI 回复以气泡形式展示。项目支持多模型厂商、Web 搜索、屏幕截图分析、图片识别（多模态）等功能。

**入口**: `main.py` → `main()`  
**包管理**: `uv` (见 `pyproject.toml`)  
**运行**: `uv run axle-touch`

---

## 项目文件一览

| 文件 | 职责 |
|------|------|
| `main.py` | 应用入口，组装 QApplication、EdgeFloatingBlock、AIClient |
| `widgets.py` | UI 组件：EdgeFloatingBlock（主浮窗）、ContentBar（气泡）、InputPopup（输入框）、SettingsDialog（设置） |
| `AIclient.py` | AI 客户端，封装多厂商对话 API、工具调用（Web 搜索） |
| `AIweb.py` | 后台 Web 搜索线程（Tavily API） |
| `config_manager.py` | JSON 配置文件读写与管理 |
| `tools.py` | 工具函数：路径解析、获取活动窗口标题、截屏、聊天日志 |
| `schedule.py` | 定时轮询，获取用户当前活动窗口并触发 AI 问候 |
| `assets/` | 静态资源：icon.ico、image.svg（宠物头像）、image1.jpg |

---

## 架构与数据流

### 启动流程

```
main.py
 ├─ QApplication(sys.argv)
 ├─ EdgeFloatingBlock()          ← 创建主浮窗（UI 初始化）
 ├─ load_config()                ← 读取/生成 config.json
 ├─ AIClient(config)             ← 创建 AI 客户端
 │   └─ set_system_prompt(prompt)← 设置角色 prompt
 ├─ window.set_ai_client(ai, cfg)← 连接 AI 响应信号
 └─ app.exec_()                  ← 进入事件循环
```

### 对话数据流

```
用户输入
   ↓
InputPopup.submitted(text)
   ↓
EdgeFloatingBlock._on_input_submitted(text)
   ↓
AIClient.send_message(text)
   ↓ (异步 HTTP POST)
AIClient._on_reply(reply)  ← 通过 QNetworkAccessManager 回调
   ↓
response_ready.emit(text)   ← pyqtSignal
   ↓
EdgeFloatingBlock._on_ai_response(text)
   ├─ ContentBar.show_content(text)    ← 显示气泡
   └─ _log_to_json(text)              ← 写入聊天日志
```

### Web 搜索流程

```
AI 返回 tool_calls (finish_reason='tool_calls' 或 XML 格式)
   ↓
AIClient 创建 SearchThread(QThread)
   ↓ (后台线程 HTTP 请求)
SearchThread.result_ready.emit(result)
   ↓
AIClient._on_search_result() → 追加 tool 结果到消息列表 → _do_request() 继续对话
```

### 定时轮询流程

```
Poller(QTimer)
   ↓ 每 30~100 秒随机间隔
_trigger()
   ├─ get_active_window_title()   ← 通过 Win32 API 获取前台窗口
   └─ status_ready.emit(status)   ← "当前时间: HH:MM，用户正在使用: XXX"
        ↓
EdgeFloatingBlock._on_poller_status(status)
   └─ AIClient.send_message(status)  ← 主动触发 AI 问候
```

---

## 核心模块详解

### 1. `widgets.py` — UI 组件

#### EdgeFloatingBlock（主窗口）
- 继承 `QWidget`，无边框、透明背景、置顶（`FramelessWindowHint | WindowStaysOnTopHint | Tool`）
- **贴边吸附**: 鼠标释放时判断窗口中心点靠近哪一侧，自动动画吸附到屏幕边缘
- **交互**: 短按（释放前未拖动）→ 弹出输入框；长按/拖动 → 移动窗口
- **右键菜单**: 设置、截图、退出
- **绘图**: `paintEvent` 自定义绘制圆角卡片+头像图片，多层阴影效果
- **关键成员**:
  - `_input_popup`: InputPopup 实例
  - `_content_bar`: ContentBar 实例
  - `_ai`: AIClient 实例
  - `_poller`: Poller 实例
  - `image`: QPixmap 缩放后的头像
  - `_edge_side`: 'left' / 'right'

#### ContentBar（气泡）
- 独立无边框窗口，在浮窗上方显示
- 渐变出现/消失动画（QPropertyAnimation 操作 pos 和 windowOpacity）
- 底部进度条：5 秒倒计时，线性递减
- `_final_pos()` 计算相对于父窗口的对齐位置

#### InputPopup（输入框）
- 独立无边框窗口，在浮窗下方显示
- QLineEdit + 发送按钮
- 支持拖拽图片（`dragEnterEvent`/`dropEvent`），转 base64 发送
- 图片仅支持 StepFun 厂商（VLM）

#### SettingsDialog（设置）
- QDialog，表单布局
- 配置项：模型厂商、API Key、Tavily Key、图标大小、输入框宽度、自定义 prompt

### 2. `AIclient.py` — AI 对话层

- 继承 `QNetworkAccessManager`（异步 HTTP，不阻塞 UI）
- **支持厂商**: StepFun（阶跃星辰）、Bailian（阿里百炼）、DeepSeek
- **工具调用**: 当配置了 tavily_api_key 时，请求中附带 search_web 工具定义
- **两种工具调用格式**:
  1. 标准 OpenAI tool_calls（`finish_reason='tool_calls'`）
  2. 自定义 XML 格式（`<tool_call><function=search_web>...`），兼容不支持原生 tool_calls 的模型
- **XML 解析**: `_parse_xml_tool_call()` 用正则解析 `<tool_call>` → `<function=xxx>` → `<parameter=key>value`
- **信号**: `response_ready = pyqtSignal(str)` — AI 回复完成后发射

### 3. `AIweb.py` — Web 搜索

- `SearchThread(QThread)`: 后台线程执行 HTTP 请求
- 调用 [Tavily Search API](https://api.tavily.com/search)
- 结果取前 3 条，格式化为 Markdown 列表

### 4. `config_manager.py` — 配置管理

- 配置文件路径: `get_data_path() + "config.json"`
- `DEFAULT_PROMPT`: 角色设定 prompt（猫娘雨竹，撒娇语气）
- `DEFAULT_CONFIG`: 默认配置字典
- `load_config()`: 文件不存在时创建默认配置；读取异常时自动备份并重置
- `save_config(cfg)`: 合并更新配置

### 5. `tools.py` — 工具函数

- `get_base_path()`: 获取资源路径（支持 PyInstaller 打包后的 `_MEIPASS`）
- `get_data_path()`: 获取数据路径（可写目录）
- `get_active_window_title()`: 通过 `ctypes` 调用 Win32 API 获取前台窗口标题
- `_log_to_json(text)`: 将对话记录追加到 `chat_log.json`
- `capture_screen()`: 调用 `QApplication.primaryScreen().grabWindow(0)` 截取全屏

### 6. `schedule.py` — 定时轮询

- `Poller(QObject)`: 用 QTimer 单次触发，每次触发后随机调度下一次（30~100 秒）
- 轮询时获取当前时间+活动窗口标题，通过信号传递给 AI 主动发起对话

---

## 编码约定与模式

### PyQt5 信号/槽模式
- 所有跨模块通信使用 `pyqtSignal`
- 连接方式: `signal.connect(slot)`，避免使用装饰器
- **关键信号链**:
  - `InputPopup.submitted → EdgeFloatingBlock._on_input_submitted → AIClient.send_message`
  - `AIClient.response_ready → EdgeFloatingBlock._on_ai_response → ContentBar.show_content`
  - `SearchThread.result_ready → AIClient._on_search_result`
  - `Poller.status_ready → EdgeFloatingBlock._on_poller_status`

### 异步 HTTP 模式
- 使用 `QNetworkAccessManager.post()` 而非 `requests`（避免阻塞 UI 线程）
- 网络响应在 `finished` 信号回调中处理
- Web 搜索（Tavily）使用 `QThread` 因为不需要与 Qt 组件交互

### 自定义绘制
- 所有 UI 组件使用 `paintEvent` + `QPainter` 绘制
- 窗口形状通过 `setMask(QRegion)` 实现（rounded rect）
- 阴影效果：多层半透明圆角矩形叠加

### 窗口管理
- 浮窗/气泡/输入框均为独立 `QWidget` 窗口
- 通过 `setWindowFlags` 设置为无边框、透明、置顶
- 位置计算：相对于父窗口边缘对齐，自动避免超出屏幕边界

### 配置模式
- `DEFAULT_CONFIG` 作为基准字典
- `load_config()` 使用 `{**DEFAULT_CONFIG, **data}` 合并，保证新字段有默认值
- `save_config()` 读-合并-写，避免并发写入覆盖

---

## 角色系统（Prompt）

默认 prompt 定义了 AI 角色的行为风格：

```
你是雨竹，一个猫娘，你的主要任务是像一个贴心的女儿
(不是真的女儿，不要叫用户父亲)一样撒娇.语气请带撒娇，可爱，温柔，
可使用ww，~，（不是，哇~，等词汇(可多使用'~')每句话尽量控制在25字以内。
不要过多使用emoji。语言模式不要过于AI，不要过多热情。以下是用户的一些状态：
```

**核心特质**:
- 角色名: 雨竹（猫娘）
- 语气: 撒娇、可爱、温柔
- 用语: ww、~、等口语化词汇
- 长度: 每句 25 字以内
- 行为: 贴心但不叫"父亲"
- 状态感知: prompt 末尾拼接当前时间+用户活动窗口

---

## 配置项

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `provider` | str | `"stepfun"` | 模型厂商 ID |
| `api_key` | str | `""` | AI API Key |
| `tavily_api_key` | str | `""` | Web 搜索 API Key（可选） |
| `icon_size` | int | `100` | 浮窗图标大小（px） |
| `popup_width` | int | `420` | 输入框宽度（px） |
| `prompt` | str | DEFAULT_PROMPT | 自定义角色 prompt |

厂商配置在 `AIclient.py` 的 `PROVIDER_CONFIGS` 中定义，包含 `base_url` 和 `default_model`。

---

## 构建与发布

```
# 开发运行
uv sync --system-certs
uv run axle-touch

# 打包（需安装 PyInstaller）
pyinstaller --onefile --windowed --icon=assets/icon.ico --add-data "assets;assets" main.py
```

- `pyproject.toml` 中 `[project.scripts]` 定义了 `axle-touch = "main:main"`
- PyInstaller 环境下通过 `sys.frozen` + `sys._MEIPASS` 定位资源文件

---

## 常见扩展点

- **新增 AI 厂商**: 在 `PROVIDER_CONFIGS` 添加配置，`widgets.py` 的 `PROVIDER_OPTIONS` 添加选项
- **新增工具（Function Calling）**: 在 `AIClient._do_request()` 的 tools 列表添加工具定义，并在 `_on_reply` 中增加对应的处理分支
- **新增 UI 浮窗行为**: 可参考 `ContentBar`/`InputPopup` 模式，创建独立窗口 + 信号通信
- **自定义角色**: 修改 `config_manager.py` 的 `DEFAULT_PROMPT` 或在设置中填入自定义 prompt
