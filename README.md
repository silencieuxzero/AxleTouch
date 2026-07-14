# AxleTouch

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

> **AxleTouch 增强版** — 更快更新节奏、更强功能体验的 AI 桌宠。

---

## 📖 项目简介

AxleTouch 增强版是基于 **PyQt5** 开发的轻量级桌面宠物应用，核心角色为猫娘“雨竹”。她会以浮窗形式贴边吸附在屏幕侧边，用户单击即可唤出输入框与她对话，AI 回复以气泡形式展示。

增强版在保持原有轻量特性的基础上，持续迭代更快的更新速度与更多新功能，包括多模型厂商接入、Web 搜索、屏幕截图分析、图片识别（多模态）、TTS 语音合成等，适合作为桌面助手或个人娱乐使用。

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

- **操作系统**：Windows 7/10/11
- **Python**：>= 3.8（推荐 3.10+）
- **包管理器**：[uv](https://docs.astral.sh/uv/)（推荐）或 pip
- **依赖库**：
  - PyQt5 >= 5.15
  - requests >= 2.28
  - pyttsx3 >= 2.90

---

## 📥 安装步骤

### 方式一：快速体验（EXE）

直接下载 [Releases 页面](https://github.com/baizhou830/AxleTouch/releases) 中的 `AxleTouch.zip`，解压后双击 `AxleTouch.exe` 即可运行。

如需本地重新打包，可下载对应 release 中的 `build.py` 执行打包。

---

### 方式二：二次开发/调试

```bash
# 1. 克隆仓库
git clone https://github.com/baizhou830/AxleTouch.git
cd AxleTouch

# 2. 同步依赖（如遇 SSL 证书错误，加 --system-certs）
uv sync --system-certs

# 3. 运行
uv run axle-touch
```

> 首次启动会自动生成 `config.json` 配置文件。右键桌宠 → “设置”，选择厂商并填入对应的 API Key 即可开始对话。

---

### 方式三：手动安装依赖（pip）

```bash
pip install PyQt5>=5.15 requests>=2.28 pyttsx3>=2.90
python main.py
```

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

- **GitHub 仓库**：[baizhou830/AxleTouch](https://github.com/baizhou830/AxleTouch)
- **问题反馈**：[Issues](https://github.com/baizhou830/AxleTouch/issues)

---

<p align="center">Made with ❤️ by AxleTouch Team</p>
