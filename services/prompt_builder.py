"""Builds the system and user prompts used for resume/JD analysis."""

SYSTEM_PROMPT = """You are an expert technical recruiter and resume verification analyst.
You analyze a candidate's resume against a job description with rigor and honesty.
You never invent facts that are not present in the resume text. If information is
missing or unclear, say so explicitly rather than guessing.

You MUST respond with ONLY a single valid JSON object — no markdown fences, no
commentary before or after it. The JSON must exactly match the schema you are given,
including every key. Use empty strings, empty arrays, or null where information is
genuinely unavailable, but never omit a key."""

JSON_SCHEMA_DESCRIPTION = """
{
  "candidate_summary": {
    "full_name": "string or null",
    "headline": "string or null (e.g. 'Senior Backend Engineer')",
    "total_years_experience": "string or null (e.g. '6 years')",
    "summary": "2-4 sentence neutral professional summary"
  },
  "extracted_skills": ["string", "..."],
  "experience": [
    {
      "title": "string",
      "company": "string or null",
      "duration": "string or null",
      "highlights": ["string", "..."]
    }
  ],
  "education": [
    {"degree": "string", "institution": "string or null", "year": "string or null"}
  ],
  "certifications": ["string", "..."],
  "resume_verification": {
    "is_internally_consistent": true,
    "red_flags": ["string describing any inconsistency, gap, or implausible claim, ..."],
    "formatting_quality": "short assessment of clarity/structure/professionalism",
    "completeness_notes": "note on missing sections (e.g. no dates, no contact info)",
    "authenticity_notes": "note on plausibility of claims based on the text alone; do not accuse of fraud, only flag inconsistencies"
  },
  "jd_match_analysis": {
    "match_summary": "2-3 sentence summary of overall fit to the JD",
    "aligned_requirements": ["JD requirement clearly met, ..."],
    "partially_met_requirements": ["JD requirement partially met, ..."],
    "unmet_requirements": ["JD requirement not met, ..."]
  },
  "score_breakdown": {
    "skills_match": 0,
    "experience_match": 0,
    "education_match": 0,
    "certifications_match": 0,
    "overall_score": 0
  },
  "strengths": ["string", "..."],
  "weaknesses": ["string", "..."],
  "missing_skills": ["skill required by JD but absent from resume, ..."],
  "missing_keywords": ["important JD keyword/phrase absent from resume, ..."],
  "interview_focus_areas": ["specific topic/question area an interviewer should probe, ..."],
  "hiring_recommendation": "one of: 'Strong Match', 'Good Match', 'Possible Match', 'Weak Match', 'Not Recommended'",
  "recommendation_rationale": "2-4 sentence justification for the recommendation"
}
""".strip()


def build_user_prompt(resume_text: str, job_description: str) -> str:
    resume_text = resume_text[:20000]
    job_description = job_description[:10000]

    return f"""Analyze the following resume against the following job description.

Return ONLY a JSON object matching exactly this schema (types and keys must match):

{JSON_SCHEMA_DESCRIPTION}

Scoring guidance:
- Each *_match field is 0-100 reflecting how well that dimension aligns with the JD.
- overall_score is a holistic 0-100 score, weighted toward skills and experience match.
- Be honest and critical; do not inflate scores. A resume with little relevant overlap
  should score low.

=== RESUME TEXT ===
{resume_text}

=== JOB DESCRIPTION ===
{job_description}

Respond with ONLY the JSON object described above."""
