"""Model provider abstraction for MiniMax-based text support."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Dict, Generator

import requests
from flask import current_app

from app.services.chatglm_service import ChatGLMService
from app.utils.errors import APIError


class BaseModelProvider(ABC):
    """Abstract base class for AI model providers."""

    name: str = "base"
    display_name: str = "Base Model"

    @abstractmethod
    def parse_problem(self, text: str) -> Dict:
        """Parse problem and extract metadata."""

    @abstractmethod
    def generate_solution(self, text: str, parse_result: Dict) -> Dict:
        """Generate solution for the problem."""

    @abstractmethod
    def generate_solution_stream(
        self, text: str, parse_result: Dict
    ) -> Generator[str, None, None]:
        """Generate solution with streaming."""

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the model is available."""

    @abstractmethod
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Run a generic completion request and return normalized text output."""

    def get_config(self, key: str, default=None):
        """Get configuration value."""
        config_key = f"{self.name.upper()}_{key}"
        return current_app.config.get(config_key, default)


class MiniMaxProvider(BaseModelProvider):
    """MiniMax text provider using the OpenAI-compatible chat completions API."""

    name = "minimax"
    display_name = "MiniMax-M2.7-highspeed"

    def __init__(self):
        self._parser = ChatGLMService()

    def _request(self, data: dict, stream: bool = False) -> requests.Response:
        api_key = self.get_config("API_KEY") or current_app.config.get("MINIMAX_API_KEY")
        api_url = self.get_config("API_URL") or current_app.config.get("MINIMAX_API_URL")
        timeout = current_app.config.get("REQUEST_TIMEOUT", 120)

        if not api_key:
            raise APIError("MiniMax API Key 未配置", 500)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                api_url,
                json=data,
                headers=headers,
                timeout=timeout,
                stream=stream,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            message = str(exc)
            detail = ""
            if exc.response is not None:
                try:
                    detail = json.dumps(exc.response.json(), ensure_ascii=False)
                except Exception:
                    detail = exc.response.text
            if detail:
                message = f"{message}; {detail}"
            raise APIError(f"MiniMax API 错误: {message}", 500) from exc

    def _build_request(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        stream: bool = False,
    ) -> dict:
        request_data = {
            "model": self.get_config("MODEL", "MiniMax-M2.7-highspeed"),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if stream:
            request_data["stream"] = True
        return request_data

    def _extract_message_text(self, payload: dict) -> str:
        try:
            message = payload["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise APIError("MiniMax 响应结构异常", 500) from exc

        if not isinstance(message, dict):
            raise APIError("MiniMax 响应结构异常: message is not a dict", 500)

        content = ChatGLMService._normalize_text_content(message.get("content", "") or "")
        if content:
            return content

        reasoning = ChatGLMService._normalize_text_content(
            message.get("reasoning_content", "") or ""
        )
        if reasoning:
            return reasoning

        raise APIError("MiniMax 未返回有效内容", 500)

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        request_data = self._build_request(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        response = self._request(request_data)
        return self._extract_message_text(response.json())

    def parse_problem(self, text: str) -> Dict:
        content = self.complete(
            system_prompt=(
                "你是一位专业的教育分析师，擅长分析各类学科题目。"
                "你必须只输出纯 JSON 格式，不要添加任何 markdown 标记或其他文字。"
            ),
            user_prompt=f"""你是一位经验丰富的教师，请分析以下题目：

题目：{text}

请按以下 JSON 格式输出分析结果（只输出 JSON，不要添加 markdown 代码块标记或其他内容）：

{{
    "type": "题目类型（选择/填空/解答/判断）",
    "subject": "所属学科",
    "knowledgePoints": ["知识点1", "知识点2"],
    "difficulty": "难度等级（简单/中等/困难）",
    "prerequisites": ["前置知识1", "前置知识2"]
}}""",
            temperature=0.0,
            max_tokens=512,
        )

        try:
            parsed = ChatGLMService._extract_json(content)
            return self._parser._coerce_parse_result(parsed, text)
        except APIError:
            current_app.logger.warning(
                "MiniMax 解析返回非标准 JSON，降级提取字段。content=%s",
                content[:600],
            )
            return self._parser._extract_fields_from_text(content, text)

    def generate_solution(self, text: str, parse_result: Dict) -> Dict:
        knowledge_points = parse_result.get("knowledgePoints", [])
        if isinstance(knowledge_points, list):
            knowledge_text = "、".join(str(item) for item in knowledge_points)
        else:
            knowledge_text = str(knowledge_points)

        content = self.complete(
            system_prompt=(
                "你是一位优秀的 AI 教师。你必须只输出纯 JSON，"
                "禁止输出 markdown 代码块和额外说明。JSON 字段内容允许 Markdown 与 LaTeX。"
            ),
            user_prompt=f"""你是一位耐心的 AI 教师，针对以下题目提供详细解答。

