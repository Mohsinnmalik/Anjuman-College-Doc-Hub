# app.py
from flask import Flask, render_template, request, session, redirect, url_for, send_file
from config import Config
from ocr.processor import extract_text
from ocr.detector import is_medical_document
from utils.pdf import create_official_pdf
import os
from datetime import datetime
from utils.certificate import generate_certificate
from utils.poster import generate_poster
from ai.generator import generate_professional_letter
from models.db import db, Submission
import os
from datetime import datetime
import sys
sys.path.append('.')
from ai.generator import generate_professional_letter

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
os.makedirs('temp', exist_ok=True)
os.makedirs('static/assets', exist_ok=True)

# Create DB
with app.app_context():
    db.create_all()

# === LOGIN & DASHBOARD ===
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    session['username'] = request.form['username']
    session['role'] = request.form['role']
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect('/')
    return render_template('dashboard.html', **session)

@app.route('/templates')
def templates():
    if 'username' not in session: return redirect('/')
    from config import TEMPLATES
    return render_template('select_templates.html', templates=TEMPLATES.get(session['role'], []))

# === SICK LEAVE ===
@app.route('/form/sick_leave')
def form_sick_leave():
    if 'username' not in session: return redirect('/')
    return render_template('forms/sick_leave.html')

@app.route('/submit/sick_leave', methods=['POST'])
def submit_sick_leave():
    if 'username' not in session: return redirect('/')
    
    username = session['username']
    proof_file = request.files.get('document')
    
    to_whom = request.form.get('to_whom', '').strip()
    to_name = request.form.get('to_name', '').strip()
    subject = request.form.get('subject', '').strip()
    reason = request.form.get('reason', '').strip()
    duration = request.form.get('duration', '').strip()
    from_date = request.form.get('from_date', datetime.now().strftime('%d/%m/%Y'))
    contact = request.form.get('contact', '')
    
    if not all([to_whom, subject, reason, duration]):
        session['error'] = "All required fields must be filled"
        return redirect('/form/sick_leave')
    
    if not proof_file or not proof_file.filename:
        session['error'] = "Medical proof is required"
        return redirect('/form/sick_leave')
    
    proof_path = os.path.join('temp', f"proof_{username}_{int(datetime.now().timestamp())}.jpg")
    proof_file.save(proof_path)
    
    text = extract_text(proof_path)
    is_valid, message = is_medical_document(text)
    if not is_valid:
        session['error'] = f"Invalid document: {message}"
        os.remove(proof_path)
        return redirect('/form/sick_leave')
    
    letter = generate_professional_letter(username, to_whom, to_name, subject, reason, duration, from_date, contact)
    pdf_buffer = create_official_pdf(letter, username, proof_path)
    
    # SAVE TO DB
    submission = Submission(
        username=username,
        type='sick_leave',
        data=f"To: {to_whom} | Subject: {subject} | Duration: {duration}",
        status='generated'
    )
    db.session.add(submission)
    db.session.commit()
    
    os.remove(proof_path)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{username}_Sick_Leave.pdf",
        mimetype='application/pdf'
    )

# === CERTIFICATE ===
@app.route('/form/certificate')
def form_certificate():
    if 'username' not in session: return redirect('/')
    return render_template('forms/certificate.html')

@app.route('/submit/certificate', methods=['POST'])
def submit_certificate():
    if 'username' not in session: return redirect('/')
    
    username = session['username']
    bg_file = request.files.get('background')
    recipient = request.form.get('recipient', username)
    event = request.form.get('event', 'Achievement')
    date = request.form.get('date', datetime.now().strftime('%d %B %Y'))
    
    bg_path = None
    if bg_file and bg_file.filename:
        bg_path = os.path.join('temp', f"bg_cert_{username}.jpg")
        bg_file.save(bg_path)

    # Optional Signatures
    principal_file = request.files.get('principal_signature')
    max_sig_path = None # This line seems like a typo, but keeping it as per instruction
    if principal_file and principal_file.filename:
        principal_path = os.path.join('temp', f"principal_{username}.png")
        principal_file.save(principal_path)
    else:
        principal_path = None

    hod_file = request.files.get('hod_signature')
    hod_path = None
    if hod_file and hod_file.filename:
        hod_path = os.path.join('temp', f"hod_{username}.png")
        hod_file.save(hod_path)
    
    output_path = os.path.join('temp', f"cert_{username}.png")
    
    try:
        generate_certificate(bg_path, output_path, recipient, event, date, principal_path, hod_path)
    except Exception as e:
        session['error'] = str(e)
        return redirect('/form/certificate')
    
    # SAVE TO DB
    submission = Submission(
        username=username,
        type='certificate',
        data=f"{recipient} - {event}",
        status='generated'
    )
    db.session.add(submission)
    db.session.commit()
    
    if bg_path:
        os.remove(bg_path)
    
    return send_file(output_path, as_attachment=True, download_name=f"{recipient}_Certificate.png", mimetype='image/png')

# === POSTER ===
@app.route('/form/poster')
def form_poster():
    if 'username' not in session: return redirect('/')
    return render_template('forms/poster.html')

@app.route('/submit/poster', methods=['POST'])
def submit_poster():
    if 'username' not in session: return redirect('/')
    
    username = session['username']
    bg_file = request.files.get('background')
    title = request.form.get('title', 'Event')
    subtitle = request.form.get('subtitle', '')
    date = request.form.get('date', 'DD MMM YYYY')
    venue = request.form.get('venue', 'Venue')
    
    if not bg_file or not bg_file.filename:
        session['error'] = "Upload background"
        return redirect('/form/poster')
    
    bg_path = os.path.join('temp', f"bg_poster_{username}.jpg")
    bg_file.save(bg_path)
    output_path = os.path.join('temp', f"poster_{username}.png")
    
    generate_poster(bg_path, output_path, title, subtitle, date, venue)
    
    # SAVE TO DB
    submission = Submission(
        username=username,
        type='poster',
        data=f"{title} - {venue}",
        status='generated'
    )
    db.session.add(submission)
    db.session.commit()
    
    os.remove(bg_path)
    
    return send_file(output_path, as_attachment=True, download_name=f"{title}_Poster.png", mimetype='image/png')

# === ADMIN PANEL ===
@app.route('/admin')
def admin():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect('/')
    
    submissions = Submission.query.all()
    return render_template('admin.html', submissions=submissions)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# === JINJA FILTER ===
@app.template_filter('strftime')
def _jinja2_filter_strftime(date, fmt):
    return date.strftime(fmt) if isinstance(date, datetime) else datetime.now().strftime(fmt)

if __name__ == '__main__':
    app.run(debug=True)