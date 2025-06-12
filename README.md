# Multi-Platform OAuth Integration

A Flask-based web application that implements OAuth 2.0 authentication for both Google and GitHub platforms. This project allows users to log in using either their Google or GitHub accounts and displays their repositories (if logged in via GitHub) or Google Drive files (if logged in via Google).

## Features

| Category | Feature | Description |
|----------|---------|-------------|
| **Authentication** | Google OAuth 2.0 | Secure login using Google account with Drive access |
| | GitHub OAuth | Secure login using GitHub account with repository access |
| | Session Management | Secure session handling with automatic timeout |
| | Profile Display | Shows user profile information after login |
| **GitHub Integration** | Repository List | View all GitHub repositories |
| | Repository Details | Name, description, star count, fork count, watcher count |
| | Direct Access | One-click access to repository on GitHub |
| **Google Drive Integration** | File Browser | View all Google Drive files |
| | File Metadata | Name, type, creation date, modification date, size |
| | File Types | Support for Docs, Sheets, Slides, Folders, Images, PDFs, Videos, Audio |
| | Direct Access | One-click access to files in Google Drive |
| **User Interface** | Responsive Design | Works on all screen sizes and devices |
| | Modern Design | Animated gradient background and card-based layout |
| | Interactive Elements | Hover effects and smooth transitions |
| | File Icons | Visual indicators for different file types |
| | Clean Layout | Intuitive and user-friendly interface |

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
google-api-python-client
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
     - Enable Google Drive API and Google+ API
     - Create OAuth 2.0 credentials
     - Add authorized redirect URIs (http://127.0.0.1:5000/google-callback)
     - Download the credentials and save as `client-google.json`
   - For GitHub OAuth:
     - Create a new OAuth App in GitHub Developer Settings
     - Set the callback URL to http://127.0.0.1:5000/git-callback
     - Save the client ID and secret in `client-git.json`

5. Run the application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

## Usage

1. Visit the application homepage
2. Choose your login method (Google or GitHub)
3. After authentication:
   - GitHub login: View your repositories with detailed information
   - Google login: View your Drive files with comprehensive metadata
4. Click on repository/file links to open them in their respective platforms
5. Use the logout button to end your session

## Security Notes

- The application uses secure session management
- OAuth credentials are stored in separate JSON files
- Sensitive files are excluded from version control via .gitignore
- HTTPS is recommended for production deployment
- State parameter validation for OAuth flows
- Secure token handling and storage

## Development Notes

- The application uses Flask for the backend
- Frontend is built with HTML, CSS, and minimal JavaScript
- Font Awesome icons are used for visual elements
- Responsive design works on all screen sizes
- Error handling for API failures and authentication issues

## Author

Vaibhav - [GitHub Profile](https://github.com/Its-Vaibhav-2005)

## License

This project is licensed under the MIT License - see the LICENSE file for details. 