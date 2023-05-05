import time
import uuid


def get_random_name():
    timestamp = int(time.time())
    hash = uuid.uuid4().hex[:6].upper()
    filename : str = f"Notebook_{timestamp}_{hash}.ipynb" 
    return filename