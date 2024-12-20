import requests
from requests.auth import HTTPBasicAuth
import time 

confluence_base_url = 'https://atlassian-dc-test.miniorange.com/wiki'
parent_page_id = '2506391559'
auth = HTTPBasicAuth('mo_conf_admin', 'L#1wmHQE')

def get_page_content(parent_page_id, retries=3, timeout=10):
    url = f"{confluence_base_url}/rest/api/content/{parent_page_id}"
    params = {'expand': 'body.storage,version'}
    for attempt in range(retries):
        try:
            response = requests.get(url, auth=auth, params=params, timeout=timeout)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            title = data['title']
            body_content = data['body']['storage']['value']
            created_date = data['version']['when']
            return title, body_content, created_date
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            if attempt < retries - 1:
                print("Retrying...")
                time.sleep(2)  # Wait for 2 seconds before retrying
            else:
                raise
        except Exception as err:
            print(f"Other error occurred: {err}")
            raise

try:
    title, content, created_date = get_page_content(parent_page_id)
    print(f"Title: {title}, Created Date: {created_date}")
    print(content)
except Exception as e:
    print(f"An error occurred: {e}")