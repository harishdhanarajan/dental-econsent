import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response, send_file
from datetime import datetime
import uuid
from weasyprint import HTML
from google.oauth2.service_account import Credentials
import gspread

app = Flask(__name__)
app.secret_key = '/src/routes/creds.json'

# Google Sheets config
creds_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
gc = gspread.authorize(creds)
SPREADSHEET_ID = "12OeqcsRsceo5QQviYyqdPi7LenzVwSG8DvFGAapRlyQ"
sh = gc.open_by_key(SPREADSHEET_ID)

# Worksheets
patients_ws = sh.worksheet("patient_data")
followup_ws = sh.worksheet("follow_up")

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def clean_record(record):
    """Strip whitespace from keys but keep the original structure."""
    return {k.strip(): v for k, v in record.items()}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/personal_details", methods=["GET", "POST"])
def personal_details():
    if request.method == "POST":
        session['personal_details'] = {
            'full_name': request.form.get('full_name',''),
            'age': request.form.get('age',''),
            'gender': request.form.get('gender',''),
            'dob': request.form.get('dob',''),
            'address': request.form.get('address',''),
            'phone': request.form.get('phone',''),
            'email': request.form.get('email',''),
            'emergency_contact': request.form.get('emergency_contact',''),
            'relationship': request.form.get('relationship',''),
            'emergency_phone': request.form.get('emergency_phone','')
        }
        return redirect(url_for('medical_history'))
    return render_template('personal_details.html')

@app.route("/medical_history", methods=["GET", "POST"])
def medical_history():
    if request.method == "POST":
        conditions = []
        for key in request.form:
            if key.startswith('condition_'):
                condition_name = key.replace('condition_', '').replace('_', ' ')
                conditions.append(condition_name)
        session['medical_history'] = {
            'under_treatment': request.form.get('under_treatment',''),
            'taking_medications': request.form.get('taking_medications',''),
            'have_allergies': request.form.get('have_allergies',''),
            'is_pregnant': request.form.get('is_pregnant',''),
            'is_breastfeeding': request.form.get('is_breastfeeding',''),
            'medical_conditions': ', '.join(conditions) or 'None reported'
        }
        return redirect(url_for('dental_history'))
    return render_template('medical_history.html')

@app.route("/dental_history", methods=["GET", "POST"])
def dental_history():
    if request.method == "POST":
        issues = []
        for key in request.form:
            if key.startswith('issue_'):
                issue_name = key.replace('issue_', '').replace('_', ' ')
                issues.append(issue_name)
        session['dental_history'] = {
            'first_visit': request.form.get('first_visit',''),
            'visit_reason': request.form.get('visit_reason',''),
            'previous_treatment': request.form.get('previous_treatment',''),
            'dental_issues': ', '.join(issues) or 'None reported'
        }
        return redirect(url_for('consent'))
    return render_template('dental_history.html')

@app.route("/consent", methods=["GET", "POST"])
def consent():
    if request.method == "POST":
        session['signature_data'] = request.form.get('signature_data','')
        return redirect(url_for('register'))
    return render_template('consent.html')

@app.route("/register", methods=["POST"])
def register():
    # Generate patient ID
    patient_id = str(uuid.uuid4())[:8]
    registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Prepare data for Google Sheets
    sheet_data = {
        'Patient ID': patient_id,
        'Registration Date': registration_date,
        'Full Name': session.get('personal_details', {}).get('full_name', ''),
        'Age': session.get('personal_details', {}).get('age', ''),
        'Gender': session.get('personal_details', {}).get('gender', ''),
        'Date of Birth': session.get('personal_details', {}).get('dob', ''),
        'Address': session.get('personal_details', {}).get('address', ''),
        'Phone': session.get('personal_details', {}).get('phone', ''),
        'Email': session.get('personal_details', {}).get('email', ''),
        'Emergency Contact': session.get('personal_details', {}).get('emergency_contact', ''),
        'Relationship': session.get('personal_details', {}).get('relationship', ''),
        'Emergency Phone': session.get('personal_details', {}).get('emergency_phone', ''),
        'Medical Conditions': session.get('medical_history', {}).get('medical_conditions', ''),
        'First Dental Visit': session.get('dental_history', {}).get('first_visit', ''),
        'Reason for Visit': session.get('dental_history', {}).get('visit_reason', ''),
        'Dental Issues': session.get('dental_history', {}).get('dental_issues', '')
    }
    # Append to sheet
    headers = patients_ws.row_values(1)
    row = [sheet_data.get(h.strip(), '') for h in headers]
    patients_ws.append_row(row)

    # Generate PDF
    filename = f"patient_{patient_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    signature_data = request.form.get('signature_data') or session.get('signature_data', '')
    pdf_data = {
        'personal_details': session.get('personal_details', {}),
        'medical_history': session.get('medical_history', {}),
        'dental_history': session.get('dental_history', {}),
        'signature_data': signature_data,
        'registration_date': registration_date,
        'patient_id': patient_id
    }
    html = render_template('pdf_template.html', **pdf_data)
    pdf_bytes = HTML(string=html, base_url=request.url_root).write_pdf()
    pdf_path = os.path.join(DATA_DIR, filename)
    with open(pdf_path, 'wb') as f:
        f.write(pdf_bytes)
    session['pdf_filename'] = filename
    session['patient_id'] = patient_id
    # Clear form data from session but keep pdf info
    for key in ['personal_details', 'medical_history', 'dental_history', 'signature_data']:
        session.pop(key, None)
    return render_template(
        'registration_success.html',
        patient_id=patient_id,
        filename=filename
    )

