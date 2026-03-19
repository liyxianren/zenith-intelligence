"""AI service layer that combines multimodal and multi-model support."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Generator, Optional

from flask import current_app

from app.services.chatglm_service import ChatGLMService
from app.services.model_provider import model_provider_factory, BaseModelProvider
from app.utils.errors import APIError


class AIService:
    """AI service with multi-model support."""

    _PLACEHOLDER_TEXT_PATTERNS = (
        "未知",
        "无法确定",
        "题目信息不足",
        "信息不足",
        "无法判断",
        "不明确",
        "未提供",
        "无法识别",
    )

    def __init__(self):
        self._default_provider: Optional[str] = None

    @property
    def default_provider(self) -> str:
        """Get the default model provider."""
        if self._default_provider is None:
            self._default_provider = current_app.config.get("DEFAULT_MODEL_PROVIDER", "minimax")
        return self._default_provider

    @default_provider.setter
    def default_provider(self, value: str):
        """Set the default model provider."""
        self._default_provider = value

    def get_provider(self, provider_name: Optional[str] = None) -> BaseModelProvider:
        """Get a model provider by name."""
        name = provider_name or self.default_provider
        return model_provider_factory.get_provider(name)

    def list_providers(self) -> list[Dict]:
        """List all available model providers."""
        return model_provider_factory.list_providers()

    @staticmethod
    def _normalize_text_content(content) -> str:
        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            chunks = []
            for item in content:
                if isinstance(item, str):
                    if item.strip():
                        chunks.append(item.strip())
                    continue
                if not isinstance(item, dict):
                    continue

                text_value = item.get("text")
                if isinstance(text_value, str) and text_value.strip():
                    chunks.append(text_value.strip())
                    continue

                content_value = item.get("content")
                if isinstance(content_value, str) and content_value.strip():
                    chunks.append(content_value.strip())
            return "\n".join(chunks).strip()

        if isinstance(content, dict):
            for key in ("text", "content", "output_text"):
                value = content.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            return json.dumps(content, ensure_ascii=False).strip()

        if content is None:
            return ""

        return str(content).strip()

    @staticmethod
    def _strip_code_fences(content: str) -> str:
        code_block_matches = re.findall(r"```(?:[\w+-]+)?\s*([\s\S]*?)```", content)
        if code_block_matches:
            return AIService._strip_reasoning_blocks(code_block_matches[0].strip())
        return AIService._strip_reasoning_blocks(content.strip())

    @staticmethod
    def _strip_reasoning_blocks(content: str) -> str:
        stripped = re.sub(r"<think>[\s\S]*?</think>", "", content, flags=re.IGNORECASE).strip()
        if stripped:
            return stripped

        split_content = re.split(r"</think>", content, maxsplit=1, flags=re.IGNORECASE)
        if len(split_content) > 1:
            trailing_content = split_content[-1].strip()
            if trailing_content:
                return trailing_content

        return content.strip()

    @staticmethod
    def _iter_json_object_candidates(content: str):
        stack: list[int] = []
        in_string = False
        escape = False

        for index, char in enumerate(content):
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
                continue

            if char == "{":
                stack.append(index)
                continue

            if char == "}" and stack:
                start_index = stack.pop()
                yield content[start_index : index + 1]

    @staticmethod
    def _extract_json_object(content: str) -> Optional[Dict[str, Any]]:
        cleaned_content = AIService._strip_reasoning_blocks(content)
        candidates = []

        if cleaned_content:
            candidates.extend(reversed(re.findall(r"```(?:json)?\s*([\s\S]*?)```", cleaned_content)))
            candidates.append(cleaned_content)

        candidates.extend(reversed(re.findall(r"```(?:json)?\s*([\s\S]*?)```", content)))
        candidates.append(content)

        for candidate in candidates:
            normalized_candidate = candidate.strip()
            if not normalized_candidate:
                continue

            try:
                parsed_directly = json.loads(normalized_candidate)
                if isinstance(parsed_directly, dict):
                    return parsed_directly
            except json.JSONDecodeError:
                pass

            json_matches = list(AIService._iter_json_object_candidates(normalized_candidate))
            for match in reversed(json_matches):
                try:
                    parsed_match = json.loads(match)
                    if isinstance(parsed_match, dict):
                        return parsed_match
                except json.JSONDecodeError:
                    continue

        return None

    @staticmethod
    def _coerce_structured_value(value: Any, default: Any) -> Any:
        if isinstance(default, list):
            if isinstance(value, list):
                return value
            if value is None or value == "":
                return []
            return [str(value).strip()]

        if isinstance(default, dict):
            return value if isinstance(value, dict) else default

        if value is None:
            return default

        return str(value).strip()

    @staticmethod
    def _strip_solution_heading(text: str, heading_aliases: list[str]) -> str:
        normalized = (text or "").strip()
        if not normalized:
            return ""

        escaped_aliases = "|".join(re.escape(alias) for alias in heading_aliases if alias)
        if not escaped_aliases:
            return normalized

        patterns = [
            rf"^\s*#{1,6}\s*(?:{escaped_aliases})\s*[:：]?\s*",
            rf"^\s*(?:{escaped_aliases})\s*[:：]?\s*",
        ]

        previous = None
        while previous != normalized:
            previous = normalized
            for pattern in patterns:
                normalized = re.sub(pattern, "", normalized, flags=re.IGNORECASE).strip()

        return normalized

    @classmethod
    def _sanitize_solution_result(cls, solution: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {
            "thinking": cls._strip_solution_heading(
                str(solution.get("thinking", "") or ""),
                ["解题思路", "思路", "thinking"],
            ),
            "steps": [],
            "answer": cls._strip_solution_heading(
                str(solution.get("answer", "") or ""),
                ["最终答案", "答案", "answer"],
            ),
            "summary": cls._strip_solution_heading(
                str(solution.get("summary", "") or ""),
                ["知识总结", "总结", "summary"],
            ),
        }

        raw_steps = solution.get("steps", [])
        if isinstance(raw_steps, list):
            for step in raw_steps:
                cleaned_step = cls._strip_solution_heading(str(step or ""), ["步骤", "解题步骤", "详细步骤", "step"])
                cleaned_step = re.sub(r"^\s*步骤\s*\d+\s*[:：.\-、]?\s*", "", cleaned_step, flags=re.IGNORECASE).strip()
                if cleaned_step:
                    sanitized["steps"].append(cleaned_step)

        return sanitized

    @classmethod
    def _is_placeholder_text(cls, value: Any) -> bool:
        normalized = cls._normalize_text_content(value)
        if not normalized:
            return False

        lowered = normalized.lower()
        return any(pattern in normalized or pattern in lowered for pattern in cls._PLACEHOLDER_TEXT_PATTERNS)

    @classmethod
    def _sanitize_parse_result(cls, parse_result: Dict[str, Any] | None) -> Dict[str, Any]:
        raw = parse_result if isinstance(parse_result, dict) else {}

        def _clean_text_field(key: str) -> str:
            value = cls._normalize_text_content(raw.get(key))
            if not value or cls._is_placeholder_text(value):
                return ""
            return value

        def _clean_list_field(key: str) -> list[str]:
            items = raw.get(key)
            if isinstance(items, list):
                normalized_items = [cls._normalize_text_content(item) for item in items]
            elif items is None:
                normalized_items = []
            else:
                normalized_items = [cls._normalize_text_content(items)]

            return [
                item for item in normalized_items
                if item and not cls._is_placeholder_text(item)
            ]

        return {
            "type": _clean_text_field("type"),
            "subject": _clean_text_field("subject"),
            "knowledgePoints": _clean_list_field("knowledgePoints"),
            "difficulty": _clean_text_field("difficulty"),
            "prerequisites": _clean_list_field("prerequisites"),
        }

    @classmethod
    def _has_parse_result_content(cls, parse_result: Dict[str, Any] | None) -> bool:
        if not isinstance(parse_result, dict):
            return False

        return bool(
            cls._normalize_text_content(parse_result.get("type"))
            or cls._normalize_text_content(parse_result.get("subject"))
            or cls._normalize_text_content(parse_result.get("difficulty"))
            or parse_result.get("knowledgePoints")
            or parse_result.get("prerequisites")
        )

    @classmethod
    def _sanitize_recognized_problem_text(cls, value: Any) -> str:
        normalized = cls._normalize_text_content(value)
        if not normalized:
            return ""

        if normalized in {"图片题目", "(图片题目)", "图文混合题目", "(图文混合题目)"}:
            return ""

        return normalized

    def _resolve_multimodal_config(self) -> Dict[str, str]:
        return {
            "provider": "ark",
            "api_key": current_app.config.get("ARK_API_KEY") or "",
            "api_url": current_app.config.get(
                "ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"
            ),
            "model": current_app.config.get(
                "ARK_VISION_MODEL", "doubao-seed-2-0-pro-260215"
            ),
        }

    @staticmethod
    def _get_ark_client(api_key: str, base_url: str):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise APIError("豆包客户端未安装，请运行: pip install openai", 500) from exc

        return OpenAI(base_url=base_url, api_key=api_key)

    def _extract_ark_output_text(self, response) -> str:
        output_text = getattr(response, "output_text", None)
        normalized_output = self._normalize_text_content(output_text)
        if normalized_output:
            return normalized_output

        output_items = getattr(response, "output", None)
        if output_items:
            chunks = []
            for item in output_items:
                content_items = getattr(item, "content", None) or []
                for content in content_items:
                    content_type = getattr(content, "type", None)
                    if content_type == "output_text":
                        text = self._normalize_text_content(getattr(content, "text", ""))
                        if text:
                            chunks.append(text)
            if chunks:
                return "\n".join(chunks).strip()

        if hasattr(response, "model_dump"):
            dumped = response.model_dump()
            normalized_dump = self._normalize_text_content(dumped.get("output_text"))
            if normalized_dump:
                return normalized_dump

            chunks = []
            for item in dumped.get("output", []) or []:
                for content in item.get("content", []) or []:
                    if content.get("type") == "output_text":
                        text = self._normalize_text_content(content.get("text"))
                        if text:
                            chunks.append(text)
            if chunks:
                return "\n".join(chunks).strip()

        raise APIError("豆包视觉模型未返回有效内容", 500)

    def _recognize_image_with_ark(self, image_base64: str, config: Dict[str, str]) -> str:
        client = self._get_ark_client(config["api_key"], config["api_url"])

        response = client.responses.create(
            model=config["model"],
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_image", "image_url": image_base64},
                        {
                            "type": "input_text",
                            "text": (
                                "请仔细识别图片中的题目内容，提取所有文字、数字、公式。"
                                "保持题目的原始格式，如果是数学题保留公式表达式。"
                                "只输出识别到的文本内容，不要添加任何解释。"
                            ),
                        },
                    ],
                }
            ],
        )

        return self._extract_ark_output_text(response)

    def _solve_with_image_ark(
        self, images: list[str], text: str, config: Dict[str, str]
    ) -> Dict[str, Any]:
        client = self._get_ark_client(config["api_key"], config["api_url"])
        prompt_text = text.strip()

        content_parts = [
            {"type": "input_image", "image_url": image_data}
            for image_data in images
        ]
        content_parts.append(
            {
                "type": "input_text",
                "text": f"""你是一位高效、准确的 AI 教师。请根据图片中的题目内容{("以及附加文字说明" if prompt_text else "")}，一次性完成“识题、题目解析、详细解答”并输出 JSON。

