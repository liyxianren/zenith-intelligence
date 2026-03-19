"""Pipeline service coordinating recognition, parsing and solving."""

from __future__ import annotations

from typing import Dict, Generator, Optional

from app.extensions import db
from app.models.history import History
from app.services.ai_service import ai_service


class PipelineService:
    def solve_problem(self, input_data: Dict) -> Dict:
        result = {"success": True, "data": {}}

        try:
            provider = input_data.get("provider")
            input_type = input_data.get("type", "text")

            if input_type == "image":
                # Pure image input: let the multimodal model return recognition, parsing and solution together
                images = [input_data.get("content", "")]
                combined_result = ai_service.solve_problem_with_image_structured(
                    images,
                    provider_name=provider,
                )
                result["data"]["recognizedText"] = combined_result.get("recognizedText", "") or "(图片题目)"
                result["data"]["parseResult"] = combined_result.get("parseResult", {})
                result["data"]["solution"] = combined_result.get("solution", {})

            elif input_type == "mixed":
                # Text + image: pass both to multimodal model and let it return complete structured output
                images = input_data.get("images") or []
                text = input_data.get("text") or ""
                combined_result = ai_service.solve_problem_with_image_structured(
                    images,
                    text,
                    provider_name=provider,
                )
                result["data"]["recognizedText"] = combined_result.get("recognizedText", "") or text or "(图文混合题目)"
                result["data"]["parseResult"] = combined_result.get("parseResult", {})
                result["data"]["solution"] = combined_result.get("solution", {})

            else:
                # Pure text input: original two-step flow
                problem_text = str(input_data.get("content", ""))
                result["data"]["recognizedText"] = problem_text

                combined_result = ai_service.solve_problem_structured(problem_text, provider)
                result["data"]["parseResult"] = combined_result["parseResult"]
                result["data"]["solution"] = combined_result["solution"]

            user_id = input_data.get("userId")
            if user_id:
                history_record = History(
                    user_id=user_id,
                    username=input_data.get("username"),
                    question=result["data"].get("recognizedText", ""),
                    parse_result=result["data"].get("parseResult"),
                    solution=result["data"].get("solution"),
                )
                db.session.add(history_record)
                db.session.commit()
                result["data"]["historyId"] = history_record.id

            return result
        except Exception as exc:  # noqa: BLE001
            db.session.rollback()
            return {
                "success": False,
                "error": str(exc),
                "data": result["data"],
            }

    def recognize_only(self, image_base64: str) -> Dict:
        try:
            text = ai_service.recognize_image(image_base64)
            return {"success": True, "data": {"text": text}}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def parse_only(self, text: str, provider: Optional[str] = None) -> Dict:
        try:
            parse_result = ai_service.parse_problem(text, provider)
            return {"success": True, "data": parse_result}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def solve_only(self, text: str, parse_result: Dict, provider: Optional[str] = None) -> Dict:
        try:
            solution = ai_service.generate_solution(text, parse_result, provider)
            return {"success": True, "data": solution}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def solve_stream(self, text: str, parse_result: Dict, provider: Optional[str] = None) -> Generator[str, None, None]:
        yield from ai_service.generate_solution_stream(text, parse_result, provider)


pipeline_service = PipelineService()
