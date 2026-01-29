# OneDrive Graph API Integration

A Microsoft Graph API integration enabling external applications to securely read files from OneDrive for Business.

## The Problem

A client needed their AI assistant (ChatGPT/custom app) to read documents stored in OneDrive for Business. They wanted:

- Secure, read-only access to specific user's files
- No user sign-in required (background service)
- Simple API calls their developers could use
- Complete documentation for their team

## The Solution

Built a complete Graph API integration using Azure App Registration with Client Credentials flow.

### Capabilities

| Feature | Description |
|---------|-------------|
| List Files | Browse folders and files in OneDrive |
| Get Metadata | Retrieve file details (name, size, dates, type) |
| Download Files | Read file content programmatically |
| Search | Find files by name across the drive |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  External App   │────▶│   Azure AD      │────▶│  Microsoft      │
│  (ChatGPT/Bot)  │     │   OAuth2        │     │  Graph API      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │ 1. Request Token      │                       │
        │   (Client Creds)      │                       │
        │──────────────────────▶│                       │
        │                       │                       │
        │ 2. Access Token       │                       │
        │◀──────────────────────│                       │
        │                       │                       │
        │ 3. API Call + Token   │                       │
        │──────────────────────────────────────────────▶│
        │                       │                       │
        │ 4. OneDrive Data      │                       │
        │◀──────────────────────────────────────────────│
```

## Authentication Flow

Using **OAuth2 Client Credentials** flow:

1. App authenticates with Client ID + Client Secret
2. Azure AD issues access token (valid 1 hour)
3. App uses token for Graph API calls
4. Token auto-renewed when expired

**Why Client Credentials?**
- No user interaction needed
- Perfect for background services
- Tokens managed programmatically

## Azure App Setup

### Permissions Required

| Permission | Type | Purpose |
|------------|------|---------|
| Files.Read.All | Application | Read all files in OneDrive |
| User.Read.All | Application | Access user's drive |

Both require **Admin Consent** in Azure Portal.

### Security Configuration

```
App Registration
├── Supported account types: Single tenant only
├── Redirect URI: None (client credentials)
├── Client Secret: 12-24 month expiry
└── Permissions: Read-only (cannot modify/delete)
```

## API Endpoints

**Base URL:** `https://graph.microsoft.com/v1.0`

| Action | Endpoint |
|--------|----------|
| List root files | `/users/{email}/drive/root/children` |
| List folder contents | `/users/{email}/drive/items/{folder_id}/children` |
| Get file metadata | `/users/{email}/drive/items/{file_id}` |
| Download file | `/users/{email}/drive/items/{file_id}/content` |
| Search files | `/users/{email}/drive/root/search(q='{query}')` |

## Code Examples

### Get Access Token

```bash
curl -X POST "https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&scope=https://graph.microsoft.com/.default&grant_type=client_credentials"
```

### List Files

```bash
curl -X GET "https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/drive/root/children" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### Download File

```bash
curl -L -X GET "https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/drive/items/{FILE_ID}/content" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -o filename.ext
```

**Note:** `-L` flag follows redirects (required for downloads).

### Python Implementation

```python
import requests

class OneDriveAPI:
    def __init__(self, tenant_id, client_id, client_secret, user_email):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_email = user_email
        self.access_token = None
    
    def get_token(self):
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }
        response = requests.post(url, data=data)
        self.access_token = response.json()["access_token"]
        return self.access_token
    
    def list_files(self, folder_id=None):
        if not self.access_token:
            self.get_token()
        
        if folder_id:
            url = f"https://graph.microsoft.com/v1.0/users/{self.user_email}/drive/items/{folder_id}/children"
        else:
            url = f"https://graph.microsoft.com/v1.0/users/{self.user_email}/drive/root/children"
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()
    
    def download_file(self, file_id):
        if not self.access_token:
            self.get_token()
        
        url = f"https://graph.microsoft.com/v1.0/users/{self.user_email}/drive/items/{file_id}/content"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers, allow_redirects=True)
        return response.content
    
    def search_files(self, query):
        if not self.access_token:
            self.get_token()
        
        url = f"https://graph.microsoft.com/v1.0/users/{self.user_email}/drive/root/search(q='{query}')"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()
```

## Token Management

### Access Token Lifecycle

| Token Type | Lifetime | Renewal Method |
|------------|----------|----------------|
| Access Token | 1 hour | Request new token |
| Client Secret | 12-24 months | Regenerate in Azure Portal |

### Handling Expired Tokens

When token expires, API returns:
```json
{
  "error": {
    "code": "InvalidAuthenticationToken",
    "message": "Access token has expired or is not yet valid."
  }
}
```

**Solution:** Catch error, request new token, retry call.

## Deliverables

```
/docs
  Azure_Setup_Guide.md      → Step-by-step app registration
  Token_Renewal_Guide.md    → Token lifecycle management
  API_Reference.md          → Endpoint documentation

/src
  onedrive_api.py           → Python implementation
  
/examples
  curl_commands.md          → Ready-to-use curl examples
```

## Security Best Practices

1. **Store secrets securely** - Use environment variables or key vault
2. **Rotate secrets** - Before expiration date
3. **Minimum permissions** - Read-only, single tenant
4. **Monitor usage** - Check Azure AD sign-in logs
5. **No secrets in code** - Use configuration files

## Results

- Client's AI assistant can now read OneDrive documents
- Zero user interaction required
- Complete documentation for developer handoff
- Secure, read-only access with proper scoping

---

## About Me

I'm Hamad, a Microsoft 365 & Power Platform consultant specializing in Graph API integrations, SharePoint solutions, and enterprise automation.

- 🌐 [hamad365.com](https://hamad365.com)
- 💼 [Upwork](https://www.upwork.com/freelancers/~01f28bdcd32df9fe01)
- 📧 h@hamad365.com

---

*Note: All credentials shown are placeholders. Actual client credentials have been removed for security.*
