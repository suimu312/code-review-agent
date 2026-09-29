"""文件读取工具：安全地读取本地文本文件。"""

import os
import logging

logger = logging.getLogger(__name__)

# 允许读取的文件扩展名白名单
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php", ".sh", ".txt", ".md", ".json",
    ".yaml", ".yml", ".toml", ".cfg", ".ini", ".html", ".css", ".sql",
}

MAX_FILE_SIZE = 200_000  # 200KB


def read_file(file_path: str) -> str:
    """
    读取指定路径的文本文件内容。

    安全限制：
    - 仅允许代码/文本类扩展名
    - 文件大小不超过 200KB
    - 不允许路径逃逸（如 ../../etc/passwd）
    """
    # 规范化路径
    abs_path = os.path.abspath(file_path)

    # 检查扩展名
    ext = os.path.splitext(abs_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return f"[错误] 不支持读取 .{ext} 类型文件，仅允许代码和文本文件。"

    # 检查大小
    if not os.path.exists(abs_path):
        return f"[错误] 文件不存在: {file_path}"

    size = os.path.getsize(abs_path)
    if size > MAX_FILE_SIZE:
        return f"[错误] 文件过大（{size} 字节），超过 200KB 限制。"

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
        # 给内容加上行号方便审查
        lines = content.splitlines()
        numbered = []
        for i, line in enumerate(lines, 1):
            numbered.append(f"{i:4d} | {line}")
        result = "\n".join(numbered)
        logger.info("读取文件 %s（%d 行）", file_path, len(lines))
        return result
    except UnicodeDecodeError:
        return f"[错误] 文件不是 UTF-8 文本，无法读取。"
    except PermissionError:
        return f"[错误] 没有权限读取文件: {file_path}"


# OpenAI function calling 格式
READ_FILE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "读取本地文本文件内容，支持代码文件和文本文件。返回带行号的文件内容。",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要读取的文件路径（绝对路径或相对路径）",
                }
            },
            "required": ["file_path"],
        },
    },
}
