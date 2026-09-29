"""对话记忆管理：维护多轮对话上下文。"""

from collections import deque


class ConversationMemory:
    """
    滑动窗口式对话记忆。

    只保留最近 max_turns 轮对话（一轮 = 用户 + 助手各一条），
    避免上下文无限增长。系统消息始终保留在头部。
    """

    def __init__(self, system_prompt: str, max_turns: int = 10):
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self._messages: deque[dict] = deque(maxlen=max_turns * 2)

    def add(self, role: str, content: str | None = None, tool_calls=None, tool_call_id=None, name=None):
        """
        添加一条消息。
        - role: system / user / assistant / tool
        - tool_calls: assistant 发起的工具调用列表
        - tool_call_id / name: tool 角色消息必填
        """
        msg: dict = {"role": role}
        if content is not None:
            msg["content"] = content
        if tool_calls:
            msg["tool_calls"] = tool_calls
        if tool_call_id:
            msg["tool_call_id"] = tool_call_id
        if name:
            msg["name"] = name
        self._messages.append(msg)

    def get_messages(self) -> list[dict]:
        """获取完整消息列表（系统消息 + 滑动窗口历史）。"""
        return [{"role": "system", "content": self.system_prompt}] + list(self._messages)

    def clear(self):
        """清空对话历史。"""
        self._messages.clear()

    def __len__(self):
        return len(self._messages)
