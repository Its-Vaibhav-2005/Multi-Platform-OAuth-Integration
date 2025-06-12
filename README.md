# Multi-Platform OAuth Integration

A Flask-based web application that implements OAuth 2.0 authentication for both Google and GitHub platforms. This project allows users to log in using either their Google or GitHub accounts and displays their basic profile information along with GitHub repositories (if logged in via GitHub).

## Features

- Google OAuth 2.0 Integration
- GitHub OAuth Integration
- Session Management
- Profile Information Display
- GitHub Repository List (for GitHub login)
- Secure Credential Management

## Prerequisites

- Python 3.7+
- Flask
- Google Cloud Platform Account (for Google OAuth)
- GitHub Developer Account (for GitHub OAuth)

## Dependencies

```txt
Flask
requests
google-auth-oauthlib
google-auth
cachecontrol
Flask-Dance
```

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/Its-Vaibhav-2005/Multi-Platform-OAuth-Integration.git
cd Multi-Platform-OAuth-Integration
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure OAuth Credentials:
   - For Google OAuth:
     - Create a project in Google Cloud Console
     - Enable Google+ API
     - Create OAuth 2.0 credentials
     - Download the credentials and save as `client-google.json`
   - For GitHub OAuth:
     - Create a new OAuth App in GitHub Developer Settings
     - Save the client ID and secret in `client-git.json`

5. Run the application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

## Important Code Snippets

### Google OAuth Setup
```python
with open('client-google.json') as f:
    data = json.load(f)
    GOOGLE_CLIENT_ID = data['web']['client_id']
clientSecFile = os.path.join(pathlib.Path(__file__).parent, "client-google.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=clientSecFile,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", 
            "https://www.googleapis.com/auth/userinfo.email", 
            "openid"],
    redirect_uri="http://127.0.0.1:5000/google-callback"
)
```

### GitHub OAuth Setup
```python
gitBlueprint = make_github_blueprint(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    redirect_to="gitCallback"
)
app.register_blueprint(blueprint=gitBlueprint, url_prefix="/git-login")
```

### Session Management
```python
@app.route('/log-out')
def logout():
    session.clear()
    repos.clear()
    return redirect(url_for('loginReq'))
```

## Security Notes

- The application uses secure session management
- OAuth credentials are stored in separate JSON files
- Sensitive files are excluded from version control via .gitignore
- HTTPS is recommended for production deployment

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Vaibhav - [GitHub Profile](https://github.com/Its-Vaibhav-2005) 