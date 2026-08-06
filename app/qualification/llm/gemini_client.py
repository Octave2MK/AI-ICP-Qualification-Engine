import time

from google import genai

from app.qualification.interfaces import BaseLLM
from app.qualification.exceptions import LLMError


class GeminiClient(BaseLLM):

    def __init__(
        self,
        api_key: str,
        model: str
    ):
        self._client = genai.Client(
            api_key=api_key
        )

        self._model = model


    def analyze(
        self,
        text: str
    ) -> str:

        max_attempts = 3


        for attempt in range(max_attempts):

            try:

                response = (
                    self._client.models.generate_content(
                        model=self._model,
                        contents=text,
                    )
                )

                return response.text


            except Exception as exc:

                error_message = str(exc).lower()


                # Rate limit Gemini
                if (
                    "429" in error_message
                    or "resource_exhausted" in error_message
                    or "rate" in error_message
                ):

                    if attempt < max_attempts - 1:

                        wait_time = (
                            10 * (attempt + 1)
                        )

                        time.sleep(wait_time)

                        continue


                raise LLMError(
                    f"Gemini API request failed: {exc}"
                ) from exc