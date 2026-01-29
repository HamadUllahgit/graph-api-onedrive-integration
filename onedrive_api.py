"""
OneDrive Graph API Client

A Python client for interacting with OneDrive for Business via Microsoft Graph API.
Uses OAuth2 Client Credentials flow for application-level access.

Usage:
    from onedrive_api import OneDriveClient
    
    client = OneDriveClient(
        tenant_id="your-tenant-id",
        client_id="your-client-id",
        client_secret="your-client-secret",
        user_email="user@domain.com"
    )
    
    # List files
    files = client.list_files()
    
    # Download a file
    content = client.download_file(file_id)
"""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any


class OneDriveClient:
    """Client for OneDrive Graph API operations."""
    
    GRAPH_URL = "https://graph.microsoft.com/v1.0"
    TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        user_email: str
    ):
        """
        Initialize the OneDrive client.
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: Application (client) ID
            client_secret: Client secret value
            user_email: Target user's email address
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_email = user_email
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
    
    @property
    def access_token(self) -> str:
        """Get valid access token, refreshing if needed."""
        if self._is_token_expired():
            self._refresh_token()
        return self._access_token
    
    def _is_token_expired(self) -> bool:
        """Check if current token is expired or missing."""
        if not self._access_token or not self._token_expiry:
            return True
        # Refresh 5 minutes before expiry
        return datetime.utcnow() >= (self._token_expiry - timedelta(minutes=5))
    
    def _refresh_token(self) -> None:
        """Request new access token from Azure AD."""
        url = self.TOKEN_URL.format(tenant=self.tenant_id)
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self._access_token = token_data["access_token"]
        # Token typically valid for 1 hour
        expires_in = token_data.get("expires_in", 3600)
        self._token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authorization."""
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """Make authenticated request to Graph API."""
        url = f"{self.GRAPH_URL}{endpoint}"
        headers = self._get_headers()
        headers.update(kwargs.pop("headers", {}))
        
        response = requests.request(method, url, headers=headers, **kwargs)
        
        # Handle token expiry during request
        if response.status_code == 401:
            self._refresh_token()
            headers = self._get_headers()
            response = requests.request(method, url, headers=headers, **kwargs)
        
        response.raise_for_status()
        return response
    
    def list_files(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files and folders in OneDrive.
        
        Args:
            folder_id: Optional folder ID. If None, lists root folder.
            
        Returns:
            List of file/folder objects with metadata.
        """
        if folder_id:
            endpoint = f"/users/{self.user_email}/drive/items/{folder_id}/children"
        else:
            endpoint = f"/users/{self.user_email}/drive/root/children"
        
        response = self._make_request("GET", endpoint)
        return response.json().get("value", [])
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific file.
        
        Args:
            file_id: The file's unique ID.
            
        Returns:
            File metadata including name, size, dates, etc.
        """
        endpoint = f"/users/{self.user_email}/drive/items/{file_id}"
        response = self._make_request("GET", endpoint)
        return response.json()
    
    def download_file(self, file_id: str) -> bytes:
        """
        Download file content.
        
        Args:
            file_id: The file's unique ID.
            
        Returns:
            File content as bytes.
        """
        endpoint = f"/users/{self.user_email}/drive/items/{file_id}/content"
        response = self._make_request("GET", endpoint, allow_redirects=True)
        return response.content
    
    def search_files(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for files by name.
        
        Args:
            query: Search term.
            
        Returns:
            List of matching files.
        """
        endpoint = f"/users/{self.user_email}/drive/root/search(q='{query}')"
        response = self._make_request("GET", endpoint)
        return response.json().get("value", [])
    
    def get_file_by_path(self, path: str) -> Dict[str, Any]:
        """
        Get file by its path in OneDrive.
        
        Args:
            path: File path (e.g., "/Documents/report.pdf")
            
        Returns:
            File metadata.
        """
        # URL encode the path
        encoded_path = requests.utils.quote(path)
        endpoint = f"/users/{self.user_email}/drive/root:{encoded_path}"
        response = self._make_request("GET", endpoint)
        return response.json()


# Example usage
if __name__ == "__main__":
    import os
    
    # Load credentials from environment variables
    client = OneDriveClient(
        tenant_id=os.environ["TENANT_ID"],
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        user_email=os.environ["USER_EMAIL"]
    )
    
    # List root files
    print("Files in root:")
    for item in client.list_files():
        item_type = "📁" if "folder" in item else "📄"
        print(f"  {item_type} {item['name']}")
    
    # Search for documents
    print("\nSearch results for 'report':")
    for item in client.search_files("report"):
        print(f"  📄 {item['name']}")
