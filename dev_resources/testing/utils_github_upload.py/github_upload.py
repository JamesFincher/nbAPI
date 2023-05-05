import os
from fastapi import HTTPException
import requests
import base64
from dotenv import load_dotenv

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO_OWNER = os.environ["REPO_OWNER"]
REPO_NAME = os.environ["REPO_NAME"]
BRANCH_NAME = os.environ["BRANCH_NAME"]

def create_github_file(file_path):
    commit_message=f'Add {file_path} from API'
    contents = open(file_path).read()
    
    file_content = base64.b64encode(contents.encode("utf-8")).decode("utf-8")

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json',
    }

    url = (
        f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}?ref={BRANCH_NAME}'
    )
    data = {
        'message': commit_message,
        'content': file_content,
        'branch': BRANCH_NAME,
    }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()['content']['html_url']
    else:
        raise HTTPException(status_code=response.status_code, detail="Error creating file on GitHub")