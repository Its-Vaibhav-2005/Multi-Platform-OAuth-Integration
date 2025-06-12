# all imports . . .
from flask import Flask, render_template, session, request, redirect, url_for, abort
import os
import json
import pathlib
import requests
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from pip._vendor import cachecontrol
from google.oauth2 import id_token
from flask_dance.contrib.github import make_github_blueprint, github
#____________________________________________________Initialize__________________________________________________
# initialize Flask app . . .
app = Flask(__name__)
app.secret_key = os.urandom(32)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
# git blueprintInitializing
gitBlueprint = make_github_blueprint(
    client_id='Ov23liJrIOCBuTz0Yx6Y',
    client_secret='bf2c37c1a10180012a1d5bac0df1748974383622',
    redirect_to="gitCallback"
)
app.register_blueprint(blueprint=gitBlueprint, url_prefix="/git-login")

# google initializing
with open('client-google.json') as f:
    data = json.load(f)
    GOOGLE_CLIENT_ID = data['web']['client_id']
clientSecFile = os.path.join(pathlib.Path(__file__).parent, "client-google.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=clientSecFile,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/google-callback"
)
#______________________________________________LOGIN____________________________________________________________
# git login
@app.route('/git-log-in')
def gitLogin():
    global repos
    if not github.authorized:
        return redirect(url_for("github.login"))  # Redirect to GitHub OAuth login
    resp = github.get("/user")
    print(github)
    if resp.ok:
        userInfo = resp.json()
        session['github_info'] = userInfo
        session['github_id'] = userInfo['login']  # Save GitHub username in session
        session['git_name'] = userInfo['name']
        # repositry response . . .
        repo = github.get("/user/repos")
        if repo.ok:
            repos = repo.json()
            print(repos)
        else:
            repos = []
        return redirect(url_for('main'))
    return "Failed to fetch GitHub user info", 400
# google login
@app.route("/google-log-in")
def googleLogin():
    global repos
    authUrl, sts = flow.authorization_url()
    session['state'] = sts
    repos = []
    return redirect(authUrl)
#______________________________________________________CALLBACK_____________________________________________
# git callback 
@app.route('/git-callback') 
def gitCallback():
    if github.authorized:
        return redirect(url_for('main'))
    return "GitHub authentication failed", 400
# google callback
@app.route("/google-callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        abort(500)
    creds = flow.credentials
    reqSession = requests.session()
    cacheSess = cachecontrol.CacheControl(reqSession)
    tknReq = google.auth.transport.requests.Request(session=cacheSess)
    idInfo = id_token.verify_oauth2_token(
        id_token=creds._id_token,
        request=tknReq,
        audience=GOOGLE_CLIENT_ID
    )
    session['google_id'] = idInfo.get('sub')
    session['google_name'] = idInfo.get('name')
    print(idInfo)
    return redirect(url_for('main'))
#_____________________________________________________LOGOUT_________________________________________________
@app.route('/log-out')
def logout():
    session.clear()
    repos.clear()
    return redirect(url_for('loginReq'))
#__________________________________________________UNPROTECTED-PAGE___________________________________________
@app.route('/login-req')
def loginReq():
    return render_template('login.html')
#_________________________________________________HOME-PAGE___________________________________________________
@app.route('/')
@app.route('/main')
def main():
    if 'github_id' not in session and 'google_id' not in session:
        return redirect(url_for('loginReq'))
    print(repos, len(repos))
    return render_template(
        'index.html',
        name= session['google_name'] if 'google_id' in session else session['git_name'],
        repos = repos
    )
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')