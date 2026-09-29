#!/usr/bin/env python3
"""Code Review Agent — 命令行交互入口。"""

import os
import sys
import logging

# 简单的 .env 加载（不依赖 python-dotenv）
def _load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

_load_env()

from agent.agent import CodeReviewAgent


BANNER = """
╔══════════════════════════════════════════╗
║     Code Review Agent · 代码审查助手      ║
╠══════════════════════════════════════════╣
║  输入代码或文件路径，我来帮你审查。       ║
║  输入 :quit 退出，:clear 清空对话历史     ║
╚══════════════════════════════════════════╝
"""


def main():
    # 日志级别
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # 检查 API Key
    if os.getenv("OPENAI_API_KEY", "") in ("", "your-api-key-here"):
        print("=" * 50)
        print("提示：尚未配置 API Key。")
        print("请复制 .env.example 为 .env 并填入你的 API 信息。")
        print("支持 OpenAI、通义千问、DeepSeek 等 OpenAI 兼容接口。")
        print("=" * 50)
        print()

    print(BANNER)
    agent = CodeReviewAgent()

    while True:
        try:
            user_input = input("\n你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input in (":quit", ":exit", "quit", "exit", "q"):
            print("再见！")
            break
        if user_input == ":clear":
            agent.reset()
            print("（对话历史已清空）")
            continue

        # 执行 Agent 循环
        try:
            response = agent.chat(user_input)
            print(f"\n助手 > {response}")
        except Exception as e:
            print(f"\n[错误] {e}")
            print("（可以输入 :clear 重置对话后重试）")


if __name__ == "__main__":
    main()
