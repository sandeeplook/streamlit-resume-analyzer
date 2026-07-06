"""Wraps calls to the Anthropic Claude API and parses structured JSON output."""
import json
import re

import anthropic

from config import Settings
from services.exceptions import ClaudeAPIError, ClaudeResponseParsingError, ConfigurationError
from services.prompt_builder import SYSTEM_PROMPT, build_user_prompt

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)

REQUIRED_TOP_LEVEL_KEYS = [
    "candidate_summary",
    "extracted_skills",
    "experience",
    "education",
    "certifications",
    "resume_verification",
    "jd_match_analysis",
    "score_breakdown",
    "strengths",
    "weaknesses",
    "missing_skills",
    "missing_keywords",
    "interview_focus_areas",
    "hiring_recommendation",
    "recommendation_rationale",
]


def analyze_resume(settings: Settings, resume_text: str, job_description: str) -> dict:
    if not settings.anthropic_api_key:
        raise ConfigurationError(
            "ANTHROPIC_API_KEY is not configured.",
            details="Add it to Streamlit secrets (Settings → Secrets) or your environment.",
        )

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    prompt = build_user_prompt(resume_text, job_description)

    try:
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=settings.anthropic_max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIStatusError as exc:
        raise ClaudeAPIError("The Claude API returned an error.", details=str(exc)) from exc
    except anthropic.APIConnectionError as exc:
        raise ClaudeAPIError("Could not connect to the Claude API.", details=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise ClaudeAPIError("Unexpected error calling the Claude API.", details=str(exc)) from exc

    raw_text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    ).strip()

    return _parse_response(raw_text)


def _parse_response(raw_text: str) -> dict:
    candidate = raw_text.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(json)?", "", candidate).strip()
        candidate = re.sub(r"```$", "", candidate).strip()

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        match = _JSON_BLOCK_RE.search(candidate)
        if not match:
            raise ClaudeResponseParsingError(
                "The analysis response was not valid JSON.", details=candidate[:500]
            )
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ClaudeResponseParsingError(
                "The analysis response could not be parsed as JSON.", details=str(exc)
            ) from exc

    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in data]
    if missing:
        raise ClaudeResponseParsingError(
            "The analysis response was missing expected fields.",
            details=f"Missing keys: {', '.join(missing)}",
        )

    return data
