import nbformat as nbf
from typing import Optional
from random_filename import get_random_name


def create_notebook(text_content, output_file: Optional[str] = 'output.ipynb'):


    
    if output_file == 'output.ipynb' or output_file == None:
        output_file = get_random_name()
        
    # Initialize notebook object
    nb = nbf.v4.new_notebook()

    # Process the text content
    lines = text_content.split("\n")
    in_code_block = False
    code_lines = []
    markdown_lines = []

    for line in lines:
        if not in_code_block and "```python" in line:
            in_code_block = True
            if markdown_lines:
                markdown_cell = nbf.v4.new_markdown_cell("\n".join(markdown_lines))
                nb.cells.append(markdown_cell)
                markdown_lines.clear()
        elif in_code_block and "```" in line:
            in_code_block = False
            if code_lines:
                code_cell = nbf.v4.new_code_cell("\n".join(code_lines))
                nb.cells.append(code_cell)
                code_lines.clear()
        elif in_code_block:
            code_lines.append(line)
        else:
            markdown_lines.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    return output_file



def create_notebook_from_file(text_file, output_file: Optional[str] = 'output.ipynb'):

    with open(text_file, "r", encoding="utf-8") as f:
        text_content = f.read()
        notebook = create_notebook(text_content, output_file)

    return notebook
    

