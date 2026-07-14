# AxleTouch

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

> **雨竹** — 一只贴心的 AI 桌宠，陪你聊天、帮你搜索、时刻陪伴。

---

## 📖 项目简介

AxleTouch 是一个基于 **PyQt5** 开发的轻量级桌面宠物应用，核心角色为猫娘“雨竹”。她会以浮窗形式贴边吸附在屏幕侧边，用户单击即可唤出输入框与她对话，AI 回复以气泡形式展示。

项目支持多模型厂商接入、Web 搜索、屏幕截图分析、图片识别（多模态）等功能，适合作为桌面助手或个人娱乐使用。

**技术栈**：Python 3.8+ / PyQt5 / QNetworkAccessManager / Tavily Search API

---

## ✨ 核心功能与特性

| 特性 | 说明 |
|------|------|
| 🖥️ 贴边吸附 | 拖拽后自动吸附到屏幕左/右侧，保持界面清爽 |
| 💬 AI 对话 | 单击桌宠弹出输入框，AI 回复以气泡形式展示，带有进度倒计时 |
| ⏰ 定时问候 | 定时获取当前活动窗口状态，主动发起对话问候 |
| 🤖 多模型支持 | 支持阶跃星辰、阿里百炼、DeepSeek 等厂商，可在设置中切换 |
| 🖼️ 多模态识别 | 支持拖拽图片到输入框进行图片识别（StepFun 厂商） |
| 🔍 Web 搜索 | 配置 Tavily API Key 后，雨竹可自动进行网络搜索并汇总结果 |
| 🖱️ 右键菜单 | 右键桌宠可打开 GUI 设置、查看屏幕或退出程序 |
| 📸 屏幕查看 | 邀请雨竹查看当前屏幕截图，并进行内容分析 |
| 📝 聊天日志 | 自动记录对话历史，方便回溯 |
| 🎨 自定义角色 | 可在设置中修改角色 prompt，自定义雨竹的说话风格 |

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
| **拖拽图片** 到输入框 | 发送图片给支持多模态的模型（StepFun） |

### 配置说明

首次启动或通过右键菜单打开“设置”对话框，可配置以下内容：

```json
{
    "provider": "stepfun",           // 模型厂商：stepfun / bailian / deepseek
    "api_key": "",                   // 对应厂商的 API Key
    "tavily_api_key": "",            // Tavily Web 搜索 API Key（可选）
    "icon_size": 100,                // 浮窗图标大小（px）
    "popup_width": 420,              // 输入框宽度（px）
    "prompt": "你是雨竹，一个猫娘..."  // 自定义角色 prompt
}
```

**厂商 API Key 获取地址**：

| 厂商 | provider 值 | 获取地址 |
|------|-------------|----------|
| 阶跃星辰 | `stepfun` | [platform.stepfun.com](https://platform.stepfun.com) |
| 阿里百炼 | `bailian` | [bailian.console.aliyun.com](https://bailian.console.aliyun.com) |
| DeepSeek | `deepseek` | [platform.deepseek.com](https://platform.deepseek.com) |

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
├── assets/                 # 静态资源
│   ├── icon.ico            # 应用图标
│   ├── image.svg           # 桌宠头像
│   └── image1.jpg          # 备用图片
├── pyproject.toml          # 项目元数据与依赖配置
├── README.md               # 项目说明文档
├── LICENSE                 # 开源许可证
├── PRIVACY.md              # 隐私声明
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
