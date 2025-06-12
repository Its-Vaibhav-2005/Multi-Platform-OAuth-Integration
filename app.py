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
from googleapiclient.discovery import build
from flask_dance.contrib.github import make_github_blueprint, github
import secrets
from datetime import datetime

#____________________________________________________Initialize__________________________________________________
# initialize Flask app . . .
app = Flask(__name__)
app.secret_key = os.urandom(32)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
# Base URL for the application
BASE_URL = "http://127.0.0.1:5000"
# git blueprintInitializing
gitBlueprint = make_github_blueprint(
    client_id='Ov23liJrIOCBuTz0Yx6Y',
    client_secret='bf2c37c1a10180012a1d5bac0df1748974383622',
    redirect_to="gitCallback",
    redirect_url="/git-callback"  # Explicitly set the redirect URL
)
app.register_blueprint(blueprint=gitBlueprint, url_prefix="/git-login")

# google initializing
with open('client-google.json') as f:
    data = json.load(f)
    googleClientId = data['web']['client_id']
clientSecFile = os.path.join(pathlib.Path(__file__).parent, "client-google.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=clientSecFile,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "openid"
    ],
    redirect_uri=f"{BASE_URL}/google-callback"
)

# Global variables
userRepos = []
userDriveFiles = []

#______________________________________________LOGIN____________________________________________________________
# git login
@app.route('/git-log-in')
def gitLogin():
    global userRepos
    if not github.authorized:
        return redirect(url_for("github.login"))
    try:
        resp = github.get("/user")
        if resp.ok:
            userInfo = resp.json()
            session['github_info'] = userInfo
            session['github_id'] = userInfo['login']
            session['git_name'] = userInfo['name']
            session['login_type'] = 'github'
            
            # Fetch repositories
            repoResp = github.get("/user/repos")
            if repoResp.ok:
                userRepos = repoResp.json()
            else:
                userRepos = []
            return redirect(url_for('main'))
        return "Failed to fetch GitHub user info", 400
    except Exception as e:
        print(f"GitHub login error: {str(e)}")
        session.clear()
        return "GitHub authentication failed", 400
# google login
@app.route("/google-log-in")
def googleLogin():
    global userDriveFiles
    try:
        # Generate a random state token
        state = secrets.token_urlsafe(16)
        session['state'] = state
        
        # Create authorization URL with state
        authUrl, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent screen to ensure we get a refresh token
        )
        
        userDriveFiles = []
        return redirect(authUrl)
    except Exception as e:
        print(f"Google login error: {str(e)}")
        session.clear()
        return "Google login initialization failed", 400
#______________________________________________________CALLBACK_____________________________________________
# git callback 
@app.route('/git-callback') 
def gitCallback():
    if not github.authorized:
        return "GitHub authentication failed", 400
    try:
        return redirect(url_for('main'))
    except Exception as e:
        print(f"GitHub callback error: {str(e)}")
        session.clear()
        return "GitHub callback failed", 400
# google callback
@app.route("/google-callback")
def callback():
    try:
        # Get the state from the request
        requestState = request.args.get('state')
        sessionState = session.get('state')
        
        # Verify state
        if not sessionState or not requestState or sessionState != requestState:
            print(f"State mismatch - Session: {sessionState}, Request: {requestState}")
            session.clear()
            return "Invalid state parameter", 400
            
        # Exchange authorization code for credentials
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        
        # Create session and verify token
        reqSession = requests.session()
        cacheSess = cachecontrol.CacheControl(reqSession)
        tknReq = google.auth.transport.requests.Request(session=cacheSess)
        
        idInfo = id_token.verify_oauth2_token(
            id_token=creds._id_token,
            request=tknReq,
            audience=googleClientId
        )
        
        # Store user info in session
        session['google_id'] = idInfo.get('sub')
        session['google_name'] = idInfo.get('name')
        session['login_type'] = 'google'
        
        # Fetch Google Drive files with pagination
        driveService = build('drive', 'v3', credentials=creds)
        pageToken = None
        allFiles = []
        
        while True:
            try:
                # List files with specific fields and ordering
                results = driveService.files().list(
                    pageSize=100,
                    fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, iconLink, thumbnailLink, webViewLink)",
                    orderBy="modifiedTime desc",
                    pageToken=pageToken,
                    q="trashed = false"  # Exclude trashed files
                ).execute()
                
                files = results.get('files', [])
                allFiles.extend(files)
                
                # Get next page token
                pageToken = results.get('nextPageToken')
                if not pageToken:
                    break
                    
            except Exception as e:
                print(f"Error fetching files: {str(e)}")
                break
        
        # Process and format file data
        for file in allFiles:
            # Format dates
            if 'createdTime' in file:
                file['createdTime'] = datetime.fromisoformat(file['createdTime'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            if 'modifiedTime' in file:
                file['modifiedTime'] = datetime.fromisoformat(file['modifiedTime'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            
            # Format file size
            if 'size' in file:
                size = int(file['size'])
                if size < 1024:
                    file['formattedSize'] = f"{size} B"
                elif size < 1024 * 1024:
                    file['formattedSize'] = f"{size/1024:.1f} KB"
                elif size < 1024 * 1024 * 1024:
                    file['formattedSize'] = f"{size/(1024*1024):.1f} MB"
                else:
                    file['formattedSize'] = f"{size/(1024*1024*1024):.1f} GB"
            
            # Add file type icon
            mimeType = file.get('mimeType', '')
            if 'google-apps' in mimeType:
                file['icon'] = 'fas fa-file-word'  # Google Docs
            elif 'spreadsheet' in mimeType:
                file['icon'] = 'fas fa-file-excel'  # Google Sheets
            elif 'presentation' in mimeType:
                file['icon'] = 'fas fa-file-powerpoint'  # Google Slides
            elif 'folder' in mimeType:
                file['icon'] = 'fas fa-folder'
            elif 'image' in mimeType:
                file['icon'] = 'fas fa-file-image'
            elif 'pdf' in mimeType:
                file['icon'] = 'fas fa-file-pdf'
            elif 'video' in mimeType:
                file['icon'] = 'fas fa-file-video'
            elif 'audio' in mimeType:
                file['icon'] = 'fas fa-file-audio'
            else:
                file['icon'] = 'fas fa-file'
        
        userDriveFiles = allFiles
        
        # Clear the state after successful authentication
        session.pop('state', None)
        
        return redirect(url_for('main'))
        
    except Exception as e:
        print(f"Google callback error: {str(e)}")
        session.clear()
        return "Authentication failed", 400
#_____________________________________________________LOGOUT_________________________________________________
@app.route('/log-out')
def logout():
    session.clear()
    userRepos.clear()
    userDriveFiles.clear()
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
    print(userRepos, len(userRepos))
    
    loginType = session.get('login_type', '')
    userName = session.get('google_name') if loginType == 'google' else session.get('git_name')
    
    return render_template(
        'index.html',
        name=userName,
        loginType=loginType,
        repos=userRepos if loginType == 'github' else [],
        driveFiles=userDriveFiles if loginType == 'google' else []
    )
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')