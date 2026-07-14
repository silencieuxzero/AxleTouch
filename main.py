import sys
from AIclient import Client_creater
from PyQt5.QtWidgets import QApplication
from widgets import EdgeFloatingBlock
from config_manager import load_config

def main():
    app = QApplication(sys.argv)
    window = EdgeFloatingBlock()
    config = load_config()
    ai = Client_creater(config)
    ai.set_system_prompt(config.get("prompt", ""))
    # 传递 chat 模块模型名（如有自定义则替换默认）
    chat_cfg = config.get("chat", {})
    provider = chat_cfg.get("provider", "stepfun")
    custom_model = chat_cfg.get("models", {}).get(provider, "")
    if custom_model:
        ai._cfg_override_model = custom_model
    window.set_ai_client(ai, config)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

