import os

def format_bytes(size):
    """Formats bytes to a human-readable string."""
    if size is None:
        return "0 B"
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    size = float(size)
    while size > power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

def get_file_info(path):
    """Returns basic file info for UI feedback."""
    if not path or not isinstance(path, str) or not os.path.exists(path):
        return {"size_str": "0 B", "ext": "N/A", "modified": 0}
    
    try:
        size = os.path.getsize(path)
        return {
            "size_str": format_bytes(size),
            "ext": os.path.splitext(path)[1].lower().replace('.', ''),
            "modified": os.path.getmtime(path)
        }
    except Exception:
        return {"size_str": "Error", "ext": "ERR", "modified": 0}

def validate_path(path):
    """Ensures the directory for the path exists."""
    if not path or not isinstance(path, str):
        return False
    try:
        directory = os.path.dirname(os.path.abspath(path))
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    except Exception:
        return False
