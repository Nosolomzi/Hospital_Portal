import json, csv, os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "gauteng_ems_2026_secure"
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # fixed typo
app.config['SESSION_COOKIE_HTTPONLY'] = True
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FIELDNAMES = ['incident', 'district', 'station', 'billing_class', 'capture_date', 'prf_filename', 'downloaded']

# 1. STATION DATA
DISTRICTS = {
    "CITY OF TSHWANE (COT)": ["Mamelodi", "Block JJ", "Odi", "Kalafong", "Cullinan", "Prinshof", "Laudium", "Bronkhorstpruit", "Ekangala"],
    "WESTRAND (WR)": ["Leratong", "Krugersdorp", "Carltonville", "bekkersdal", "Dr Yusuf Dadoo", "Khutsong", "Magalies", "Mohlakeng/Randfontein", "Sterkfontein", "Wedela", "Westonaria"],
    "CITY OF JOHANNESBURG (COJ)": ["Hillbrow", "Bara/Eldos", "Alexandra", "Chiawelo", "Discovery", "Ebony Park", "Edenvale", "Imbalenhle/Orange Farm", "Lenasia", "Lenasia South", "Midrand", "Mofolo", "Orlando East", "Selby", "Zola/Tsepo Temba", "Witkoppen/Tara", "Diepsloot/OR Tambo"],
    "CITY OF EKURHULENI (COE)": ["Bertha Gxowa/Germiston", "Thembisa", "Daggafontein/Springs", "Devon", "Dun Swart", "Far East Rand", "Phillip Moyo", "Nokuthela Ngwenya", "Goba/Iluthundweni", "Itereleng", "Pholosong", "Tambo Memorial", "Thelle Mogoerane"],
    "SEDIBENG (SED)": ["Sebokeng", "Heidelberg", "Evaton", "Meyerton/Pontshong", "Vanderbijlpark/J Heyns", "Vereeniging"],
}

# 2. CREDENTIALS
COMMON_PWD = "Gauteng@2026"
USER_DATA = {station: COMMON_PWD for stations in DISTRICTS.values() for station in stations}
USER_DATA["Finance"] = "Admin2026"
USER_DATA["Raphiri"] = "Admin2026"
USER_DATA["Nosolomzi"] = "Admin2026"
USER_DATA["Ruiters"] = "Admin2026"
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    error = None
    if request.method == 'POST':
        u_input = request.form.get('username', '').strip()
        p_input = request.form.get('password', '').strip()
        
        user_match = next((k for k in USER_DATA if k.lower() == u_input.lower()), None)

        if user_match and USER_DATA[user_match] == p_input:
            FINANCE_USERS =["finance", "raphiri", "nosolomzi", "ruiters"]
            is_finance_user = u_input.lower() in FINANCE_USERS
            
            if role == 'finance' and not is_finance_user:
                error = "Access Denied: Station staff must use the EMS Frontline portal."
            elif role == 'ems' and is_finance_user:
                error = "Access Denied: Finance Admin must use the Finance Dept portal."
            else:
                session.permanent = True
                session['user'] = user_match
                session['role'] = 'finance' if is_finance_user else 'ems'
                print(f"DEBUG LOGIN: role set to {session['role']}")  
                if is_finance_user:
                    return redirect(url_for('dashboard_page'))
                else:
                    return redirect(url_for('submit_page'))
        else:
            error = "Invalid Username or Password. Please contact Nosolomzi."
            
    return render_template('login.html', role=role, error=error)

@app.route('/submit')
def submit_page():
    if session.get('role') != 'ems':
        return redirect(url_for('index'))
    return render_template('submit.html', districts=sorted(DISTRICTS.keys()), districts_json=json.dumps(DISTRICTS))

@app.route('/dashboard')
def dashboard_page():
    print(f"DEBUG DASHBOARD: session contains {dict(session)}")
    current_role = str(session.get('role', '')).lower()
    
    if current_role != 'finance':
        print(f"DEBUG: Access denied. Role is: '{current_role}'")
        return redirect(url_for('index'))
    
    submissions = []
    if os.path.exists('hospital_tracker.csv'):
        with open('hospital_tracker.csv', 'r') as f:
            reader = csv.DictReader(f)
            submissions = list(reader)
            
    return render_template('dashboard.html', submissions=submissions, username=session.get('user'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/save', methods=['POST'])
def save():
    if session.get('role') != 'ems':
        return redirect(url_for('index'))

    incident = request.form.get('incident')
    district = request.form.get('district')
    station = request.form.get('station')
    billing_class = request.form.get('billing_class')
    capture_date = datetime.now().strftime('%d-%b-%Y %H:%M')

    # Handle PRF file upload
    prf_file = request.files.get('prf_file')
    prf_filename = ''
    if prf_file and prf_file.filename:
        if not prf_file.filename.lower().endswith('.pdf'):
            return "Only PDF files are allowed.", 400
        prf_filename = secure_filename(prf_file.filename)
        prf_file.save(os.path.join(UPLOAD_FOLDER, prf_filename))

    # Read existing rows if CSV exists
    existing_rows = []
    if os.path.exists('hospital_tracker.csv'):
        with open('hospital_tracker.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Rebuild each row with only the correct fields
                clean_row = {field: row.get(field, '') for field in FIELDNAMES}
                existing_rows.append(clean_row)

    # Add new row
    existing_rows.append({
        'incident': incident,
        'district': district,
        'station': station,
        'billing_class': billing_class,
        'capture_date': capture_date,
        'prf_filename': prf_filename,
        'downloaded': ''
    })

    # Rewrite entire CSV with correct headers
    with open('hospital_tracker.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(existing_rows)

    return redirect(url_for('submit_page'))

@app.route('/download/<filename>')
def download_prf(filename):
    if session.get('role') != 'finance':
        return redirect(url_for('index'))

    # Mark as downloaded in CSV
    rows = []
    if os.path.exists('hospital_tracker.csv'):
        with open('hospital_tracker.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('prf_filename') == filename:
                    row['downloaded'] = 'yes'
                rows.append(row)

        with open('hospital_tracker.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)

    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)


    return redirect(url_for('submit_page'))

@app.route('/export')
def export():
    if session.get('role') != 'finance':
        return redirect(url_for('index'))
    return send_file('hospital_tracker.csv', as_attachment=True, download_name='EMS_Submissions.csv')



if __name__ == '__main__':
    app.run(debug=True, port=5001)