import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def summarize_report(report_text: str, patient_context: str = "") -> dict:
    """
    Send medical report to Gemini and get structured summary back.
    Returns a dict with different sections of analysis.
    """
    
    context_block = f"Additional context provided: {patient_context}" if patient_context else ""
    
    prompt = f"""
You are a medical AI assistant helping patients understand their medical reports.
Analyze the following medical report and provide a structured summary.

{context_block}

MEDICAL REPORT:
{report_text}

Respond ONLY in the following format with these exact section headers:

## PLAIN ENGLISH SUMMARY
(2-3 sentences explaining what this report is about in simple language a non-doctor can understand)

## KEY FINDINGS
(Bullet points of the most important findings from the report)

## ABNORMAL VALUES
(List any values that are outside normal range. Write "None detected" if everything is normal)

## RISK FLAGS
(Any concerning findings that may need immediate attention. Write "None" if nothing urgent)

## RECOMMENDED NEXT STEPS
(What the patient should typically do next — always recommend consulting a doctor)

## DISCLAIMER
Always end with: "This is an AI-generated summary for informational purposes only. Always consult a qualified medical professional for diagnosis and treatment."
"""

    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        
        sections = parse_response(raw_text)
        return {"success": True, "sections": sections, "raw": raw_text}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_response(text: str) -> dict:
    """Parse Gemini's response into sections."""
    sections = {
        "plain_summary": "",
        "key_findings": "",
        "abnormal_values": "",
        "risk_flags": "",
        "next_steps": "",
        "disclaimer": ""
    }
    
    mappings = {
        "PLAIN ENGLISH SUMMARY": "plain_summary",
        "KEY FINDINGS": "key_findings",
        "ABNORMAL VALUES": "abnormal_values",
        "RISK FLAGS": "risk_flags",
        "RECOMMENDED NEXT STEPS": "next_steps",
        "DISCLAIMER": "disclaimer"
    }
    
    current_section = None
    lines = text.split('\n')
    
    for line in lines:
        matched = False
        for header, key in mappings.items():
            if header in line.upper():
                current_section = key
                matched = True
                break
        if not matched and current_section:
            sections[current_section] += line + "\n"
    
    
    return {k: v.strip() for k, v in sections.items()}


def ask_followup(report_text: str, question: str, history: list) -> str:
    """Let users ask follow-up questions about their report."""
    
    history_text = "\n".join([f"Q: {h['q']}\nA: {h['a']}" for h in history])
    
    prompt = f"""
You are a helpful medical AI assistant. A patient has uploaded a medical report and has a follow-up question.

MEDICAL REPORT (summarized context):
{report_text[:3000]}  # Limit to avoid token overflow

CONVERSATION HISTORY:
{history_text}

PATIENT QUESTION: {question}

Answer clearly and simply. Always remind them to consult a real doctor for medical decisions.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"