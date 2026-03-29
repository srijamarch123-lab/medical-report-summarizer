import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_report(report_text: str, patient_context: str = "") -> dict:
    context_block = f"Additional context: {patient_context}" if patient_context else ""
    
    prompt = f"""
You are a medical AI assistant helping patients understand their medical reports.
Analyze the following medical report and provide a structured summary.

{context_block}

MEDICAL REPORT:
{report_text}

Respond ONLY in the following format:

## PLAIN ENGLISH SUMMARY
(2-3 sentences in simple language)

## KEY FINDINGS
(Bullet points of important findings)

## ABNORMAL VALUES
(Values outside normal range, or "None detected")

## RISK FLAGS
(Concerning findings, or "None")

## RECOMMENDED NEXT STEPS
(What to do next — always recommend consulting a doctor)

## DISCLAIMER
This is an AI-generated summary for informational purposes only. Always consult a qualified medical professional for diagnosis and treatment.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
        raw_text = response.choices[0].message.content
        sections = parse_response(raw_text)
        return {"success": True, "sections": sections, "raw": raw_text}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def parse_response(text: str) -> dict:
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
    for line in text.split('\n'):
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
    history_text = "\n".join([f"Q: {h['q']}\nA: {h['a']}" for h in history])
    
    prompt = f"""
You are a helpful medical AI assistant. A patient has a follow-up question about their report.

REPORT CONTEXT:
{report_text[:3000]}

CONVERSATION HISTORY:
{history_text}

PATIENT QUESTION: {question}

Answer clearly and simply. Always remind them to consult a real doctor.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"