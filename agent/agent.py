"""Code Review Agent 核心：实现 Agent 循环（输入 → 推理 → 工具调用 → 输出）。"""

import json
import logging
from agent.llm import LLMClient
from agent.memory import ConversationMemory
from agent.prompts import SYSTEM_PROMPT
from tools.file_reader import read_file, READ_FILE_SCHEMA
from tools.code_executor import execute_python, EXECUTE_PYTHON_SCHEMA
from tools.code_analyzer import analyze_code, ANALYZE_CODE_SCHEMA

logger = logging.getLogger(__name__)

# 工具注册表：名字 -> (执行函数, schema)
TOOL_REGISTRY = {
    "read_file": (read_file, READ_FILE_SCHEMA),
    "execute_python": (execute_python, EXECUTE_PYTHON_SCHEMA),
    "analyze_code": (analyze_code, ANALYZE_CODE_SCHEMA),
}

MAX_TOOL_ROUNDS = 5  # 防止无限工具调用循环


class CodeReviewAgent:
    """
    代码审查 Agent。

    工作循环：
    1. 接收用户输入，写入记忆
    2. 调用 LLM 推理
    3. 如果 LLM 要求调用工具 → 执行工具 → 结果写回记忆 → 回到步骤 2
    4. 如果 LLM 给出最终回答 → 返回给用户
    """

    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()
        self.memory = ConversationMemory(system_prompt=SYSTEM_PROMPT)
        self.tools = [schema for _, schema in TOOL_REGISTRY.values()]

    def chat(self, user_input: str) -> str:
        """
        与用户进行一轮对话。完整执行 Agent 循环。
        """
        # 1. 写入用户消息
        self.memory.add("user", user_input)
        logger.info("用户输入: %s", user_input[:100])

        # 2. Agent 循环
        for round_num in range(1, MAX_TOOL_ROUNDS + 1):
            logger.info("--- Agent 循环第 %d 轮 ---", round_num)

            # 调用 LLM
            messages = self.memory.get_messages()
            assistant_msg = self.llm.chat(messages, tools=self.tools)

            # 如果没有工具调用，直接返回最终回答
            if "tool_calls" not in assistant_msg or not assistant_msg["tool_calls"]:
                self.memory.add("assistant", content=assistant_msg.get("content") or "")
                return assistant_msg.get("content") or "（无回复）"

            # 有工具调用：先把 assistant 消息写入记忆
            self.memory.add(
                "assistant",
                content=assistant_msg.get("content"),
                tool_calls=assistant_msg["tool_calls"],
            )

            # 逐个执行工具调用
            for tool_call in assistant_msg["tool_calls"]:
                result = self._execute_tool(tool_call)
                # 工具结果写入记忆
                self.memory.add(
                    "tool",
                    content=result,
                    tool_call_id=tool_call["id"],
                    name=tool_call["function"]["name"],
                )

        # 超过最大轮数
        return "（工具调用达到最大轮数，已停止。请简化你的问题。）"

    def _execute_tool(self, tool_call: dict) -> str:
        """根据 LLM 的工具调用请求执行对应工具。"""
        func_name = tool_call["function"]["name"]
        try:
            args = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError:
            return f"[错误] 工具参数 JSON 解析失败: {tool_call['function']['arguments']}"

        if func_name not in TOOL_REGISTRY:
            return f"[错误] 未知工具: {func_name}"

        func, _ = TOOL_REGISTRY[func_name]
        logger.info("调用工具 %s, 参数: %s", func_name, args)
        try:
            result = func(**args)
            return result
        except Exception as e:
            logger.exception("工具 %s 执行异常", func_name)
            return f"[错误] 工具 {func_name} 执行异常: {e}"

    def reset(self):
        """清空对话历史。"""
        self.memory.clear()
