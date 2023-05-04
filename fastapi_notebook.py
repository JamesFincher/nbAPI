import base64
import os
import requests
import shutil
import time
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import nbformat as nbf
from typing import Optional
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Configure these according to your GitHub setup
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO_OWNER = os.environ["REPO_OWNER"]
REPO_NAME = os.environ["REPO_NAME"]
BRANCH_NAME = os.environ["BRANCH_NAME"]

app = FastAPI()
print(GITHUB_TOKEN, REPO_OWNER)
def parse_input_text(text: str) -> str:
    nb = nbf.v4.new_notebook()

    cell_type = None
    cell_content = ""

    for line in text.splitlines():
        cell_type, cell_content = process_line(line, cell_type, cell_content, nb)

    # Append the last cell
    append_cell(cell_type, cell_content, nb)

    return nb

def process_line(line, cell_type, cell_content, nb):
    if line.startswith("# "):
        append_cell(cell_type, cell_content, nb)
        cell_content = f"<h1>{line[1:].strip()}</h1>\n"
        cell_type = "markdown"
    elif line.startswith("## "):
        append_cell(cell_type, cell_content, nb)
        cell_content = f"<h2>{line[2:].strip()}</h2>\n"
        cell_type = "markdown"
    elif line.startswith("```python"):
        append_cell(cell_type, cell_content, nb)
        cell_type = "code"
        cell_content = ""
    elif line.startswith("```"):
        append_cell(cell_type, cell_content, nb, is_code=True)
        cell_type = None
    else:
        if cell_type:
            cell_content += line + "\n"

    return cell_type, cell_content

def append_cell(cell_type, cell_content, nb, is_code=False):
    if not cell_type:
        return
    cell = nbf.v4.new_markdown_cell(cell_content) if cell_type == "markdown" else nbf.v4.new_code_cell(cell_content)
    nb.cells.append(cell)
    if is_code:
        nb.cells.append(nbf.v4.new_code_cell(cell_content))

def create_github_file(file_path, file_content, commit_message):
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

@app.post("/create_notebook/")
async def create_notebook(input_file: UploadFile = File(...), output: Optional[str] = 'output.ipynb'):
    # If the output is not provided, assign a unique file name
    if output == 'output.ipynb' or None:
        timestamp = int(time.time())
        random_hash = uuid.uuid4().hex[:8]
        output = f"output_{timestamp}_{random_hash}.ipynb"

    with open(input_file.filename, "wb") as buffer:
        shutil.copyfileobj(input_file.file, buffer)

    with open(input_file.filename, "r", encoding="utf-8") as f:
        txt = f.read()

    nb = parse_input_text(txt)

    with open(output, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)

    with open(output, "r", encoding="utf-8") as f:
        contents = f.read()

    contents_base64 = base64.b64encode(contents.encode("utf-8")).decode("utf-8")
    commit_message = f"Created {output} via FastAPI"
    github_url = create_github_file(output, contents_base64, commit_message)

    return JSONResponse(content={"result": f"Notebook '{output}' created successfully.", "github_url": github_url})
