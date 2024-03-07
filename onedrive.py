import os
from msal import PublicClientApplication
import requests

# Authentication
def authenticate(client_id, tenant_id, client_secret):
    app = PublicClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant_id}", client_credential=client_secret)
    result = None
    # Look for the existing token in cache
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(["Files.Read"], account=accounts[0])

    if not result:
        # No suitable token exists in cache. Let's get a new one from AAD.
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    
    if "access_token" in result:
        return result['access_token']
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        print(result.get("correlation_id"))  # You may need this when reporting a bug
        return None

def list_and_download_files(access_token, download_folder):
    headers = {'Authorization': 'Bearer ' + access_token}
    endpoint = 'https://graph.microsoft.com/v1.0/me/drive/root/children'
    r = requests.get(endpoint, headers=headers)
    items = r.json().get('value', [])
    for item in items:
        file_name = item['name']
        download_url = item['@microsoft.graph.downloadUrl']
        print(f"Downloading {file_name}...")
        response = requests.get(download_url)
        file_path = os.path.join(download_folder, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {file_name} to {file_path}")

def main():
    client_id = 'your_client_id'
    tenant_id = 'your_tenant_id'
    client_secret = 'your_client_secret'
    download_folder = 'path/to/your/download/folder'

    access_token = authenticate(client_id, tenant_id, client_secret)
    if access_token:
        list_and_download_files(access_token, download_folder)

if __name__ == "__main__":
    main()
