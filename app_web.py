import json, os, csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
app.secret_key = "gauteng_ems_2026_secure"
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.rnlzboymgcpklspogdvu:Nosolomzi_ngcwabe10@aws-0-eu-west-1.pooler.supabase.com:6543/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── DATABASE MODEL ───
class Submission(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    incident      = db.Column(db.String(100), nullable=False)
    district      = db.Column(db.String(100), nullable=False)
    station       = db.Column(db.String(100), nullable=False)
    billing_class = db.Column(db.String(100), nullable=False)
    capture_date  = db.Column(db.String(50), nullable=False)
    prf_filename  = db.Column(db.String(255), default='')
    downloaded    = db.Column(db.String(10), default='')

# ─── STATION DATA ───
DISTRICTS = {
    "CITY OF TSHWANE (COT)": ["Mamelodi", "Block JJ", "Odi", "Kalafong", "Cullinan", "Prinshof", "Laudium", "Bronkhorstpruit", "Ekangala"],
    "WESTRAND (WR)": ["Leratong", "Krugersdorp", "Carltonville", "bekkersdal", "Dr Yusuf Dadoo", "Khutsong", "Magalies", "Mohlakeng/Randfontein", "Sterkfontein", "Wedela", "Westonaria"],
    "CITY OF JOHANNESBURG (COJ)": ["Hillbrow", "Bara/Eldos", "Alexandra", "Chiawelo", "Discovery", "Ebony Park", "Edenvale", "Imbalenhle/Orange Farm", "Lenasia", "Lenasia South", "Midrand", "Mofolo", "Orlando East", "Selby", "Zola/Tsepo Temba", "Witkoppen/Tara", "Diepsloot/OR Tambo"],
    "CITY OF EKURHULENI (COE)": ["Bertha Gxowa/Germiston", "Thembisa", "Daggafontein/Springs", "Devon", "Dun Swart", "Far East Rand", "Phillip Moyo", "Nokuthela Ngwenya", "Goba/Iluthundweni", "Itereleng", "Pholosong", "Tambo Memorial", "Thelle Mogoerane"],
    "SEDIBENG (SED)": ["Sebokeng", "Heidelberg", "Evaton", "Meyerton/Pontshong", "Vanderbijlpark/J Heyns", "Vereeniging"],
}

# ─── CREDENTIALS ───
COMMON_PWD = "Gauteng@2026"
USER_DATA = {station: COMMON_PWD for stations in DISTRICTS.values() for station in stations}
USER_DATA["Finance"]   = "Admin2026"
USER_DATA["Raphiri"]   = "Admin2026"
USER_DATA["Nosolomzi"] = "Admin2026"
USER_DATA["Ruiters"]   = "Admin2026"

FINANCE_USERS = ["finance", "raphiri", "nosolomzi", "ruiters"]

# ─── ROUTES ───
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
            is_finance_user = u_input.lower() in FINANCE_USERS

            if role == 'finance' and not is_finance_user:
                error = "Access Denied: Station staff must use the EMS Frontline portal."
            elif role == 'ems' and is_finance_user:
                error = "Access Denied: Finance Admin must use the Finance Dept portal."
            else:
                session.permanent = True
                session['user'] = user_match
                session['role'] = 'finance' if is_finance_user else 'ems'
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

    user_station = session.get('user')
    user_district = None
    for district, stations in DISTRICTS.items():
        if user_station in stations:
            user_district = district
            break

    return render_template('submit.html',
                           districts=sorted(DISTRICTS.keys()),
                           districts_json=json.dumps(DISTRICTS),
                           user_district=user_district)

@app.route('/dashboard')
def dashboard_page():
    if str(session.get('role', '')).lower() != 'finance':
        return redirect(url_for('index'))

    submissions = Submission.query.order_by(Submission.id.desc()).all()
    return render_template('dashboard.html', submissions=submissions, username=session.get('user'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/save', methods=['POST'])
def save():
    if session.get('role') != 'ems':
        return redirect(url_for('index'))

    prf_file = request.files.get('prf_file')
    prf_filename = ''
    if prf_file and prf_file.filename:
        if not prf_file.filename.lower().endswith('.pdf'):
            return "Only PDF files are allowed.", 400
        prf_filename = secure_filename(prf_file.filename)
        prf_file.save(os.path.join(UPLOAD_FOLDER, prf_filename))

    submission = Submission(
        incident      = request.form.get('incident'),
        district      = request.form.get('district'),
        station       = request.form.get('station'),
        billing_class = request.form.get('billing_class'),
        capture_date  = datetime.now().strftime('%d-%b-%Y %H:%M'),
        prf_filename  = prf_filename,
        downloaded    = ''
    )
    db.session.add(submission)
    db.session.commit()

    return redirect(url_for('submit_page'))

@app.route('/download/<filename>')
def download_prf(filename):
    if session.get('role') != 'finance':
        return redirect(url_for('index'))

    # Mark as downloaded
    submission = Submission.query.filter_by(prf_filename=filename).first()
    if submission:
        submission.downloaded = 'yes'
        db.session.commit()

    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

@app.route('/export')
def export():
    if session.get('role') != 'finance':
        return redirect(url_for('index'))

    submissions = Submission.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['incident', 'district', 'station', 'billing_class', 'capture_date', 'prf_filename', 'downloaded'])
    for s in submissions:
        writer.writerow([s.incident, s.district, s.station, s.billing_class, s.capture_date, s.prf_filename, s.downloaded])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='EMS_Submissions.csv'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # creates ems.db automatically
    app.run(debug=True, port=5001)