附加文字说明：
{prompt_text if prompt_text else "（无）"}

请严格输出一个合法的 JSON 对象，禁止包含 Markdown 代码块标签（如 ```json）、禁止输出任何 JSON 之外的解释文字。

JSON 结构必须严格如下：
{{
  "questionText": "整理后的完整题目文本，不要写“图片题目”这类占位词",
  "type": "题目类型（选择/填空/解答/判断）",
  "subject": "所属学科",
  "knowledgePoints": ["知识点1", "知识点2"],
  "difficulty": "难度等级（简单/中等/困难）",
  "prerequisites": ["前置知识1", "前置知识2"],
  "thinking": "只写思路正文，不要再写“解题思路”等标题",
  "steps": ["只写步骤内容，不要写“步骤1：”前缀", "只写步骤内容，不要写“步骤2：”前缀"],
  "answer": "只写最终答案内容，不要写“最终答案”标题",
  "summary": "只写总结正文，不要写“知识总结”标题"
}}

附加要求：
1. `questionText` 必须尽量完整转写图片中的题目文字、数字和公式；如果附加文字说明有助于补全题意，请一并融合。
2. `steps` 必须至少包含 2 个步骤。
3. 数学表达式使用 LaTeX。
4. 对 `subject`、`knowledgePoints`、`difficulty`、`prerequisites`，如果能根据题目内容推断就直接给出；只有完全无法判断时返回空字符串或空数组，不要输出“未知”“无法确定”“题目信息不足”等占位词。
5. 题目简单时保持简洁，不要过度展开。
6. 不要重复提示词内容。""",
            }
        )

        response = client.responses.create(
            model=config["model"],
            input=[{"role": "user", "content": content_parts}],
        )

        normalized_content = self._extract_ark_output_text(response)
        parsed = self._extract_json_object(normalized_content)

        if isinstance(parsed, dict):
            parse_result = self._sanitize_parse_result({
                "type": parsed.get("type"),
                "subject": parsed.get("subject"),
                "knowledgePoints": parsed.get("knowledgePoints"),
                "difficulty": parsed.get("difficulty"),
                "prerequisites": parsed.get("prerequisites"),
            })
            solution = self._sanitize_solution_result(
                {
                    "thinking": parsed.get("thinking", ""),
                    "steps": parsed.get("steps", []),
                    "answer": parsed.get("answer", ""),
                    "summary": parsed.get("summary", ""),
                }
            )
            recognized_text = self._sanitize_recognized_problem_text(
                parsed.get("questionText")
                or parsed.get("recognizedText")
                or parsed.get("problemText")
                or parsed.get("question")
            )

            return {
                "recognizedText": recognized_text,
                "parseResult": parse_result,
                "solution": solution,
            }

        return {
            "recognizedText": "",
            "parseResult": {},
            "solution": self._sanitize_solution_result(ChatGLMService.parse_solution_content(normalized_content)),
        }

    def recognize_image(self, image_base64: str) -> str:
        """Recognize text from image using the Doubao vision model."""
        config = self._resolve_multimodal_config()
        if not config["api_key"] or not config["api_url"]:
            raise APIError("豆包视觉服务未配置", 500)
        return self._recognize_image_with_ark(image_base64, config)

    def solve_with_image(self, images: list[str], text: str = "") -> Dict:
        """Directly solve a problem containing images using the Doubao vision model.
        Returns a structured solution dict with `thinking`, `steps`, `answer`, `summary`.
        """
        return self.solve_problem_with_image_structured(images, text)["solution"]

    def solve_problem_with_image_structured(
        self,
        images: list[str],
        text: str = "",
        provider_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Solve an image problem and return recognized text, parse result and solution."""
        config = self._resolve_multimodal_config()
        if not config["api_key"] or not config["api_url"]:
            raise APIError("豆包视觉服务未配置", 500)

        structured = self._solve_with_image_ark(images, text, config)
        recognized_text = self._sanitize_recognized_problem_text(structured.get("recognizedText"))
        if not recognized_text:
            recognized_text = self._sanitize_recognized_problem_text(text)

        if not recognized_text and images:
            try:
                recognized_text = self._sanitize_recognized_problem_text(
                    self._recognize_image_with_ark(images[0], config)
                )
            except Exception:  # noqa: BLE001
                recognized_text = ""

        parse_result = self._sanitize_parse_result(structured.get("parseResult"))
        if not self._has_parse_result_content(parse_result) and recognized_text:
            try:
                parse_result = self._sanitize_parse_result(
                    self.parse_problem(recognized_text, provider_name)
                )
            except Exception:  # noqa: BLE001
                parse_result = parse_result or {}

        solution = self._sanitize_solution_result(structured.get("solution", {}))

        return {
            "recognizedText": recognized_text,
            "parseResult": parse_result,
            "solution": solution,
        }

    def parse_problem(self, text: str, provider_name: Optional[str] = None) -> Dict:
        """Parse problem using specified or default provider."""
        provider = self.get_provider(provider_name)
        return provider.parse_problem(text)

    def complete_structured_response(
        self,
        system_prompt: str,
        user_prompt: str,
        response_template: Dict[str, Any],
        provider_name: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        fallback_field: Optional[str] = None,
    ) -> Dict[str, Any]:
        provider = self.get_provider(provider_name)
        raw_content = provider.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        parsed = self._extract_json_object(raw_content)
        if parsed is None:
            if not fallback_field:
                raise APIError("模型返回格式异常: 未返回合法 JSON", 500)
            parsed = {fallback_field: self._strip_code_fences(raw_content)}

        normalized: Dict[str, Any] = {}
        for key, default in response_template.items():
            normalized[key] = self._coerce_structured_value(parsed.get(key), default)

        if fallback_field and fallback_field in normalized and not str(normalized[fallback_field]).strip():
            normalized[fallback_field] = self._strip_code_fences(raw_content)

        return normalized

    def generate_solution(
        self, text: str, parse_result: Dict, provider_name: Optional[str] = None
    ) -> Dict:
        """Generate solution using specified or default provider."""
        provider = self.get_provider(provider_name)
        return self._sanitize_solution_result(provider.generate_solution(text, parse_result))

    def solve_problem_structured(self, text: str, provider_name: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        response_template = {
            "type": "解答",
            "subject": "数学",
            "knowledgePoints": [],
            "difficulty": "中等",
            "prerequisites": [],
            "thinking": "",
            "steps": [],
            "answer": "",
            "summary": "",
        }

        structured = self.complete_structured_response(
            system_prompt=(
                "你是一位高效、准确的 AI 教师。"
                "你必须只输出一个合法 JSON 对象，不要输出 markdown 代码块、思考过程或额外说明。"
            ),
            user_prompt=f"""请对以下题目同时完成“题目解析”和“详细解答”，并一次性输出 JSON。

题目：
{text}

JSON 结构必须严格如下：
{{
  "type": "题目类型（选择/填空/解答/判断）",
  "subject": "所属学科",
  "knowledgePoints": ["知识点1", "知识点2"],
  "difficulty": "难度等级（简单/中等/困难）",
  "prerequisites": ["前置知识1", "前置知识2"],
  "thinking": "只写思路正文，不要再写“解题思路”等标题",
  "steps": ["只写步骤内容，不要写“步骤1：”前缀", "只写步骤内容，不要写“步骤2：”前缀"],
  "answer": "只写最终答案内容，不要写“最终答案”标题",
  "summary": "只写总结正文，不要写“知识总结”标题"
}}

约束：
1. `steps` 必须是字符串数组，至少 2 步。
2. `thinking`、`summary` 不要包含章节标题、编号或提示词回显。
3. 题目简单时保持简洁，不要过度展开。
4. 数学公式使用 LaTeX。
5. 仅输出 JSON。""",
            response_template=response_template,
            provider_name=provider_name,
            temperature=0.1,
            max_tokens=1200,
        )

        parse_result = self._sanitize_parse_result(
            {
                "type": structured.get("type"),
                "subject": structured.get("subject"),
                "knowledgePoints": structured.get("knowledgePoints"),
                "difficulty": structured.get("difficulty"),
                "prerequisites": structured.get("prerequisites"),
            }
        )

        solution = self._sanitize_solution_result(
            {
                "thinking": structured.get("thinking", ""),
                "steps": structured.get("steps", []),
                "answer": structured.get("answer", ""),
                "summary": structured.get("summary", ""),
            }
        )

        return {"parseResult": parse_result, "solution": solution}

    def generate_solution_stream(
        self, text: str, parse_result: Dict, provider_name: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Generate solution with streaming using specified or default provider."""
        provider = self.get_provider(provider_name)
        return provider.generate_solution_stream(text, parse_result)

    def parse_solution_content(self, content: str) -> Dict:
        """Parse solution content into structured format."""
        try:
            import re
            json_str = content
            code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", json_str)
            if code_block_match:
                json_str = code_block_match.group(1).strip()
            json_match = re.search(r"\{[\s\S]*\}", json_str)
            if json_match:
                json_str = json_match.group(0)
            parsed = json.loads(json_str)
            return {
                "thinking": str(parsed.get("thinking", "")).strip(),
                "steps": parsed.get("steps", []) if isinstance(parsed.get("steps"), list) else [],
                "answer": str(parsed.get("answer", "")).strip(),
                "summary": str(parsed.get("summary", "")).strip(),
            }
        except json.JSONDecodeError:
            return {"thinking": content, "steps": [], "answer": "", "summary": ""}

    def health_check(self) -> Dict[str, bool]:
        """Check health of all services."""
        result = {"multimodal": False}

        providers = self.list_providers()
        for provider_info in providers:
            provider_name = provider_info["name"]
            try:
                provider = self.get_provider(provider_name)
                result[provider_name] = provider.health_check()
            except Exception:
                result[provider_name] = False

        config = self._resolve_multimodal_config()

        if config["api_key"] and config["api_url"]:
            try:
                client = self._get_ark_client(config["api_key"], config["api_url"])
                response = client.responses.create(
                    model=config["model"],
                    input=[
                        {
                            "role": "user",
                            "content": [{"type": "input_text", "text": "hi"}],
                        }
                    ],
                )
                result["multimodal"] = bool(self._extract_ark_output_text(response))
            except Exception:
                result["multimodal"] = False

        return result


ai_service = AIService()
