import os
import json
import logging
import requests
from pydantic import BaseModel
from typing import List

class CandidateReportContext(BaseModel):
    summary: str
    strengths: List[str]
    gaps: List[str]
    interview_questions: List[str]

OLLAMA_PRIMARY_HOST = os.environ.get("OLLAMA_HOST", "localhost")
HOST_CANDIDATES = list(dict.fromkeys([OLLAMA_PRIMARY_HOST, "localhost", "127.0.0.1", "host.docker.internal"]))

def get_available_ollama_model(base_url):
    """Check installed models via /api/tags and pick best match."""
    try:
        res = requests.get(f"{base_url}/api/tags", timeout=2)
        if res.status_code == 200:
            models = [m.get("name", "") for m in res.json().get("models", [])]
            for target in ["resume_scanner", "resume_scanner:latest", "llama3", "llama3:latest", "llama2", "mistral"]:
                for m in models:
                    if target in m:
                        return m
            if models:
                return models[0]
    except Exception:
        pass
    return "resume_scanner"

def generate_insights(resume_data, jd_data, match_score):
    """
    Generate insights using local LLM via Ollama.
    Tries multiple host endpoints and auto-discovers available models.
    Falls back to intelligent heuristics if Ollama is unreachable.
    """
    resume_skills = resume_data.get('skills', [])
    jd_skills = jd_data.get('must_have_skills', []) + jd_data.get('good_to_have', [])
    experience = resume_data.get('experience_years', 0)
    projects = resume_data.get('projects', [])
    
    prompt = f"""
Candidate Info:
- Experience: {experience} years
- Extracted Skills: {', '.join(resume_skills) if resume_skills else 'None specified'}
- Key Projects: {'; '.join(projects[:2]) if projects else 'None specified'}

Job Requirements:
- Extracted Requirements: {', '.join(jd_skills) if jd_skills else 'Standard tech role requirements'}

Match Score: {match_score}/100

Generate the Candidate Report Context JSON as instructed in your SYSTEM prompt:
{{
  "summary": "Candidate fit summary...",
  "strengths": ["Strength 1", "Strength 2"],
  "gaps": ["Gap 1", "Gap 2"],
  "interview_questions": ["Question 1", "Question 2", "Question 3"]
}}
"""
    
    for host in HOST_CANDIDATES:
        base_url = f"http://{host}:11434"
        try:
            model_name = get_available_ollama_model(base_url)
            response = requests.post(f"{base_url}/api/generate", json={
                "model": model_name,
                "prompt": prompt,
                "format": "json",
                "stream": False
            }, timeout=(3, 20))
            
            if response.status_code != 200:
                continue
                
            result = response.json()
            raw_json = result.get('response', '{}')
            
            clean_str = raw_json.strip()
            if clean_str.startswith("```json"):
                clean_str = clean_str[7:]
            elif clean_str.startswith("```"):
                clean_str = clean_str[3:]
            if clean_str.endswith("```"):
                clean_str = clean_str[:-3]
                
            parsed = json.loads(clean_str.strip())

            summary = (parsed.get("summary") or parsed.get("candidate_summary") or 
                       f"Candidate scored {match_score}/100 with {experience} years of experience.")
            
            strengths = (parsed.get("strengths") or parsed.get("key_strengths") or [])
            if not isinstance(strengths, list) or len(strengths) == 0:
                strengths = [f"Strong background in {', '.join(resume_skills[:3])}" if resume_skills else "Solid general experience."]
                
            gaps = (parsed.get("gaps") or parsed.get("skill_gaps") or parsed.get("missing_skills") or [])
            if not isinstance(gaps, list) or len(gaps) == 0:
                gaps = ["No major skill gaps identified."]
                
            questions = (parsed.get("interview_questions") or parsed.get("interviewQuestions") or 
                         parsed.get("questions") or parsed.get("suggested_questions") or [])
            if not isinstance(questions, list) or len(questions) == 0:
                questions = _build_fallback_questions(resume_skills, jd_skills, experience)

            return CandidateReportContext(
                summary=summary,
                strengths=strengths,
                gaps=gaps,
                interview_questions=questions
            ).model_dump()
            
        except Exception:
            continue

    logging.info("Ollama unavailable or unreachable. Falling back to heuristic insight generation.")
    return _heuristic_fallback(resume_data, jd_data, match_score)

def _build_fallback_questions(resume_skills, jd_skills, experience):
    questions = []
    resume_skills_lower = [s.lower() for s in resume_skills]
    jd_skills_lower = [s.lower() for s in jd_skills]
    
    missing = [s for s in jd_skills if s.lower() not in resume_skills_lower]
    matched = [s for s in resume_skills if s.lower() in jd_skills_lower]
    
    if missing:
        questions.append(f"How would you approach learning or implementing {missing[0].capitalize()} in a production environment?")
    if len(missing) > 1:
        questions.append(f"Do you have hands-on experience or familiarity with tools similar to {missing[1].capitalize()}?")
    
    if matched:
        questions.append(f"Can you explain how you leveraged {matched[0].capitalize()} to optimize performance or solve a complex problem in a past role?")
    elif resume_skills:
        questions.append(f"How have you applied your core proficiency in {resume_skills[0].capitalize()} to deliver technical projects?")
        
    questions.append(f"With {experience} year(s) of experience, how do you handle cross-functional collaboration and architectural decisions?")
    questions.append("Can you walk us through the architecture and deployment lifecycle of your most complex recent project?")
    
    return questions[:4]

def _heuristic_fallback(resume_data, jd_data, match_score):
    strengths = []
    gaps = []
    
    resume_skills = set([s.lower() for s in resume_data.get('skills', [])])
    must_have_skills = set([s.lower() for s in jd_data.get('must_have_skills', [])])
    good_to_have_skills = set([s.lower() for s in jd_data.get('good_to_have', [])])
    all_jd_skills = must_have_skills.union(good_to_have_skills)
    
    matches = list(resume_skills.intersection(all_jd_skills))
    if matches:
        strengths.append(f"Strong alignment in core required skills: {', '.join([m.capitalize() for m in matches[:4]])}.")
    if resume_data.get('experience_years', 0) > 0:
        strengths.append(f"Demonstrated industry experience: {resume_data.get('experience_years')} years.")
    if resume_data.get('projects'):
        strengths.append(f"Relevant project portfolio: {len(resume_data['projects'])} documented project(s).")
        
    missing = list(must_have_skills - resume_skills)
    if missing:
        gaps.append(f"Missing essential job requirements: {', '.join([m.capitalize() for m in missing[:3]])}.")
    else:
        gaps.append("No critical must-have skill gaps identified.")
        
    summary = f"Candidate scored {match_score}/100 with {resume_data.get('experience_years', 0)} years of relevant experience. "
    if match_score > 75:
        summary += "Highly recommended strong fit for the position."
    elif match_score > 50:
        summary += "Moderate candidate fit; recommendation to assess skill gaps in technical interview."
    else:
        summary += "Weak candidate fit relative to current role specifications."
        
    questions = _build_fallback_questions(
        resume_data.get('skills', []),
        list(all_jd_skills),
        resume_data.get('experience_years', 0)
    )
    
    return CandidateReportContext(
        summary=summary,
        strengths=strengths if strengths else ["Demonstrates foundational professional skills."],
        gaps=gaps,
        interview_questions=questions
    ).model_dump()
