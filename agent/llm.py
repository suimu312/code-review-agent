"""LLM 客户端封装：支持 OpenAI 兼容接口，带重试机制。"""

import os
import time
import logging
from openai import OpenAI, APIError, APITimeoutError, RateLimitError

logger = logging.getLogger(__name__)


class LLMClient:
    """对 OpenAI SDK 的薄封装，统一处理配置、重试和超时。"""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "your-api-key-here")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.max_retries = int(os.getenv("MAX_RETRIES", max_retries))
        self.timeout = int(os.getenv("REQUEST_TIMEOUT", timeout))

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )
        logger.info("LLMClient 初始化完成，模型=%s，base_url=%s", self.model, self.base_url)

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """
        发起一次对话补全请求，带指数退避重试。

        返回 OpenAI 原始 message 对象（dict），包含 role / content / tool_calls 等字段。
        """
        last_err = None
        for attempt in range(1, self.max_retries + 1):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                resp = self.client.chat.completions.create(**kwargs)
                msg = resp.choices[0].message
                # 转成 dict 方便后续处理
                result = {
                    "role": "assistant",
                    "content": msg.content,
                }
                if msg.tool_calls:
                    result["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ]
                logger.debug("LLM 返回: content=%s, tool_calls=%s",
                             bool(result["content"]),
                             len(result.get("tool_calls", [])))
                return result

            except (APITimeoutError, RateLimitError, APIError) as e:
                last_err = e
                wait = 2 ** (attempt - 1)
                logger.warning("LLM 请求第 %d 次失败: %s，%d 秒后重试…", attempt, e, wait)
                time.sleep(wait)

        raise RuntimeError(f"LLM 连续 {self.max_retries} 次请求失败: {last_err}")
