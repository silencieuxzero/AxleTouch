# AxleTouch

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

> **AxleTouch 探索版（AxleTouch Explorer Edition）** — 更快更新节奏、更多功能体验的 AI 桌宠。

---

## 📖 项目简介

AxleTouch 探索版（AxleTouch Explorer Edition）是基于 **PyQt5** 开发的轻量级桌面宠物应用，核心角色为猫娘“雨竹”。她会以浮窗形式贴边吸附在屏幕侧边，用户单击即可唤出输入框与她对话，AI 回复以气泡形式展示。

探索版在保持原有轻量特性的基础上，持续迭代更快的更新速度与更多新功能，包括多模型厂商接入、Web 搜索、屏幕截图分析、图片识别（多模态）、TTS 语音合成等，适合作为桌面助手或个人娱乐使用。

**技术栈**：Python 3.8+ / PyQt5 / QNetworkAccessManager / Tavily Search API

---

## ✨ 核心特性

### 主要功能

| 功能 | 说明 |
|------|------|
| 💬 AI 对话 | 单击桌宠弹出输入框，AI 回复以气泡形式展示，带有进度倒计时 |
| ⏰ 定时问候 | 定时获取当前活动窗口状态，主动发起对话问候 |
| 🤖 多模型支持 | 支持阶跃星辰、阿里百炼、DeepSeek、硅基流动等厂商，可在设置中切换 |
| 🖼️ 多模态识别 | 支持拖拽图片到输入框进行图片识别，新增阶跃星辰识图厂商 |
| 🔍 Web 搜索 | 配置 Tavily API Key 后，雨竹可自动进行网络搜索并汇总结果 |
| 🔊 TTS 语音 | 集成阿里百炼 Qwen3-TTS-Flash / CosyVoice 语音合成，AI 回复自动朗读 |
| 🖱️ 右键菜单 | 右键桌宠可打开 GUI 设置、查看屏幕或退出程序 |
| 📸 屏幕查看 | 邀请雨竹查看当前屏幕截图，并进行内容分析 |
| 📝 聊天日志 | 自动记录对话历史，方便回溯 |
| 🎨 自定义角色 | 可在设置中修改角色 prompt，自定义雨竹的说话风格 |

### 技术优势

- **异步非阻塞**：基于 `QNetworkAccessManager` 实现异步 HTTP 通信，UI 线程永不阻塞
- **模块化架构**：对话、TTS、识图三大模块独立配置，厂商与模型可灵活切换
- **跨模态支持**：统一的消息格式支持文本、图片 URL 混合输入，适配多模态模型
- **后台任务隔离**：Web 搜索、TTS 合成均在独立 `QThread` 中执行，不干扰主界面
- **配置热更新**：设置对话框修改配置后立即生效，无需重启应用
- **自适应布局**：气泡根据文本长度自动调整高度，图标尺寸与输入框自动联动

### 独特创新点

- **角色化交互**：猫娘“雨竹”的拟人化对话体验，支持自定义 prompt 调整性格
- **状态感知**：通过定时轮询获取当前活动窗口，实现上下文感知的主动问候
- **拖拽识图**：直接将图片拖入输入框即可发送给多模态模型，无需复杂操作
- **屏幕分析**：一键截图并发送给 AI，实现“让雨竹看看你的屏幕”的趣味交互
- **视觉优化**：统一色彩体系、5 层阴影、自适应气泡高度、流畅动画过渡

### 适用场景

- 🖥️ **桌面助手**：作为常驻桌面助手，快速获取信息、搜索内容
- 💬 **情感陪伴**：通过拟人化角色获得轻松愉快的交互体验
- 🔍 **效率工具**：快速截图分析、网页搜索，提升工作效率
- 🎨 **个性化定制**：自定义角色 prompt、厂商模型、语音音色，打造专属桌宠
- 🧪 **二次开发**：模块化代码结构便于扩展新厂商、新工具、新交互方式

---

## 🛠️ 环境要求

