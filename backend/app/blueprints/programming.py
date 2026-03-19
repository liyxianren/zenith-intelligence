"""Programming assistant API blueprint."""

import json
import os
import shutil
import subprocess
import sys
import tempfile

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.ai_service import ai_service

programming_bp = Blueprint("programming", __name__)


def _find_command(*candidates: str) -> str | None:
    for candidate in candidates:
        if candidate and shutil.which(candidate):
            return candidate
    return None


def _build_execution_response(result: subprocess.CompletedProcess[str], language: str):
    return jsonify({
        "success": True,
        "data": {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returnCode": result.returncode,
            "language": language
        }
    })


def _build_programming_user_prompt(task_prompt: str, response_template: dict) -> str:
    template_json = json.dumps(response_template, ensure_ascii=False, indent=2)
    return (
        f"{task_prompt}\n\n"
        "请严格输出一个合法 JSON 对象，不要使用 Markdown 代码块，也不要添加 JSON 之外的说明文字。\n"
        f"JSON 结构如下：\n{template_json}"
    )


def _run_programming_ai_task(
    task_prompt: str,
    response_template: dict,
    provider: str | None = None,
    fallback_field: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> dict:
    system_prompt = (
        "你是一位资深编程教练、代码审查专家和调试助手。"
        "请严格返回一个合法 JSON 对象。"
        "除 JSON 本身外，不要输出任何额外说明。"
        "如果字段内容包含代码，请直接输出原始代码文本，不要再包裹 Markdown 代码块。"
    )
    user_prompt = _build_programming_user_prompt(task_prompt, response_template)
    return ai_service.complete_structured_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        response_template=response_template,
        provider_name=provider,
        temperature=temperature,
        max_tokens=max_tokens,
        fallback_field=fallback_field,
    )


