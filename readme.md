# FastAPI Notebook Creator

A FastAPI web service that creates Jupyter notebooks from text input or files, and commits the generated notebooks to a specified GitHub repository.

## Table of contents
- [Description](#description)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)

## Description

The service accepts input text (with specific formatting) or a file and generates a Jupyter notebook from it. It then commits the generated notebook to a specified GitHub repository, returning the GitHub URL of the notebook.

The input text should have the following format:
- `#` followed by a space, for an `<h1>` markdown cell.
- `##` followed by a space, for an `<h2>` markdown cell.
- Triple backticks followed by "python" to start a code cell, and triple backticks again to close it.

## Installation

1. Clone the repository.
    ```
    git clone https://github.com/your-username/repository-name.git
    ```
2. Create a virtual environment and activate it.
    ```
    python -m venv venv
    source venv/bin/activate
    ```
3. Install the required packages from `requirements.txt` using pip.
    ```
    pip install -r requirements.txt
    ```
4. Rename the `.env.sample` file to `.env` and fill in your GitHub token, repository owner, repository name, and branch.

## Configuration

Set environment variables in the starter `.env` file. Fill in the following environment variable values:

```
GITHUB_TOKEN=your_github_token_here
REPO_OWNER=your_repo_owner_here
REPO_NAME=your_repo_name_here
BRANCH_NAME=your_branch_name_here
```

## Usage

1. Start the FastAPI server.
    ```
    uvicorn main:app --reload
    ```

2. Access the interactive documentation at http://localhost:8000/docs.

## API Endpoints

- `GET /`: Get a status message to check if the API is working fine
- `POST /create_notebook/`: Create a Jupyter notebook from an uploaded file
    - Input: FormData with file containing input text
    - Output: JSON with a message indicating the success result, and the GitHub URL of the created notebook
- `POST /create_notebook_text/`: Create a Jupyter notebook from a text input
    - Input: Form input containing text (content type: `application/x-www-form-urlencoded`)
    - Output: JSON with a message indicating the success result, and the GitHub URL of the created notebook