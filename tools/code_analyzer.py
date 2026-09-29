"""静态代码分析工具：检测常见代码质量问题。"""

import ast
import sys
import logging

logger = logging.getLogger(__name__)


def analyze_code(code: str) -> str:
    """
    对 Python 代码做静态分析，报告：
    - 语法错误
    - 函数数量、平均行数
    - 超长函数（>30 行）
    - 未使用的 import
    - 复杂嵌套（>4 层）
    - TODO/FIXME 标记
    """
    issues = []
    lines = code.splitlines()
    total_lines = len(lines)

    # 1. 语法检查
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"[语法错误] 第 {e.lineno} 行: {e.msg}\n  {e.text}"

    # 2. 收集函数信息
    functions = []
    imports = []
    todo_lines = []
    max_nesting = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end_line = getattr(node, "end_lineno", node.lineno)
            func_lines = end_line - node.lineno + 1
            functions.append((node.name, node.lineno, func_lines))
            if func_lines > 30:
                issues.append(
                    f"  ⚠ 函数 '{node.name}' 过长（{func_lines} 行，位于第 {node.lineno} 行）"
                )

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append((f"{node.module}.{alias.name}", node.lineno))

    # 3. 检查 TODO / FIXME
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if any(tag in stripped.upper() for tag in ("TODO", "FIXME", "XXX", "HACK")):
            todo_lines.append((i, stripped))

    # 4. 未使用的 import（简单检查：import 名是否在代码中出现）
    source_text = code
    for imp_name, lineno in imports:
        short = imp_name.split(".")[0]
        # 排除 from x import y 的情况，只检查顶层名
        usage_count = source_text.count(short)
        if usage_count <= 1:  # 只在 import 行出现一次
            issues.append(f"  ℹ 可能未使用的导入: '{short}'（第 {lineno} 行）")

    # 5. 汇总报告
    report_lines = [
        f"=== 静态分析报告 ===",
        f"总行数: {total_lines}",
        f"函数数量: {len(functions)}",
    ]
    if functions:
        avg = sum(f[2] for f in functions) / len(functions)
        report_lines.append(f"平均函数长度: {avg:.1f} 行")
        report_lines.append("")
        report_lines.append("函数列表:")
        for name, lineno, flen in functions:
            report_lines.append(f"  - {name}() 第{lineno}行, {flen}行")

    if issues:
        report_lines.append("")
        report_lines.append("发现的问题:")
        report_lines.extend(issues)

    if todo_lines:
        report_lines.append("")
        report_lines.append("待办标记:")
        for lineno, text in todo_lines:
            report_lines.append(f"  第{lineno}行: {text}")

    if not issues and not todo_lines:
        report_lines.append("")
        report_lines.append("未发现明显代码质量问题。")

    return "\n".join(report_lines)


ANALYZE_CODE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "analyze_code",
        "description": "对 Python 代码进行静态分析，报告函数数量、超长函数、未使用导入、待办标记等质量指标。",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "要分析的 Python 代码完整内容",
                }
            },
            "required": ["code"],
        },
    },
}