@programming_bp.route("/explain", methods=["POST"])
@jwt_required()
def explain_code():
    """Explain code using AI."""
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    provider = data.get("provider")

    if not code:
        return jsonify({"success": False, "error": "代码不能为空"}), 400

    try:
        prompt = f"""请解释以下 {language} 代码：

```{language}
{code}
```

要求：
1. 直接回答，不要输出思考过程、分析草稿或客套开场。
2. 使用简洁的 Markdown，优先用短段落或 3-5 条要点。
3. 必须用行内代码或代码块引用关键语句，例如 `print(1)`。
4. 说明代码作用、执行结果，以及关键语句为什么这样写。
5. 如果代码非常简单，不要过度展开，不要凭空补充底层实现细节。
6. 只有在确实存在改进空间时再提优化建议，否则明确写“这段代码已经足够简单，无需优化”。

输出风格：
- 面向初学者
- 简短、直接、易读
- 保留 Markdown 格式，不要转义成纯文本"""

        result = _run_programming_ai_task(
            task_prompt=prompt,
            response_template={
                "explanation": "使用 Markdown 简洁解释代码，包含关键语句引用、运行结果和必要说明。"
            },
            provider=provider,
            fallback_field="explanation",
            temperature=0.1,
            max_tokens=700,
        )

        return jsonify({
            "success": True,
            "data": {
                "explanation": result.get("explanation", ""),
                "language": language
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@programming_bp.route("/review", methods=["POST"])
@jwt_required()
def review_code():
    """Review code and provide suggestions."""
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    provider = data.get("provider")

    if not code:
        return jsonify({"success": False, "error": "代码不能为空"}), 400

    try:
        prompt = f"""请审查以下 {language} 代码：

```{language}
{code}
```

请从以下几个方面进行审查：
1. 代码质量和可读性
2. 潜在的 bug 或错误
3. 性能问题
4. 安全隐患
5. 最佳实践建议

请提供具体的改进建议和示例代码。"""

        result = _run_programming_ai_task(
            task_prompt=prompt,
            response_template={
                "review": "从代码质量、潜在 bug、性能、安全和最佳实践角度给出结构化审查意见。"
            },
            provider=provider,
            fallback_field="review",
        )

        return jsonify({
            "success": True,
            "data": {
                "review": result.get("review", ""),
                "language": language
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@programming_bp.route("/debug", methods=["POST"])
@jwt_required()
def debug_code():
    """Debug code and find errors."""
    data = request.get_json() or {}
    code = data.get("code", "")
    error_message = data.get("errorMessage", "")
    language = data.get("language", "python")
    provider = data.get("provider")

    if not code:
        return jsonify({"success": False, "error": "代码不能为空"}), 400

    try:
        prompt = f"""请帮助调试以下 {language} 代码：

```{language}
{code}
```

错误信息：
{error_message if error_message else '无具体错误信息'}

请：
1. 分析可能的错误原因
2. 指出具体的错误位置
3. 提供修复方案
4. 给出修正后的代码"""

        result = _run_programming_ai_task(
            task_prompt=prompt,
            response_template={
                "debug": "分析错误原因，指出问题位置，并给出修复后的完整代码与解释。"
            },
            provider=provider,
            fallback_field="debug",
        )

        return jsonify({
            "success": True,
            "data": {
                "debug": result.get("debug", ""),
                "language": language
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@programming_bp.route("/execute", methods=["POST"])
@jwt_required()
def execute_code():
    """Execute supported code safely."""
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    timeout = min(data.get("timeout", 5), 10)

    if not code:
        return jsonify({"success": False, "error": "代码不能为空"}), 400

    if language not in ["python", "javascript", "java", "cpp", "c"]:
        return jsonify({"success": False, "error": "目前只支持 Python、JavaScript、Java、C++ 和 C 语言代码执行"}), 400

    if language == "python":
        dangerous_keywords = [
            "import os", "import sys", "import subprocess", "import shutil",
            "import glob", "import pickle", "import marshal", "import socket",
            "open(", "exec(", "eval(", "compile(", "__import__",
            "exit(", "quit(", "input("
        ]
        
        for keyword in dangerous_keywords:
            if keyword in code:
                return jsonify({
                    "success": False,
                    "error": f"代码包含不允许的关键字: {keyword}"
                }), 400

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = os.path.join(temp_dir, "main.py")
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(code)

                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            return _build_execution_response(result, language)
        except subprocess.TimeoutExpired:
            return jsonify({"success": False, "error": f"代码执行超时（超过 {timeout} 秒）"}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif language == "javascript":
        dangerous_keywords = [
            "require('child_process')", 'require("child_process")',
            "require('fs')", 'require("fs")',
            "require('net')", 'require("net")',
            "require('http')", 'require("http")',
            "require('https')", 'require("https")',
            "process.exit(", "eval("
        ]

        for keyword in dangerous_keywords:
            if keyword in code:
                return jsonify({
                    "success": False,
                    "error": f"代码包含不允许的关键字: {keyword}"
                }), 400

        node_command = _find_command("node")
        if not node_command:
            return jsonify({"success": False, "error": "未检测到 Node.js 运行时"}), 500

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = os.path.join(temp_dir, "main.js")
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(code)

                result = subprocess.run(
                    [node_command, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            return _build_execution_response(result, language)
        except subprocess.TimeoutExpired:
            return jsonify({"success": False, "error": f"代码执行超时（超过 {timeout} 秒）"}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif language in ["c", "cpp"]:
        dangerous_keywords = [
            "system(", "exec(", "popen(", "fork(", "fopen("
        ]

        for keyword in dangerous_keywords:
            if keyword in code:
                return jsonify({
                    "success": False,
                    "error": f"{'C++' if language == 'cpp' else 'C'} 语言沙盒安全拦截：不允许包含敏感系统指令如: {keyword}"
                }), 400

        compiler = _find_command("g++") if language == "cpp" else _find_command("gcc")
        if not compiler:
            return jsonify({
                "success": False,
                "error": f"未检测到{'g++' if language == 'cpp' else 'gcc'} 编译器"
            }), 500

        try:
            suffix = ".cpp" if language == "cpp" else ".c"
            with tempfile.TemporaryDirectory() as temp_dir:
                source_file = os.path.join(temp_dir, f"main{suffix}")
                exe_file = os.path.join(temp_dir, "main.exe")

                with open(source_file, "w", encoding="utf-8") as f:
                    f.write(code)

                compile_result = subprocess.run(
                    [compiler, source_file, "-o", exe_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if compile_result.returncode != 0:
                    return jsonify({
                        "success": True,
                        "data": {
                            "stdout": "",
                            "stderr": "编译错误:\n" + compile_result.stderr,
                            "returnCode": compile_result.returncode,
                            "language": language
                        }
                    })

                run_result = subprocess.run(
                    [exe_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            return _build_execution_response(run_result, language)
        except subprocess.TimeoutExpired:
            return jsonify({"success": False, "error": f"代码执行超时（超过 {timeout} 秒）"}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif language == "java":
        dangerous_keywords = [
            "Runtime.getRuntime()", "ProcessBuilder", "System.exit(",
            "java.io.File", "java.nio.file", "java.net."
        ]

        for keyword in dangerous_keywords:
            if keyword in code:
                return jsonify({
                    "success": False,
                    "error": f"Java 沙盒安全拦截：不允许包含敏感系统指令如: {keyword}"
                }), 400

        javac_command = _find_command("javac")
        java_command = _find_command("java")
        if not javac_command or not java_command:
            return jsonify({"success": False, "error": "未检测到 Java 运行环境"}), 500

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                source_file = os.path.join(temp_dir, "Main.java")
                with open(source_file, "w", encoding="utf-8") as f:
                    f.write(code)

                compile_result = subprocess.run(
                    [javac_command, source_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if compile_result.returncode != 0:
                    return jsonify({
                        "success": True,
                        "data": {
                            "stdout": "",
                            "stderr": "编译错误:\n" + compile_result.stderr,
                            "returnCode": compile_result.returncode,
                            "language": language
                        }
                    })

                run_result = subprocess.run(
                    [java_command, "-cp", temp_dir, "Main"],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            return _build_execution_response(run_result, language)
        except subprocess.TimeoutExpired:
            return jsonify({"success": False, "error": f"代码执行超时（超过 {timeout} 秒）"}), 400
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500


@programming_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_code():
    """Generate code based on description."""
    data = request.get_json() or {}
    description = data.get("description", "")
    language = data.get("language", "python")
    provider = data.get("provider")

    if not description:
        return jsonify({"success": False, "error": "描述不能为空"}), 400

    try:
        prompt = f"""请根据以下描述生成 {language} 代码：

{description}

要求：
1. 代码应该简洁、高效、易读
2. 添加适当的注释
3. 遵循 {language} 的最佳实践
4. 处理可能的错误情况

请只输出代码，不要添加额外的解释。"""

        result = _run_programming_ai_task(
            task_prompt=prompt,
            response_template={
                "code": f"符合 {language} 最佳实践的完整可运行代码。"
            },
            provider=provider,
            fallback_field="code",
        )

        return jsonify({
            "success": True,
            "data": {
                "code": result.get("code", ""),
                "language": language
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@programming_bp.route("/convert", methods=["POST"])
@jwt_required()
def convert_code():
    """Convert code from one language to another."""
    data = request.get_json() or {}
    code = data.get("code", "")
    from_language = data.get("fromLanguage") or data.get("language", "python")
    to_language = data.get("toLanguage") or ("python" if from_language != "python" else "javascript")
    provider = data.get("provider")

    if not code:
        return jsonify({"success": False, "error": "代码不能为空"}), 400

    try:
        prompt = f"""请将以下 {from_language} 代码转换为 {to_language}：

```{from_language}
{code}
```

要求：
1. 保持相同的功能和逻辑
2. 遵循 {to_language} 的语法和最佳实践
3. 添加适当的注释
4. 处理语言差异（如类型系统、标准库等）

请只输出转换后的代码，不要添加额外的解释。"""

        result = _run_programming_ai_task(
            task_prompt=prompt,
            response_template={
                "code": f"等价的 {to_language} 代码。"
            },
            provider=provider,
            fallback_field="code",
        )

        return jsonify({
            "success": True,
            "data": {
                "code": result.get("code", ""),
                "fromLanguage": from_language,
                "toLanguage": to_language
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@programming_bp.route("/optimize", methods=["POST"])
@jwt_required()
def optimize_code():
    """Optimize code for better performance."""
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    provider = data.get("provider")

    if not code:
        return jsonify({"success": False, "error": "代码不能为空"}), 400

    try:
        prompt = f"""请优化以下 {language} 代码：

```{language}
{code}
```

请从以下方面进行优化：
1. 时间复杂度
2. 空间复杂度
3. 代码可读性
4. 算法改进

请提供优化后的代码，并解释优化点。"""

        result = _run_programming_ai_task(
            task_prompt=prompt,
            response_template={
                "optimizedCode": "优化后的完整代码。"
            },
            provider=provider,
            fallback_field="optimizedCode",
        )

        return jsonify({
            "success": True,
            "data": {
                "optimizedCode": result.get("optimizedCode", ""),
                "language": language
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@programming_bp.route("/test", methods=["POST"])
@jwt_required()
def generate_tests():
    """Generate unit tests for code."""
    data = request.get_json() or {}
    code = data.get("code", "")
    language = data.get("language", "python")
    provider = data.get("provider")

    if not code:
        return jsonify({"success": False, "error": "代码不能为空"}), 400

    try:
        prompt = f"""请为以下 {language} 代码生成单元测试：

```{language}
{code}
```

要求：
1. 覆盖主要功能和边界情况
2. 包含正常情况和异常情况
3. 使用 {language} 的标准测试框架
4. 添加清晰的测试描述

请只输出测试代码。"""

        result = _run_programming_ai_task(
            task_prompt=prompt,
            response_template={
                "testCode": f"基于 {language} 常用测试框架的完整测试代码。"
            },
            provider=provider,
            fallback_field="testCode",
        )

        return jsonify({
            "success": True,
            "data": {
                "testCode": result.get("testCode", ""),
                "language": language
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
