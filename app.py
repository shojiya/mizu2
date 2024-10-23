from flask import Flask, redirect, url_for, session, request, render_template
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Google OAuth 2.0の設定
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = "あなたのクライアントID"
GOOGLE_CLIENT_SECRET = "あなたのクライアントシークレット"
REDIRECT_URI = "http://localhost:5000/callback"

flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
    redirect_uri=REDIRECT_URI
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session['state'] == request.args['state']:
        return 'State mismatch error', 400

    credentials = flow.credentials
    request_session = google_requests.Request()

    id_info = id_token.verify_oauth2_token(
        credentials.id_token, request_session, GOOGLE_CLIENT_ID
    )

    session['google_id'] = id_info.get("sub")
    session['email'] = id_info.get("email")
    session['name'] = id_info.get("name")

    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    if 'google_id' not in session:
        return redirect(url_for('index'))

    user_info = {
        'name': session.get('name'),
        'email': session.get('email')
    }

    return render_template('profile.html', user=user_info)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)