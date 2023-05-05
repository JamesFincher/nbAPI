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
#custom openapi spec
from fastapi.openapi.utils import get_openapi


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
@app.get('/')
async def root():
    return {"message": "Hello World... API is working fine"}

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

@app.post("/create_notebook_text/")
async def create_notebook_text(input_text: str , output: Optional[str] = 'output.ipynb'):
    # If the output is not provided, assign a unique file name
    if output == 'output.ipynb' or None:
        timestamp = int(time.time())
        random_hash = uuid.uuid4().hex[:8]
        output = f"output_{timestamp}_{random_hash}.ipynb"

   
    txt = input_text
    print(txt)
    nb = parse_input_text(txt)

    with open(output, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)

    with open(output, "r", encoding="utf-8") as f:
        contents = f.read()

    contents_base64 = base64.b64encode(contents.encode("utf-8")).decode("utf-8")
    commit_message = f"Created {output} via FastAPI"
    github_url = create_github_file(output, contents_base64, commit_message)

    return JSONResponse(content={"result": f"Notebook '{output}' created successfully.", "github_url": github_url})


@app.get("/spec")
async def openapi_spec():
    spec =  {
  "openapi": "3.1.0",
  "info": {
    "title": "FastAPI",
    "version": "0.1.0"
  },
  "paths": {
    "/": {
      "get": {
        "summary": "Root",
        "operationId": "root__get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/create_notebook/": {
      "post": {
        "summary": "Create Notebook",
        "operationId": "create_notebook_create_notebook__post",
        "parameters": [
          {
            "required": "false",
            "schema": {
              "title": "Output",
              "type": "string",
              "default": "output.ipynb"
            },
            "name": "output",
            "in": "query"
          }
        ],
        "requestBody": {
          "content": {
            "multipart/form-data": {
              "schema": {
                "$ref": "#/components/schemas/Body_create_notebook_create_notebook__post"
              }
            }
          },
          "required": 'true'
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Body_create_notebook_create_notebook__post": {
        "title": "Body_create_notebook_create_notebook__post",
        "required": [
          "input_file"
        ],
        "type": "object",
        "properties": {
          "input_file": {
            "title": "Input File",
            "type": "string",
            "format": "binary"
          }
        }
      },
      "HTTPValidationError": {
        "title": "HTTPValidationError",
        "type": "object",
        "properties": {
          "detail": {
            "title": "Detail",
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/ValidationError"
            }
          }
        }
      },
      "ValidationError": {
        "title": "ValidationError",
        "required": [
          "loc",
          "msg",
          "type"
        ],
        "type": "object",
        "properties": {
          "loc": {
            "title": "Location",
            "type": "array",
            "items": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "integer"
                }
              ]
            }
          },
          "msg": {
            "title": "Message",
            "type": "string"
          },
          "type": {
            "title": "Error Type",
            "type": "string"
          }
        }
      }
    }
  }
}

    return spec

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI",
        version="0.1.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
        servers=[{"url": "https://nbapi.fincher.dev/"}],

    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi