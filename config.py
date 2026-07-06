"""
Application configuration.

Settings are read from Streamlit secrets first (st.secrets, used on Streamlit
Community Cloud), falling back to environment variables (useful for local
runs or other hosts). No values are hard-coded.
"""
import os
import streamlit as st


def _get(key: str, default: str = "") -> str:
    # st.secrets raises if no secrets.toml exists at all in some versions,
    # so guard defensively.
    try:
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.environ.get(key, default)


class Settings:
    def __init__(self) -> None:
        self.anthropic_api_key: str = _get("ANTHROPIC_API_KEY", "")
        self.anthropic_model: str = _get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        self.anthropic_max_tokens: int = int(_get("ANTHROPIC_MAX_TOKENS", "4096"))
        self.app_name: str = _get("APP_NAME", "AI Resume Verification & JD Match Analyzer")
        self.max_upload_size_mb: int = int(_get("MAX_UPLOAD_SIZE_MB", "10"))
        self.allowed_extensions = [".pdf", ".docx"]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@st.cache_resource
def get_settings() -> Settings:
    return Settings()
