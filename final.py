import requests
from requests.auth import HTTPBasicAuth
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os

# Confluence API Details
confluence_base_url = 'https://atlassian-dc-test.miniorange.com/wiki'
parent_page_id = '2506391559'
auth = HTTPBasicAuth('mo_conf_admin', 'L#1wmHQE')

# Azure Blob Storage Details
azure_connection_string = 'DefaultEndpointsProtocol=https;AccountName=csg100320005363b3a0;AccountKey=9n7oVbv+T6PA0lcW9cjwCutlTOxD1W2pWvhS4qCSj/swGMWdVZIG/CrN/IqcHl1UcEvdzA56NIUd+AStmoV1OQ==;EndpointSuffix=core.windows.net'
container_name = 'confluencedemo'

# Initialize Blob Service Client
def get_child_pages(parent_page_id):
    url = f"{confluence_base_url}/rest/api/content/{parent_page_id}/child/page"
    print(url,1)
    response = requests.get(url, auth=auth)
    print(response)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()['results']

# Function to get page content
def get_page_content(parent_page_id):
    url = f"{confluence_base_url}/rest/api/content/{parent_page_id}"
    print(url)
    params = {'expand': 'body.storage,version'}
    response = requests.get(url, auth=auth, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    title = data['title']
    body_content = data['body']['storage']['value']
    created_date = data['version']['when']
    return title, body_content, created_date

try:
    if azure_connection_string is None:
        raise ValueError("Azure connection string is not set. Please set the AZURE_CONNECTION_STRING environment variable.")
    blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    print("Successfully connected to Azure Blob Storage.")
except Exception as e:
    print(f"Failed to connect to Azure Blob Storage: {e}")

# Create container if it doesn't exist
#try:
    if container_client:
        container_client.create_container()
        print(f"Container '{container_name}' created successfully.")
#except Exception as e:
    else:
     print(f"Container already exists we can append data in same ")

# Function to upload content to Azure Blob Storage
def upload_to_azure_blob(content, blob_name, metadata):
    try:
        blob_client = container_client.get_blob_client(blob_name)
        if blob_client.exists():
            existing_content = blob_client.download_blob().readall().decode('utf-8')
            content = existing_content + content
        blob_client.upload_blob(content, overwrite=True)
        blob_client.set_blob_metadata(metadata)
        print(f"Uploaded {blob_name} to Azure Blob Storage.")
    except Exception as e:
        print(f"Failed to upload {blob_name}: {e}")

def process_page(page_id, path=''):
    try:
        # Get page content
        title, content, created_date = get_page_content(page_id)
        # Define blob name based on path and title
        blob_name = os.path.join(path, f"{title}.html").replace("\\", "/")
        metadata = {'created_date': created_date}
        # Upload content to Azure Blob Storage
        upload_to_azure_blob(content, blob_name, metadata)
        # Get child pages and process them recursively
        child_pages = get_child_pages(page_id)
        for child in child_pages:
            process_page(child['id'], os.path.join(path, title))
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
   process_page(parent_page_id)
