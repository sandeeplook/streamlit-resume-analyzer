# AI Resume Verification & JD Match Analyzer — Streamlit Edition

A single-process app (frontend + backend combined) built with Streamlit,
ready to deploy on [Streamlit Community Cloud](https://streamlit.io).

- **No database.** Everything runs in memory for the current session.
- **No authentication.**
- Upload a resume (PDF/DOCX) + paste or upload a job description → Claude
  extracts, verifies, and scores the match → view results in collapsible
  sections → download as PDF or Markdown.

## Project structure

```
streamlit-resume-analyzer/
├── app.py                        # Streamlit UI + orchestration (entry point)
├── config.py                     # Settings from st.secrets / env vars
├── services/
│   ├── text_extraction.py        # PDF/DOCX -> plain text
│   ├── prompt_builder.py         # System/user prompt construction
│   ├── claude_service.py         # Anthropic API call + JSON parsing
│   ├── report_export.py          # Markdown + PDF report generation
│   └── exceptions.py             # Typed app errors
├── requirements.txt
├── .streamlit/
│   ├── config.toml               # Theme
│   └── secrets.toml.example      # Copy to secrets.toml locally
└── .gitignore
```

## Run locally

```bash
cd streamlit-resume-analyzer
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml and set your real ANTHROPIC_API_KEY

streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. **Push this folder to a GitHub repo** (public or private). Make sure
   `app.py` and `requirements.txt` are at the repo root (or note the
   subfolder path for step 3). Do **not** commit a real `secrets.toml` —
   it's already git-ignored.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in
   with GitHub.
3. Click **New app**, select your repo/branch, and set the **main file
   path** to `app.py` (or `streamlit-resume-analyzer/app.py` if this folder
   isn't the repo root).
4. Before or after the first deploy, open the app's **Settings → Secrets**
   and paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ANTHROPIC_MODEL = "claude-sonnet-4-6"
   ANTHROPIC_MAX_TOKENS = "4096"
   MAX_UPLOAD_SIZE_MB = "10"
   ```
5. Click **Deploy**. Streamlit Cloud installs `requirements.txt` and starts
   `app.py` automatically — no separate backend to host.

Any time you push to the connected branch, Streamlit Cloud redeploys
automatically.

## Environment variables / secrets reference

| Key | Description | Default |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | **Required.** Your Anthropic API key. | — |
| `ANTHROPIC_MODEL` | Claude model to use. | `claude-sonnet-4-6` |
| `ANTHROPIC_MAX_TOKENS` | Max tokens for the analysis response. | `4096` |
| `MAX_UPLOAD_SIZE_MB` | Max resume upload size in MB. | `10` |

`config.py` reads `st.secrets` first, then falls back to OS environment
variables — so the same code works locally (via `.env`/shell export or
`secrets.toml`) and on Streamlit Cloud (via the Secrets UI).

## Notes

- PDF/Markdown reports are generated entirely in Python (`fpdf2` for PDF) —
  no browser-side JS is involved, consistent with the single-process design.
- The three original stages (Upload & JD Input → Analysis Progress → Results
  Dashboard) are preserved as one script: the upload form is replaced by a
  `st.status` progress panel while Claude is called, then by the results
  dashboard, using `st.session_state` to hold the result between reruns.
- Click **"← Analyze another candidate"** on the results page to reset and
  run another analysis in the same session.
