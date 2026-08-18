import json
import time

from google import genai

from app.qualification.interfaces import BaseLLM
from app.qualification.exceptions import LLMError


class GeminiClient(BaseLLM):
    def __init__(
        self,
        api_key: str,
        model: str,
    ):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def analyze(self, text: str) -> str:
        return self._generate(text)

    def analyze_batch(self, texts: list[str]) -> list[str]:
        if not texts:
            return []

        prompt = self._build_batch_prompt(texts)
        response = self._generate(prompt)

        try:
            data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise LLMError("Gemini batch response is not valid JSON.") from exc

        if not isinstance(data, list) or len(data) != len(texts):
            raise LLMError(
                "Gemini batch response must be a JSON array with one result per profile."
            )

        return [json.dumps(item, ensure_ascii=False) for item in data]

    @staticmethod
    def _build_batch_prompt(texts: list[str]) -> str:
        profiles = "\n\n".join(
            f"PROFILE {index}\n{prompt}"
            for index, prompt in enumerate(texts, start=1)
        )

        return f"""
You are an expert B2B ICP qualification engine.

Analyze each profile independently using the qualification instructions contained
in each profile prompt.

Return JSON only as a JSON array, in exactly the same order as the profiles.
Return exactly one qualification object for each profile.
Do not omit, merge, reorder, or invent profiles.

{profiles}
""".strip()

    def _generate(self, text: str) -> str:
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=text,
                )
                if response.text is None:
                    raise LLMError(
                        "Gemini API returned an empty response (no text)."
                    )
                return response.text

            except LLMError:
                raise

            except Exception as exc:
                error_message = str(exc).lower()

                if (
                    "429" in error_message
                    or "resource_exhausted" in error_message
                    or "rate" in error_message
                ):
                    if attempt < max_attempts - 1:
                        wait_time = 10 * (attempt + 1)
                        time.sleep(wait_time)
                        continue

                raise LLMError(
                    f"Gemini API request failed: {exc}"
                ) from exc

        raise LLMError("Gemini API request failed: no attempts were made.")