@app.route("/registration_success")
def registration_success():
    patient_id = session.get('patient_id', 'Unknown')
    filename = session.get('pdf_filename', '')
    return render_template('registration_success.html', patient_id=patient_id, filename=filename)

@app.route("/download_pdf/<filename>")
def download_pdf(filename):
    try:
        pdf_path = os.path.join(DATA_DIR, filename)
        return send_file(pdf_path, as_attachment=True, download_name=filename, mimetype='application/pdf')
    except Exception as e:
        flash(f'Error downloading PDF: {e}', 'danger')
        return redirect(url_for('home'))

@app.route("/existing_visitor")
def existing_visitor():
    return render_template('existing_visitor.html')

@app.route("/search_patient", methods=["GET","POST"])
def search_patient():
    term = (request.form.get('search_term') if request.method=='POST' else request.args.get('search_term','')).lower()
    stype = (request.form.get('search_type') if request.method=='POST' else request.args.get('search_type','id'))
    try:
        raw = patients_ws.get_all_records()
        records = [clean_record(r) for r in raw]
        if stype=='id':
            matches = [r for r in records if term in r.get('Patient ID','').lower()]
        else:
            matches = [r for r in records if term in r.get('Full Name','').lower()]
        return jsonify({'patients': matches})
    except Exception as e:
        return jsonify({'error': str(e), 'patients': []}), 500

@app.route("/patient_profile/<patient_id>")
def patient_profile(patient_id):
    try:
        raw = patients_ws.get_all_records()
        record = next((r for r in raw if r.get('Patient ID')==patient_id), None)
        patient = clean_record(record) if record else None
        if not patient:
            flash('Patient not found','warning')
            return redirect(url_for('existing_visitor'))
        
        # Debug print
        print(f"Patient data: {patient}")
        
        rawf = followup_ws.get_all_records()
        history = [clean_record(h) for h in rawf if clean_record(h).get('Patient ID')==patient_id]
        history.sort(key=lambda x: x.get('Visit Date',''), reverse=True)
        return render_template('patient_profile.html', patient=patient, history=history)
    except Exception as e:
        flash(f'Error loading profile: {e}','danger')
        return redirect(url_for('existing_visitor'))

@app.route("/add_followup/<patient_id>", methods=["GET","POST"])
def add_followup(patient_id):
    try:
        if request.method=='POST':
            # Collect all form data for comprehensive clinical examination
            followup_data = {
                'Patient ID': patient_id,
                'Visit Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Chief Complaint': request.form.get('chief_complaint',''),
                'History of Presenting Illness': request.form.get('history_presenting_illness',''),
                'Past Medical History': request.form.get('past_medical_history',''),
                'Past Dental History': request.form.get('past_dental_history',''),
                'Face Symmetry': request.form.get('face_symmetry',''),
                'TMJ': request.form.get('tmj',''),
                'Lymph Nodes': request.form.get('lymph_nodes',''),
                'Skin/Other': request.form.get('skin_other',''),
                'Lips': request.form.get('lips',''),
                'Buccal Mucosa': request.form.get('buccal_mucosa',''),
                'Tongue': request.form.get('tongue',''),
                'Floor of Mouth': request.form.get('floor_of_mouth',''),
                'Palate': request.form.get('palate',''),
                'Gingiva': request.form.get('gingiva',''),
                'Caries': request.form.get('caries',''),
                'Missing Teeth': request.form.get('missing_teeth',''),
                'Occlusion': request.form.get('occlusion',''),
                'Mobility': request.form.get('mobility',''),
                'Periodontal Status': request.form.get('periodontal_status',''),
                'Attrition/Abrasion/Erosion': request.form.get('attrition_abrasion_erosion',''),
                'Radiographs Taken': request.form.get('radiographs_taken',''),
                'Radiographic Observations': request.form.get('radiographic_observations',''),
                'Diagnosis': request.form.get('diagnosis',''),
                'Treatment': request.form.get('treatment',''),
                'Prescription': request.form.get('prescription',''),
                'Follow-up Notes': request.form.get('followup_notes',''),
                'Next Appointment': request.form.get('next_appointment','')
            }
            
            # Get headers and append row
            headers = followup_ws.row_values(1)
            row = [followup_data.get(h.strip(),'') for h in headers]
            followup_ws.append_row(row)
            
            flash('Clinical examination recorded successfully!', 'success')
            return redirect(url_for('patient_profile', patient_id=patient_id))
            
        # GET request - show form
        raw = patients_ws.get_all_records()
        patient = clean_record(next((r for r in raw if r.get('Patient ID')==patient_id), {}))
        current_date = datetime.now().strftime('%Y-%m-%d')
        return render_template('add_followup.html', patient=patient, current_date=current_date)
    except Exception as e:
        flash(f'Error recording follow-up: {e}','danger')
        return redirect(url_for('patient_profile', patient_id=patient_id))

@app.route("/validate_age", methods=["POST"])
def validate_age():
    try:
        age = int(request.form.get('age',0))
        if not 0<age<=120:
            return jsonify({'valid':False,'errors':{'age':'Please enter a valid age'}})
        return jsonify({'valid':True,'errors':{}})
    except ValueError:
        return jsonify({'valid':False,'errors':{'age':'Age must be a number'}})

# Debug route to check column names
@app.route("/debug_sheets")
def debug_sheets():
    try:
        patient_headers = patients_ws.row_values(1)
        all_records = patients_ws.get_all_records()
        sample_record = all_records[0] if all_records else {}
        
        followup_headers = followup_ws.row_values(1)
        
        debug_info = {
            "patient_sheet_headers": patient_headers,
            "sample_patient_record": sample_record,
            "followup_sheet_headers": followup_headers
        }
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
