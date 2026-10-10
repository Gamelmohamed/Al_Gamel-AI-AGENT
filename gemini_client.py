import time

from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL


def get_client():
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not configured in the project .env file."
        )

    return genai.Client(api_key=GEMINI_API_KEY)


def generate_content(prompt, retries=3):
    client = get_client()
    retry_delays = [2, 5, 10]

    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            return response.text

        except Exception as error:
            error_text = str(error).lower()
            temporary_error = any(
                marker in error_text
                for marker in (
                    "503",
                    "unavailable",
                    "high demand",
                    "429",
                    "resource_exhausted",
                    "504",
                    "deadline_exceeded",
                )
            )

            if not temporary_error or attempt == retries:
                raise

            delay = retry_delays[min(attempt, len(retry_delays) - 1)]
            print(
                f"Gemini temporarily unavailable. "
                f"Retry {attempt + 1}/{retries} in {delay} seconds."
            )
            time.sleep(delay)
