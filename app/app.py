from flask import Flask, request, session, redirect, render_template_string
import sqlite3, os

app = Flask(__name__)
app.secret_key = 'supersecretkey123'
DB = '/var/www/bank/db.sqlite'

LOGIN = '''
<!DOCTYPE html><html><head><title>SecureBank</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#0B1F3A;min-height:100vh;
  display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px}
.logo{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.logo-icon{width:40px;height:40px;background:#1A6EA8;border-radius:10px;
  display:flex;align-items:center;justify-content:center;font-size:20px}
.logo-text{color:#fff;font-size:26px;font-weight:700}
.tagline{color:#6B8CAE;font-size:13px;margin-bottom:32px}
.card{background:#fff;border-radius:14px;padding:36px;width:100%;max-width:400px}
.card h2{font-size:20px;font-weight:600;color:#0B1F3A;margin-bottom:4px}
.card p{font-size:13px;color:#6b7280;margin-bottom:28px}
.field{margin-bottom:18px}
.field label{display:block;font-size:12px;font-weight:600;color:#374151;
  margin-bottom:7px;text-transform:uppercase;letter-spacing:.04em}
.field input{width:100%;padding:11px 14px;border:1.5px solid #e5e7eb;
  border-radius:8px;font-size:14px;color:#111}
.btn{width:100%;padding:13px;background:#1A6EA8;color:#fff;border:none;
  border-radius:8px;font-size:15px;font-weight:600;cursor:pointer}
.error{color:#DC2626;font-size:13px;margin-top:14px;padding:10px 12px;
  background:#FEF2F2;border-radius:6px;border:1px solid #FECACA}
.badges{display:flex;gap:20px;margin-top:28px;justify-content:center}
.badge{font-size:11px;color:#6B8CAE}
</style></head>
<body>
<div class='logo'><div class='logo-icon'>&#127970;</div>
<div class='logo-text'>SecureBank</div></div>
<div class='tagline'>Secure. Reliable. Trusted.</div>
<div class='card'>
  <h2>Welcome back</h2>
  <p>Sign in to your SecureBank account</p>
  <form method='POST'>
    <div class='field'><label>Email address</label>
      <input name='username' type='text' placeholder='you@securebank.com'></div>
    <div class='field'><label>Password</label>
      <input name='password' type='password' placeholder='password'></div>
    <button class='btn' type='submit'>Sign in to online banking</button>
    {% if error %}<div class='error'>{{ error }}</div>{% endif %}
  </form>
</div>
<div class='badges'>
  <span class='badge'>&#128274; 256-bit SSL</span>
  <span class='badge'>&#128737; FDIC Insured</span>
  <span class='badge'>&#10003; 2FA Ready</span>
</div></body></html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        # VULNERABLE: direct string concatenation — intentional for lab
        query = "SELECT * FROM accounts WHERE email='" + u + "' AND password='" + p + "'"
        con = sqlite3.connect(DB)
        try:
            row = con.execute(query).fetchone()
        except Exception:
            row = None
        con.close()
        if row:
            session['user_id'] = row[0]
            session['name'] = str(row[1])
            session['balance'] = row[2]
            injection_keywords = ["'", 'OR', 'UNION', 'SELECT', '--', '1=1']
            session['is_injected'] = any(k.upper() in u.upper() for k in injection_keywords)
            return redirect('/dashboard')
        return render_template_string(LOGIN, error='Invalid email or password.')
    return render_template_string(LOGIN, error=None)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    con = sqlite3.connect(DB)
    if session.get('is_injected'):
        accounts = con.execute('SELECT * FROM accounts').fetchall()
    else:
        accounts = con.execute('SELECT * FROM accounts WHERE id=?', (session['user_id'],)).fetchall()
    con.close()
    return f"<h1>Good morning, {session['name']}</h1><p>Balance: ${session['balance']}</p>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/')
def index():
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)