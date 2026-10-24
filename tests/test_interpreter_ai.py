
from unittest.mock import patch

from backend.interpreter import classify_with_ai


def test_ai_classifier_returns_valid_classification():
    with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
        with patch("groq.Groq") as mock_groq:
            mock_groq.return_value.chat.completions.create.return_value.choices[
                0
            ].message.content = '{"type": "top_region", "months": []}'

            result = classify_with_ai(
                "Which area of the business performed best?"
            )

    assert result == {"type": "top_region", "months": []}


def test_ai_classifier_returns_none_without_api_key():
    with patch.dict("os.environ", {}, clear=True):
        result = classify_with_ai("Which area performed best?")

    assert result is None


def test_ai_classifier_handles_api_error():
    with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
        with patch("groq.Groq", side_effect=Exception("API unavailable")):
            result = classify_with_ai("Which area performed best?")

    assert result is None


def test_ai_classifier_rejects_invalid_json():
    with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
        with patch("groq.Groq") as mock_groq:
            mock_groq.return_value.chat.completions.create.return_value.choices[
                0
            ].message.content = "not valid json"

            result = classify_with_ai("Which area performed best?")

    assert result is None
