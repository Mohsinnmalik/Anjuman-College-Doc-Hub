# ai/generator.py
import requests
from config import Config
from datetime import datetime

def generate_professional_letter(username, to_whom, to_name, subject, reason, duration, from_date, contact):
    # OFFLINE MODE / CONNECTION CHECK
    if not Config.AI_ENABLED:
        return get_fallback_letter(username, to_whom, to_name, subject, reason, duration, from_date, contact)

    prompt = f"""Generate a professional sick leave application in the EXACT format below:

To
{to_whom}
{to_name}

Subject: {subject}

Dear {to_name or 'Sir/Madam'},

I hope this message finds you well. I am writing to formally request a sick leave of {duration} starting from {from_date}.

The reason for my request is: {reason}. I have consulted a doctor and have attached the medical certificate for your reference.

I have ensured that all my current responsibilities are up to date. I will remain available on {contact or 'my registered contact number'} for any urgent matters.

I kindly request your approval for this leave. Please let me know if you need any additional information.

Thank you for your understanding and support.

Yours sincerely,
{username}
{contact or ''}

Return ONLY the letter. No extra text."""

    try:
        r = requests.post(Config.OLLAMA_API, json={
            "model": "llama3.1:8b-instruct-q4_0",
            "prompt": prompt,
            "stream": False
        }, timeout=5) # Add timeout to fail fast
        
        if r.status_code == 200:
            return r.json()['response'].strip()
        else:
            return get_fallback_letter(username, to_whom, to_name, subject, reason, duration, from_date, contact)
    except:
        # Request Failed (Offline)
        return get_fallback_letter(username, to_whom, to_name, subject, reason, duration, from_date, contact)

def get_fallback_letter(username, to_whom, to_name, subject, reason, duration, from_date, contact):
    return f"""To
{to_whom}
{to_name}

Subject: {subject}

Respected {to_name or 'Sir/Madam'},

I hope this message finds you well. I am writing to formally request a sick leave of {duration} starting from {from_date}.

The reason for my request is: {reason}. I have consulted a doctor and have attached the medical certificate for your reference.

I have ensured that all my current responsibilities are up to date. I will remain available on {contact or 'my registered contact number'} for any urgent matters.

I kindly request your approval for this leave. Please let me know if you need any additional information.

Thank you for your understanding and support.

Yours sincerely,
{username}
{contact or ''}"""