### 题目内容
{text}

### 辅助信息
- 题目类型：{parse_result.get('type', '')}
- 所属学科：{parse_result.get('subject', '')}
- 核心知识点：{knowledge_text}
- 难度等级：{parse_result.get('difficulty', '')}

### 输出要求
请严格输出一个合法、简洁的 JSON 对象。禁止包含任何 Markdown 代码块标签（如 ```json）、禁止包含任何解释性文字或提示词的副本。

JSON 结构必须严格如下：
{{
    "thinking": "只写思路正文，不要再写“解题思路”等标题",
    "steps": ["只写步骤内容，不要写“步骤1：”前缀", "只写步骤内容，不要写“步骤2：”前缀"],
    "answer": "只写最终答案内容，不要写“最终答案”标题",
    "summary": "只写总结正文，不要写“知识总结”标题"
}}

### 具体约束
1. **禁止重复**：严禁在输出中重复本提示词中的规则内容。
2. **数组要求**：`steps` 字段必须是字符串数组，包含至少 2 个明确的逻辑步骤。
3. **格式规范**：`thinking`、`steps`、`answer` 和 `summary` 字段内容都不要包含章节标题、序号前缀或字段名回显。
4. **数学公式**：所有数学表达式必须使用 LaTeX 格式：行内公式用 $...$，独立块级公式用 $$...$$。
5. **JSON 转义**：确保所有换行符和引号在 JSON 字符串中正确转义（使用 \\n）。""",
            temperature=0.1,
            max_tokens=1200,
        )

        return ChatGLMService.parse_solution_content(content)

    def generate_solution_stream(
        self, text: str, parse_result: Dict
    ) -> Generator[str, None, None]:
        knowledge_points = parse_result.get("knowledgePoints", [])
        if isinstance(knowledge_points, list):
            knowledge_text = "、".join(str(item) for item in knowledge_points)
        else:
            knowledge_text = str(knowledge_points)

        request_data = self._build_request(
            messages=[
                {
                    "role": "system",
                    "content": "你是一位优秀的 AI 教师，擅长用清晰、易懂的方式讲解题目。",
                },
                {
                    "role": "user",
                    "content": f"""你是一位耐心的 AI 教师，请为学生提供详细的解答。

题目：{text}
题目类型：{parse_result.get('type', '')}
所属学科：{parse_result.get('subject', '')}
知识点：{knowledge_text}

请提供详细的解题思路、步骤、答案和知识总结。

格式要求：
1. 使用 Markdown 组织内容；
2. 数学公式使用 LaTeX（行内 $...$，块级 $$...$$）；
3. 不要输出与答案无关的自我反思。""",
                },
            ],
            temperature=0.7,
            max_tokens=2000,
            stream=True,
        )

        response = self._request(request_data, stream=True)

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            line = line.strip()
            if not line.startswith("data:"):
                continue

            data = line[5:].strip()
            if data == "[DONE]":
                break

            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                continue

            delta = parsed.get("choices", [{}])[0].get("delta", {})
            if not isinstance(delta, dict):
                continue

            content = ChatGLMService._normalize_text_content(delta.get("content"))
            if content:
                yield content

    def health_check(self) -> bool:
        request_data = self._build_request(
            messages=[{"role": "user", "content": "你好"}],
            temperature=0.1,
            max_tokens=10,
        )
        try:
            self._request(request_data)
            return True
        except APIError:
            return False


class ModelProviderFactory:
    """Factory for creating model providers."""

    _providers: Dict[str, type[BaseModelProvider]] = {
        "minimax": MiniMaxProvider,
    }
    _aliases: Dict[str, str] = {
        "chatglm": "minimax",
        "deepseek": "minimax",
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: type[BaseModelProvider]):
        """Register a new model provider."""
        cls._providers[name] = provider_class

    @classmethod
    def get_provider(cls, name: str) -> BaseModelProvider:
        """Get a model provider by name."""
        resolved_name = cls._aliases.get(name, name)
        if resolved_name not in cls._providers:
            raise APIError(f"未知的模型提供商: {name}", 400)
        return cls._providers[resolved_name]()

    @classmethod
    def list_providers(cls) -> list[Dict]:
        """List all available model providers."""
        return [
            {"name": name, "display_name": cls._providers[name].display_name}
            for name in cls._providers
        ]


model_provider_factory = ModelProviderFactory()
