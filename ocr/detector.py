# ocr/detector.py
def is_medical_document(text):
    text_lower = text.lower()
    keywords = [
        'rx', 'prescription', 'hospital', 'clinic', 'doctor', 'dr.', 'mbbs',
        'rest', 'days', 'fever', 'headache', 'pain', 'ibuprofen', 'paracetamol',
        'date', 'age', 'male', 'female', 'm/', 'f/', 'opd', 'emergency'
    ]
    found = [k for k in keywords if k in text_lower]
    if len(found) >= 2:
        return True, f"Medical ({', '.join(found[:3])})"
    if any(word in text_lower for word in ['hospital', 'clinic', 'health']):
        return True, "Medical facility"
    return False, "Not medical"