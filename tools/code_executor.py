"""Python 代码执行工具：在受控环境中执行代码片段。"""

import subprocess
import sys
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

EXEC_TIMEOUT = 10  # 秒
MAX_OUTPUT = 10_000  # 字符


def execute_python(code: str) -> str:
    """
    在临时文件中执行 Python 代码，捕获 stdout 和 stderr。

    安全措施：
    - 超时 10 秒自动终止
    - 输出截断到 10000 字符
    - 使用独立子进程，不影响主进程
    """
    # 写入临时文件
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=EXEC_TIMEOUT,
            cwd=os.path.dirname(tmp_path),
        )
        output_parts = []
        if result.stdout:
            out = result.stdout[:MAX_OUTPUT]
            output_parts.append(f"标准输出:\n{out}")
            if len(result.stdout) > MAX_OUTPUT:
                output_parts.append(f"...（输出已截断，共 {len(result.stdout)} 字符）")
        if result.stderr:
            err = result.stderr[:MAX_OUTPUT]
            output_parts.append(f"标准错误:\n{err}")
        if not output_parts:
            output_parts.append("（程序正常退出，无输出）")

        exit_info = f"退出码: {result.returncode}"
        output_parts.append(exit_info)
        return "\n".join(output_parts)

    except subprocess.TimeoutExpired:
        return f"[错误] 代码执行超时（>{EXEC_TIMEOUT} 秒），已终止。"
    except Exception as e:
        return f"[错误] 执行失败: {e}"
    finally:
        os.unlink(tmp_path)


EXECUTE_PYTHON_SCHEMA = {
    "type": "function",
    "function": {
        "name": "execute_python",
        "description": "执行一段 Python 代码并返回标准输出和错误输出。用于验证代码行为、复现 Bug。",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "要执行的完整 Python 代码片段",
                }
            },
            "required": ["code"],
        },
    },
}