- **操作系统**：Windows 10/11
- **Python**：>= 3.8（推荐 3.10+）
- **包管理器**：[uv](https://docs.astral.sh/uv/)（推荐）或 pip
- **依赖库**：
  - PyQt5 >= 5.15
  - requests >= 2.28
  - pyttsx3 >= 2.90

---

## 📥 安装步骤

### 方式一：快速体验（EXE）

直接下载 [Releases 页面](https://github.com/baizhou830/AxleTouch/releases) 中的 `AxleTouch.exe`，双击即可运行。

如需本地重新打包，可根据 [打包指南](#📦-打包指南) 进行操作。

---

### 方式二：二次开发/调试

```bash
# 1. 克隆仓库
git clone https://github.com/silencieuxzero/AxleTouch.git
cd AxleTouch

# 2. 同步依赖（如遇 SSL 证书错误，加 --system-certs）
uv sync

# 3. 运行
uv run python main.py
```

> 首次启动会自动生成 `config.json` 配置文件。右键桌宠 → “设置”，选择厂商并填入对应的 API Key 即可开始对话。

---

### 方式三：手动安装依赖（pip）

```bash
pip install PyQt5>=5.15 requests>=2.28 pyttsx3>=2.90
python main.py
```

---

## 📦 打包指南

将项目打包为独立的 `.exe` 可执行文件，方便在未安装 Python 的 Windows 系统上直接运行。

### 环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10/11（64 位） |
| Python | 3.8 ~ 3.14（推荐 3.10+） |
| 打包工具 | [PyInstaller](https://pyinstaller.org/) >= 6.0 |
| 包管理器 | [uv](https://docs.astral.sh/uv/)（推荐）或 pip |
| 磁盘空间 | 至少 2GB 可用空间（用于缓存和临时文件） |

### 安装打包工具

```bash
# 方式一：使用 uv（推荐，项目已预置 dev 依赖）
uv sync --group dev

# 方式二：使用 pip
pip install pyinstaller
```

### 打包前的准备工作

1. **确认所有依赖已安装**：

   ```bash
   uv sync
   ```

2. **确保代码可正常运行**：

   ```bash
   uv run python main.py
   ```

3. **检查资源文件完整性**：确认 `assets/` 目录下存在 `icon.ico`、`image.svg`、`image1.jpg`。

4. **清理缓存**（可选，可减少打包体积）：

   ```bash
   # 清理 Python 缓存文件
   Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
   Get-ChildItem -Recurse -Filter __pycache__ | Remove-Item -Recurse -Force
   ```

### 完整打包命令

#### 生产环境打包（推荐）

生成单文件 exe，隐藏控制台窗口，适合分发给最终用户：

```powershell
pyinstaller --onefile --windowed --noconfirm --clean `
  --name AxleTouch `
  --icon assets/icon.ico `
  --add-data "assets;assets" `
  --hidden-import pyttsx3 `
  --hidden-import ctypes `
  --exclude-module PyQt5.QtWebEngineWidgets `
  --exclude-module PyQt5.QtWebEngine `
  --exclude-module PyQt5.QtBluetooth `
  --exclude-module PyQt5.QtNfc `
  --exclude-module PyQt5.QtPositioning `
  --exclude-module PyQt5.QtMultimedia `
  --exclude-module PyQt5.QtSensors `
  --exclude-module PyQt5.QtXmlPatterns `
  --exclude-module PyQt5.QtQuick `
  --exclude-module PyQt5.QtQml `
  --exclude-module PyQt5.QtDesigner `
  --exclude-module PyQt5.QtHelp `
  --exclude-module PyQt5.QtTest `
  --exclude-module PyQt5.QtSql `
  --exclude-module PyQt5.QtPrintSupport `
  --exclude-module numpy `
  --exclude-module pandas `
  --exclude-module matplotlib `
  --exclude-module scipy `
  --exclude-module IPython `
  --exclude-module PIL `
  --exclude-module tkinter `
  --exclude-module unittest `
  --exclude-module pytest `
  --exclude-module setuptools `
  --exclude-module pip `
  --exclude-module cryptography `
  --exclude-module lxml `
  main.py
```

> **注意**：以上命令在 PowerShell 中执行。如果使用 CMD，请将行尾的反引号（`` ` ``）替换为脱字符（`^`），或将所有参数写在同一行。

#### 开发环境打包（带控制台）

生成带控制台窗口的 exe，便于调试和查看日志输出：

```powershell
pyinstaller --onefile --noconfirm --clean `
  --name AxleTouch_Debug `
  --icon assets/icon.ico `
  --add-data "assets;assets" `
  --hidden-import pyttsx3 `
  --hidden-import ctypes `
  --exclude-module PyQt5.QtWebEngineWidgets `
  --exclude-module PyQt5.QtWebEngine `
  --exclude-module PyQt5.QtBluetooth `
  --exclude-module PyQt5.QtNfc `
  --exclude-module PyQt5.QtPositioning `
  --exclude-module PyQt5.QtMultimedia `
  --exclude-module PyQt5.QtSensors `
  --exclude-module PyQt5.QtXmlPatterns `
  --exclude-module PyQt5.QtQuick `
  --exclude-module PyQt5.QtQml `
  --exclude-module PyQt5.QtDesigner `
  --exclude-module PyQt5.QtHelp `
  --exclude-module PyQt5.QtTest `
  --exclude-module PyQt5.QtSql `
  --exclude-module PyQt5.QtPrintSupport `
  --exclude-module numpy `
  --exclude-module pandas `
  --exclude-module matplotlib `
  --exclude-module scipy `
  --exclude-module IPython `
  --exclude-module PIL `
  --exclude-module tkinter `
  --exclude-module unittest `
  --exclude-module pytest `
  --exclude-module setuptools `
  --exclude-module pip `
  --exclude-module cryptography `
  --exclude-module lxml `
  main.py
```

#### 最小化打包（体积优先）

仅保留核心功能，进一步排除 pyttsx3（TTS 离线引擎）：

```powershell
pyinstaller --onefile --windowed --noconfirm --clean `
  --name AxleTouch_Min `
  --icon assets/icon.ico `
  --add-data "assets;assets" `
  --hidden-import ctypes `
  --exclude-module pyttsx3 `
  --exclude-module PyQt5.QtWebEngineWidgets `
  --exclude-module PyQt5.QtWebEngine `
  --exclude-module PyQt5.QtBluetooth `
  --exclude-module PyQt5.QtNfc `
  --exclude-module PyQt5.QtPositioning `
  --exclude-module PyQt5.QtMultimedia `
  --exclude-module PyQt5.QtSensors `
  --exclude-module PyQt5.QtXmlPatterns `
  --exclude-module PyQt5.QtQuick `
  --exclude-module PyQt5.QtQml `
  --exclude-module PyQt5.QtDesigner `
  --exclude-module PyQt5.QtHelp `
  --exclude-module PyQt5.QtTest `
  --exclude-module PyQt5.QtSql `
  --exclude-module PyQt5.QtPrintSupport `
  --exclude-module numpy `
  --exclude-module pandas `
  --exclude-module matplotlib `
  --exclude-module scipy `
  --exclude-module IPython `
  --exclude-module PIL `
  --exclude-module tkinter `
  --exclude-module unittest `
  --exclude-module pytest `
  --exclude-module setuptools `
  --exclude-module pip `
  --exclude-module cryptography `
  --exclude-module lxml `
  main.py
```

### 打包参数说明

| 参数 | 说明 |
|------|------|
| `--onefile` | 打包为单个 exe 文件 |
| `--windowed` / `-w` | 隐藏控制台窗口（GUI 模式） |
| `--noconfirm` | 覆盖输出目录时不提示确认 |
| `--clean` | 打包前清理临时缓存 |
| `--name` | 指定输出 exe 文件名 |
| `--icon` | 指定 exe 图标文件 |
| `--add-data "src;dst"` | 将资源文件夹嵌入 exe，分号前为源路径，分号后为目标路径 |
| `--hidden-import` | 强制包含 PyInstaller 无法自动发现的模块 |
| `--exclude-module` | 排除不需要的模块以减小体积 |
| `--upx-dir` | 指定 [UPX](https://upx.github.io/) 压缩工具目录（可选，可进一步减小体积） |

### 打包后文件目录结构

```text
AxleTouch/
├── dist/                          # 打包输出目录
│   └── AxleTouch.exe              # 最终生成的可执行文件（约 40~45 MB）
├── build/                         # 打包中间文件（可安全删除）
│   └── AxleTouch/
│       ├── Analysis-00.toc
│       ├── PYZ-00.pyz
│       ├── base_library.zip
│       └── ...
├── AxleTouch.spec                 # PyInstaller 配置文件（可删除或保留用于后续构建）
├── config.json                    # 首次运行时自动生成（与 exe 同目录）
├── chat_log.json                  # 运行时自动生成（与 exe 同目录）
└── ...
```

**运行时的文件结构**（exe 首次启动后）：

```text
AxleTouch.exe 所在目录/
├── AxleTouch.exe                  # 主程序
├── config.json                    # 配置文件（自动生成，包含 API Key 等设置）
├── chat_log.json                  # 聊天日志（自动生成）
└── _internal/                     # （仅非 --onefile 模式）依赖库目录
```

> 用户可直接将 `dist/AxleTouch.exe` 复制到任意目录运行，首次启动会自动在同级目录生成 `config.json`。

### 注意事项

1. **杀软误报**：单文件 exe 可能被部分杀毒软件误报为病毒。这是由于 PyInstaller 的打包特性（自解压 + 代码合并）导致的误判。如需解决：
   - 提交至杀软厂商申诉白名单
   - 或使用 `--key` 参数加密打包（需用户输入密钥运行）
   - 或使用数字签名工具对 exe 进行签名

2. **体积说明**：生成 exe 约 40~45 MB，其中 PyQt5 的 Qt 运行时库（DLL）占 ~30 MB，Python 解释器及标准库占 ~8 MB，项目代码和资源占 ~2 MB。这是 PyQt5 应用的正常体积范围。

3. **Python 3.14 兼容性**：PyInstaller 6.x 已支持 Python 3.14，但某些第三方 hook 可能需要更新。如遇兼容问题，建议使用 Python 3.10 ~ 3.13。

4. **资源路径**：
   - 打包后，`get_base_path()` 返回 PyInstaller 解压临时目录（`sys._MEIPASS`）
   - `get_data_path()` 返回 exe 所在目录
   - 配置文件 `config.json` 和聊天日志 `chat_log.json` 存储在 exe 同级目录

5. **API Key 安全**：`config.json` 以明文存储 API Key，请勿将生成的 `dist/` 目录或 `config.json` 上传至公开仓库。

6. **增量构建**：如果仅修改了 Python 源代码，无需每次都 `--clean`，移除该参数可大幅缩短二次打包时间。

7. **UPX 压缩**（可选）：下载 [UPX](https://upx.github.io/) 并解压后，使用 `--upx-dir` 参数指定路径，可将 exe 体积减小 10%~20%，但会增加启动解压时间。

### 常见打包问题及解决方法

#### Q1: 打包后 exe 启动报错 "Failed to execute script"

**原因**：通常由缺少隐藏导入（hidden import）或资源文件路径错误导致。

**解决方法**：
1. 先在命令行中运行 exe 查看具体报错（使用不带 `--windowed` 的打包方式）：
   ```bash
   pyinstaller --onefile --name AxleTouch_Debug main.py
   ```
2. 根据报错信息添加对应的 `--hidden-import` 参数
3. 检查 `--add-data` 中的资源路径是否正确（在打包环境中，`assets` 目录必须存在于项目根目录）

#### Q2: 打包体积过大（超过 100MB）

**原因**：未排除不必要的 PyQt5 模块或第三方库。

**解决方法**：
1. 检查是否遗漏了 `--exclude-module` 参数
2. 确认是否包含了 PyQt5.QtWebEngine（该模块约 50MB+）
3. 使用最小化打包方案（见上文）
4. 检查是否存在不必要的 `site-packages` 依赖

#### Q3: 打包后 TTS 功能异常

**原因**：`pyttsx3` 可能未被正确包含，或缺少 Windows 音频依赖。

**解决方法**：
1. 确认打包命令中包含 `--hidden-import pyttsx3`
2. 确保目标系统安装了音频输出设备
3. 检查 `tts_manager.py` 中是否正确传递了 API Key
4. 如使用在线 TTS（Qwen/Bailian），需确保目标系统可访问阿里百炼 API

#### Q4: 打包后截图功能失效

**原因**：截图功能依赖 `QApplication.primaryScreen()`，在无显示器的环境下（如远程桌面）可能不可用。

**解决方法**：
1. 确保在本地桌面环境运行，而非远程桌面或无 GUI 的终端
2. 检查是否有其他程序独占屏幕资源

#### Q5: 杀毒软件报毒或拦截

**原因**：PyInstaller 打包的单文件 exe 包含自解压代码和行为特征与某些病毒相似。

**解决方法**：
1. 添加杀毒软件信任区/白名单
2. 使用数字签名工具对 exe 进行签名
3. 向杀毒厂商提交误报申诉
4. 或上传至 [VirusTotal](https://www.virustotal.com/) 检查具体报毒引擎

#### Q6: 打包报错 "UPX is not available"

**原因**：系统未安装 UPX 压缩工具。

**解决方法**：此错误仅为警告，不影响打包过程。可忽略，或下载 [UPX](https://upx.github.io/) 后通过 `--upx-dir` 指定路径。

#### Q7: 打包后窗口无法贴边或位置异常

**原因**：多显示器环境或屏幕分辨率获取异常。

**解决方法**：
- 确认 `QApplication.primaryScreen().geometry()` 正确返回屏幕尺寸
- 在主显示器上运行，或在代码中添加多显示器支持

#### Q8: 打包后 exe 可以在本机运行，但复制到其他电脑报错

**原因**：目标系统缺少必要的 Visual C++ 运行库，或 Windows 版本过低。

**解决方法**：
1. 确保目标系统安装了 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)（2015-2022 版本）
2. 目标系统需为 Windows 10 及以上版本
3. 如果目标系统为 Windows 7，需使用 Python 3.8 打包并确保安装了相关补丁

---

## 🚀 使用指南

### 基本操作

| 操作 | 效果 |
|------|------|
| **单击** 桌宠图标 | 弹出输入框，输入文字后按回车或点击发送 |
| **拖拽** 桌宠图标 | 移动窗口位置，释放后自动贴边吸附 |
| **右键** 桌宠图标 | 打开菜单：设置 / 截图 / 退出 |
| **拖拽图片** 到输入框 | 发送图片给支持多模态的模型 |

### 配置说明

首次启动或通过右键菜单打开“设置”对话框，可配置以下内容：

```json
{
    "chat": {
        "provider": "stepfun",                          // 对话厂商：stepfun / bailian / deepseek / siliconflow
        "api_keys": { "stepfun": "...", "bailian": "..." },
        "models": { "stepfun": "step-3.7-flash", "bailian": "qwen-turbo" }
    },
    "tts": {
        "enabled": true,
        "engine": "qwen",                                // qwen / bailian
        "api_key": "...",
        "voice": "Cherry"
    },
    "vision": {
        "provider": "bailian",                           // 识图厂商：bailian / siliconflow / stepfun
        "api_keys": { "bailian": "...", "stepfun": "..." },
        "models": { "bailian": "qwen-vl-max", "stepfun": "step-1.5v-mini" }
    },
    "tavily_api_key": "",                               // Web 搜索 API Key（可选）
    "icon_size": 135,                                   // 浮窗图标大小（px）
    "popup_width": 420,                                 // 输入框宽度（px）
    "prompt": "你是雨竹，一个猫娘..."                    // 自定义角色 prompt
}
```

**厂商 API Key 获取地址**：

| 厂商 | provider 值 | 获取地址 |
|------|-------------|----------|
| 阶跃星辰 | `stepfun` | [platform.stepfun.com](https://platform.stepfun.com) |
| 阿里百炼 | `bailian` | [bailian.console.aliyun.com](https://bailian.console.aliyun.com) |
| DeepSeek | `deepseek` | [platform.deepseek.com](https://platform.deepseek.com) |
| 硅基流动 | `siliconflow` | [siliconflow.cn](https://siliconflow.cn) |

---

### 常见功能使用示例

#### 1. AI 对话

```python
# 无需代码，直接在输入框输入即可
# 示例：
你：今天天气怎么样？
雨竹：让我帮你查一下哦~
# 若已配置 Tavily Key，雨竹会自动搜索并回复最新天气信息
```

#### 2. 图片识别（多模态）

1. 在设置中切换识图厂商为 **阶跃星辰** 或 **阿里百炼**
2. 填写对应厂商的 API Key
3. 将本地图片（PNG/JPG/JPEG/BMP/GIF）直接拖入输入框
4. 雨竹会自动识别图片内容并回复

#### 3. 屏幕截图分析

1. 右键桌宠 → 选择 **"让雨竹看看！"**
2. 雨竹会自动截取当前屏幕并分析内容
3. 分析结果以气泡形式展示

#### 4. TTS 语音合成

1. 在设置中切换到 **TTS** 标签页
2. 启用 TTS 开关
3. 选择引擎（Qwen3-TTS-Flash 或 CosyVoice）
4. 填写 API Key 并选择音色
5. 保存后，雨竹的每次回复都会自动朗读

#### 5. Web 搜索

1. 在设置中填写 **Tavily API Key**
2. 询问雨竹实时信息，如“今天新闻有什么？”
3. 雨竹会自动调用搜索工具并汇总结果

#### 6. 自定义角色

1. 在设置中切换到 **通用** 标签页
2. 在 Prompt 输入框中修改角色设定
3. 保存后，雨竹会按照新的角色设定进行对话

---

### 注意事项

- **API Key 安全**：`config.json` 以明文存储 API Key，请勿将其上传至公开仓库
- **网络要求**：AI 对话、Web 搜索、TTS 等功能需要保持网络连接
- **厂商兼容性**：不同厂商的模型能力不同，识图功能需选择支持多模态的厂商（阶跃星辰/阿里百炼/硅基流动）
- **配置备份**：升级版本前建议备份 `config.json` 和 `chat_log.json`
- **Windows 兼容性**：TTS 功能依赖 Windows MCI API，仅支持 Windows 系统
- **资源路径**：打包为 EXE 后，资源文件位于 `_MEIPASS` 临时目录，开发模式下位于项目根目录

---

## 📁 项目结构说明

```
AxleTouch/
├── main.py                 # 应用入口，组装 QApplication、EdgeFloatingBlock、AIClient
├── widgets.py              # UI 组件：主浮窗、气泡、输入框、设置对话框
├── AIclient.py             # AI 客户端：封装多厂商对话 API、工具调用（Web 搜索）
├── AIweb.py                # 后台 Web 搜索线程（Tavily API）
├── config_manager.py       # JSON 配置文件读写与管理
├── tools.py                # 工具函数：路径解析、获取活动窗口标题、截屏、聊天日志
├── schedule.py             # 定时轮询：获取活动窗口并触发 AI 问候
├── tts_manager.py          # TTS 语音合成管理器
├── tts_qwen.py             # 阿里百炼 Qwen3-TTS-Flash 引擎
├── tts_bailian.py          # 阿里百炼 CosyVoice 引擎
├── assets/                 # 静态资源
│   ├── icon.ico            # 应用图标
│   ├── image.svg           # 桌宠头像
│   └── image1.jpg          # 备用图片
├── pyproject.toml          # 项目元数据与依赖配置
├── README.md               # 项目说明文档
├── update.md               # 更新日志
├── LICENSE                 # 开源许可证
└── config.json             # 用户配置文件（首次运行自动生成）
```

---

## 🤝 贡献规范

欢迎提交 Issue 和 Pull Request！

1. **提交 Issue**：请描述清楚问题现象、复现步骤、环境信息（Python 版本、操作系统等）。
2. **代码风格**：遵循 PEP 8，保持代码简洁，关键逻辑添加必要注释。
3. **提交 PR**：请确保代码可正常运行，并在 PR 描述中说明修改内容与目的。
4. **新增厂商/工具**：请同步更新 `AIclient.py` 中的厂商配置与 `widgets.py` 中的厂商选项。

如有疑问，可通过 [GitHub Issues](https://github.com/baizhou830/AxleTouch/issues) 联系维护者。

---

## 📄 许可证

本项目基于 **GNU General Public License v3 (GPL-3.0-only)** 开源协议发布。

详见 [LICENSE](LICENSE) 文件。

---

## 📬 联系方式

- **GitHub 仓库**：[silencieuxzero/AxleTouch](https://github.com/silencieuxzero/AxleTouch)
- **问题反馈**：[Issues](https://github.com/silencieuxzero/AxleTouch/issues)

---

<p align="center">Made with ❤️ by AxleTouch Team</p>
