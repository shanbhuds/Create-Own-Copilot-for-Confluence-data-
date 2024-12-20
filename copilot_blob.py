import requests
from requests.auth import HTTPBasicAuth
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import json
import os

# Confluence API Details
confluence_base_url = ' your url'
parent_page_id = 'id'
auth = HTTPBasicAuth('login id', 'pass')
 # Azure Blob Storage Details
azure_connection_string = ''
container_name = 'name'

# # Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
container_client = blob_service_client.get_container_client(container_name)

# # Create container if it doesn't exist
try:
    container_client.create_container()
except Exception as e:

     print(f"Container already exists or could not be created: {e}")

# # Function to upload content to Azure Blob Storage
def upload_to_azure_blob(content, blob_name,metadata):
   try:
       blob_client = container_client.get_blob_client(blob_name)
       blob_client.upload_blob(content, overwrite=True)
       blob_client.set_blob_metadata(metadata)
       print(f"Uploaded {blob_name} to Azure Blob Storage.")
   except Exception as e:
        print(f"Failed to upload {blob_name}: {e}")

# Function to get child pages
def get_child_pages(parent_id):
    url = f"{confluence_base_url}/{parent_id}/child/page"
    response = requests.get(url, auth=auth)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()['results']

# Function to get page content
def get_page_content(page_id):
    url = f"{confluence_base_url}/{page_id}"
    params = {'expand': 'body.storage,version'}
    response = requests.get(url, auth=auth, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    title = data['title']
    body_content = data['body']['storage']['value']
    created_date = data['version']['when']
    return title, body_content, created_date




# Recursive function to process pages
def process_page(page_id, path=''):
    try:
#         # Get page content
        title, content,created_date = get_page_content(page_id)
#         # Define blob name based on path and title
        blob_name = os.path.join(path, f"{title}.html").replace("\\", "/")
        metadata = {'created_date': created_date}
#         # Upload content to Azure Blob Storage
        upload_to_azure_blob(content, blob_name,metadata)
#         # Get child pages and process them recursively
#         child_pages = get_child_pages(page_id)
#         for child in child_pages:
#             process_page(child['id'], os.path.join(path, title))
    except Exception as e:
     print(f"An error occurred: {e}")

# Main script
if __name__ == "__main__":
   process_page(parent_page_id)
