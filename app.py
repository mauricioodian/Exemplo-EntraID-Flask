from flask import Flask, render_template, redirect, url_for, session, request
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
import requests
import os

# Carregar as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configurações do Microsoft Entra ID (Azure AD)
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
authority = os.getenv('AUTHORITY')
redirect_uri = os.getenv('REDIRECT_URI')
scope = ['User.Read']

# Instância da aplicação confidencial
msal_app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret
)

@app.route('/')
def index():
    if not session.get("user"):
        return render_template('index.html')
    return render_template('index.html', usuario=session['user']['name'])

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_ms')
def login_ms():
    if not session.get("user"):
        auth_url = msal_app.get_authorization_request_url(scope, redirect_uri=redirect_uri)
    return redirect(auth_url)

@app.route('/getAToken')
def get_a_token():
    if request.args.get('code'):
        code = request.args['code']
        result = msal_app.acquire_token_by_authorization_code(code, scopes=scope, redirect_uri=redirect_uri)
        if "access_token" in result:
            session["user"] = result.get("id_token_claims")
            return redirect(url_for("index"))
    return "Autenticação falhou", 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect('https://login.microsoftonline.com/common/oauth2/v2.0/logout?post_logout_redirect_uri=http://localhost:5000')


if __name__ == '__main__':
    app.run()
