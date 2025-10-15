# utils.py
import os
import shutil

def ensure_dirs():
    base = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(base, exist_ok=True)
    os.makedirs(os.path.join(base, "answer_keys"), exist_ok=True)

def copy_answer_key_to_store(src_path):
    """
    Copy uploaded answer key to data/answer_keys with timestamped name.
    Returns destination path and filename.
    """
    import time
    if not os.path.exists(src_path):
        raise FileNotFoundError(src_path)
    dest_dir = os.path.join(os.path.dirname(__file__), "data", "answer_keys")
    os.makedirs(dest_dir, exist_ok=True)
    base = os.path.basename(src_path)
    name, ext = os.path.splitext(base)
    ts = int(time.time())
    dest_name = f"{name}_{ts}{ext}"
    dest_path = os.path.join(dest_dir, dest_name)
    shutil.copy2(src_path, dest_path)
    return dest_path, dest_name
